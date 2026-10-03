from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stock.db"
app.config["SECRET_KEY"] = "change-this-secret-key"
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    threshold = db.Column(db.Integer, nullable=False, default=5)


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # "manager" or "seller"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def manager_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        if current_user.role != "manager":
            return "Access denied", 403
        return f(*args, **kwargs)
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password_hash, request.form["password"]):
            login_user(user)
            return redirect(url_for("home"))
        error = "Wrong username or password"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    products = Product.query.all()
    return render_template("index.html", products=products)


@app.route("/add", methods=["POST"])
@manager_required
def add_product():
    product = Product(
        name=request.form["name"],
        price=float(request.form["price"]),
        quantity=int(request.form["quantity"]),
        threshold=int(request.form["threshold"]),
    )
    db.session.add(product)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete/<int:product_id>", methods=["POST"])
@manager_required
def delete_product(product_id):
    product = db.get_or_404(Product, product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
@manager_required
def edit_product(product_id):
    product = db.get_or_404(Product, product_id)
    if request.method == "POST":
        product.name = request.form["name"]
        product.price = float(request.form["price"])
        product.quantity = int(request.form["quantity"])
        product.threshold = int(request.form["threshold"])
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", product=product)


@app.route("/sell/<int:product_id>", methods=["POST"])
@login_required
def sell_product(product_id):
    product = db.get_or_404(Product, product_id)
    quantity = int(request.form["quantity"])
    if quantity <= 0 or quantity > product.quantity:
        return "Not enough stock", 400
    product.quantity -= quantity
    sale = Sale(
        product_name=product.name,
        quantity=quantity,
        total=quantity * product.price,
    )
    db.session.add(sale)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/sales")
@manager_required
def sales():
    all_sales = Sale.query.order_by(Sale.date.desc()).all()
    total = sum(s.total for s in all_sales)
    return render_template("sales.html", sales=all_sales, total=total)


@app.route("/sales/cancel/<int:sale_id>", methods=["POST"])
@manager_required
def cancel_sale(sale_id):
    sale = db.get_or_404(Sale, sale_id)
    product = Product.query.filter_by(name=sale.product_name).first()
    if product:
        product.quantity += sale.quantity
    db.session.delete(sale)
    db.session.commit()
    return redirect(url_for("sales"))


with app.app_context():
    db.create_all()
    if not User.query.first():
        db.session.add(User(
            username="manager",
            password_hash=generate_password_hash("manager123"),
            role="manager",
        ))
        db.session.add(User(
            username="seller",
            password_hash=generate_password_hash("seller123"),
            role="seller",
        ))
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)