# Order-Management-Engine
Order Management Engine in Trade Life Cycle


## A Simple REST API

The API currently accepts JSON from client. On receiving true JSON, it prints the content of JSON at server side and then sends a JSON acknowledgement 'ack' to client with {'success':'true'}.

In recent commits, code for order/fill insertion and updation is added. Now, whenever JSON order/fill is sent, it is added/updated in the MongoDB database which is set up on an AWS machine.

Following functionalities have been implemented :-
From Order entry gateway :- Add new order, Update price of order, Update quantity of order, Cancel an order;
From Execution links :- Add new fill

Functionalities like storing user subscriptions to particular orders in cache and handling notifications are yet to be implemented.


You need to install [Flask](http://flask.pocoo.org/) and [requests](http://docs.python-requests.org/en/master/):
```
$ pip install flask gevent requests
```

## Starting the Flask server
```
$ python run_flask_server.py 
...
 * Running on http://127.0.0.1:5000
```

You can now access the REST API via `http://127.0.0.1:5000`.


## Submitting requests to the server

Requests can be submitted via cURL from another terminal instance:
```
$ curl  -X POST  -H "Content-Type: application/json"  -d '{"key1":"value1", "key2":"value2"}' 'http://localhost:5000/order_endpoint'  
{
  "success": false
}
```

OR programmatically using python/PHP/any other language

### A Python Driver program - Endpoint to be called by Order entry gateway

```
$ python order_request.py
```

### A Python Driver program - Endpoint to be called by Execution links

```
$ python execution_request.py
```


## Installing MongoDB on Ubuntu :-
Follow the steps on https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
It requires 64 bit Ubuntu.
This is not required, since MongoDB database is created and running on AWS server


## Installing Flask-PyMongo on Ubuntu :-
```
$ pip install Flask-PyMongo
```

https://flask-pymongo.readthedocs.io/en/latest/
https://pypi.python.org/pypi/Flask-PyMongo


## About the project files :-
run_flask_server.py :- It is the main file containing code for web service which has the REST API created and has two endpoints - "/order_endpoint" and "/execution_endpoint"

new_order_request.py :- It is a driver program that emulates sending POST request from Order Entry for adding new order

update_order_price_qty.py :- It is a driver program that emulates sending POST request from Order Entry for updating price and quantity of existing order

cancel_order.py - It is a driver program that emulates sending POST request from Order Entry for cancelling an existing order

get_order_details.py :- It is a driver program that emulates sending POST request from Order Entry for getting the orders placed by a user and correspoding fills to those orders

execution_request.py :- It is a driver program that emulates sending POST request from Execution Links for sending new fill coming from Matching Engine

exec_link_dummy_REST.py :- A dummy REST API web service created for Execution Links to test that OME can send new order/update in order coming from Order Entry to Execution Links

trad_post_dummy_REST.py :- A dummy REST API web service created for Trade Post Management to test that OME can send new fill coming from Execution Links to Trade Post Management

check_mongodb_contents_utility_program - A utility program containing python code snippet for checking the MongoDB collection contents to test the working

redis-cache-notifs :- It is directory containing code files for Pub Sub Notifications (Not integrated with the project)
