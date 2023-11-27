from flask import render_template, redirect, url_for, flash, request
from grocerystore.models import User, Product, Category, Cart, Order
from grocerystore.forms import LoginForm, RegistrationForm, UpdateAccountForm, ProductForm, UpdateProductForm, CategoryForm, UpdateCategoryForm
from grocerystore import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps
from datetime import date

# Decorator for admin routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You are not authorized to view this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Route for home page
@app.route('/')
@app.route('/home')
@login_required
def home():
    # Get all products in descending order of manufacture date
    products = Product.query.order_by(Product.manufacture_date.desc()).all()
    return render_template('home.html', products=products, title='Home')


# Route for admin dashboard
@app.route('/admin')
@login_required
@admin_required
def admin():
    # Get all users
    users = User.query.all()
    # Get all products
    products = Product.query.all()
    # Get all categories
    categories = Category.query.all()
    return render_template('admin.html', users=users, products=products, categories=categories, title='Admin Dashboard')

# Route for adding new user
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

# Route for logging in
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
        if user and bcrypt.check_password_hash(user.password, form.password.data) and not user.is_admin:
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

# Route for logging in as admin
@app.route("/login/admin", methods=['GET', 'POST'])
def admin_login():
    # If user is logged in, redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # Check if user exists
        user = User.query.filter_by(email=form.email.data).first()
        # Check if password is correct and user is admin
        if user and bcrypt.check_password_hash(user.password, form.password.data) and user.is_admin:
            # Log in user
            login_user(user, remember=form.remember.data)
            # Redirect to next page if it exists
            next_page = request.args.get('next')
            # Flash message
            flash('Login Successful!', 'success')
            # If next page doesn't exist, redirect to home page
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. User not an admin', 'danger')
            return redirect(url_for('admin_login'))
    return render_template('login.html', title='Admin Login', form=form, admin=True)

# Route for logging out
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route for account page
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

# Route for deleting account
@app.route('/account/delete', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get_or_404(current_user.id)
    # Check if user is admin
    if user.is_admin:
        flash('Admin account cannot be deleted!', 'danger')
        return redirect(url_for('account'))
    # Delete user
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted!', 'success')
    return redirect(url_for('register'))

# Route for adding new category
@app.route('/category/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Category added!', 'success')
        return redirect(url_for('admin'))
    return render_template('category/new.html', title='New Category', form=form)

# Route for viewing a category
@app.route('/category/<int:category_id>', methods=['GET'])
@login_required
def view_category(category_id):
    # Get category by id
    category = Category.query.get_or_404(category_id)
    # Get all products in the category
    products = Product.query.filter_by(category_id=category.id).all()
    return render_template('category/view.html', title=category.name, category=category, products=products)

# Route for updating a category
@app.route('/category/<int:category_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_category(category_id):
    # Get category by id
    category = Category.query.get_or_404(category_id)
    # Create form
    form = UpdateCategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated!', 'success')
        return redirect(url_for('admin'))
    elif request.method == 'GET':
        form.name.data = category.name
    return render_template('category/update.html', title='Update Category', form=form, category=category)

# Get route for deleting a category
@app.route('/category/<int:category_id>/delete', methods=['GET'])
@login_required
@admin_required
def delete_category_get(category_id):
    # Get category by id
    category = Category.query.get_or_404(category_id)
    return render_template('category/delete.html', title='Delete Category', category=category)

# Route for deleting a category
@app.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    # Get category by id
    category = Category.query.get_or_404(category_id)
    # If category has products, delete products before deleting category
    if category.products:
        for product in category.products:
            db.session.delete(product)
            db.session.commit()
    # Delete category
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted!', 'success')
    return redirect(url_for('admin'))

# Route for adding a product to category
@app.route('/category/<int:category_id>/add_product', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product_to_category(category_id):
    # Get category by id
    category = Category.query.get_or_404(category_id)
    # Create form
    form = ProductForm()
    # Change category_id field to display category name instead of id
    form.category_id.choices = [(category.id, category.name) for category in Category.query.all()]
    # Change manufacture_date field to display date picker
    form.manufacture_date.render_kw = {'type': 'date', 'max': date.today()}
    if form.validate_on_submit():
        product = Product(name=form.name.data, price=form.price.data, category_id=form.category_id.data, quantity=form.quantity.data, manufacture_date=form.manufacture_date.data)
        db.session.add(product)
        db.session.commit()
        flash('Product added!', 'success')
        return redirect(url_for('view_category', category_id=category.id))
    elif request.method == 'GET':
        form.category_id.data = str(category_id)
    return render_template('product/new.html', title='Add Product', form=form, category=category)

# Route for adding a new product
@app.route('/product/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_product():
    # Create form
    form = ProductForm()
    # Change category_id field to display category name instead of id
    form.category_id.choices = [(category.id, category.name) for category in Category.query.all()]
    # Change manufacture_date field to display date picker
    form.manufacture_date.render_kw = {'type': 'date', 'max': date.today()}
    if form.validate_on_submit():
        product = Product(name=form.name.data, price=form.price.data, category_id=form.category_id.data, quantity=form.quantity.data, manufacture_date=form.manufacture_date.data)
        db.session.add(product)
        db.session.commit()
        flash('Product added!', 'success')
        return redirect(url_for('admin'))
    return render_template('product/new.html', title='New Product', form=form)

# Route for viewing a product
@app.route('/product/<int:product_id>', methods=['GET'])
@login_required
def view_product(product_id):
    # Get product by id
    product = Product.query.get_or_404(product_id)
    return render_template('product/view.html', title=product.name, product=product)

# Route for updating a product
@app.route('/product/<int:product_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_product(product_id):
    # Get product by id
    product = Product.query.get_or_404(product_id)
    # Create form
    form = UpdateProductForm()
    # Change category_id field to display category name instead of id
    form.category_id.choices = [(category.id, category.name) for category in Category.query.all()]
    # Change manufacture_date field to display date picker
    form.manufacture_date.render_kw = {'type': 'date', 'max': date.today()}
    # Populate category_id field with all categories
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.category_id = form.category_id.data
        product.quantity = form.quantity.data
        product.manufacture_date = form.manufacture_date.data
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('admin'))
    elif request.method == 'GET':
        form.name.data = product.name
        form.price.data = product.price
        form.category_id.data = str(product.category_id)
        form.quantity.data = product.quantity
        form.manufacture_date.data = product.manufacture_date
    return render_template('product/update.html', title='Update Product', form=form, product=product)

# Get route for deleting a product
@app.route('/product/<int:product_id>/delete', methods=['GET'])
@login_required
@admin_required
def delete_product_get(product_id):
    # Get product by id
    product = Product.query.get_or_404(product_id)
    return render_template('product/delete.html', title='Delete Product', product=product)

# Route for deleting a product
@app.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    # Get product by id
    product = Product.query.get_or_404(product_id)
    # Delete product
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted!', 'success')
    return redirect(url_for('admin'))