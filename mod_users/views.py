from flask import request, render_template, flash , abort , session , redirect , url_for
from sqlalchemy.exc import IntegrityError

from app import db

from . import users
from .forms import RegisterForm
from mod_users.models import User

@users.route('/')
def index():
    return "11111"




@users.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('users/register.html', form=form)
        if not form.password.data == form.confirm_password.data:
            error_msg = 'Password and Confirm Password does not match.'
            form.password.errors.append(error_msg)
            form.confirm_password.errors.append(error_msg)
            return render_template('users/register.html', form=form)
        new_user = User()
        new_user.full_name = form.full_name.data
        new_user.email = form.email.data
        new_user.set_password(form.password.data)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('You created your account successfully.', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Email is in use.', 'error')
    return render_template('users/register.html', form=form)    


@users.route('/login/' , methods=['POST' , 'GET'])
def login():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('users/register.html', form=form)
        user = User.query.filter(User.email.ilike(f"{form.email.data}")).first()

        if not user:
            flash('Incorrect Credentials', category='error')
            return render_template('users/login.html' , form = form )
        if not form.password.data == form.confirm_password.data:
            error_msg = 'Password and Confirm Password does not match.'
            form.password.errors.append(error_msg)
            form.confirm_password.errors.append(error_msg)
            return render_template('users/login.html' , form=form )
        if not user.check_password(form.password.data):
            flash('Incorrect Credentials', category='error')
            return render_template('users/login.html' , form=form )


        fullname = User.query.filter(User.full_name.ilike(f"{form.full_name.data}")).first()
        if not fullname:
            flash('Your username is incrrect' , category='error')
            return render_template('users/login.html' , form = form)
        session['email'] = user.email
        session['full_name'] = user.full_name
        session['user_id'] = user.id
        session['role'] = user.role
        return render_template('blog/index.html')
        # return render_template('users/login.html' , form = form )
    return render_template('users/login.html' , form = form )