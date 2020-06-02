from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed

import couchdb
couch=couchdb.Server('http://***************')
class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    designation = StringField('designation')
    linkedin = StringField('linkedin/insta')
    phone = StringField('phone',validators=[DataRequired(), Length(10)])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        #user = User.query.filter_by(username=username.data).first()
        db1 = couch['users'] 
        for id in db1:
            b=db1.get(id)
            if(username.data==b['name']):
                raise ValidationError('That username is taken. Please choose a different one.')
'''         
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
'''

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
    
class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    designation=StringField('designation', validators=[DataRequired()])
    phone = StringField('phone',validators=[DataRequired(), Length(10)])
    linkedin=StringField('linkedin/insta', validators=[DataRequired()])
    submit = SubmitField('Update')
    def validate_username(self, username):
        db1 = couch['users'] 
        for id in db1:
            b=db1.get(id)
            if(username.data==b['name']):
                raise ValidationError('That username is taken. Please choose a different one.')
'''
    def validate_email(self, email):
        db1 = couch['users'] 
        for id in db1:
            b=db1.get(id)
            if(email.data==b['email']):
                raise ValidationError('That email is taken. Please choose a different one.')
'''                  
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')                  
                  
class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        c=0
        db1 = couch['users'] 
        for id in db1:
            b=db1.get(id)
            if(email.data==b['email']):
                c=1
        if c==0:       
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')                