#from crypt import methods
import os
import secrets
from shutil import ExecError
from statistics import quantiles
from flask import render_template, request, Blueprint, flash, redirect, url_for, current_app, session
from flaskblog import db,photos, app
from flaskblog.models import Brand, Category, Addproduct
from flaskblog.admin.forms import AddProducts
from flaskblog.admin.utils import MagerDicts
from  sqlalchemy.sql.expression import func

cart = Blueprint('cart', __name__)


#---------------------------------------------------Produkt zum Warenkorb hinzufügen---------------------------------------------------------
@cart.route('/addcart', methods=['POST'] )
def AddCart():
    #Es wird versucht "product_id", "quantity" und "colors" aus dem Eingabeformular abzurufen
    try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        colors = request.form.get('colors')
        #Anhand der Produkt ID wird dann das entsprechende Produkt aus der Datenbank abgerufen. 
        product = Addproduct.query.filter_by(id=product_id).first()
        #Beim Klick auf den Button, werden dann alle Informationen über das Produkt in ein Dictionary "DictItems" eingefügt.
        if product_id and quantity and colors and request.method == "POST":
            DictItems = {product_id: {'name': product.name, 'price': product.price, 'discount': product.discount, 'color': colors, 'quantity': quantity, 'image': product.image_1, 'colors': product.colors}}
            # Wenn das Produkt bereits im Warenkorb ist, wird die Menge um 1 erhöht.
            if 'Shoppingcart' in session:
                if product_id in session['Shoppingcart']:
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += 1
                            flash("Das Produkt wurde zum Warenkorb hinzugefügt!", "success")
                #Wenn "Shoppingcart" bereits in der Session vorhanden ist (also bereits ein Produkt im Warenkorb liegt), das ausgwählte Produkt jedoch noch nicht, dann wird das neue Produkt zur Session hinzugefügt.
                #Hierfür wird die Funktion "MagerDicts" genutzt, um die Dictionarys zu verbinden. 
                else:
                    session['Shoppingcart'] = MagerDicts(session['Shoppingcart'], DictItems)
                    print(session['Shoppingcart'])
                    flash("Das Produkt wurde zum Warenkorb hinzugefügt!", "success")
                    return redirect(request.referrer)
            
            #Wenn noch keine Session "Shoppingcart" existiert, wird das Dictionary in die Session eingefügt.
            else:
                session['Shoppingcart'] = DictItems
                flash("Das Produkt wurde zum Warenkorb hinzugefügt!", "success")
                return redirect(request.referrer)

    except Exception as e:
        print(e)

    finally:
        return redirect(request.referrer)
#---------------------------------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------Inhalte aus dem Warenkorb abrufen---------------------------------------------------------
@cart.route('/carts')
def getCart():
    #Wenn der Warenkorb leer ist, wird "empty" dem Template übergeben.
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        empty = "empty"
        return render_template("products/carts.html", empty = empty)
    #Wenn der Warenkorb nicht leer ist, werden discount, subtotal, tax und grandtotal aus den Produkten im Warenkorb berechnet und am Ende dem Template übergeben.
    subtotal = 0
    grandtotal = 0
    for key, product in session['Shoppingcart'].items():
        discount = (product['discount']/100 * float(product['price']))
        subtotal += float(product['price']) * int(product['quantity'])
        subtotal -= discount * int(product['quantity'])
        tax = ("%.2f" % (.19 * float (subtotal)))
        grandtotal = float("%.2f" % (subtotal))

    #Produktempfehlung
    #products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.pub_date.desc()).limit(4)
    keys = list(session['Shoppingcart'].keys())
    if len(session['Shoppingcart']) >=2:
        #Es werden die Produkt-IDs von den ersten beiden Warenkorbeinträgen aus der Session ermittelt
        id_1 = keys[0]
        id_2 = keys[1]

        #Beide Produkte werden anschließend aus der Datenbank abgerufen
        product_1 = Addproduct.query.filter_by(id = id_1).first()
        product_2 = Addproduct.query.filter_by(id = id_2).first()

        #Im nächsten Schritt werden die zugehörigen Marken IDs ermittelt und in einer Liste zusammengefasst
        brand_id_1 = product_1.brand_id
        brand_id_2 = product_2.brand_id
        brands = [brand_id_1, brand_id_2]

        #Es werden nun die Produkte von den passenden Marken zufällig aus der Datenbank gezogen
        products = Addproduct.query.filter(Addproduct.brand_id.in_(brands)).order_by(func.random()).limit(4)
    
    #Ist nur ein Produkt im Warenkorb, so werden die Empfehlungen nur anhand der Marke des einen Produktes ausgeben
    else:
        id_1 = keys[0]
        product_1 = Addproduct.query.filter_by(id = id_1).first()
        brand_id_1 = product_1.brand_id
        products = Addproduct.query.filter(Addproduct.brand_id == brand_id_1).order_by(func.random()).limit(4)
    

    return render_template("products/carts.html", tax = tax, grandtotal = grandtotal, products=products)
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------Produkt im Warenkorb aktualisieren-------------------------------------------------------
@cart.route('/updatecart/<int:code>', methods=['POST'])
def updatecart(code):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('main.home'))

    #Wird der "Aktualsieren" Button geklickt, wird die Menge und die Farbe angepasst.
    #Dabei werden die Menge und die Farbe aus dem Formular abgerufen.
    if request.method == "POST":
        #Die Maximale Menge ist der Lagerbestand eines Produktes.
        max_quantity = Addproduct.query.filter_by(id = code).first()
        quantity = request.form.get('quantity')
        color = request.form.get('color')
        #Hier werden die neuen Angaben zu Farbe und Menge in die Session geschrieben.
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['color'] = color
                    #Die Menge wird nur aktualisiert, wenn der Lagerbestand nicht überschritten wurde.
                    if int(quantity) <= max_quantity.stock:
                        item['quantity'] = quantity
                        flash(f'Das Produkt wurde aktualisiert.', 'success')
                    #Wenn eine größere Menge als der aktuelle Lagerbestand eingegeben wird, wird die Menge auf den maximalen Lagerbestand reduziert.
                    else:
                        item['quantity'] = str(max_quantity.stock)
                        flash(f'Es sind nicht genügend Produkte auf Lager, Ihre Menge wurde auf die maximale Anzahl reduziert.', 'info')
                    return redirect(url_for('cart.getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('cart.getCart'))
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------Produkt aus Warenkorb löschen------------------------------------------------------------
@cart.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('main.home'))
    #Wenn der "Löschen" Button im Warenkorb geklickt wird, wird das Produkt aus dem Warenkorb gelöscht.
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
        return redirect(url_for('cart.getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('cart.getCart'))
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------Kompletten Warenkorb löschen-------------------------------------------------------------
@cart.route('/clearcart')
def clearcart():
    #Wenn der "Alles löschen" Button im Warenkorb geklickt wird, werden alle Produkte aus dem Warenkorb gelöscht.
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('cart.getCart'))
    except Exception as e:
        print(e)
#--------------------------------------------------------------------------------------------------------------------------------------------  