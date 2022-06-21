import os
import secrets
from flask import render_template, request, Blueprint, flash, redirect, url_for, current_app, session
from flaskblog import db,photos, app
from flaskblog.models import Brand, Category, Addproduct
from flaskblog.admin.forms import AddProducts
from flaskblog.admin.utils import MagerDicts
from flask_login import login_required, current_user

admin = Blueprint('admin', __name__)

#---------------------------------------------------Kontext Prozessor----------------------------------------------------
#Übergibt Daten an alle Templates. Wird genutzt, um die Kategorien aus der Datenbank auszulesen und in layout.html in der Navbar darzustellen
@app.context_processor
def inject_menu():
    # Zeigt nur Kategorien an, für die es auch passende Produkte gibt. 
    categories2 = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    brands3 = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    # Zeigt alle Kategorien in Dropdown Menü an
    return dict(categories2=categories2, brands3 = brands3)
#-----------------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------Hinzufügen einer Marke----------------------------------------------------
@admin.route('/addbrand', methods=['GET', 'POST'])
#Um die Seite aufzurufen, muss man eingeloggt sein.
@login_required
def addbrand():
    #Es wird überprüft, welche User-ID der aktuelle benutzer hat. Nur User-ID 1 (Admin) hat Zugriff auf die Seite
    user_id = current_user.id
    if user_id == 1:
        # Wird eine Marke hinzugefügt und das Formular abgeschickt, wird die neue Marke zur Datenbank hinzugefügt
        if request.method=="POST":
            getbrand = request.form.get('brand')
            brand = Brand(name=getbrand)
            db.session.add(brand)
            #Es wird eine Erfolgsnachricht ausgegeben.
            flash(f'Die Marke "{getbrand}" wurde zur Datenbank hinzugefügt!', 'success')
            db.session.commit()
            #Anschließend wird der Nutzer auf die gleiche Seite geleitet und kann weitere Marken hinzufügen
            return redirect(url_for("admin.addbrand"))

        return render_template('products/addbrand.html', addbrands = 'addbrands')
    
    #Wenn der Nutzer keine Admin-Rechte besitzt, wird eine entsprechende Nachricht ausgegeben.
    else: 
        flash("Entschuldigung. Um diese Website zu sehen, brauchen Sie Administratorenrechte!", "info")
        return redirect(url_for('users.login'))
#-----------------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------Marken anzeigen (Adminansicht)--------------------------------------------
@admin.route("/brands")
#Um die Seite aufzurufen, muss man eingeloggt sein.
@login_required
def brands():
    #Es wird überprüft, welche User-ID der aktuelle benutzer hat. Nur User-ID 1 (Admin) hat Zugriff auf die Seite
    user_id = current_user.id
    if user_id == 1:
        #Aus der Tabelle "Brand" der Datenbank werden alle Marken nach ihrer ID abgerufen und absteigend sortiert. 
        brands = Brand.query.order_by(Brand.id.desc()).all()
        #Das Template wird gerendert und die abgerufenen Marken werden übergeben.
        return render_template("products/brands.html", title = "Marken", brands = brands)

    #Wenn der Nutzer keine Admin-Rechte besitzt, wird eine entsprechende Nachricht ausgegeben und zur Login-Page weitergeleitet.
    else: 
        flash("Entschuldigung. Um diese Website zu sehen, brauchen Sie Administratorenrechte!", "info")
        return redirect(url_for('users.login'))
#-----------------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------Marke ändern / umbenennen-------------------------------------------------
@admin.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
#Um die Seite aufzurufen, muss man eingeloggt sein.
@login_required
def updatebrand(id):
    #Es wird überprüft, welche User-ID der aktuelle benutzer hat. Nur User-ID 1 (Admin) hat Zugriff auf die Seite
    user_id = current_user.id
    if user_id == 1:
        #Aus der Datenbank wird die Marke anhand ihrer ID abgerufen. 
        #Die ID wird beim Klick auf der Seite vom html-Template an die Funktion "updatebrand" übergeben.
        updatebrand = Brand.query.get_or_404(id)
        #Die vom Nutzer in das Formular eingebene neue Marke wird in der Variablen "brand" gespeichert.
        brand = request.form.get('brand')
        #Beim abschicken des Formulars, wird die neue Marke dann in die Datenbank geschrieben.
        if request.method=="POST":
            updatebrand.name = brand
            #Es wird eine Erfolgsnachricht ausgegeben.
            flash(f'Die Marke wurde erfolgreich aktualisiert.', 'success')
            db.session.commit()
            return redirect(url_for("admin.brands"))
        return render_template('products/updatebrand.html', title = 'Update Marke', updatebrand = updatebrand)

    #Wenn der Nutzer keine Admin-Rechte besitzt, wird eine entsprechende Nachricht ausgegeben.
    else: 
        flash("Entschuldigung. Um diese Website zu sehen, brauchen Sie Administratorenrechte!", "info")
        return redirect(url_for('users.login'))
