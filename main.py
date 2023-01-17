#!/usr/bin/python3

import requests
from flask import Flask, request, render_template, make_response 
from datetime import datetime, date, timezone
from dateutil import tz
#from zoneinfo import ZoneInfo

import canvas


app = Flask(__name__)

def upcoming(month):
	if date.today().month <= month:
		return True 
	else:
		return False 

def getCourseNameFromId(id):	
	u = request.cookies.get('url')
	t = request.cookies.get('token')
	data = canvas.requestBuilder("courses/"+id, t, u)
	return data['name']

@app.route("/assignments/<id>", methods=['GET'])
def getAssignments(id):
	u = request.cookies.get('url')
	t = request.cookies.get('token')
	c_name = getCourseNameFromId(id)
	data = canvas.requestBuilder("courses/"+id+"/assignments", t, u)
	#print(data)
	times = []
	for d in range(len(data)):
		try:
			if data[d]['due_at'] != None:
				shorter = datetime.strptime(data[d]['due_at'], "%Y-%m-%dT%H:%M:%S%z").astimezone(tz.gettz("US/Chicago"))
				#print(shorter.year, date.today().year)
				if upcoming(shorter.month) == False:
					data.pop(d)	
				else:
					data[d]['due_at'] = str(shorter.month)+"/"+str(shorter.day)
				
		except IndexError:
			pass
	return render_template("assignment.html", data=data, name=c_name)


@app.route("/classes-raw")
def classes_json():
	u = request.cookies.get('url')
	t = request.cookies.get('token')
	data = canvas.requestBuilder("courses", t, u)	
	return data

@app.route("/classes", methods=['GET'])
def getClasses():
	u = request.cookies.get('url')
	t = request.cookies.get('token')
	data = canvas.requestBuilder("courses", t, u)	
	for d in range(len(data)):	
		try:
			# course access is restricted
			if len(list(data[d].keys())) == 2:
				data.pop(d)
		except IndexError:
			pass
	return render_template("classes.html", data=data)



@app.route("/set-vars", methods=['POST'])
def setToken():
	if request.method != 'POST':
		return "<h1>Request Error</h1>"
	
	r = make_response("Token saved")
	r.set_cookie('token', request.form['token'])
	r.set_cookie('url', request.form['url'])
	return r

@app.route("/setup")
def TokenPage():
	return render_template("setup.html")

@app.route("/", methods=['GET'])
def Home():
	return "<h1>HW Planner</h1>"


if __name__ == "__main__":
	app.run()
