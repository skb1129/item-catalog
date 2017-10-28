import os
import re
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Users, Genres, Movies

app = Flask(__name__)

engine = create_engine('sqlite:///movies.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
Session = DBSession()

@app.route('/')
@app.route('/movies/')
def main_page():
	genres = Session.query(Genres).all()
	return render_template('main_page.html', genres=genres)


@app.route('/movies/<genre>/')
def genre_page(genre):
	genres = Session.query(Genres).all()
	movies = Session.query(Movies).filter_by(genre=genre).all()
	return render_template('genre_page.html', movies=movies, genre=genre,
							genres=genres)


@app.route('/movies/<int:movie_id>/')
def movie_page(movie_id):
	genres = Session.query(Genres).all()
	movie = Session.query(Movies).filter_by(id=movie_id).one()
	return render_template('movie_page.html', movie=movie, movie_id=movie_id,
							genres=genres)


@app.route('/post_movie/', methods=['GET', 'POST'])
def post_movie():
	if request.method == 'POST':
		movie = Movies(name=request.form['name'],
						director=request.form['director'],
						description=request.form['description'],
						posterUrl=request.form['posterUrl'],
						genre=request.form['genre'])
		Session.add(movie)
		Session.commit()
		return redirect(url_for('movie_page', movie_id=movie.id))
	else:
		genres = Session.query(Genres).all()
		return render_template('post_movie.html', genres=genres)


@app.route('/create_genre/', methods=['GET', 'POST'])
def create_genre():
	if request.method == 'POST':
		genre = Genres(name=request.form['name'])
		Session.add(genre)
		Session.commit()
		return redirect(url_for('main_page'))
	else:
		genres = Session.query(Genres).all()
		return render_template('create_genre.html', genres=genres)


@app.route('/delete_movie/<int:movie_id>/')
def delete_movie(movie_id):
	movie = Session.query(Movies).filter_by(id=movie_id).one()
	Session.delete(movie)
	Session.commit()
	return redirect(url_for('main_page'))


@app.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
	if request.method == 'POST':
		movie = Session.query(Movies).filter_by(id=movie_id).one()
		movie.name=request.form['name']
		movie.director=request.form['director']
		movie.description=request.form['description']
		movie.posterUrl=request.form['posterUrl']
		movie.genre=request.form['genre']
		Session.add(movie)
		Session.commit()
		return redirect(url_for('movie_page', movie_id=movie_id))


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
