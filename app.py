#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/fyyur'
#make migrations
migrate=Migrate(app,db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
#creates Venue table
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website=db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent=db.Column(db.String(120))
    seeking_description=db.Column(db.String(500))
    show = db.relationship('Show', backref='Artist', lazy=True)

#returns info about the venue
    def __repr__(self):
        return f"the vevnu name is {self.name}"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
# create artist model
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website= db.Column(db.String(120))
    seeking_venue=db.Column(db.String(120))
    seeking_description= db.Column(db.String(500))
    show = db.relationship('Show', backref='Venue', lazy=True)


#return info about the artist
    def __repr__(self):
        return f"the Artist name is {self.name}"
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
#creting show model
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer,primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"the  of {self.artist_id} starts at {self.start_time} at {self.venue_id} "
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

#home page
@app.route('/')
def index():
  return render_template('pages/home.html')


# display  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    cur_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
    Venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
    stateAndcity = ''
    data = []
    for venue in Venues:
        upcoming_shows = Show.query.options(db.joinedload(Show.Venue)).filter(Show.start_time > cur_time).all()
        data.append({
            "city":venue.city,
            "state":venue.state,
            "venues": [{
            "id": venue.id,
            "name":venue.name,

            }]})
    return render_template('pages/venues.html', areas=data);


#find venues
@app.route('/venues/search', methods=['POST'])
def search_venues():
    venue_search= Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))
    venue_list =venue_search.order_by(Venue.name).all()
    response={
        "data": venue_list
      }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue_search = Venue.query.get(venue_id)
    cur_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    venue_details = {}
    venue_details['venue_search']=venue_search
    venue= venue_details['venue_search']
    new_shows_search = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(Show.start_time > cur_time).all()
    venue_details["upcoming_shows"] = new_shows_search
    venue_details["upcoming_shows_count"] = len(new_shows_search)
    past_shows_search = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(Show.start_time <= cur_time).all()
    venue_details["past_shows"] = past_shows_search
    venue_details["past_shows_count"] = len(past_shows_search)
    return render_template('pages/show_venue.html', venue=venue_details)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
     try:
         venue = Venue(
          name=request.form['name'],
          genres=request.form.getlist('genres'),
          address=request.form['address'],
          city=request.form['city'],
          state=request.form['state'],
          phone=request.form['phone'],
          facebook_link=request.form['facebook_link'],

        )
         db.session.add(venue)
         flash('Venue ' + request.form['name'] + ' was successfully listed!')
     except SQLAlchemyError as e:
         flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
     finally:
         db.session.commit()
         db.session.close()
     return render_template('pages/home.html')


#delete venue which gets its id from the view
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist_search = Artist.query.all()
  return render_template('pages/artists.html', artists=artist_search)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    artist_search = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
    artist_list =artist_search.order_by(Artist.name).all()
    response={
            "data": artist_list
      }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist_search = Artist.query.get(artist_id)
    artist_details = {}
    artist_details['artist_search']=artist_search
    cur_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #getting the upcoming show
    new_shows_search = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(Show.start_time > cur_time).all()
    artist_details["upcoming_shows"] = new_shows_search
    artist_details["upcoming_shows_count"] = len(new_shows_search)
    #getting the past shows for the artist
    past_shows_search = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(Show.start_time <= cur_time).all()
    artist_details["past_shows"] = past_shows_search
    artist_details["past_shows_count"] = len(past_shows_search)
    return render_template('pages/show_artist.html', artist=artist_details)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)
    artist_details = Artist.details(artist)
    form.name.data = artist_details["name"]
    form.genres.data = artist_details["genres"]
    form.city.data = artist_details["city"]
    form.state.data = artist_details["state"]
    form.phone.data = artist_details["phone"]
    form.website.data = artist_details["website"]
    form.facebook_link.data = artist_details["facebook_link"]
    form.seeking_venue.data = artist_details["seeking_venue"]
    form.seeking_description.data = artist_details["seeking_description"]
    form.image_link.data = artist_details["image_link"]
    return render_template('forms/edit_artist.html', form=form, artist=artist_details)

