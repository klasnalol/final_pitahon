import os
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, jsonify
from app import db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from app.models import User, Post
from app.forms import RegistrationForm, LoginForm, PostForm
from PIL import Image

main = Blueprint('main', __name__)

# Utility function to save profile pictures
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    # Resize the image to save space
    output_size = (125, 125)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_fn

# Utility function to save post media
def save_media(form_media):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_media.filename)
    media_fn = random_hex + f_ext
    media_path = os.path.join(current_app.root_path, 'static/post_media', media_fn)
    form_media.save(media_path)
    return media_fn

@main.route('/')
def feed():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('feed.html', posts=posts)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    form = RegistrationForm()
    if form.validate_on_submit():
        picture_file = 'default.jpg'
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, image_file=picture_file)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.feed'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.feed'))

@main.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        media_file = None
        if form.media.data:
            media_file = save_media(form.media.data)
        post = Post(title=form.title.data, content=form.content.data, media_file=media_file, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.feed'))
    return render_template('post.html', form=form)

@main.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('The post has been deleted.', 'success')
    return redirect(url_for('main.feed'))

@main.route('/profile/<string:username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).all()

    # Handle profile picture update
    if request.method == 'POST' and 'picture' in request.files:
        picture_file = save_picture(request.files['picture'])
        user.image_file = picture_file
        db.session.commit()
        flash('Your profile picture has been updated!', 'success')
        return redirect(url_for('main.profile', username=user.username))

    return render_template('profile.html', user=user, posts=posts)

# API to get posts (Paginated)
@main.route('/api/posts', methods=['GET'])
def api_get_posts():
    """
    Fetches posts in a paginated format.
    Query Parameters:
    - `page`: Page number (default is 1)
    - `per_page`: Number of posts per page (default is 10)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Fetch paginated posts
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=per_page)

    # Format posts into a JSON response
    posts_list = []
    for post in posts.items:
        posts_list.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'media_file': post.media_file,
            'author': post.author.username,
            'date_posted': post.date_posted.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({
        'posts': posts_list,
        'page': posts.page,
        'total_pages': posts.pages,
        'total_posts': posts.total
    })

# API to create a post
@main.route('/api/post', methods=['POST'])
@login_required
def api_create_post():
    """
    Creates a new post.
    Request Body:
    - `title`: The title of the post
    - `content`: The content of the post
    - `media`: Optional media for the post (image/video)
    """
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    media_file = None
    if 'media' in data:
        media_file = save_media(data['media'])

    if title and content:
        post = Post(title=title, content=content, media_file=media_file, author=current_user)
        db.session.add(post)
        db.session.commit()

        return jsonify({
            'message': 'Post created successfully',
            'post': {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'media_file': post.media_file,
                'author': post.author.username,
                'date_posted': post.date_posted.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 201
    return jsonify({'message': 'Title and content are required'}), 400
