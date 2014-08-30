from flask import Flask, request, render_template, Response
from flask.views import View
from bson import json_util
import pymongo
from ema import utils, mongo


class Search(View):

	methods = ['GET']

	def dispatch_request(self, observer, year, election_type, election_round):
		''' Get the results for the parameters that are taken from the GET Method.
		:param observer: The observing organization.
		:param year: The year of the election.
		:param election_type: The type of the election. Can be local (local-election) or general (general-election).
		:param election_round: The round of the election (e.g. firt-round, second-round...).
		'''
	
		# Build the query into a dictionary
		query_dict = []

		# Add query conditions to the query dictionary.
		self.add_query_condition(query_dict, "pollingStation.commune.slug", 'commune')
		self.add_query_condition(query_dict, "pollingStation.name.slug", 'polling-station')		
		self.add_query_condition(query_dict, "votingProcess.voters.ultraVioletControl", 'ultra-violet-control')
		self.add_query_condition(query_dict, "votingProcess.voters.fingerSprayed", 'finger-sprayed')
		self.add_query_condition(query_dict, "preparation.missingMaterials.votingBooth", 'missing-voting-booth')
		self.add_query_condition(query_dict, "preparation.missingMaterials.ballotBox",'missing-ballot-box')
		self.add_query_condition(query_dict, "preparation.missingMaterials.ballots", 'missing-ballots')
		self.add_query_condition(query_dict, "preparation.missingMaterials.pollBook", 'missing-poll-book')
		self.add_query_condition(query_dict, "preparation.missingMaterials.uvLamp", 'missing-uv-lamp')

		# Get the collection name.
		collection_name = utils.get_collection_name(year, election_type, election_round)

		# Build query object depending on given filter arguments
		query = {'pollingStation.name.slug': {'$nin': ['', 'n-a']}}
		if len(query_dict) > 0:
			query['$and'] = query_dict

		# Execute query.
		search_results = mongo.db[collection_name].find(query).sort([
			("pollingStation.commune.slug", pymongo.ASCENDING),
			("pollingStation.name.slug", pymongo.ASCENDING),
			("pollingStation.room", pymongo.ASCENDING)
		])

		# Build the JSON response
		resp = Response(response = json_util.dumps(search_results), mimetype = 'application/json')

		# Return JSON response.
		return resp

	def add_query_condition(self, query_dict, query_dict_key, query_string_key):
		''' add a query condition to the give query dictionary.
		'''
		# Get the query string param value from the request for the given query string param key
		value = request.args.get(query_string_key)

		# Append the query argument to the dictionary
		if value != '' and value != 'None':
			if value == 'true':
				value = True

			query_dict.append({query_dict_key : value})
	


