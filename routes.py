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
stockTable = db['stock'] #Only contains name of stock
stockHolderTable = db['stockHolder'] 

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


# Display portfolio along with 5 stock sample
@bp.route('/portfolio', methods=["GET"])
def portfolio():
	login = 0
	cash = 0
	user = request.cookies.get('username')	
	# If user is not logged in, then notify the state of session
	if user != None:
		login = 1
		cash = userTable.find_one({'username': user})['cash']

	# Generate 5 sample stocks
	stocks = generateStock()
	return render_template("portfolio.html", login=login, stocks=stocks, cash=cash)


# Get the price and data of a single stock using AJAX/JSON
@bp.route('/getStock', methods=["POST"])
def getStock():
	form = request.json
	symbol = form['symbol']

	if 'previous' in form:
		obj={ 'symbol': current, 'previous': form['previous'], 'current' : form['current'] }
		return responseOK({'symbol': symbol })
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
	symbol = form['symbol'].encode("utf-8")
	price = form['price']
	unit = form['unit'] # unit price
	quantity = form['quantity']

	# Shareholder count
	obj = stockHolderTable.find_one({'username': user, 'symbol': symbol})
	if obj == None:
		stock = stockTable.find_one({'symbol': symbol})
		shareholder = stock['shareholder'] + 1

		query = {'symbol': symbol}
		new_value = {'$set': {'shareholder': shareholder}}
		
		stockTable.update_one(query, new_value) # add 1 to shareholder
		# if first time buyer, then set the quantity to amount bought
		stockHolderTable.insert({'username': user, 'symbol': symbol, 'quantity': quantity})
	else:
		# if not first time buyer, then add additional qunatity to stockHolderTable
		new_quantity = stockHolderTable.find_one({'username': user, 'symbol': symbol})
		new_quantity=new_quantity['quantity'] + quantity

		query = {'username': user, 'symbol': symbol}
		new_value = {'$set': {'quantity': new_quantity}}
		stockHolderTable.update_one(query, new_value)

	
	# Get user current amount of cash
	item = userTable.find_one({'username' : user})
	cash = item['cash']

	# total - stockAmount 
	cash = cash - float(price)

	# update mongodb to reflect cash change
	query = {'username': user}
	new_value = {'$set': {'cash': cash}}
	userTable.update_one(query, new_value)

	item=	{ 
				'username': user,
				'symbol' : symbol,
				'price' : price,
				'unit': unit, # unit price
				'quantity': quantity
			}
	print(item )
	tranTable.insert(item)
	#---------------------------------------------
	return responseOK({'status': 'OK'})


@bp.route('/transaction', methods=["GET"])
def transaction():
	user = request.cookies.get('username')
	login = 0
	cash = 0
	user = request.cookies.get('username')	
	
	if user != None:
		login = 1
		cash = userTable.find_one({'username': user})['cash']

	if login == 1:
		stocks = tranTable.find({"username": user})
		return render_template('transaction.html', login=login, cash=cash, stocks=stocks)
	
	return render_template('transaction.html', login=login, cash=cash)


@bp.route('/restart', methods=["POST", "GET"])
def restart():
	userTable.delete_many({})
	tranTable.delete_many({})
	stockTable.delete_many({})
	stockHolderTable.delete_many({})
	
	import addData
	addData.deleteAndAddDatabase()


	return "clear all"

@bp.route('/show', methods=["GET"])
def showDB():
	res = tranTable.find({})
	count = tranTable.count()
	print ('transac count = ',count)
	for i in res:
		print i
	
	return  'transa count = ' + str(count) 


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



