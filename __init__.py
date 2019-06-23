    
from flask import Flask
import pymongo
from routes import bp, app


app.register_blueprint(bp)
app.config['CORS_HEADERS'] = 'Content-Type'

'''
from iexfinance.stocks import Stock

a = Stock("AAPL", token="sk_b54033ac091e48f0a23bbaf9e0273ce9")
d = a.get_price()
print d

import urllib, json
url = "https://api.iextrading.com/1.0/ref-data/symbols"
response = urllib.urlopen(url)
data = json.loads(response.read())
'''


if __name__ == '__main__':
	app.run()