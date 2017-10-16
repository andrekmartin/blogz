from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

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

    def __init__ (self, title, body):
        self.title = title
        self.body = body



@app.route('/blog')
def blog():

    if request.args:
        blog_id = request.args.get('id')
        post = Blog.query.get(blog_id)
        return render_template('post.html', post=post)
   
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods = ['POST', 'GET'])
def new_post():
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if not title or not body:
            flash("Add a title & blog entry.", 'error')
            return redirect('/newpost')
            
        else:
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            post = Blog.query.order_by(Blog.id.desc()).first()
            return render_template('post.html', post=post)
    
    return render_template('new_post.html')


@app.route('/')
def index():
    return redirect('blog')




if __name__ == '__main__':
    app.run()