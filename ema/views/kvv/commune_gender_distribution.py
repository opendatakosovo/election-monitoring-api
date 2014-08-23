from flask import Flask, request, render_template, Response
from flask.views import View
from bson import json_util

from ema import utils, mongo

class KvvCommuneGenderDistribution(View):

	methods = ['GET']

	def dispatch_request(self, year, election_type, election_round, commune_name):
		''' Get the gender distribution of KVV members in a specified commune.
	
		:param year: The year of the election
		:param election_type: The type of the election. Can be local (local-election) or general (general-election)
		:param election_round: The round of the election (e.g. firt-round, second-round...)
		:param commune_name: the name of the commune.
		'''
	
		# Get the name of the collection we must query on.
		collection_name = utils.get_collection_name(year, election_type, election_round)
	
		# Execute query.
		gender_observation = mongo.db[collection_name].aggregate([
			{ "$match": 
				{ "pollingStation.communeSlug":commune_name }
			}, 
			{'$group':
				{'_id':'$pollingStation.communeSlug',
				'total':
					{'$sum':'$preparation.votingMaterialsPlacedInAndOutVotingStation.kvvMembers.total'},
				'totalFemale':
					{'$sum':'$preparation.votingMaterialsPlacedInAndOutVotingStation.kvvMembers.female'}
				}
			}
		])
	
		# Create JSON response object.
		resp = Response(response=json_util.dumps(gender_observation), mimetype='application/json')

		print gender_observation
	
		# Return JSON response.
		return resp
