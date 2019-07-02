from flask import Blueprint, render_template, Flask, request, url_for, json, redirect, Response, make_response, jsonify
import  datetime
import pymongo 
from pymongo import MongoClient
import time, random, string
from bson.objectid import ObjectId

from iexfinance.stocks import Stock
import urllib, json, random

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
stockTable = db['stock']


@bp.route('/', methods=['GET','POST'])
def index():
	return redirect(url_for('routes.login'))


@bp.route('/signup', methods=["POST", "GET"])
def signup():	
	if request.method == "GET":
		return render_template('signup.html')
	
	username = request.form['username']
	password = request.form['password'] 
	email = request.form['email'] 
	email_exist = userTable.find_one({'email': email})
	user_exist = userTable.find_one({'username': username})

	if email_exist != None or user_exist != None:
		return render_template("signup.html" ,error ="*Username/Email already exist")
	
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
	
	response = make_response(redirect('/portfolio') )	
	response.set_cookie('username', username)
	return response


@bp.route('/logout')
def logout():
	response = make_response(redirect('/login'))	
	response.set_cookie('username', "-", expires=0)
	return response

@bp.route('/portfolio', methods=["GET"])
def portfolio():
	login = 0
	cash = 0
	user = request.cookies.get('username')	
	
	if user != None:
		login = 1
		cash = userTable.find_one({'username': user})['cash']

	stocks = generateStock()
	return render_template("portfolio.html", login=login, stocks=stocks, cash=cash)

@bp.route('/getStock', methods=["POST"])
def getStock():
	form = request.json
	symbol = form['symbol']

	print("==================== " , symbol)
	if 'previous' in form:
		obj={ 'symbol': current, 'previous': form['previous'], 'current' : form['current'] }
		return responseOK({'symbol': symbol, })
	else:
		stock = getStockInfo(symbol)
		item =	{	
					'symbol': symbol,
					'current' : stock['latestPrice'],
					'previous': stock['previousClose'],
					'change' : stock['changePercent']
				}
		return responseOK(item)

@bp.route('/purchase', methods=["POST"])
def purchase():
	user = request.cookies.get('username').encode("utf-8")

	form = request.json
	symbol = form['symbol']
	price = form['price']

	print(symbol, float(price) )

	userTable.find_one({'username' : user})

	item=	{ 
				'username': user,
				'symbol' : symbol,
				'price' : price 
			}

	#tranTable.insert(item)
	return responseOK({'status': 'OK'})


def generateStock():
	arr = []

	while len(arr) < 5:
		num = random.randint(0,8820)
		result = stockTable.find_one({'index': num})
		symbol = result['symbol']

		stock = getStockInfo(symbol)
		item ={
					'symbol': symbol,
					'price' : stock['latestPrice'],
					'previous': stock['previousClose'],
					'change' : stock['changePercent']
				}
		if stock['changePercent'] < 0:
			item['color'] = -1
		else:
			item['color'] = 1

		arr.append(item)
	return arr


def responseOK(stat):
	data = stat
	jsonData = json.dumps(data)
	respond = Response(jsonData,status=200, mimetype='application/json')
	return respond



def getStockInfo(symbol):
	stock = Stock(symbol.encode("utf-8"), token="sk_b54033ac091e48f0a23bbaf9e0273ce9")
	stock = stock.get_quote()
	return stock

'''
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
'''