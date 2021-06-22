from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, BooleanField,
                     IntegerField, SelectField, DecimalField, TextAreaField)
from wtforms.validators import (DataRequired, Length, Email, EqualTo,
                                ValidationError)
from sandwich.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)], render_kw={'autofocus': True})
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    netto = IntegerField('Netto', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose another one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose another one')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'autofocus': True})
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ShopForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    shop_of_the_day = BooleanField('Shop of the Day')
    submit = SubmitField('Add')


class SandwichForm(FlaskForm):
    shop = SelectField('Shop', coerce=int, choices=[])
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=20)])
    price = DecimalField('Price', validators=[DataRequired()])
    submit = SubmitField('Add')


class ToppingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=20)])
    price = DecimalField('Price', validators=[DataRequired()])
    submit = SubmitField('Add')


class OrderForm(FlaskForm):
    sandwich = SelectField('Sandwich', coerce=int, choices=[])
    comment = TextAreaField('Comment')
    submit = SubmitField('Add')
