import json
class Utils(object):

	def __init__(self):
		pass
	
	
	def get_collection_name(self, year, election_type, election_round):
		''' Build String with value set to the collection name
		
		:param: year: The year of the election
		:param: election_type: The type of the election. Can be local (local-election) or general (general-election)
		:param: election_round: The round of the election (e.g. firt-round, second-round...)
		'''
		
		election_type = election_type.replace('-', '')
		election_round = election_round.replace('-', '')
		
		collection_name = election_type + election_round + str(year)
		
		return collection_name

