from flask import Flask, request, render_template, Response
from flask.views import MethodView
from bson import json_util
import pymongo
from ema import utils, mongo


class Search(MethodView):
	methods = ['GET']
	def dispatch_request(self,year,election_type,election_round):
		''' Get the results for the parameters that are taken from the GET Method.

		:param year: The year of the election
		:param election_type: The type of the election. Can be local (local-election) or general (general-election)
		:param election_round: The round of the election (e.g. firt-round, second-round...)
		:param commune_name: the name of the commune.
		:param polling_station: the name of the polling station.
		:param ultra_violet_control: checks if UV check happened in that polling station
		:param finger_sprayed: checks if finger spray happened in that polling station
		'''
	
		#Build the query into a dictionary
		query_dict=[]

		# Request the 'commune' property from the GET Method
		if request.args.get('commune'):
			# Append the query argument to the dictionary
			query_dict.append({"pollingStation.commune" : request.args.get('commune')})

		# Request the 'name' property from the GET Method
		if request.args.get('pollingStation'):
			# Append the query argument to the dictionary
			query_dict.append({"pollingStation.name" : request.args.get('pollingStation')})

		# Request the 'ultraVioletControl' property from the GET Method
		if request.args.get('ultraVioletControl'):
			# Append the query argument to the dictionary
			query_dict.append({"votingProcess.voters.ultraVioletControl" : request.args.get('ultraVioletControl')})

		# Request the 'fingerSprayed' property from the GET Method
		if request.args.get('fingerSprayed'):
			# Append the query argument to the dictionary
			query_dict.append({"votingProcess.voters.fingerSprayed" : request.args.get('fingerSprayed')})
	
		# Get the 
		collection_name = utils.get_collection_name(year, election_type, election_round)

		print collection_name
		print query_dict
		# Execute query.
		search_results = mongo.db[collection_name].find({"$and" : query_dict}).sort([("pollingStation.commune", pymongo.ASCENDING),("pollingStation.name", pymongo.ASCENDING), ("pollingStation.roomNumber", pymongo.ASCENDING)])

		# Build the JSON response
		resp = Response(response = json_util.dumps(search_results), mimetype = 'application/json')

		# Return JSON response.
		return resp
