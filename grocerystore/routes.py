from flask import render_template, redirect, url_for, flash, request
from grocerystore.models import User, Product, Category, Cart, Order
from grocerystore.forms import LoginForm, RegistrationForm, UpdateAccountForm, ProductForm
from grocerystore import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You are not authorized to view this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/home')
@login_required
def home():
    # Get all products
    products = Product.query.all()
    return render_template('home.html', products=products)

@app.route("/register", methods=['GET', 'POST'])
def register():
    # If user is logged in, redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.name.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    # If user is logged in, redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # Check if user exists
        user = User.query.filter_by(email=form.email.data).first()
        # Check if password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Log in user
            login_user(user, remember=form.remember.data)
            # Redirect to next page if it exists
            next_page = request.args.get('next')
            # Flash message
            flash('Login Successful!', 'success')
            # If next page doesn't exist, redirect to home page
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    # If form is submitted
    if form.validate_on_submit():
        # Update user info
        current_user.name = form.name.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        # Commit changes to database
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    # If form is not submitted, populate form with user info
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)

@app.route('/product_new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, price=form.price.data, category_id=form.category_id.data, quantity=form.quantity.data, manufacture_date=form.manufacture_date.data)
        db.session.add(product)
        db.session.commit()
        flash('Product added!', 'success')
        return redirect(url_for('home'))
    return render_template('create_product.html', title='New Product', form=form)