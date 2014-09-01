from flask import Flask, request, render_template, Response
from flask.views import View
from bson import json_util

from ema import utils, mongo

class KvvPollingStationGenderDistribution(View):
	methods = ['GET']
	def dispatch_request(self, year, election_type, election_round, commune_name, polling_station_name):
	
		''' Get the gender distribution of KVV members in a specified polling station.
	
		:param year: The year of the election
		:param election_type: The type of the election. Can be local (local-election) or general (general-election)
		:param election_round: The round of the election (e.g. firt-round, second-round...)
		:param commune_name: the name of the commune.
		:param polling_station_name: the name of the polling station.
		'''

		# Get the name of the collection we must query on.
		collection_name = utils.get_collection_name(year, election_type, election_round)

		# Execute query.
		gender_observation_by_polling_station = mongo.db[collection_name].aggregate([
			{ "$match": { 
				"votingCenter.commune.slug": commune_name,
				"votingCenter.slug": polling_station_name}
			}, 
			{'$group': {
				'_id':'$votingCenter.slug',
				'total': {
					'$sum':'$preparation.pscMembers.total'},
				'totalWomen':{
					'$sum':'$preparation.pscMembers.women'}
				}
			}
		])

		# Create JSON response object.
		resp = Response(response=json_util.dumps(gender_observation_by_polling_station), mimetype='application/json')
	
		# Return JSON response.
		return resp
