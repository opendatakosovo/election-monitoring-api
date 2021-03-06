from flask import Flask, request, render_template, Response
from flask.views import View
from bson import json_util

from ema import utils, mongo

class KvvRoomGenderDistribution(View):

	methods = ['GET']

	def dispatch_request(self, year, election_type, election_round, commune_name, polling_station_name, room_number):
		''' Get the gender distribution of KVV members in a specified room.
	
		:param year: The year of the election
		:param election_type: The type of the election. Can be local (local-election) or general (general-election)
		:param election_round: The round of the election (e.g. firt-round, second-round...)
		:param commune_name: the name of the commune.
		:param polling_station_name: The name of the polling station.
		:param room_number: The number of the room.
		'''
	
		# Get the name of the collection we must query on.
		collection_name = utils.get_collection_name(year, election_type, election_round)
	
		# Execute query.
		gender_observation = mongo.db[collection_name].aggregate([
			{ "$match": {
				"votingCenter.commune.slug":commune_name,
				"votingCenter.slug":polling_station_name,
				"votingCenter.stationNumber": room_number}
			}, 
			{'$group': {
				'_id':'$votingCenter.stationNumber',
				'total': {
					'$sum':'$preparation.pscMembers.total'},
				'totalWomen':{
					'$sum':'$preparation.pscMembers.women'}
				}
			}
		])
	
		# Create JSON response object.
		resp = Response(response=json_util.dumps(gender_observation), mimetype='application/json')
	
		# Return JSON response.
		return resp
