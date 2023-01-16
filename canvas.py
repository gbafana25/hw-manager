import requests
import json

def requestBuilder(endpoint, token, url):
	headers = {"Authorization": "Bearer " + token}
	req = requests.get("http://"+url+"/api/v1/"+endpoint+"?per_page=50", headers=headers)
	return json.loads(req.text)
	
