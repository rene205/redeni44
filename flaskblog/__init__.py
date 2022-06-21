import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
#pip install flask-msearch
from flask_msearch import Search
#pip install flask-migrate
#from flask_migrate import Migrate



from flask_uploads import IMAGES, UploadSet, configure_uploads
import os


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'


app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/product_pics')
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
search = Search()
search.init_app(app)

#migrate = Migrate(app, db)
#with app.app_context():
    #if db.engine.url.drivername == "sqlite":
        #migrate.init_app(app, db, render_as_batch=True)
    #else:
        #migrate.init_app(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT']= 2525
app.config['MAIL_USE_TLS']= True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME']= 'a4a8fd30b81c14'
app.config['MAIL_PASSWORD']= '9dc17298bf83bd'
mail = Mail(app)

from flaskblog.items.routes import items
from flaskblog.users.routes import users
from flaskblog.posts.routes import posts
from flaskblog.main.routes import main
from flaskblog.admin.routes import admin
from flaskblog.footer.routes import footer
from flaskblog.cart.routes import cart
from flaskblog.errors.handlers import errors

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
app.register_blueprint(admin)
app.register_blueprint(footer)
app.register_blueprint(items)
app.register_blueprint(cart)
app.register_blueprint(errors)


