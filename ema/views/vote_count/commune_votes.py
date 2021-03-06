from flask import Flask, request, render_template, Response
from flask.views import View
from bson import json_util

from ema import utils, mongo
class CommuneVoteCount(View):
	methods = ['GET']

	def dispatch_request(self, year, election_type, election_round, commune_name):
		''' Get the number of votes casted in a specified commune.
		The votes are grouped by the following hours: 10 AM, 1 PM, 4 PM, and 7 PM.
	
		:param year: The year of the election
		:param election_type: The type of the election. Can be local (local-election) or general (general-election)
		:param election_round: The round of the election (e.g. firt-round, second-round...)
		:param commune_name: the name of the commune.
		'''
	
		# Get the name of the collection we must query on.
		collection_name = utils.get_collection_name(year, election_type, election_round)
	
		# Execute query.
		voted_by_observation = mongo.db[collection_name].aggregate([
				{ "$match":
					{ "votingCenter.commune.slug": commune_name } 
				},
				{'$group':
					{'_id':'$votingCenter.commune.slug',
						'tenAM':{
							'$sum':'$voting.process.voters.howManyVotedBy.tenAM'
						},
						'onePM':{
							'$sum':'$voting.process.voters.howManyVotedBy.onePM'
						},
						'fourPM':{
							'$sum':'$voting.process.voters.howManyVotedBy.fourPM'
						},
						'sevenPM':{
							'$sum':'$voting.process.voters.howManyVotedBy.sevenPM'
						}
					}
				}
			])
	
		# Create JSON response object.
		resp = Response(response=json_util.dumps(voted_by_observation), mimetype='application/json')
	
		# Return JSON response.
		return resp
