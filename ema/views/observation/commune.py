from flask import Flask, request, render_template, Response
from flask.views import View
from bson import json_util

from ema import utils, mongo

class CommuneObservation(View):
	
	methods = ['GET']
	
	def dispatch_request(self, year, election_type, election_round, commune_slug):
		''' Get observations for given commune.
	
		:param year: The year of the election
		:param election_type: The type of the election. Can be local (local-election) or general (general-election)
		:param election_round: The round of the election (e.g. firt-round, second-round...)
		:param commune_slug: The slug of the commune.
		'''

		# Get the name of the collection we must query on.
		collection_name = utils.get_collection_name(year, election_type, election_round)
	
		# Execute query.
		observations = mongo.db[collection_name].find({
			'votingCenter.commune.slug': commune_slug
		})
	
		# Create JSON response object.
		resp = Response(response=json_util.dumps(observations), mimetype='application/json')

		# Return JSON response.
		return resp
