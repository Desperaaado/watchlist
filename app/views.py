from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (login_required, login_user, logout_user,
                         current_user)
from app import db, app
from app.models import User, Movie
from app.forms import MovieForm, LoginForm


@app.route('/', methods=['GET', 'POST'])
def index():
    form = MovieForm()
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Please Login.')
            return redirect(url_for('login'))

        if form.validate_on_submit():
            title = form.title.data
            year = form.year.data
            movie = Movie(title=title, year=year)
            db.session.add(movie)
            db.session.commit()
            flash('Item created.')
            return redirect(url_for('index'))
        else:
            flash('Invalid input.')
            return redirect(url_for('index'))
    movies = Movie.query.all()
    return render_template('index.html', movies=movies, form=form)

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
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
            flash('Invalid input.')
            return redirect(url_for('movie_edit', movie_id=movie_id))
    
    form.title.data = movie.title
    form.year.data = movie.year
    return render_template('movie_edit.html', form=form, movie=movie)

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
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
            if user.user_name == user_name and user.validate_password(password):
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

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('GoodBye.')
    return redirect(url_for('index'))
