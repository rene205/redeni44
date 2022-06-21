from math import prod
from flask import render_template, request, Blueprint
from flaskblog.models import Addproduct
from flaskblog import app, search

items = Blueprint('items', __name__)


#---------------------------------------------------Anzeigen der Suchergebnisse--------------------------------------------------------------
@app.route('/result')
def result():
    #Das in die Suchleiste eingegebene Suchwort wird als "searchword" gespeichert.
    searchword = request.args.get('q')
    #Anschließend wird mit dem Suchwort in der Datenbank "Addproduct" nach dem Suchwort in den Spalten "name" und "desc" gesucht.
    #Die Ergebnisse werden in "products" gespeichert.
    products = Addproduct.query.msearch(searchword, fields= ['name', 'desc'], limit=10)
    #Rendert das Template und übergibt "products".
    return render_template("products/result.html", products=products)
#--------------------------------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------Darstellung der Produktseite-------------------------------------------------------------
@items.route("/products")
def products():
    page = request.args.get('page',1, type=int)
    #Filtert alle Produkte aus der Datenbank, die auf Lager sind und speichert diese dann in "products"
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page, per_page=12)
    #Rendert das Template und übergibt die Produkte
    return render_template("products/products.html", products = products)
#--------------------------------------------------------------------------------------------------------------------------------------------  


#---------------------------------------------------Anzeigen einer einzelnen Produktseite----------------------------------------------------
@items.route("/product/<int:id>")
def single_page(id):
    #Beim anklicken eines Produktes auf der Produktübersichtsseite, wird die Produkt ID an die Funktion "single_page" übergeben.
    #Es wird dann das entsprechende Produkt aus der Datenbank abgerufen. 
    product = Addproduct.query.get_or_404(id)
    #Rendert das Template und übergibt das Produkt.
    return render_template('products/single_page.html', product = product)
#--------------------------------------------------------------------------------------------------------------------------------------------  