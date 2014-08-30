from flask import Flask, request, render_template, Response
from flask.views import View
from collections import OrderedDict
from bson import json_util
import pymongo
from ema import utils, mongo
from generate_polling_stations import PollingStationsGenerator

class PollingStation(View, PollingStationsGenerator):

	methods = ['GET']

	def dispatch_request(self, year, election_type, election_round):

		collection_name = utils.get_collection_name(year, election_type, election_round)

		polling_stations = mongo.db[collection_name].find().sort([
			("pollingStation.commune.slug", pymongo.ASCENDING),
			("pollingStation.slug", pymongo.ASCENDING), 
			("pollingStation.room", pymongo.ASCENDING)])

		# Create a empty OrderedDictionary
		polling_station_grouped_by_commune_dict = OrderedDict()
		
		#Get the dictionary from get_polling_stations method of the PollingStationGeerator
		polling_station_grouped_by_commune_dict = super(PollingStation, self).get_polling_stations(polling_stations)
		
		# Build response object				
		resp = Response(response=json_util.dumps(polling_station_grouped_by_commune_dict), mimetype='application/json')

		# Return JSON response.
		return resp
