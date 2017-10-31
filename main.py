from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:zgolb@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '9Zo5D26xIVw3Kh'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text())
    pub_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    
    def __init__(self, title, body, user_id, pub_date=None):
        self.title = title
        self.body = body
        self.user = user_id
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged In")
            return redirect('/newpost')
        else: 
            if not user:
                flash('Invalid Username', 'error')
                return render_template('/login.html', username=username)
            else:
                flash('Invalid Password', 'error')
                return render_template('/login.html', username=username)

    return render_template('login.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    
    del session['username']
    flash("Logged Out")
    return redirect('/blog')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == '' or password == '' or verify == '': 
            flash('One or more fields invalid', 'error')
            return render_template('/signup.html', username=username)

        if len(username) < 3 or len(username) > 20 :
            flash('Username must be  between 3 and 20 characters', 'error')
            return render_template('/signup.html', username=username)

        if len(password) < 3 or len(password) > 20:
            flash('Password must be between 3 and 20 characters ', 'error')
            return render_template('/signup.html', username=username)

        if password != verify:
            flash('Passwords do not match', 'error')
            return render_template('/signup.html', username=username)
        else:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash("Logged In")
                return redirect('/newpost')
            else:
                flash('Username already exists', 'error')
                return render_template('/signup.html', username=username)

    return render_template('signup.html')



@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.args.get('id'):
        blog_id = request.args.get('id')
        post = Blog.query.get(blog_id)
        user_id = request.args.get('id')
        user = Blog.query.get(user_id)
        return render_template('post.html', post=post, user=user)

    if request.args.get('user'):
        username = request.args.get('user')
        user = User.query.filter_by(username=username).first()
        posts = user.blogs
        return render_template('singleUser.html', posts=posts, user=user)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not title or not body:
            flash('Please fill in both fields', 'error')
            return render_template('new_post.html')
        else:
            user = User.query.filter_by(username=session['username']).first()
            new_post = Blog(title, body, user, pub_date=None)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_post.id))

    posts = Blog.query.all()
    users = User.query.all()
    return render_template('blog.html', posts=posts, users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    return render_template('new_post.html')


@app.route('/', methods=['POST', 'GET'])
def index():

    users = User.query.all()
    return render_template('index.html', users=users)





if __name__ == '__main__':
    app.run()