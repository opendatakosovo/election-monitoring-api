from flask import Flask, request, render_template, Response
from flask.ext.pymongo import PyMongo
from flask import request
import pymongo
from collections import OrderedDict
from bson import json_util

from utils import Utils

utils = Utils()

app = Flask(__name__)

# connect to MongoDB database
app.config['MONGO_DBNAME'] = 'kdi'
mongo = PyMongo(app, config_prefix='MONGO')

@app.route('/')
def index():
	return 'Welcome to the Election Monitoring API. TODO: Instructions page.'


@app.route('/api/kdi/observations/<int:year>/<string:election_type>/<string:election_round>/<string:commune_name>', methods=['GET'])
def get_observations_for_given_commune(year, election_type, election_round, commune_name):
	''' Get observations for given commune.
	
	:param: year: The year of the election
	:param: election_type: The type of the election. Can be local (local-election) or general (general-election)
	:param: election_round: The round of the election (e.g. firt-round, second-round...)
	:param: commune_name: The name of the commune.
	'''

	# Get the name of the collection we must query on.
	collection_name = utils.get_collection_name(year, election_type, election_round)
	
	# Execute query.
	observations = mongo.db[collection_name].find({'pollingStation.commune': commune_name})
	
	# Create JSON response object.
	resp = Response(response=json_util.dumps(observations), mimetype='application/json')

	# Return JSON response.
	return resp


@app.route('/api/kdi/observations/<int:year>/<string:election_type>/<string:election_round>/<string:commune_name>/<string:polling_station_name>', methods=['GET'])
def get_observations_for_given_polling_station(year, election_type, election_round, commune_name, polling_station_name):
	''' Get observations for given commune and polling station.
	
	:param: year: The year of the election
	:param: election_type: The type of the election. Can be local (local-election) or general (general-election)
	:param: election_round: The round of the election (e.g. firt-round, second-round...)
	:param: commune_name: The name of the commune.
	:param: polling_station_name: The name of the polling station.
	'''
		
	# Get the name of the collection we must query on.
	collection_name = utils.get_collection_name(year, election_type, election_round)
	
	# Execute query.
	observations = mongo.db[collection_name].find({'pollingStation.commune': commune_name, 'pollingStation.name': polling_station_name})
	
	# Create JSON response object.
	resp = Response(response=json_util.dumps(observations), mimetype='application/json')

	# Return JSON response.
	return resp


@app.route('/api/kdi/observations/kvv-members-gender-distribution/<int:year>/<string:election_type>/<string:election_round>/<string:commune_name>', methods=['GET'])
def get_kvv_members_gender_distribution_for_given_commune(year, election_type, election_round, commune_name):
	''' Get the gender distribution of KVV members in a specified commune.
	
	:param: year: The year of the election
	:param: election_type: The type of the election. Can be local (local-election) or general (general-election)
	:param: election_round: The round of the election (e.g. firt-round, second-round...)
	:param: commune_name: the name of the commune.
	'''
	
	# Get the name of the collection we must query on.
	collection_name = utils.get_collection_name(year, election_type, election_round)
	
	# Execute query.
	gender_observation = mongo.db[collection_name].aggregate([
		{ "$match": 
			{ "pollingStation.commune":commune_name }
		}, 
		{'$group':
			{'_id':'$pollingStation.commune',
			'total':
				{'$sum':'$preparation.votingMaterialsPlacedInAndOutVotingStation.kvvMembers.total'},
			'totalFemale':
				{'$sum':'$preparation.votingMaterialsPlacedInAndOutVotingStation.kvvMembers.female'}
			}
		}
	])
	
	# Create JSON response object.
	resp = Response(response=json_util.dumps(gender_observation), mimetype='application/json')
	
	# Return JSON response.
	return resp

	
@app.route('/api/kdi/observations/kvv-members-gender-distribution/<int:year>/<string:election_type>/<string:election_round>/<string:commune_name>/<string:polling_station_name>', methods=['GET'])
def get_kvv_members_gender_distribution_for_given_polling_station(year, election_type, election_round, commune_name, polling_station_name):
	
	''' Get the gender distribution of KVV members in a specified polling station.
	
	:param: year: The year of the election
	:param: election_type: The type of the election. Can be local (local-election) or general (general-election)
	:param: election_round: The round of the election (e.g. firt-round, second-round...)
	:param: commune_name: the name of the commune.
	:param: polling_station_name: the name of the polling station.
	'''

	# Get the name of the collection we must query on.
	collection_name = utils.get_collection_name(year, election_type, election_round)

	# Execute query.
	gender_observation_by_polling_station = mongo.db[collection_name].aggregate([
		{ "$match": 
			{ "pollingStation.commune":commune_name,  "pollingStation.name":polling_station_name}
		}, 
		{'$group':
			{'_id':'$pollingStation.commune',
			'total':
				{'$sum':'$preparation.votingMaterialsPlacedInAndOutVotingStation.kvvMembers.total'},
			'totalFemale':
				{'$sum':'$preparation.votingMaterialsPlacedInAndOutVotingStation.kvvMembers.female'}
			}
		}
	])

	# Create JSON response object.
	resp = Response(response=json_util.dumps(gender_observation_by_polling_station), mimetype='application/json')
	
	# Return JSON response.
	return resp