#-----------------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------Marke löschen-------------------------------------------------------------
@admin.route('/deletebrand/<int:id>', methods=['POST'])
#Um die Seite aufzurufen, muss man eingeloggt sein.
@login_required
def deletebrand(id):
    #Es wird überprüft, welche User-ID der aktuelle benutzer hat. Nur User-ID 1 (Admin) hat Zugriff auf die Seite
    user_id = current_user.id
    if user_id == 1:
        #Aus der Datenbank wird die Marke anhand ihrer ID abgerufen. 
        #Die ID wird beim Klick auf der Seite vom html-Template an die Funktion "deletebrand" übergeben.
        brand = Brand.query.get_or_404(id)
        #Beim abschicken des Formulars, wird die ausgewählte Marke aus der Datenbank gelöscht.
        if request.method=="POST":
            db.session.delete(brand)
            db.session.commit()
            #Es wird eine Erfolgsnachricht ausgegeben.
            flash(f'Die Marke "{brand.name}" wurde erfolgreich gelöscht.', 'success')
            return redirect(url_for("admin.brands"))
        #Wenn die Marke nicht gelöscht werden konnte, wird eine entsprechende Warnung ausgegeben.
        flash(f'Die Marke "{brand.name}" konnte nicht gelöscht werden.', 'warning')
        return redirect(url_for("admin.brands"))

    #Wenn der Nutzer keine Admin-Rechte besitzt, wird eine entsprechende Nachricht ausgegeben.
    else: 
        flash("Entschuldigung. Um diese Website zu sehen, brauchen Sie Administratorenrechte!", "info")
        return redirect(url_for('users.login'))
#-----------------------------------------------------------------------------------------------------------------------------   


#---------------------------------------------------Hinzufügen einer Kategorie------------------------------------------------
@admin.route('/addcat', methods=['GET', 'POST'])
#Um die Seite aufzurufen, muss man eingeloggt sein.
@login_required
def addcat():
    #Es wird überprüft, welche User-ID der aktuelle benutzer hat. Nur User-ID 1 (Admin) hat Zugriff auf die Seite
    user_id = current_user.id
    if user_id == 1:
        # Wird eine Kategorie hinzugefügt und das Formular abgeschickt, wird die neue Kategorie zur Datenbank hinzugefügt
        if request.method=="POST":
            getcat = request.form.get('category')
            cat = Category(name=getcat)
            db.session.add(cat)
            #Es wird eine Erfolgsnachricht ausgegeben.
            flash(f'Die Kategorie "{getcat}" wurde zur Datenbank hinzugefügt.', 'success') 
            db.session.commit()
            return redirect(url_for("admin.addcat"))
        
        return render_template('products/addbrand.html')

    #Wenn der Nutzer keine Admin-Rechte besitzt, wird eine entsprechende Nachricht ausgegeben.
    else: 
        flash("Entschuldigung. Um diese Website zu sehen, brauchen Sie Administratorenrechte!", "info")
        return redirect(url_for('users.login'))
#-----------------------------------------------------------------------------------------------------------------------------   


#---------------------------------------------------Kategorien anzeigen (Adminansicht)----------------------------------------
@admin.route("/categories")
#Um die Seite aufzurufen, muss man eingeloggt sein.
@login_required
def categories():
    #Es wird überprüft, welche User-ID der aktuelle benutzer hat. Nur User-ID 1 (Admin) hat Zugriff auf die Seite
    user_id = current_user.id
    if user_id == 1:
        #Aus der Tabelle "Category" der Datenbank werden alle Kategorien nach ihrer ID abgerufen und absteigend sortiert. 
        categories = Category.query.order_by(Category.id.desc()).all()
        #Das Template wird gerendert und die abgerufenen Kategorien werden übergeben.
        return render_template("products/brands.html", title = "Kategorien", categories = categories)

    #Wenn der Nutzer keine Admin-Rechte besitzt, wird eine entsprechende Nachricht ausgegeben.
    else: 
        flash("Entschuldigung. Um diese Website zu sehen, brauchen Sie Administratorenrechte!", "info")
        return redirect(url_for('users.login'))
