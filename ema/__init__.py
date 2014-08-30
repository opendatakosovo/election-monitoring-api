import os
import ConfigParser
import logging
import logging.config

from logging.handlers import RotatingFileHandler

from flask import Flask
from flask.views import View
from flask.ext.pymongo import PyMongo

from utils.utils import Utils


# Create MongoDB database object.
mongo = PyMongo()

# Create utils instance.
utils = Utils()

def create_app():
	''' Create the Flask app.
	'''
	# Create the Flask app.
	app = Flask(__name__)

	# Load application configurations
	load_config(app)

	# Configure logging.
	configure_logging(app)

	# Register URL rules.
	register_url_rules(app)

	# Init app for use with this PyMongo
	# http://flask-pymongo.readthedocs.org/en/latest/#flask_pymongo.PyMongo.init_app
	mongo.init_app(app, config_prefix='MONGO')

	return app

	
def load_config(app):
	''' Reads the config file and loads configuration properties into the Flask app.
	:param app: The Flask app object.
	'''

	# Get the path to the application directory, that's where the config file resides.
	par_dir = os.path.join(__file__, os.pardir)
	par_dir_abs_path = os.path.abspath(par_dir)
	app_dir = os.path.dirname(par_dir_abs_path)

	# Read config file
	# FIXME: Use the "common pattern" described in "Configuring from Files": http://flask.pocoo.org/docs/config/
	config = ConfigParser.RawConfigParser()
	config_filepath = app_dir + '/config.cfg'
	config.read(config_filepath)

	# Set up config properties
	app.config['SERVER_PORT'] = config.get('Application', 'SERVER_PORT')

	app.config['MONGO_DBNAME'] = config.get('Mongo', 'DB_NAME')

	# Logging path might be relative or starts from the root.
	# If it's relative then be sure to prepend the path with the application's root directory path.
	log_path = config.get('Logging', 'PATH')
	if log_path.startswith('/'):
		app.config['LOG_PATH'] = log_path
	else:
		app.config['LOG_PATH'] = app_dir + '/' + log_path

	app.config['LOG_LEVEL'] = config.get('Logging', 'LEVEL').upper()

def configure_logging(app):
	
	# Get the path of the log from the config
	log_path = app.config['LOG_PATH']
	
	# Get the level of logging from the config
	log_level = app.config['LOG_LEVEL']

	# If path directory doesn't exist, create it.
	log_dir = os.path.dirname(log_path)
	if not os.path.exists(log_dir):
		os.makedirs(log_dir)

	# Create formatter
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	
	# Create Log_Handler
	log_handler = RotatingFileHandler(log_path, maxBytes=250000, backupCount=5)

	# add formatter to log handler
	log_handler.setFormatter(formatter)

	# Get the level of the Debug and set it to the logger
	app.logger.setLevel(log_level)

	# Add the handlers to the logger
	app.logger.addHandler(log_handler)
	
	# Test if the logging is working by typing this string to a file.
	app.logger.info('Logging to: %s', log_path)


# Index page view.
from views.index import Index

# Polling station views.
from views.polling_station.all import PollingStation
from views.polling_station.commune import CommunePollingStation
from views.polling_station.polling_station import PollingStationPollingStation

# Observation views.
from views.observation.commune import CommuneObservation
from views.observation.polling_station import PollingStationObservation
from views.observation.room import RoomObservation

# KVV members gender distribution views.
from views.kvv.room_gender_distribution import KvvRoomGenderDistribution
from views.kvv.commune_gender_distribution import KvvCommuneGenderDistribution
from views.kvv.polling_station_gender_distribution import KvvPollingStationGenderDistribution

# Hour vote count views.
from views.vote_count.commune_votes import CommuneVoteCount
from views.vote_count.polling_station_votes import PollingStationVoteCount
from views.vote_count.room_votes import RoomVoteCount

from views.search import Search

def register_url_rules(app):
	''' Register the URL rules. 
		Use pluggable class-based views: http://flask.pocoo.org/docs/views/
	:param app: The Flask application instance.
	''' 

	# Show instructional index page.
	app.add_url_rule('/', view_func=Index.as_view('index'))

	# Search observation documents
	app.add_url_rule('/<string:observer>/search/<int:year>/<string:election_type>/<string:election_round>/', view_func=Search.as_view('search'))

	# Register URL rules for polling staions.
	register_url_rules_polling_stations(app)

	# Register URL rules for observations.
	register_url_rules_observations(app)

	# Register URL rules for KVV members gender distribution.
	register_url_rules_kvv_members_gender_distribution(app)
	
	# Register URL rults for hour votes count.
	register_url_rules_hour_votes_count(app)


