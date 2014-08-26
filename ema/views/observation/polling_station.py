from flask import Flask, request, render_template, Response
from flask.views import View
from bson import json_util

from ema import utils, mongo

class PollingStationObservation(View):

	methods = ['GET']

	def dispatch_request(self, year, election_type, election_round, commune_slug, polling_station_slug):
		''' Get observations for given commune and polling station.
	
		:param year: The year of the election
		:param election_type: The type of the election. Can be local (local-election) or general (general-election)
		:param election_round: The round of the election (e.g. firt-round, second-round...)
		:param commune_slug: The name of the commune.
		:param polling_station_slug: The name of the polling station.
		'''
		
		# Get the name of the collection we must query on.
		collection_name = utils.get_collection_name(year, election_type, election_round)
	
		# Execute query.
		observations = mongo.db[collection_name].find({
			'pollingStation.communeSlug': commune_slug, 
			'pollingStation.nameSlug': polling_station_slug
		})
	
		# Create JSON response object.
		resp = Response(response=json_util.dumps(observations), mimetype='application/json')

		# Return JSON response.
		return resp