@app.route('/api/kdi/observations/votes-count/<int:year>/<string:election_type>/<string:election_round>/<string:commune_name>', methods=['GET'])
def get_number_of_votes_casted_for_given_commune(year, election_type, election_round, commune_name):
	''' Get the number of votes casted in a specified commune.
	The votes are grouped by the following hours: 10 AM, 1 PM, 4 PM, and 7 PM.
	
	:param: year: The year of the election
	:param: election_type: The type of the election. Can be local (local-election) or general (general-election)
	:param: election_round: The round of the election (e.g. firt-round, second-round...)
	:param: commune_name: the name of the commune.
	'''
	
	# Get the name of the collection we must query on.
	collection_name = utils.get_collection_name(year, election_type, election_round)
	
	# Execute query.
	voted_by_observation = mongo.db[collection_name].aggregate([
			{ "$match":
				{ "pollingStation.commune":commune_name } 
			},
			{'$group':
				{'_id':'$pollingStation.commune',
					'tenAM':{
						'$sum':'$votingProcess.voters.howManyVotedBy.tenAM'
							},
					'onePM':{
						'$sum':'$votingProcess.voters.howManyVotedBy.onePM'
							},
					'fourPM':{
						'$sum':'$votingProcess.voters.howManyVotedBy.fourPM'
							},
					'sevenPM':{
						'$sum':'$votingProcess.voters.howManyVotedBy.sevenPM'
							}
				}
			}
		])
	
	# Create JSON response object.
	resp = Response(response=json_util.dumps(voted_by_observation), mimetype='application/json')
	
	# Return JSON response.
	return resp


@app.route('/api/kdi/observations/votes-count/<int:year>/<string:election_type>/<string:election_round>/<string:commune_name>/<string:polling_station_name>', methods=['GET'])
def get_number_of_votes_casted_for_given_polling_station(year, election_type, election_round, commune_name, polling_station_name):
	''' Get the number of votes casted in a specified commune and polling stations.
	The votes are grouped by the following hours: 10 AM, 1 PM, 4 PM, and 7 PM.
	
	:param: year: The year of the election
	:param: election_type: The type of the election. Can be local (local-election) or general (general-election)
	:param: election_round: The round of the election (e.g. firt-round, second-round...)
	:param: commune_name: the name of the commune.
	:param: polling_station_name: the name of the polling station.
	'''
	# Get the name of the collection we must query on.
	collection_name = utils.get_collection_name(year, election_type, election_round)
	# Execute query.
	voted_by_observation = mongo.db[collection_name].aggregate([
			{ "$match":
				{ "pollingStation.commune":commune_name,  "pollingStation.name":polling_station_name}
			},
			{'$group':
				{'_id':'$pollingStation.commune',
					'tenAM':{
						'$sum':'$votingProcess.voters.howManyVotedBy.tenAM'
							},
					'onePM':{
						'$sum':'$votingProcess.voters.howManyVotedBy.onePM'
							},
					'fourPM':{'$sum':'$votingProcess.voters.howManyVotedBy.fourPM'
							},
					'sevenPM':{
							'$sum':'$votingProcess.voters.howManyVotedBy.sevenPM'
							}
				}
			}
		])
	
	# Create JSON response object.
	resp = Response(response=json_util.dumps(voted_by_observation), mimetype='application/json')	

	# Return JSON response.
	return resp
@app.route('/kdi/observations/search/<int:year>/<string:election_type>/<string:election_round>/<string:commune>/<string:polling_station>/<string:ultra_violet_control>/<string:finger_sprayed>/<string:query_method>', methods=['GET'])
def search(year,election_type,election_round,commune,polling_station,ultra_violet_control,finger_sprayed,query_method):
	''' Get the results for the parameters that are taken from the GET Method.
	
	:param: year: The year of the election
	:param: election_type: The type of the election. Can be local (local-election) or general (general-election)
	:param: election_round: The round of the election (e.g. firt-round, second-round...)
	:param: commune_name: the name of the commune.
	:param: polling_station: the name of the polling station.
	:param: ultra_violet_control: checks if UV check happened in that polling station
	:param: finger_sprayed: checks if finger spray happened in that polling station
	:param:	query_method: the type of the query that is going to hit MongoDB,  AND/OR
	'''
	# Get the name of the collection we must query on.
	collection_name = utils.get_collection_name(year, election_type, election_round)
	# Execute query.
	# If the query_method is equals to "and", execute mongo query with $and operator
	if(query_method == "and"):
		search_results_and = mongo.db[collection_name].find({ 
																"$and" : [ 
																	{"pollingStation.commune" : commune },
																	{"pollingStation.name" : polling_station},
																	{"votingProcess.voters.ultraVioletControl" : ultra_violet_control},
																	{"votingProcess.voters.fingerSprayed" : finger_sprayed }
																]})
		resp = Response(response = json_util.dumps(search_results_and), mimetype = 'application/json')
	# If the query_method is equals to "or", execute mongo query with $or operator
	elif( query_method == "or"):
		search_results_or = mongo.db[collection_name].find({ 
																"$or" : [ 
																	{"pollingStation.commune" : commune },
																	{"pollingStation.name" : polling_station},
																	{"votingProcess.voters.ultraVioletControl" : ultra_violet_control},
																	{"votingProcess.voters.fingerSprayed" : finger_sprayed }
																]})
		resp = Response(response = json_util.dumps(search_results_or), mimetype = 'application/json')
	
		

	# Return JSON response.
	return resp

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5001, debug=True)