def register_url_rules_polling_stations(app):
	''' Register URL rules for polling stations.
	:param app: The application instance.
	'''
	# Get all polling station for a given election.
	app.add_url_rule('/dia/polling-stations/<int:year>/<string:election_type>/<string:election_round>', view_func=PollingStation.as_view('polling_stations'))

	# Get polling station for a given commune.
	app.add_url_rule('/dia/polling-stations/<int:year>/<string:election_type>/<string:election_round>/<string:commune_slug>', view_func=CommunePollingStation.as_view('commung_polling_stations'))

	# Get polling station for a given polling station. Silly, but sometimes we only have slug and want the value.
	# Should implement a less hardcore way to get value for a slug.
	app.add_url_rule('/dia/polling-stations/<int:year>/<string:election_type>/<string:election_round>/<string:commune_slug>/<string:polling_station_slug>', view_func=PollingStationPollingStation.as_view('polling_station_polling_stations'))


def register_url_rules_observations(app):
	''' Register URL rules for observations.
	:param app: The application instance.
	'''
	# Get observations for a specified commune.
	app.add_url_rule('/dia/observations/<int:year>/<string:election_type>/<string:election_round>/<string:commune_slug>', view_func=CommuneObservation.as_view('commune_observations'))

	# Get observations for a specified commune and polling station.
	app.add_url_rule('/dia/observations/<int:year>/<string:election_type>/<string:election_round>/<string:commune_slug>/<string:polling_station_slug>', view_func=PollingStationObservation.as_view('polling_station_observations'))

	# Get observations for a specified commune, polling station, and polling station room.
	app.add_url_rule('/dia/observations/<int:year>/<string:election_type>/<string:election_round>/<string:commune_slug>/<string:polling_station_slug>/<string:polling_station_room>', view_func=RoomObservation.as_view('room_observations'))

def register_url_rules_kvv_members_gender_distribution(app):
	''' Register URL rules for KVV members gender distribution.
	:param app: The application instance.
	'''

	# Get KVV members gender distribution for a given commune.
	app.add_url_rule('/dia/psc-members-gender-distribution/<int:year>/<string:election_type>/<string:election_round>/<string:commune_name>', view_func=KvvCommuneGenderDistribution.as_view('commune_gender_distribution'))

	# Get KVV members gender distribution for a given commune and polling station.
	app.add_url_rule('/dia/psc-members-gender-distribution/<int:year>/<string:election_type>/<string:election_round>/<string:commune_name>/<string:polling_station_name>', view_func=KvvPollingStationGenderDistribution.as_view('polling_station_gender_distribution'))

	# Get KVV members gender distribution for a given commune, polling station, and polling station room number.
	app.add_url_rule('/dia/psc-members-gender-distribution/<int:year>/<string:election_type>/<string:election_round>/<string:commune_name>/<string:polling_station_name>/<string:room_number>', view_func=KvvRoomGenderDistribution.as_view('room_gender_distribution'))

	
def register_url_rules_hour_votes_count(app):
	''' Register URL rules for hour votes count.
	:param app: The application instance.
	'''
	
	# Get hour votes count for given commune.
	app.add_url_rule('/dia/hour-vote-count/<int:year>/<string:election_type>/<string:election_round>/<string:commune_name>', view_func=CommuneVoteCount.as_view('commune_votes'))

	# Get hour votes count for given commune and polling station.
	app.add_url_rule('/dia/hour-vote-count/<int:year>/<string:election_type>/<string:election_round>/<string:commune_name>/<string:polling_station_name>', view_func=PollingStationVoteCount.as_view('polling_station_votes'))

	# Get hour votes count for given commune, polling station, and room number.
	app.add_url_rule('/dia/hour-vote-count/<int:year>/<string:election_type>/<string:election_round>/<string:commune_name>/<string:polling_station_name>/<string:room_number>', view_func=RoomVoteCount.as_view('room_votes'))
