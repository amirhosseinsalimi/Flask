from flask import abort, flash , redirect , render_template , request , session , url_for
from sqlalchemy.exc import IntegrityError

from mod_blog.models import Post
from app import db
from mod_blog.forms import CreatePostForm
# from mod_blog.models import CreatePostForm
from mod_blog.models import Post
from mod_users.forms import LoginForm
from mod_users.models import User
from mod_users.forms import AdminRegister
from . import admin
from .utils import admin_only_view


@admin.route('/')
@admin_only_view
def index():
    return render_template('admin/index.html')


@admin.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            abort(400)
        user = User.query.filter(User.email.ilike(f'{form.email.data}')).first()
        if not user:
            flash('Incorrect Credentials', category='error')
            return render_template('admin/login.html', form=form)
        if not user.check_password(form.password.data):
            flash('Incorrect Credentials', category='error')
            return render_template('admin/login.html', form=form)
        if not user.is_admin():
            flash('Incorrect Credentials', category='error')
            return render_template('admin/login.html', form=form)
        session['email'] = user.email
        session['user_id'] = user.id
        session['role'] = user.role
        return redirect(url_for('admin.index'))
    if session.get('role') == 1:
        return redirect(url_for('admin.index'))
    return render_template('admin/login.html', form=form)


@admin.route('/logout/', methods=['GET'])
@admin_only_view
def logout():
    session.clear()
    flash('You logged out successfully.', 'warning')
    return redirect(url_for('admin.login'))


@admin.route('/posts/new/', methods=['GET', 'POST'])
@admin_only_view
def create_post():
    form = CreatePostForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            return "1"
        new_post = Post()
        new_post.title = form.title.data
        new_post.content = form.content.data
        new_post.slug = form.slug.data
        new_post.summary = form.summary.data
        try:
            db.session.add(new_post)
            db.session.commit()
            flash('Post created!')
            return redirect(url_for('admin.index'))
        except IntegrityError:
            db.session.rollback()
            
    return render_template('admin/create_post.html', form=form)


@admin.route('/posts/' , methods=['GET'])
@admin_only_view
def posts():
    posts = Post.query.all()

    return render_template('admin/posts.html' , posts=posts)


@admin.route('/posts/delete/<int:post_id>' , methods = ['GET'])
@admin_only_view
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post Deleted ')
    return redirect(url_for('admin.posts'))


@admin.route('/user/new/' , methods=['POST' , 'GET'])
@admin_only_view
def new_user():
    form = AdminRegister(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('admin/create_user.html', form=form)
        if not form.password.data == form.confirm_password.data:
            error_msg = 'Password and Confirm Password does not match.'
            form.password.errors.append(error_msg)
            form.confirm_password.errors.append(error_msg)
            return render_template('admin/create_user.html', form=form)
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
        return render_template('admin/create_user.html' , form=form)
    return render_template('admin/create_user.html' , form=form)



@admin.route('/users/')
@admin_only_view
def users_list():
    users = User.query.all()

    return render_template('admin/list_users.html' , users = users)