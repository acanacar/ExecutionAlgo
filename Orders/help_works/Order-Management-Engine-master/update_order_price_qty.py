# Driver program for Order entry gateway (Group 1)

# import the necessary packages
import requests
import json

# initialize the REST API endpoint URL
URL_FOR_ORDER = "http://localhost:5000/order_endpoint"
headers = {'Content-Type': 'application/json'}

order_data = {'type': 2, 'order_id': '5aeef2d7381adc298534e24c', 'ask_price': 85, 'total_qty': 20}
# type: # 1 - Add new order, 2 - Update price/qty of order, 3 - Cancel order, 4 - Get user's order details

# submit the request
r = requests.post(URL_FOR_ORDER, data=json.dumps(order_data), headers=headers).json()

# ensure the request was sucessful
if r["success"]:
    print('Request succeeded')

# otherwise, the request failed
else:
    print("Request failed")
    print(r)