#-----------------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------Kategorie ändern / umbenennen---------------------------------------------
@admin.route('/updatecat/<int:id>', methods=['GET', 'POST'])
#Um die Seite aufzurufen, muss man eingeloggt sein.
@login_required
def updatecat(id):
    #Es wird überprüft, welche User-ID der aktuelle benutzer hat. Nur User-ID 1 (Admin) hat Zugriff auf die Seite
    user_id = current_user.id
    if user_id == 1:
        #Aus der Datenbank wird die Kategorie anhand ihrer ID abgerufen. 
        #Die ID wird beim Klick auf der Seite vom html-Template an die Funktion "updatecat" übergeben.
        updatecat = Category.query.get_or_404(id)
        #Die vom Nutzer in das Formular eingebene neue Kategorie wird in der Variablen "category" gespeichert.
        category = request.form.get('category')
        #Beim abschicken des Formulars, wird die neue Kategorie dann in die Datenbank geschrieben.
        if request.method=="POST":
            updatecat.name = category
            #Es wird eine Erfolgsnachricht ausgegeben.
            flash(f'Die Kategorie wurde erfolgreich aktualisiert.', 'success')
            db.session.commit()
            return redirect(url_for("admin.categories"))
        return render_template('products/updatebrand.html', title = 'Update Kategorie', updatecat = updatecat)

    #Wenn der Nutzer keine Admin-Rechte besitzt, wird eine entsprechende Nachricht ausgegeben.
    else: 
        flash("Entschuldigung. Um diese Website zu sehen, brauchen Sie Administratorenrechte!", "info")
        return redirect(url_for('users.login'))
#-----------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------Kategorie löschen---------------------------------------------------------
@admin.route('/deletecategory/<int:id>', methods=["POST"])
#Um die Seite aufzurufen, muss man eingeloggt sein.
@login_required
def deletecategory(id):
    #Es wird überprüft, welche User-ID der aktuelle benutzer hat. Nur User-ID 1 (Admin) hat Zugriff auf die Seite
    user_id = current_user.id
    if user_id == 1:
        #Aus der Datenbank wird die Kategorie anhand ihrer ID abgerufen. 
        #Die ID wird beim Klick auf der Seite vom html-Template an die Funktion "deletecategory" übergeben.
        category = Category.query.get_or_404(id)
        #Beim abschicken des Formulars, wird die ausgewählte Kategorie aus der Datenbank gelöscht.
        if request.method=="POST":
            db.session.delete(category)
            db.session.commit()
            #Es wird eine Erfolgsnachricht ausgegeben.
            flash(f'Die Marke "{category.name}" wurde erfolgreich gelöscht.', 'success')
            return redirect(url_for("admin.categories"))
        #Wenn die Marke nicht gelöscht werden konnte, wird eine entsprechende Warnung ausgegeben.
        flash(f'Die Marke "{category.name}" konnte nicht gelöscht werden.', 'warning')
        return redirect(url_for("admin.categories"))

    #Wenn der Nutzer keine Admin-Rechte besitzt, wird eine entsprechende Nachricht ausgegeben.
    else: 
        flash("Entschuldigung. Um diese Website zu sehen, brauchen Sie Administratorenrechte!", "info")
        return redirect(url_for('users.login'))
#-----------------------------------------------------------------------------------------------------------------------------   


#---------------------------------------------------Produkt hinzufügen--------------------------------------------------------
@admin.route("/addproduct", methods=['GET', 'POST'])
#Um die Seite aufzurufen, muss man eingeloggt sein.
@login_required
def addproduct():
    #Es wird überprüft, welche User-ID der aktuelle benutzer hat. Nur User-ID 1 (Admin) hat Zugriff auf die Seite
    user_id = current_user.id
    if user_id == 1:
        #Es werden alle Kategorien und Marken aus der Datenbank abgerufen, die im html-Template dann als Dropdown Menü zur Auswahl stehen
        brands = Brand.query.all()
        categories = Category.query.all()
        #Hier wird das Formular "AddProducts" abgerufen.
        form = AddProducts(request.form)

        #Wenn der Submit-Button im Template geklickt wird, werden die eingegebenen Daten abgerufen und in den jeweiligen Variablen gespeichert. 
        if request.method == "POST":
            name = form.name.data
            price = form.price.data
            discount = form.discount.data
            stock = form.stock.data
            colors = form.colors.data
            desc = form.description.data
            #Da die Formularfelder "brand" und "category" nicht Teil von FlaskForm sind, werden diese Inhalte auf andere Weise abgerufen.
            brand = request.form.get('brand')
            category = request.form.get('category')
            #Auch die hochgeladenen Fotos werden in den Variablen gespeichert und umbenannt. 
            image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".") 
            image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            #Anschließend wird alles zur Datenbank hinzugefügt.
            addpro = Addproduct(name=name, price=price, discount=discount, stock=stock, colors=colors, desc=desc, brand_id=brand, category_id=category, image_1=image_1, image_2=image_2, image_3=image_3)
            db.session.add(addpro)
            #Es wird eine Erfolgsnachricht ausgegeben.
            flash(f'Das Produkt "{name}" wurde zur Datenbank hinzugefügt.', 'success')
            db.session.commit()

        return render_template("products/addproduct.html", title="Add Product page", form=form, brands=brands, categories=categories)

    #Wenn der Nutzer keine Admin-Rechte besitzt, wird eine entsprechende Nachricht ausgegeben.
    else: 
        flash("Entschuldigung. Um diese Website zu sehen, brauchen Sie Administratorenrechte!", "info")
        return redirect(url_for('users.login'))
