election-monitoring-api
=======================

API to access election monitoring data collected by various organizations

Example Usage
=============

Get observations for a given commune:
http://127.0.0.1:5001/api/kdi/observations/2013/local-elections/first-round/Ferizaj

Get observations for a given commune and polling station:
http://127.0.0.1:5001/api/kdi/observations/2013/local-elections/first-round/Ferizaj/Zaskok

Get KVV members gender distribtion for a given commune:
http://127.0.0.1:5001/api/kdi/observations/kvv-members-gender-distribution/2013/local-elections/first-round/Ferizaj

Get KVV members gender distribtion for a given commune and polling station:
http://127.0.0.1:5001/api/kdi/observations/kvv-members-gender-distribution/2013/local-elections/first-round/Ferizaj/Zaskok

Get vote counts for given commune:
http://127.0.0.1:5001/api/kdi/observations/votes-count/2013/local-elections/first-round/Ferizaj

Get vote counts for given commune and polling station:
http://127.0.0.1:5001/api/kdi/observations/votes-count/2013/local-elections/first-round/Ferizaj/Zaskok
