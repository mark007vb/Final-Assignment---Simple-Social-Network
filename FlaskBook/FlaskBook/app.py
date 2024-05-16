from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskbook.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a secure key
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(140), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('likes', lazy=True))
    user = db.relationship('User', backref=db.backref('likes', lazy=True))

def post_is_liked(post_id):
    post = Post.query.get(post_id)
    return current_user in post.likes if current_user.is_authenticated else False

@app.route('/')
def home():
    
    
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)

@app.route('/profile/<nickname>')
def profile(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    return render_template('profile.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nickname = request.form['nickname']
        email = request.form['email']
        birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
        password = request.form['password']
        new_user = User(nickname=nickname, email=email, birth_date=birth_date, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        user = User.query.filter_by(nickname=nickname).first()
        if user and user.password == password:
            session['user_id'] = user.id
            flash('Login successful.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid nickname or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the user session
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/create_post', methods=['POST'])
def create_post():
    if 'user_id' in session:
        user_id = session['user_id']
        content = request.form['content']
        new_post = Post(content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully.', 'success')
    else:
        flash('You must be logged in to create a post.', 'danger')
    return redirect(url_for('home'))

@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' in session:
        user_id = session['user_id']
        post = Post.query.get(post_id)
        if post:
            like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
            if not like:
                new_like = Like(post_id=post_id, user_id=user_id)
                db.session.add(new_like)
                db.session.commit()
            else:
                unlike_post(post.id)
                #return redirect(url_for('unlike_post', post_id=post.id))
                flash('You have unliked this post.', 'warning')
        else:
            flash('Post not found.', 'danger')
    else:
        flash('You must be logged in to like a post.', 'danger')
    return redirect(url_for('home'))

@app.route('/unlike_post/<int:post_id>', methods=['POST'])
def unlike_post(post_id):
    if 'user_id' in session:
        user_id = session['user_id']
        post = Post.query.get(post_id)
        if post:
            like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
            if like:
                db.session.delete(like)
                db.session.commit()
            else:
                flash('You have not liked this post.', 'warning')
        else:
            flash('Post not found.', 'danger')
    else:
        flash('You must be logged in to unlike a post.', 'danger')
    return redirect(url_for('home'))

@app.route('/birthdays')
def birthdays():
    today = datetime.now().date()
    users = User.query.filter(db.extract('month', User.birth_date) == today.month,
                              db.extract('day', User.birth_date) == today.day).all()
    return render_template('birthdays.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
