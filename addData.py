import pymongo 
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client.stockDB
stockTable = db['stock']

def addStockToDatabase():
   from iexfinance.stocks import Stock
   import urllib, json, random
   # Read arrays of Object 
   url = "https://api.iextrading.com/1.0/ref-data/symbols"
   response = urllib.urlopen(url)
   data = json.loads(response.read())
   count = 0

   # print data[0]
   for item in data:
      obj = {}
      obj['symbol'] = item['symbol']
      obj['shareholder'] = 0
      obj['index'] = count
      count+=1
      # obj['price'] = Stock(item['symbol'].encode("utf-8"), token="sk_b54033ac091e48f0a23bbaf9e0273ce9").get_price()
      stockTable.insert(obj)
      

def printAllStock():
   a = stockTable.find({})
   for s in a:
      print s

def deleteAndAddDatabase():
   stockTable.drop()
   addStockToDatabase()
   
# addStockToDatabase()
# deleteAndAddDatabase()
# printAllStock()



# from iexfinance.stocks import Stock

# a = Stock("AAwerewrwPLAA", token="sk_b54033ac091e48f0a23bbaf9e0273ce9")
# try:
#     a.get_price()
# except:
#     print "This is an error message!"

# print 'done'