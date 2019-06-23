from flask import Blueprint, render_template, Flask, request, url_for, json, redirect, Response, make_response, jsonify
import  datetime
import pymongo 
from pymongo import MongoClient
import time, random, string
from bson.objectid import ObjectId

'''
sudo service mongodb start

https://app.box.com/s/n2tsi8gruwiwgkt5pjzkjc2lonw0co52

'''

app = Flask(__name__)
bp = Blueprint('routes', __name__, template_folder='templates')
client = MongoClient('127.0.0.1', 27017)
db = client.stockDB
userTable = db['user'] 
tranTable = db['transaction']


@bp.route('/', methods=['GET','POST'])
def index():
	return redirect(url_for('routes.portfolio'))


@bp.route('/signup', methods=["POST", "GET"])
def signup():	
	if request.method == "GET":
		print "================== " + request.cookies.get('username')
		return render_template('signup.html')

	username = request.form['username']
	password = request.form['password'] 
	email = request.form['email'] 

	email_exist = userTable.find_one({'email': email})
	
	if email_exist != None :
		return "Email already exist"
	
	data ={}
	data['username'] = username
	data['email'] = email
	data['password'] = password
	data['cash'] = 5000
	userTable.insert(data)
	return redirect(url_for('routes.login'))

@bp.route('/login', methods=["POST", "GET"])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	
	username = request.form['username']
	password = request.form['password'] 
	
	valid = userTable.find_one({'username': username, 'password':password })
	if valid == None:
		return render_template("login.html", message="Invalid username and password")
	
	#If user is logged in, send back a cookie and redirect user to portfolio page
	response = make_response(render_template("portfolio.html", login=1) )	
	response.set_cookie('username', username)
	return response


@bp.route('/logout')
def logout():
	response = make_response(redirect('/login'))	
	response.set_cookie('username', "")
	return response

@bp.route('/portfolio', methods=["GET"])
def portfolio():
	user = request.cookies.get('username')
	login = 0
	if user != None:
		login = 1
	return render_template("portfolio.html", login=login)










@bp.route('/clean', methods=["POST", "GET"])
def cleanDataBase():
	userTable.delete_many({})
	tranTable.delete_many({})
	return "clear all"


@bp.route('/show', methods=["GET"])
def showDB():
	res = userTable.find({})
	count = userTable.count()
	print ('user count = ',count)
	for i in res:
		print i
	
	return  'USER count = ' + str(count)    

