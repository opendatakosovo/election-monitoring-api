from collections import OrderedDict
import pymongo
from flask.views import View
from ema import utils, mongo

class PollingStationsGenerator(object):

	def __init__(self):
		pass

	def get_polling_stations(self, polling_stations):

		#FIXED: Extract method for the following logic and put it in a superclass.
		self.polling_station_grouped_by_commune_dict = OrderedDict()
		
		#Get the polling_stations cursor
		self.polling_stations = polling_stations

		# This dictionary is for tracking purposes.
		# So that we can track the polling stations we add to polling_station_grouped_by_commune_dict and not add duplicates.
		polling_station_slugs_grouped_by_commune_slug = OrderedDict()

		for idx, polling_station in enumerate(polling_stations):

			commune_slug = polling_station['pollingStation']['commune']['slug']
			commune_name = polling_station['pollingStation']['commune']['name']
			polling_station_name = polling_station['pollingStation']['name']['value']
			polling_station_name_slug = polling_station['pollingStation']['name']['slug']
		
			# If first time we stumble on commune, create a dictionary entry for it.
			if commune_slug not in self.polling_station_grouped_by_commune_dict:
				if polling_station_name != 'N/A' and polling_station_name != '':
				
					self.polling_station_grouped_by_commune_dict[commune_slug] = {'name': commune_name, 'slug': commune_slug}
					self.polling_station_grouped_by_commune_dict[commune_slug]['pollingStations'] = [{
						'name':polling_station_name,
						'slug':polling_station_name_slug
					}]

					polling_station_slugs_grouped_by_commune_slug[commune_slug] = [polling_station_name_slug]

			else:
				# Don't add invalid station name.
				if polling_station_name != 'N/A' and polling_station_name != '':
					# Don't add duplicate station name.
					if polling_station_name_slug not in polling_station_slugs_grouped_by_commune_slug[commune_slug]:

						self.polling_station_grouped_by_commune_dict[commune_slug]['pollingStations'].append({
							'name':polling_station_name,
							'slug':polling_station_name_slug
						})
					
						polling_station_slugs_grouped_by_commune_slug[commune_slug].append(polling_station_name_slug)
		
		return self.polling_station_grouped_by_commune_dict