#-----------------------------------------------------------------------------------------------------------------------------    


#---------------------------------------------------Produkte anzeigen (Adminansicht)------------------------------------------
@admin.route("/admin_products")
#Um die Seite aufzurufen, muss man eingeloggt sein.
@login_required
def admin_addproducts():
    #Es wird überprüft, welche User-ID der aktuelle benutzer hat. Nur User-ID 1 (Admin) hat Zugriff auf die Seite
    user_id = current_user.id
    if user_id == 1:
        #Alle Produkte werden aus der Datenbank abgerufen und an das Template übergeben.
        products = Addproduct.query.all()
        return render_template("products/admin_products.html", title = "Admin Produktansicht", products=products)

    #Wenn der Nutzer keine Admin-Rechte besitzt, wird eine entsprechende Nachricht ausgegeben.
    else: 
        flash("Entschuldigung. Um diese Website zu sehen, brauchen Sie Administratorenrechte!", "info")
        return redirect(url_for('users.login'))
#-----------------------------------------------------------------------------------------------------------------------------   


#---------------------------------------------------Produkt ändern------------------------------------------------------------
@admin.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
#Um die Seite aufzurufen, muss man eingeloggt sein.
@login_required
def updateproduct(id):
    #Es wird überprüft, welche User-ID der aktuelle benutzer hat. Nur User-ID 1 (Admin) hat Zugriff auf die Seite
    user_id = current_user.id
    if user_id == 1:
        #Es werden alle Marken und Kategorien aus der Datenbank abgerufen.
        brands = Brand.query.all()
        categories = Category.query.all()
        #Es wird das Produkt aus der Datenbank abgerufen, welches vom Nutzer auf der Seite angeklickt wird.
        #Die ID wird von dem HTML-Template übergeben. 
        product = Addproduct.query.get_or_404(id)
        #Marke und Kategorie werden aus dem Formular abgerufen. 
        brand = request.form.get('brand')
        category = request.form.get('category')
        #Hier wird das Formular "AddProducts" abgerufen.
        form = AddProducts(request.form)
        #Wenn der Submit-Button vom Nutzer geklickt wird, werden die eingegebenen Daten in die Datenbank geschrieben. 
        if request.method == "POST":
            product.name = form.name.data
            product.price = form.price.data
            product.discount = form.discount.data
            product.brand_id = brand
            product.category_id = category
            product.stock = form.stock.data
            product.colors = form.colors.data
            product.desc = form.description.data
            #Die Bilder werden nur geändert, wenn neue Bilder hochgeladen werden. 
            if request.files.get('image_1'):
                try:
                    os.unlink(os.path.join(current_app.root_path, "static/product_pics/" + product.image_1))
                    product.image_1 = image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
                except:
                    product.image_1 = image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            
            if request.files.get('image_2'):
                try:
                    os.unlink(os.path.join(current_app.root_path, "static/product_pics/" + product.image_2))
                    product.image_2 = image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
                except:
                    product.image_2 = image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            
            if request.files.get('image_3'):
                try:
                    os.unlink(os.path.join(current_app.root_path, "static/product_pics/" + product.image_3))
                    product.image_3 = image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
                except:
                    product.image_3 = image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            db.session.commit()
            flash(f'Das Produkt wurde aktualisiert', 'success')
            return redirect(url_for('admin.admin_addproducts'))

        #Hier wird das angezeigt FlaskForm Formular mit den Daten befüllt, die bereits in der Datenbank stehen.
        #Der Nutzer bekommt demnach alle bereits vorhandenen Werte vorgeblendet und kann gezielte Änderungen durchführen.
        #Dies hat den Vorteil, dass nicht mehr das komplette Formular neu befüllt werden muss, wenn nur eine kleine Änderung durchgeführt werden soll. 
        form.name.data = product.name
        form.price.data = product.price
        form.discount.data = product.discount
        form.stock.data = product.stock
        form.colors.data = product.colors
        form.description.data = product.desc

        #Das Template wird gerendert und die Marken, Kategorien, Produkte und das Forumlar übergeben. 
        return render_template('products/updateproduct.html', title = 'Update Produkt', brands = brands, categories = categories, product = product, form = form)

    #Wenn der Nutzer keine Admin-Rechte besitzt, wird eine entsprechende Nachricht ausgegeben.
    else: 
        flash("Entschuldigung. Um diese Website zu sehen, brauchen Sie Administratorenrechte!", "info")
        return redirect(url_for('users.login'))
