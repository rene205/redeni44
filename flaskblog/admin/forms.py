from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import DecimalField
from wtforms.validators import DataRequired
from wtforms import IntegerField, SubmitField, StringField, TextAreaField


#---------------------------------------------------Produkt zum Warenkorb hinzufügen------------------------------------------
class AddForm(FlaskForm):
    #"quant" beschreibt das Feld im Formular, welches die gewünschte Menge des Produkts enthält
    quant = IntegerField(label="Order quantity: ", default=1, validators=[DataRequired(),])
    submit = SubmitField(label="Add to cart")
#-----------------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------Formular: Produkt hinzufügen----------------------------------------------
class AddProducts(FlaskForm):
    #Das Formular zum hinzufügen eines Produktes enthält den Namen, Preis, Rabatt (%), Lagerbestand, Beschreibung und Farben
    #"DataRequired" gibt an, dass dieses Feld ausgefüllt werden muss. 
    name = StringField('Name', validators=[DataRequired()])
    price = DecimalField('Preis', validators=[DataRequired()]) 
    discount = IntegerField('Rabatt', default=0)
    stock = IntegerField('Lagerbestand', validators=[DataRequired()])
    description = TextAreaField('Beschreibung', validators=[DataRequired()])
    colors = TextAreaField('Farben', validators=[DataRequired()])

    #Drei Bilder müssen hinzugefügt werden (Formate: jpg, png, jpeg)
    image_1 = FileField('Bild 1', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    image_2 = FileField('Bild 2', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    image_3 = FileField('Bild 3', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
#-----------------------------------------------------------------------------------------------------------------------------