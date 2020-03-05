# Driver program for Order entry gateway (Group 1)

# USAGE
# python order_request.py

# import the necessary packages
import requests
import json

# initialize the REST API endpoint URL
URL_FOR_ORDER = "http://localhost:5000/order_endpoint"
headers = {'Content-Type' : 'application/json'}


query = {'type': 5, 'symbols': ['INFY', 'TCS']}

# type: #1 - Add new order, 2 - Update price/qty of order, 3 - Cancel order, 4 - Get user's order details

# submit the request
r = requests.post(URL_FOR_ORDER, data = json.dumps(query), headers = headers).json()

# if r["success"]:
# 	print ('Request succeeded')
# else:
# 	print ("Request failed")

print(json.dumps(r, indent=4))
