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

		polling_stations = mongo.db[collection_name].find().sort([
			("pollingStation.commune.slug", pymongo.ASCENDING),
			("pollingStation.name.slug", pymongo.ASCENDING),
			("pollingStation.room", pymongo.ASCENDING)
		])

		polling_station_grouped_by_commune_dict = OrderedDict()

		# This dictionary is for tracking purposes.
		# So that we can track the polling stations we add to polling_station_grouped_by_commune_dict and not add duplicates.
		polling_station_slugs_grouped_by_commune_slug = OrderedDict()

		for idx, polling_station in enumerate(polling_stations):

			commune_slug = polling_station['pollingStation']['commune']['slug']
			commune_name = polling_station['pollingStation']['commune']['name']

			polling_station_name_slug = polling_station['pollingStation']['name']['slug']
			polling_station_name = polling_station['pollingStation']['name']['value']
		
			# If first time we stumble on commune, create a dictionary entry for it.
			if commune_slug not in polling_station_grouped_by_commune_dict:
				polling_station_grouped_by_commune_dict[commune_slug] = {'name': commune_name, 'slug': commune_slug}
				polling_station_grouped_by_commune_dict[commune_slug]['pollingStations'] = [{
					'name':polling_station_name,
					'slug':polling_station_name_slug
				}]

				polling_station_slugs_grouped_by_commune_slug[commune_slug] = [polling_station_name_slug]

			else:
				# Don't add invalid station name.
				if polling_station_name != 'N/A':
					# Don't add duplicate station name.
					if polling_station_name_slug not in polling_station_slugs_grouped_by_commune_slug[commune_slug]:

						polling_station_grouped_by_commune_dict[commune_slug]['pollingStations'].append({
							'name':polling_station_name,
							'slug':polling_station_name_slug
						})
					
						polling_station_slugs_grouped_by_commune_slug[commune_slug].append(polling_station_name_slug)
		
		# Build response object				
		resp = Response(response=json_util.dumps(polling_station_grouped_by_commune_dict), mimetype='application/json')

		# Return JSON response.
		return resp
