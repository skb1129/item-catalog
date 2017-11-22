import os, random, string, datetime, json, httplib2, requests, re
from flask import Flask, render_template, request, redirect, url_for
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Users, Genres, Movies

app = Flask(__name__)

engine = create_engine('sqlite:///movies.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
Session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'movie-cafe'

def state():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return state


@app.route('/')
@app.route('/movies/')
def main_page():
	genres = Session.query(Genres).all()
	return render_template('main_page.html', genres=genres, STATE=state())


@app.route('/movies/<genre>/')
def genre_page(genre):
	genres = Session.query(Genres).all()
	movies = Session.query(Movies).filter_by(genre=genre).all()
	return render_template('genre_page.html', movies=movies, genre=genre,
							genres=genres, STATE=state())


@app.route('/movies/<int:movie_id>/')
def movie_page(movie_id):
	genres = Session.query(Genres).all()
	movie = Session.query(Movies).filter_by(id=movie_id).one()
	return render_template('movie_page.html', movie=movie, movie_id=movie_id,
							genres=genres, STATE=state())


@app.route('/post_page/', methods=['GET', 'POST'])
def post_page():
	if request.method == 'POST':
		if 'new_genre' in request.form:
			genre = Genres(name=request.form['new_genre'])
			Session.add(genre)
			Session.commit()
			return redirect(url_for('main_page'))
		else:
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
		return render_template('post_page.html', genres=genres, STATE=state())


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
		movie.name = request.form['name']
		movie.director = request.form['director']
		movie.description = request.form['description']
		movie.posterUrl = request.form['posterUrl']
		movie.genre = request.form['genre']
		Session.add(movie)
		Session.commit()
		return redirect(url_for('movie_page', movie_id=movie_id))


@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
	if request.args.get('state') != login_session['state']:
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

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']


@app.route('/gdisconnect')
def gdisconnect():
	access_token = login_session['access_token']
	if access_token is None:
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	if result['status'] == '200':
		del login_session['access_token'] 
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		response = make_response(json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