#-----------------------------------------------------------------------------------------------------------------------------
    

#---------------------------------------------------Produkt löschen-----------------------------------------------------------
@admin.route('/deleteproduct/<int:id>', methods=['POST'])
#Um die Seite aufzurufen, muss man eingeloggt sein.
@login_required
def deleteproduct(id):
    #Es wird überprüft, welche User-ID der aktuelle benutzer hat. Nur User-ID 1 (Admin) hat Zugriff auf die Seite
    user_id = current_user.id
    if user_id == 1:
        #Das Produkt, welches gelöscht werden soll, wird anhand der ID aus der Datenbank abgerufen. 
        product = Addproduct.query.get_or_404(id)
        #Wird der Submit-Button geklickt, werden die mit dem Produkt verknüpften Bilder gelöscht. 
        if request.method == "POST":
            try:
                os.unlink(os.path.join(current_app.root_path, "static/product_pics/" + product.image_1))
                os.unlink(os.path.join(current_app.root_path, "static/product_pics/" + product.image_2))
                os.unlink(os.path.join(current_app.root_path, "static/product_pics/" + product.image_3))
            except Exception as e:
                print(e)

            #Anschließend wird das Produkt aus der Datenbank gelöscht. 
            db.session.delete(product)
            db.session.commit()
            #Es wird eine Erfolgsnachricht ausgegeben.
            flash(f'Das Produkt {product.name} wurde erfolgreich gelöscht.', 'success')
            return redirect(url_for('admin.admin_addproducts'))

        #Wenn das Produkt nicht gelöscht werden kann, wird eine entsprechende Fehlermeldung ausgegeben. 
        flash(f'Das Produkt konnte nicht gelöscht werden.', 'danger') 
        return redirect(url_for('admin.admin_addproducts'))

    #Wenn der Nutzer keine Admin-Rechte besitzt, wird eine entsprechende Nachricht ausgegeben.
    else: 
        flash("Entschuldigung. Um diese Website zu sehen, brauchen Sie Administratorenrechte!", "info")
        return redirect(url_for('users.login'))
#-----------------------------------------------------------------------------------------------------------------------------  







#---------------------------------------------------Kategorien anzeigen (Nutzeransicht)---------------------------------------
@admin.route('/category/<int:id>')
def get_category(id):
    page = request.args.get('page',1, type=int)
    #Die Kategorie, welche angezeigt werden soll, wird anhand der ID aus der Datenbank abgerufen und in Variable "c" gespeichert. 
    c = Category.query.filter_by(id=id).first_or_404()
    #Alle Produkte, die zu der Kategorie gehören, werden aus der Datenbank abgerufen. 
    category = Addproduct.query.filter_by(category=c).paginate(page=page, per_page=4)
    #Das Template wird gerendert und "category" und "c" werden übergeben.
    return render_template('products/products.html', category = category, c=c)
#-----------------------------------------------------------------------------------------------------------------------------
    

#---------------------------------------------------Marken anzeigen (Nutzeransicht)-------------------------------------------
@admin.route('/brand/<int:id>')
def get_brand(id):
    page = request.args.get('page',1, type=int)
    #Die Marke, welche angezeigt werden soll, wird anhand der ID aus der Datenbank abgerufen und in Variable "b" gespeichert. 
    b = Brand.query.filter_by(id=id).first_or_404()
    #Alle Produkte, die zu der Marke gehören, werden aus der Datenbank abgerufen. 
    brand2 = Addproduct.query.filter_by(brand=b).paginate(page=page, per_page=4)
     #Das Template wird gerendert und "brand2" und "b" werden übergeben.
    return render_template('products/products.html', brand2 = brand2, b=b)
#-----------------------------------------------------------------------------------------------------------------------------




