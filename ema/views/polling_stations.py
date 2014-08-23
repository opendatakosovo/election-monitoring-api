from flask import Flask, request, render_template, Response
from flask.views import View
from collections import OrderedDict
from bson import json_util
import pymongo
from ema import utils, mongo


class PollingStation(View):

	methods = ['GET']

	def dispatch_request(self, year, election_type, election_round):

		collection_name = utils.get_collection_name(year, election_type, election_round)

		polling_stations = mongo.db[collection_name].find().sort([("pollingStation.commune", pymongo.ASCENDING),("pollingStation.communeSlug", pymongo.ASCENDING),("pollingStation.nameSlug", pymongo.ASCENDING), ("pollingStation.name", pymongo.ASCENDING), ("pollingStation.roomNumber", pymongo.ASCENDING)])

		polling_station_grouped_by_commune_dict = OrderedDict()

		for idx, polling_station in enumerate(polling_stations):

		
			commune_slug = polling_station['pollingStation']['communeSlug']
			commune_name = polling_station['pollingStation']['commune']
			polling_station_name = polling_station['pollingStation']['name']
			polling_station_name_slug = polling_station['pollingStation']['nameSlug']
		
			# If first time we stumble on commune, create a dictionary entry for it.
			# The value for each dictionary entry is a set of election observations docs for this commune.
			if commune_slug not in polling_station_grouped_by_commune_dict:
				polling_station_grouped_by_commune_dict[commune_slug] = {'name': commune_name, 'slug': commune_slug}
				polling_station_grouped_by_commune_dict[commune_slug]['pollingStations'] = [{'name':polling_station_name, 'slug':polling_station_name_slug}]


			else:
				if polling_station_name != 'N/A':
					#FIXME: DON'T ADD POLLINGSTATION NAME IF WE ALREADY ADDED IT BEFORE.
					polling_station_grouped_by_commune_dict[commune_slug]['pollingStations'].append({'name':polling_station_name,'slug':polling_station_name_slug})

		resp = Response(response=json_util.dumps(polling_station_grouped_by_commune_dict), mimetype='application/json')

		# Return JSON response.
		return resp
