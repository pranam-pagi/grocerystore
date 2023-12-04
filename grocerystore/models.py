from grocerystore import app, db, login_manager
from flask_login import UserMixin
from grocerystore import bcrypt
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    username = db.Column(db.String(16), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String(256), nullable=False)
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    manufacture_date = db.Column(db.Date, nullable=False)
    cart = db.relationship('Cart', backref='product', lazy=True)
    orders = db.relationship('Order', backref='product', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False) 

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    orders = db.relationship('Order', backref='transaction', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

#create database if it doesn't exist
with app.app_context():
    db.create_all()

    #create admin user if it doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
        admin = User(name='Admin', username='admin', email='admin@demo.in', password=hashed_password, is_admin=True)
        db.session.add(admin)
        db.session.commit()