#!/usr/bin/python3

import requests
from flask import Flask, request, render_template, make_response, redirect, url_for 
from datetime import datetime, date, timezone
from dateutil import tz
import json

import canvas


app = Flask(__name__)

def upcoming(month):
	if date.today().month <= month:
		return True 
	else:
		return False 

def getTodoList():
	try:
		tl = json.loads(request.cookies.get('todo'))
		return tl['todo']
	except:
		print("No todo list found")
		return [] 



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

@app.route("/remove-course/<id>")
def removeClasses(id):
	r = redirect("/classes")
	try:
		t = json.loads(request.cookies.get('removed-courses'))
		t['removed-courses'].append(id)
		r.set_cookie('removed-courses', json.dumps(t), max_age=60*60*24*365)
	except:
		base = json.loads('{"removed-courses":[]}')
		base['removed-courses'].append(id)
		r.set_cookie('removed-courses', json.dumps(base), max_age=60*60*24*365)
	return r

@app.route("/classes-raw")
def classes_json():
	u = request.cookies.get('url')
	t = request.cookies.get('token')
	data = canvas.requestBuilder("courses", t, u)	
	return data

@app.route("/add-todo", methods=['GET', 'POST'])
def add_todo():
	if request.method == 'GET':
		return render_template("add-todo.html")	
	else:
		r = redirect("/")
		n = request.form['item']
		try:
			t = json.loads(request.cookies.get('todo'))
			t['todo'].append(n)
			r.set_cookie('todo', json.dumps(t), max_age=60*60*24*365)
		except:
			base = json.loads('{"todo":[]}')
			base['todo'].append(n)
			r.set_cookie('todo', json.dumps(base), max_age=60*60*24*365)
		return r


@app.route("/remove-todo/<item>")
def remove_todo(item):
	t = json.loads(request.cookies.get('todo'))
	t['todo'].remove(item)
	r = redirect("/")
	r.set_cookie('todo', json.dumps(t), max_age=60*60*24*365)
	return r


@app.route("/classes", methods=['GET'])
def getClasses():
	u = request.cookies.get('url')
	t = request.cookies.get('token')
	r = []
	try:
		f = json.loads(request.cookies.get('removed-courses'))
		r = f['removed-courses']
	except:
		pass
	data = canvas.requestBuilder("courses", t, u)	
	for d in range(len(data)):	
		try:
			# course access is restricted
			#print(len(list(data[d].keys())))
			if len(list(data[d].keys())) == 2:
				data.pop(d)
			elif str(data[d]['id']) in r:
				data.pop(d)
		except IndexError:
			pass
	return render_template("classes.html", data=data)



@app.route("/set-vars", methods=['POST'])
def setToken():	
	r = redirect("/") 
	r.set_cookie('token', request.form['token'], max_age=60*60*24*365)
	r.set_cookie('url', request.form['url'], max_age=60*60*24*365)
	return r


@app.route("/setup")
def TokenPage():
	return render_template("setup.html")

@app.route("/", methods=['GET'])
def Home():
	lt = getTodoList()
	return render_template("home.html", tlist=lt) 


if __name__ == "__main__":
	app.run()
