from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from grocerystore.models import User

# Registration Form
class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=32)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=16)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # Validate username
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
        
    # Validate email
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists. Please choose a different one.')

# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# Update Account Form
class UpdateAccountForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=32)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=16)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    # Validate username
    def validate_username(self, username):
        # If username is different than current username
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists. Please choose a different one.')
        
    # Validate email
    def validate_email(self, email):
        # If email is different than current email
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already exists. Please choose a different one.')
            
# Product Form
class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=32)])
    price = FloatField('Price', validators=[DataRequired()])
    category_id = StringField('Category ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    manufacture_date = DateField('Manufacture Date', validators=[DataRequired()])
    submit = SubmitField('Add Product')