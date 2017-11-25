import os, random, string, datetime, json, httplib2, requests, re
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import make_response, g
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Users, Genres, Movies
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

app = Flask(__name__)

engine = create_engine('sqlite:///movies.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
Session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'movie-cafe'

def set_state():
	g.state = ''.join(random.choice(string.ascii_uppercase + string.digits)
						for x in xrange(32))
	login_session['state'] = g.state


def create_user():
	if not Session.query(Users).filter_by(email=login_session.get('email')).one_or_none():
		user = Users(email=login_session.get('email'),
						name=login_session.get('name'),
						picture=login_session.get('picture'))
		Session.add(user)
		Session.commit()


@app.route('/')
@app.route('/movies/')
def main_page():
	set_state()
	genres = Session.query(Genres).all()
	return render_template('main_page.html', genres=genres,
							login_session=login_session)


@app.route('/movies/<genre>/')
def genre_page(genre):
	set_state()
	genres = Session.query(Genres).all()
	movies = Session.query(Movies).filter_by(genre=genre).all()
	return render_template('genre_page.html', movies=movies, genre=genre,
							genres=genres, login_session=login_session)


@app.route('/movies/<int:movie_id>/')
def movie_page(movie_id):
	set_state()
	genres = Session.query(Genres).all()
	movie = Session.query(Movies).filter_by(id=movie_id).one()
	return render_template('movie_page.html', movie=movie, movie_id=movie_id,
							genres=genres, login_session=login_session)


@app.route('/post_page/', methods=['GET', 'POST'])
def post_page():
	set_state()
	if login_session.get('email') is not None:
		if request.method == 'POST':
			if 'new_genre' in request.form:
				genre = Genres(name=request.form['new_genre'],
								user_email=login_session.get('email'))
				Session.add(genre)
				Session.commit()
				return redirect(url_for('main_page'))
			else:
				movie = Movies(name=request.form['name'],
								director=request.form['director'],
								description=request.form['description'],
								posterUrl=request.form['posterUrl'],
								genre=request.form['genre'],
								user_email=login_session.get('email'))
				Session.add(movie)
				Session.commit()
				return redirect(url_for('movie_page', movie_id=movie.id))
		else:
			genres = Session.query(Genres).all()
			return render_template('post_page.html', genres=genres,
									login_session=login_session)
	else:
		return redirect(url_for('error_page', error='You need to login first.'))


@app.route('/delete_movie/<int:movie_id>/')
def delete_movie(movie_id):
	movie = Session.query(Movies).filter_by(id=movie_id).one()
	if login_session.get('email') == movie.user_email:	
		Session.delete(movie)
		Session.commit()
		return redirect(url_for('main_page'))
	else:
		return redirect(url_for('error_page', error='You are not Authorized.'))


@app.route('/edit_movie/<int:movie_id>/', methods=['GET', 'POST'])
def edit_movie(movie_id):
	if request.method == 'POST':
		movie = Session.query(Movies).filter_by(id=movie_id).one()
		if login_session.get('email') == movie.user_email:
			movie.name = request.form['name']
			movie.director = request.form['director']
			movie.description = request.form['description']
			movie.posterUrl = request.form['posterUrl']
			movie.genre = request.form['genre']
			Session.add(movie)
			Session.commit()
			return redirect(url_for('movie_page', movie_id=movie_id))
		else:
			return redirect(url_for('error_page',
										error='You are not Authorized.'))


@app.route('/delete_genre/<genre>/')
def delete_genre(genre):
	genre = Session.query(Genres).filter_by(name=genre).one()
	if login_session.get('email') == genre.user_email:	
		movies = Session.query(Movies).filter_by(genre=genre).all()
		Session.delete(movies)
		Session.delete(genre)
		Session.commit()
		return redirect(url_for('main_page'))
	else:
		return redirect(url_for('error_page', error='You are not Authorized.'))


@app.route('/gconnect/', methods=['POST'])
def gconnect():
	# Validate state token
	if request.args.get('state') != login_session.get('state'):
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	code = request.data

	try:
	# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
		json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
			% access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
		json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
		json.dumps("Token's client ID does not match app's."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(
		json.dumps('Current user is already connected.'),
		200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	login_session['access_token'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['name'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	create_user()

	return jsonify(name=login_session.get('name'),
					email=login_session.get('email'),
					picture=login_session.get('picture'))


@app.route('/gdisconnect/', methods=['POST'])
def gdisconnect():
	access_token = login_session.get('access_token')
	if access_token is None:
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session.get('access_token')
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	if result['status'] == '200':
		login_session.pop('access_token', None)
		login_session.pop('gplus_id', None)
		login_session.pop('name', None)
		login_session.pop('email', None)
		login_session.pop('picture', None)
		return redirect(url_for('main_page'))
	else:
		response = make_response(json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response


@app.route('/error/')
def error_page():
	set_state()
	genres = Session.query(Genres).all()	
	return render_template('error_page.html', error=request.args.get('error'),
							genres=genres, login_session=login_session)


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
