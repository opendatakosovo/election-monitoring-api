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

		# Request the 'commune' property from the GET Method.
		if request.args.get('commune_select'):
			# Append the query argument to the dictionary
			query_dict.append({"pollingStation.communeSlug" : request.args.get('commune_select')})

		# Request the 'name' property from the GET Method.
		if request.args.get('polling_station_select'):
			# Append the query argument to the dictionary
			query_dict.append({"pollingStation.nameSlug" : request.args.get('polling_station_select')})

		# Request the 'ultraVioletControl' property from the GET Method.
		if request.args.get('ultra_violet_control_select'):
			# Append the query argument to the dictionary
			query_dict.append({"votingProcess.voters.ultraVioletControl" : request.args.get('ultra_violet_control_select')})

		# Request the 'fingerSprayed' property from the GET Method.
		if request.args.get('finger_sprayed_select'):
			# Append the query argument to the dictionary
			query_dict.append({"votingProcess.voters.fingerSprayed" : request.args.get('finger_sprayed_select')})

		# Request the 'missing_voting_cabin' property from the GET Method.
		if request.args.get('missing_voting_cabin') != 'None':
			# Append the query argument to the dictionary
			query_dict.append({"preparation.missingMaterial.votingCabin" : bool(request.args.get('missing_voting_cabin'))})

		# Request the 'missing_ballot_box' property from the GET Method.
		if request.args.get('missing_ballot_box')  != 'None':
			# Append the query argument to the dictionary
			query_dict.append({"preparation.missingMaterial.ballotBox" : bool(request.args.get('missing_ballot_box'))})

		# Request the 'missing_ballots' property from the GET Method.
		if request.args.get('missing_ballots')  != 'None':
			# Append the query argument to the dictionary
			query_dict.append({"preparation.missingMaterial.ballots" : bool(request.args.get('missing_ballots'))})

		# Request the '' property from the GET Method.
		if request.args.get('missing_voters_book')  != 'None':
			# Append the query argument to the dictionary
			query_dict.append({"preparation.missingMaterial.votersBook" : bool(request.args.get('missing_voters_book'))})

		# Request the 'missing_uv_lamp' property from the GET Method.
		if request.args.get('missing_uv_lamp')  != 'None':
			# Append the query argument to the dictionary
			query_dict.append({"preparation.missingMaterial.uvLamp" : bool(request.args.get('missing_uv_lamp'))})

		print query_dict

		# Get the collection name.
		collection_name = utils.get_collection_name(year, election_type, election_round)

		# Build query object depending on given filter arguments
		query = {}
		if len(query_dict) > 0:
			query = {"$and" : query_dict}

		# Execute query.
		search_results = mongo.db[collection_name].find(query).sort([
			("pollingStation.communeSlug", pymongo.ASCENDING),
			("pollingStation.nameSlug", pymongo.ASCENDING),
			("pollingStation.roomNumber", pymongo.ASCENDING)
		])

		# Build the JSON response
		resp = Response(response = json_util.dumps(search_results), mimetype = 'application/json')

		# Return JSON response.
		return resp
