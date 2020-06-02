from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm ,UpdateAccountForm,PostForm,RequestResetForm,ResetPasswordForm
from datetime import datetime
from flask_login import LoginManager
from flask_login import login_user,current_user,login_manager, logout_user
from flask import * 
import os
import secrets
from PIL import Image
import datetime
#from datetime import datetime
from datetime import timedelta
from flask_paginate import Pagination, get_page_parameter
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Mail,Message


login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '**********'
app.config['MAIL_PASSWORD'] = '**********'
mail = Mail(app)

import couchdb
couch=couchdb.Server('http://(your public ip)')
db1 = couch['users']
db2=couch['posts']

login_manager = LoginManager(app)


def is_authenticated(self):
    return True
@login_manager.user_loader
def load_user(user_id):
    db1 = couch['users']
    #return User.query.get(int(user_id))
    return db1.get(user_id)

def Sortbydate(a):
    return(sorted(a, key=lambda x: x['date_posted'],reverse=True))

@app.route("/")
@app.route("/home")
def home():
    posts= []
    for id in db2:
        dict={}
        b=db2.get(id)
        for key,value in b.items(): 
            if key=='content':
                value=value[:300]+"..."
            dict[key]=value
        posts.append(dict)
        
    n = 5
    posts=Sortbydate(posts)
    page = request.args.get('page', 1, type=int)
    posts = [posts[i * n:(i + 1) * n]
                 for i in range((len(posts) + n - 1) // n)]
    return render_template('home.html', posts=posts[page-1],page_count=len(posts), cur_page=page)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        db1 = couch['users']
        doc={'name':form.username.data,'password':form.password.data,'email':form.email.data,'designation':form.designation.data,
             'phone':form.phone.data,'linkedin':form.linkedin.data}
        db1.save(doc)
        return redirect(url_for('login'))
    return render_template('register.html', title='Register',form=form)


@app.route("/login", methods=['GET','POST'])
def login():
    
    form = LoginForm()
    
    if form.validate_on_submit():
        for id in db1:
            b=db1.get(id)
            if form.email.data == b['email'] and form.password.data == b['password']:
                session['email']=form.email.data
                flash('You have been logged in!', 'success')
                #login_user(b, remember=form.remember.data)
                session['name']=b['name']
                return redirect(url_for('home'))
        flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/logout")
def logout():
    logout_user()
    session.pop('email',None)
    session.pop('name',None)
    return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
#@login_required
#current_user.image_file='adi.jpg'

def account():
    form = UpdateAccountForm()
    for id in db1:
            b=db1.get(id)
            if(b['name']==session['name']):
                break
    for id in db2:
            b1=db2.get(id)
            if(b1['author']==session['name']):
                break
    if form.validate_on_submit():
        b['name'] = form.username.data
        b['email'] = form.email.data
        b['designation'] = form.designation.data
        b['phone'] = form.phone.data
        b['linkedin'] = form.linkedin.data
        b1['author']=form.username.data
        db1.save(b) 
        db2.save(b1)
        session['name']=b['name']
        session['email']=b['email']
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = b['name']
        form.email.data = b['email']
        form.designation.data = b['designation']
        form.phone.data = b['phone']
        form.linkedin.data = b['linkedin']
    image_file = url_for('static', filename='profile.jpg' )
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])

def new_post():
    if 'name' in session:
        form = PostForm()
        if form.validate_on_submit():
            a = datetime.datetime.now().strftime('%y-%m-%d %a %H:%M:%S')
            doc={'title':form.title.data,'content':form.content.data,'author':session['name'],'date_posted':str(a)}    
            db2.save(doc)
            flash('Your post has been created!', 'success')
            return redirect(url_for('home'))
        return render_template('createpost.html', title='New Post',
                               form=form, legend='New Post')

@app.route("/post/<post_title>")
def post(post_title):
    for id in db2:
      b=db2.get(id)
      dict={}
      if(post_title==b['title']):
          for key,value in b.items():  
            dict[key]=value
          return render_template('post.html', post=dict)
      
@app.route("/post/<post_title>/update", methods=['GET', 'POST'])
def update_post(post_title):
    for id in db2:
      b=db2.get(id)
      if(post_title==b['title']):
          break
  
    form = PostForm()
    if form.validate_on_submit():
        b['title']= form.title.data
        b['content'] = form.content.data
        db2.save(b)
        post_title=b['title']
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_title=post_title))
    return render_template('createpost.html', title='Update Post',
                           form=form, legend='Update Post')

@app.route("/post/<post_title>/delete", methods=['GET','POST'])
def delete_post(post_title):
    
    for id in db2:
      b=db2.get(id)
      if(post_title==b['title']):
          del db2[b.id]
    
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

def send_reset_email(user):
    msg = Message('Password Reset Request',
                  sender='*****************',
                  recipients=[user])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=user, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if 'name' in session:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        for id in db1:
            b=db1.get(id)
            if(form.email.data==b['email']):
                send_reset_email(b['email'])
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if 'name' in session:
        return redirect(url_for('home'))
    #user = User.verify_reset_token(token)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        for id in db1:
            b=db1.get(id)
            if(b['email']==token):
                b['password'] = form.password.data
                db1.save(b)
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route('/author/<post_author>',methods=['GET', 'POST'])
def author(post_author):
    for id in db1:
        b=db1.get(id)
        if(b['name']==post_author):
             return render_template('author.html', name=b['name'],email=b['email'],designation=b['designation'],phone=b['phone'],linkedin=b['linkedin'])
                

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def page_forbidden(e):
    return render_template('403.html'), 403


@app.errorhandler(500)
def error_500(e):
    return render_template('500.html'), 500



if __name__ == '__main__':
    app.run(debug=True)
    
    
    
    
    

    
