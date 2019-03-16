import os
import click
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Length
# from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        os.path.join(app.root_path, os.getenv('DATABASE_FILE', 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

# bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get_or_404(int(user_id))
    return user

class MovieForm(FlaskForm):
    title = StringField('Title', validators=[Required(), Length(1,60)])
    year = StringField('Year', validators=[Required(), Length(1,4)])
    submit = SubmitField('Add')

class LoginForm(FlaskForm):
    user_name = StringField('User Name', validators=[Required(), Length(1, 20)])
    password = StringField('Password', validators=[Required(), Length(1, 60)])
    submit = SubmitField('Submit')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    user_name = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def velidate_password(self, password):
        return check_password_hash(self.password_hash, password)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

@app.cli.command()
@click.option('--username', prompt=True, help="The username used to login.")
@click.option('--password', 
              prompt=True, 
              hide_input=True, 
              confirmation_prompt=True,
              help="The password used to login.")
def admin(username, password):
    db.create_all()
    user = User.query.first()

    if not user:
        click.echo("Creating administrator...")
        user = User(user_name=username, name='Admin')
        user.set_password(password)
        user.user_name = username
        user.set_password(password)
        db.session.add(user)
    else:
        user.user_name = username
        user.set_password(password)

    db.session.commit()
    click.echo("Done.")

@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:
        db.drop_all()
        click.echo('Drop data...\ndone.')
    db.create_all()
    click.echo('Initialized database.')

@app.cli.command()
def forge():
    db.create_all()

    name = 'Murphian Xiao'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)

    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Made data.')


@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = MovieForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            title = form.title.data
            year = form.year.data
            movie = Movie(title=title, year=year)
            db.session.add(movie)
            db.session.commit()
            flash('Item created.')
            return redirect(url_for('index'))
        else:
            flash('Invalid input')
            return redirect(url_for('index'))
    movies = Movie.query.all()
    return render_template('index.html', movies=movies, form=form)

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def movie_edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = MovieForm()
    if request.method == 'POST':
        if form.validate_on_submit() == True:
            movie.title = form.title.data
            movie.year = form.year.data
            db.session.commit()
            flash('Item updated.')
            return redirect(url_for('index'))
        else:
            print('>>>>>>', form.errors)
            flash('Invalid input')
            return redirect(url_for('movie_edit', movie_id=movie_id))
    
    form.title.data = movie.title
    form.year.data = movie.year
    return render_template('movie_edit.html', form=form, movie=movie)

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def movie_delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.first()
            user_name = form.user_name.data
            password = form.password.data
            if user.user_name == user_name and user.velidate_password(password):
                login_user(user)
                flash("Login success.")
                return redirect(url_for('index'))
            else:
                flash('Incorrect username or password.')
                return redirect(url_for('login'))
        else:
            flash('Invalid input.')
            # return render_template('login.html', form=form)
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404