#edit the artist record
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    artist_data = Artist.query.get(artist_id)
    if artist_data:
        if form.validate():
            seeking_venue = False
            seeking_description = ''
            if 'seeking_venue' in request.form:
                seeking_venue = request.form['seeking_venue'] == 'y'
            if 'seeking_description' in request.form:
                seeking_description = request.form['seeking_description']
            setattr(artist_data, 'name', request.form['name'])
            setattr(artist_data, 'genres', request.form.getlist('genres'))
            setattr(artist_data, 'city', request.form['city'])
            setattr(artist_data, 'state', request.form['state'])
            setattr(artist_data, 'phone', request.form['phone'])
            setattr(artist_data, 'website', request.form['website'])
            setattr(artist_data, 'facebook_link', request.form['facebook_link'])
            setattr(artist_data, 'image_link', request.form['image_link'])
            setattr(artist_data, 'seeking_description', seeking_description)
            setattr(artist_data, 'seeking_venue', seeking_venue)
            Artist.update(artist_data)
    return redirect(url_for('show_artist', artist_id=artist_id))

#edit venue record
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue_search = Venue.query.get(venue_id)
    if venue_search:
        venue_details = Venue.detail(venue_search)
        form.name.data = venue_details["name"]
        form.genres.data = venue_details["genres"]
        form.address.data = venue_details["address"]
        form.city.data = venue_details["city"]
        form.state.data = venue_details["state"]
        form.phone.data = venue_details["phone"]
        form.website.data = venue_details["website"]
        form.facebook_link.data = venue_details["facebook_link"]
        form.seeking_talent.data = venue_details["seeking_talent"]
        form.seeking_description.data = venue_details["seeking_description"]
        form.image_link.data = venue_details["image_link"]
    return render_template('form/edit_venue.html', form=form, Venue=venue_details)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    venue_data = Venue.query.get(venue_id)
    if venue_data:
        if form.validate():
            seeking_talent = False
            seeking_description = ''
            if 'seeking_talent' in request.form:
                seeking_talent = request.form['seeking_talent'] == 'y'
            if 'seeking_description' in request.form:
                seeking_description = request.form['seeking_description']
            setattr(venue_data, 'name', request.form['name'])
            setattr(venue_data, 'genres', request.form.getlist('genres'))
            setattr(venue_data, 'address', request.form['address'])
            setattr(venue_data, 'city', request.form['city'])
            setattr(venue_data, 'state', request.form['state'])
            setattr(venue_data, 'phone', request.form['phone'])
            setattr(venue_data, 'website', request.form['website'])
            setattr(venue_data, 'facebook_link', request.form['facebook_link'])
            setattr(venue_data, 'image_link', request.form['image_link'])
            setattr(venue_data, 'seeking_description', seeking_description)
            setattr(venue_data, 'seeking_talent', seeking_talent)
            Venue.update(venue_data)
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        seeking_venue = False
        seeking_description = ''
        if 'seeking_venue' in request.form:
            seeking_venue = request.form['seeking_venue'] == 'y'
        if 'seeking_description' in request.form:
            seeking_description = request.form['seeking_description']
        new_artist = Artist(
              name=request.form['name'],
              genres=request.form.getlist('genres'),
              city=request.form['city'],
              state= request.form['state'],
              phone=request.form['phone'],
              # website=request.form['website'],
              # image_link=request.form['image_link'],
              facebook_link=request.form['facebook_link'],
              # seeking_venue=seeking_venue,
              # seeking_description=seeking_description,
              )
        db.session.add(new_artist)
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except SQLAlchemyError as e:
        return "sssd"
        flash('An error occurred. Artist ' + request.form['name'] + 'could not be listed. ')
    finally:
        db.session.commit()
        db.session.close()
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    show_search = Show.query.options(db.joinedload(Show.Venue), db.joinedload(Show.Artist)).all()
    return render_template('pages/shows.html', shows=show_search)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        new_show = Show(
          venue_id=request.form['venue_id'],
          artist_id=request.form['artist_id'],
          start_time=request.form['start_time'],
        )
        db.session.add(new_show)
        db.session.commit()
        db.session.close()
        flash('Show was successfully listed!')
    except SQLAlchemyError as e:
        flash('An error occured. Show could not be listed.')
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
