from flask import render_template, request, Blueprint
from flaskblog.models import Post, Addproduct

main = Blueprint('main', __name__)


@main.route('/')
@main.route("/home")
def home():
    carouselproducts = Addproduct.query.filter(Addproduct.discount > 0).order_by(Addproduct.pub_date.desc()).limit(6)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.pub_date.desc()).limit(4)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    
    return render_template("home.html", posts=posts, products=products, carouselproducts=carouselproducts)


