#from crypt import methods
from operator import methodcaller
from re import sub
#from turtle import update
from flask import render_template, url_for, flash, redirect, request, Blueprint, session, make_response
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post, CustomerOrder, Addproduct
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,RequestResetForm, ResetPasswordForm)
from flaskblog.users.utils import save_picture, send_reset_email
import secrets
#pip install pdfkit
import pdfkit
import stripe

#Die beiden Keys werden benötigt, um Zahlungen über Stripe abzuwickeln. 
#Sie werden nach der Registrierung bei Stripe bereitgestellt. 
publishable_key = 'pk_test_51L9UNpJhnXbsS5Vr4IxJ4ps85ZnAw9pRR0na1Qkg5eRo0cMOSXvZda5IK1whxO4J2pELlkViz7PMPqVpcJp62fQI00Dyl1548s'
stripe.api_key= 'sk_test_51L9UNpJhnXbsS5VrT34iWSPZfZgvdxUCOfOkEM6Grqzm4ERjlOZqvvnv19DmDW5oZHAW07LEFXip9cOPSSWEHQiC006vpEK3A1'

users = Blueprint('users', __name__)

#---------------------------------------------------Benutzerregistrierung--------------------------------------------------------------------
@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(firstname=form.firstname.data,lastname=form.lastname.data,username=form.username.data, email=form.email.data, password=hashed_password, country=form.country.data, state=form.state.data, city = form.city.data, contact = form.contact.data, address = form.address.data, zipcode = form.zipcode.data)
        db.session.add(user)
        db.session.commit()
        flash('Das Konto wurde erstellt. Sie können sich jetzt einloggen.', "success")
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------User Login-------------------------------------------------------------------------------
@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Sie sind erfolgreich eingeloggt', 'success')
             #Code 307 übergibt die method "POST" an das nächste Template, ohne dass erneut ein Button geklickt werden muss.
            return redirect(next_page, code=307) if next_page else redirect(url_for('main.home'))
        #if form.email.data == 'admin@blog.com' and form.password.data == 'password':
        #    flash('Sie sind erfolgreich angemeldet', 'success')
        #    return redirect(url_for('home'))
        else:
            flash('Anmeldung fehlgeschlagen. Bitte prüfen Sie Email und Kennwort', 'danger')
            return redirect(url_for('users.login'))
            

    return render_template('login.html', title='Login', form=form)
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------User Logout------------------------------------------------------------------------------
@users.route("/Ausloggen")
def logout():
    logout_user()
    flash('Sie wurden erfolgreich abgemeldet', 'success')
    return redirect(url_for('main.home'))
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------Anzeigen der Kontoübersicht--------------------------------------------------------------
@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.country = form.country.data
        current_user.state = form.state.data
        current_user.city = form.city.data
        current_user.contact = form.contact.data
        current_user.address = form.address.data
        current_user.zipcode = form.zipcode.data
        db.session.commit()
        flash('Ihr Konto wurde erfolgreich aktualisiert!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.country.data = current_user.country
        form.state.data = current_user.state
        form.city.data = current_user.city
        form.contact.data = current_user.contact
        form.address.data = current_user.address
        form.zipcode.data = current_user.zipcode
    # Image file Variable, die auf das richtige Bild berweisen wird
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file = image_file, form=form)
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------User Posts-------------------------------------------------------------------------------
@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    return render_template("user_posts.html", posts=posts, user=user)
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------Passwort zurücksetzen--------------------------------------------------------------------
@users.route("/passwort_zurücksetzen", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Eine Email zum Zurücksetzen des Passwortes wurde versendet', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Passwort zurücksetzen', form=form)
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------Reset Token für Passwort zurücksetzen----------------------------------------------------
@users.route("/passwort_zurücksetzen/<token>", methods=['GET', 'POST'])
def reset_token(token):
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        user = User.verify_reset_token(token)
        if user is None:
            flash('Es handelt sich um einen ungültigen Schlüssel', 'warning')
            return redirect(url_for('users.reset_request'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash('Das Passwort wurde erfolgreich zurückgesetzt')
            return redirect(url_for('users.login'))
        return render_template ('reset_token.html', title='Passwort zurücksetzen', form=form)
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------Anzeigen der Bestellübersicht------------------------------------------------------------
@users.route("/orders", methods=["POST"])
#Der Benutzer muss eingeloggt sein, um die Seite zu sehen.
@login_required
def orders():
    #Wenn der Nutzer im Warenkorb auf den Button "Bestellung abschließen", wird überprüft, ob der Nutzer eingeloggt ist. 
    if request.method == "POST":
        if current_user.is_authenticated:
            grandTotal = 0
            subTotal = 0
            #Auf Basis der aktuellen User ID, werden Informationen zum Nutzer aus der Datenbank abgerufen und an das Template übergeben.
            customer_id = current_user.id
            customer = User.query.filter_by(id=customer_id).first()
            #Aus der Session werden alle Informationen zu den Produkten abgerufen.
            #Die Informationen werden mit Umformungen/Berechnungen in die benötigte Form gebracht und an das Template übergeben. 
            for key, product in session['Shoppingcart'].items():
                discount = (product['discount']/100 * float(product['price']))
                subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount * int(product['quantity'])
                tax = ("%.2f" % (.19 * float (subTotal)))
                grandTotal = float("%.2f" % (subTotal))
                amount = int(grandTotal*100)
    #Ist der Nutzer nicht eingeloggt, wird er zur Login-Seite weitergeleitet.
    else:
        return redirect(url_for('login'))

    return render_template("order.html", tax = tax, grandTotal = grandTotal, customer = customer, amount=amount)
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------Kartenzahlung mit Stripe-----------------------------------------------------------------
@users.route('/payment', methods =['POST'])
#Der Benutzer muss eingeloggt sein, um die Seite zu sehen.
@login_required
def payment():
    customer_id = current_user.id
    #Es wird eine Rechnungsnummer erzeugt.
    invoice = secrets.token_hex(5)
    #Der zu zahlende Betrag wird vom Template aus dem Formular übernommen.
    amount = request.form.get('amount')
    try:
            order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders = session['Shoppingcart'])
            #Der Lagerbestand wird um die bestellte Menge reduziert. 
            for key, product in session['Shoppingcart'].items():
                quantity = int(product['quantity'])
                updatestock = Addproduct.query.get_or_404(key)
                stock = updatestock.stock
                newstock = stock - quantity
                updatestock.stock = newstock
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            
    except Exception as e:
            print(e)
            flash(f'Something went wrong while getting order', 'danger')
            return redirect(url_for('cart.getCart'))

    #Wenn die Bestellung in die Datenbank geschrieben werden konnte, wird die Zahlung über Stripe abgewickelt.
    customer = stripe.Customer.create(
    email=request.form['stripeEmail'],
    source=request.form['stripeToken'],
    )

    charge = stripe.Charge.create(
    customer=customer.id,
    description='REDENI',
    amount=amount,
    currency='eur',
    )

    #Bei erfolgreicher Zahlung, wird der Bestallstatus von "Pending" zu "Paid" geändert.
    orders = CustomerOrder.query.filter_by(customer_id=current_user.id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()

    #Abschließend wird die Thank-You Seite ausgegeben.
    #Code 307 übergibt die method "POST" an das nächste Template, ohne dass erneut ein Button geklickt werden muss.
    return redirect(url_for('users.thanks', invoice=invoice), code=307)
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------Thank-You Page---------------------------------------------------------------------------
@users.route('/thanks/<invoice>', methods=["POST"])
#Die Rechnungsnummer wird von der Zahlungsabwicklung an die thanks-Methode übergeben. 
def thanks(invoice):
    if request.method == "POST":
        if current_user.is_authenticated:
            #Aus der Datenbank werden alle Informationen zu der neusten Bestellung des Kunden abgerufen.
            #Die Informationen werden mit Umformungen/Berechnungen in die benötigte Form gebracht und an das Template übergeben. 
            grandTotal = 0
            subTotal = 0
            customer_id = current_user.id
            customer = User.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
            for _key, product in orders.orders.items():
                discount = (product['discount']/100) * float(product['price'])
                subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount * int(product['quantity'])
                tax = ("%.2f" % (.19 * float(subTotal)))
                grandTotal = float("%.2f" % (subTotal))
                amount = int(grandTotal*100)
        else:
            return redirect(url_for('users.login'))

        return render_template('thank_you.html', invoice=invoice, tax=tax, subTotal=subTotal, grandTotal=grandTotal, customer=customer, orders=orders, amount=amount)
        
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------Anzeigen der Bestellhistorie-------------------------------------------------------------
@users.route("/orderhistory")
#Der Benutzer muss eingeloggt sein, um die Seite zu sehen.
@login_required
def orderhistory():
    #Wenn der Nutzer eingeloggt ist, werden alle vom Nutzer getätigten Bestellungen anhand der Nutzer ID aus der Datenbank abgerufen und an das Template übergeben.
    if current_user.is_authenticated:
        grandTotal = 0
        customer_id = current_user.id
        customer = User.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.date_created.desc()).all()
    else:
        return redirect(url_for('login'))

    return render_template('order_history.html', customer=customer, orders=orders, grandTotal = grandTotal)
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------Anzeigen einer Bestellung, wenn aus Bestellhistorie aufgerufen---------------------------
@users.route("/showorder/<invoice>")
#Der Benutzer muss eingeloggt sein, um die Seite zu sehen.
@login_required
#Beim Klick auf den Button "Bstellung Anzeigen" in der Bestellübersicht, wird die entsprechende Rechnungsnummer übergeben.
def showorder(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        #Auf Basis der ID des aktuell eingeloggten Nutzers, wird der Nutzer aus der Datenbank abgerufen.
        customer = User.query.filter_by(id=customer_id).first()
        #Anhand der übergebenen Rechnungsnummer, wird die zugehörige Bestellung aus der Datenbank abgerufen.  
        orders = CustomerOrder.query.filter_by(customer_id=customer_id).filter_by(invoice = invoice).first()
        #Anschließend werden die Informationen aus der Bestellung aufbereitet (Berechnungen) und an das Template übergeben.
        for _key, product in orders.orders.items():
            discount = (product['discount']/100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount * int(product['quantity'])
            tax = ("%.2f" % (.19 * float(subTotal)))
            grandTotal = float("%.2f" % (subTotal))
            amount = int(grandTotal*100)
    else:
        return redirect(url_for('login'))
    return render_template('show_order.html', invoice = invoice, tax=tax, subTotal=subTotal, grandTotal=grandTotal, customer=customer, orders=orders, amount=amount)
#--------------------------------------------------------------------------------------------------------------------------------------------  
