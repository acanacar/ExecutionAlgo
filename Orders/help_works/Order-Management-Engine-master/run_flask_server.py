import flask
from flask_pymongo import PyMongo

import time
import datetime

import requests
import json

from bson.objectid import ObjectId

from flask import Flask
from flask_cors import CORS, cross_origin

import re

app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['Access-Control-Allow-Credentials'] = 'true'
app.config['Access-Control-Allow-Origin'] = '*'

app.config['MONGO_DBNAME'] = 'order_entry'
app.config['MONGO_URI'] = 'mongodb://admin:thisisyouradmin@ds141068.mlab.com:41068/order_entry'

mongo = PyMongo(app)

# '0' - LIVE / NEW
states_dict = {'0': 'LIVE', '1': 'Partially filled', '2': 'Filled', '3': 'Done for day', '4': 'Cancelled',
               '6': 'Pending for cancel',
               '7': 'Stopped', '8': 'Rejected', '9': 'Suspended', 'A': 'PN', 'B': 'Calculated',
               'C': 'Expired', 'D': 'Accepted for binding', 'E': 'Pending replace'}

side_dict = {0: 'B', 1: 'S'}


def send_to_exec_link(new_order, new_order_id, content_type):  ## send to execution link
    # initialize the REST API endpoint URL
    URL = ""
    # URL = "http://localhost:5001/execution_REST_API_dummy"

    headers = {'Content-Type': 'application/json'}

    order_data = {'type': content_type, 'order_id': str(new_order_id),
                  'OrigClOrdID': new_order['orig_cl_ord_id'], 'user_id': new_order['user_id'],
                  'product_id': new_order['product_id'], 'side': str(new_order['side']),
                  'ask_price': str(new_order['ask_price']), 'total_qty': str(new_order['total_qty']),
                  'order_stamp': new_order['order_stamp'], 'order_qtydone': new_order['order_qtydone'],
                  'account': new_order['account'], 'exchange_id': new_order['exchange_id'],
                  'price_instruction': new_order['price_instruction']}
    # , 'state' : new_order['state']''' }

    if content_type == 1:
        URL = "http://192.168.43.219:8080/api/v1/new_order"

    elif content_type == 2:
        URL = "http://192.168.43.219:8080/api/v1/update_order"

    else:
        URL = "http://192.168.43.219:8080/api/v1/delete_order"

    exec_ack = requests.post(URL, data=json.dumps(order_data), headers=headers).json()

    # submit the request
    # exec_ack = requests.post(URL_FOR_ORDER, data = json.dumps(order_data), headers = headers).json()

    # ensure the request was sucessful
    # if r["success"]:
    #	print(('Request succeeded'))

    # otherwise, the request failed
    # else:
    #	print(("Request failed"))
    return exec_ack


def send_to_trade_post(order, fill, fill_list):  ## send to trade post
    # initialize the REST API endpoint URL
    # URL_FOR_ORDER_FILL = "http://localhost:5002/trade_post_REST_API_dummy"
    URL_FOR_ORDER_FILL = "http://192.168.43.171:5001/orderGet"
    headers = {'Content-Type': 'application/json'}

    order_fill_data = {'order_id': str(order['_id']), 'user_id': order['user_id'],
                       'product_id': order['product_id'], 'side': order['side'],
                       'ask_price': order['ask_price'], 'total_qty': order['total_qty'],
                       'order_stamp': order['order_stamp'], 'state': order['state'],
                       'fill': fill,
                       'account': order['account'], 'LTP': order['LTP']}

    # submit the request
    r = requests.post(URL_FOR_ORDER_FILL, data=json.dumps(order_fill_data), headers=headers).json()

    # ensure the request was sucessful
    if r["success"]:
        print(('Request succeeded'))

    # otherwise, the request failed
    else:
        print(("Request failed"))


# Following endpoint corresponds to order_entry() function defined below it.
# It can be called by client on 'http://localhost:5000/order_endpoint' url.

@app.route("/order_endpoint", methods=["POST"])
def order_entry():
    mongo_order = mongo.db.orders
    mongo_fill = mongo.db.fills
    mongo_exchange = mongo.db.exchange
    mongo_product = mongo.db.product

    ack = {}

    if flask.request.method == "POST":
        print('POST ', 'Request ', flask.request, 'Data = ', flask.request.data, flask.request.json, flask.request.form)

        # ack= {'suc':'232'}
        # return flask.jsonify(ack)

        # if flask.request.is_json:
        if True:
            # content = flask.request.get_json()			# When we run with "Driver programs"
            content = flask.request.form  # When we run with "GUI"
            print("JSON content ", content)
            # print('IP of sender : ', flask.request.remote_addr)
            # print(flask.request.environ['REMOTE_ADDR'])

            if int(content['type']) == 1:  # Insert new order
                ack = {"success": False}

                ts = time.time()
                order_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

                order_id = mongo_order.insert(
                    {'orig_cl_ord_id': '',
                     'user_id': int(content['user_id']),
                     'product_id': content['product_id'],
                     'side': int(content['side']),
                     'price_instruction': content['price_instruction'],
                     'ask_price': float(content['ask_price']),
                     'total_qty': int(content['total_qty']),
                     'order_qtydone': 0,
                     'LTP': -1,
                     'order_stamp': order_stamp,
                     'reason_cancellation': '',
                     'state': 'A',
                     'client': int(content['client']),
                     'exchange_id': content['exchange_id'],
                     'account': int(content['account']),
                     'counter_party': content['counter_party']})
                # state = 1 (pending), 2 (filled), 3 (cancelled), 4 (partially filled), 5 (rejected), -1 (live)
                # order_id returned is of the type "ObjectId"

                print('Order id = ', order_id)

                ack["order_id"] = str(order_id)

                # ack["success"] = True

                new_order = mongo_order.find_one({'_id': order_id})  ## new/updated/canceled order

                exec_ack = send_to_exec_link(new_order, order_id, int(content['type']))

                print(exec_ack)

                if exec_ack['success']:
                    # mongo_order.update_one({'_id': order_id}, {'$set': {'state': 1} }, upsert=False)   # Live order
                    ack['success'] = True


            elif int(content['type']) == 2:  # Update price & quantity of order
                ack = {"success": False}

                order_id = content['order_id']
                objId = ObjectId(order_id)

                ask_price = int(content['ask_price'])
                total_qty = int(content['total_qty'])

                ts = time.time()
                order_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

                existing = mongo_order.find_one({'_id': objId})
                print('< existing ', existing, ' >')

                if existing == None:
                    print("Order does not exist")
                    ack['comment'] = 'Order does not exist'
                    return flask.jsonify(ack)

                # Check if the order has got some fill(s) - In that case, do not allow update
                if existing['order_qtydone'] > 0:
                    print("Not allowed - Order has fills")
                    ack['comment'] = "Not allowed - Order has fills"
                    return flask.jsonify(ack)

                old_price = existing['ask_price']
                old_qty = existing['total_qty']
                old_stamp = existing['order_stamp']
                old_state = existing['state']

                old_values = {'ask_price': old_price, 'total_qty': old_qty, 'order_stamp': old_stamp,
                              'state': old_state}

                history = []

                if 'history' not in existing:  # Create history list and add old values
                    history.append(old_values)
                    print('here')

                else:  # Append old values to history list
                    history = existing['history']
                    history.append(old_values)
                    print('there')

                print('history ', history)

                existing['history'] = history
                existing['orig_cl_ord_id'] = order_id
                existing['ask_price'] = ask_price
                existing['total_qty'] = total_qty
                existing['order_stamp'] = order_stamp

                print('--', existing, '--')

                new_order_id = mongo_order.insert({'orig_cl_ord_id': existing['orig_cl_ord_id'],
                                                   'user_id': existing['user_id'],
                                                   'product_id': existing['product_id'],
                                                   'side': existing['side'],
                                                   'price_instruction': existing['price_instruction'],
                                                   'ask_price': existing['ask_price'],
                                                   'total_qty': existing['total_qty'],
                                                   'order_qtydone': existing['order_qtydone'],
                                                   'LTP': existing['LTP'],
                                                   'order_stamp': existing['order_stamp'],
                                                   'reason_cancellation': existing['reason_cancellation'],
                                                   'state': 'E',
                                                   'client': existing['client'],
                                                   'exchange_id': existing['exchange_id'],
                                                   'account': existing['account'],
                                                   'counter_party': existing['counter_party'],
                                                   'history': history})

                print('NEW = ', new_order_id)

                mongo_order.delete_one({'_id': objId})

                # mongo_order.update_one({'_id': objId}, {'$set': {'history': history} }, upsert=False)
                # mongo_order.update_one({'_id': objId}, {'$set': {'ask_price': ask_price} }, upsert=False)
                # mongo_order.update_one({'_id': objId}, {'$set': {'total_qty': total_qty} }, upsert=False)
                # mongo_order.update_one({'_id': objId}, {'$set': {'order_stamp': order_stamp} }, upsert=False)

                # ack["success"] = True

                # new_order = mongo_order.find_one({'_id' : objId})		## new/updated/canceled order
                exec_ack = send_to_exec_link(existing, new_order_id, int(content['type']))
                if exec_ack['success']:
                    # mongo_order.update_one({'_id': new_order_id}, {'$set': {'state': 1} }, upsert=False)   # Live order
                    ack['success'] = True


            elif int(content['type']) == 3:  # Cancel order
                ack = {"success": False}

                order_id = content['order_id']
                objId = ObjectId(order_id)

                reason_cancellation = content['reason_cancellation']

                ts = time.time()
                order_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

                existing = mongo_order.find_one({'_id': objId})
                print('<', existing, '>')

                if existing == None:
                    print("Order does not exist")
                    ack['comment'] = 'Order does not exist'
                    return flask.jsonify(ack)

                # Check if the order has got some fill(s) - In that case, do not allow cancellation
                if existing['order_qtydone'] > 0:
                    print("Not allowed - Order has fills")
                    ack['comment'] = "Not allowed - Order has fills"
                    return flask.jsonify(ack)

                old_price = existing['ask_price']
                old_qty = existing['total_qty']
                old_stamp = existing['order_stamp']
                old_state = existing['state']

                old_values = {'ask_price': old_price, 'total_qty': old_qty, 'order_stamp': old_stamp,
                              'state': old_state}

                history = []

                if 'history' not in existing:  # Create history list and add old values
                    history.append(old_values)

                else:  # Append old values to history list
                    history = existing['history']
                    history.append(old_values)

                existing['history'] = history
                existing['orig_cl_ord_id'] = order_id
                # existing['state'] = 3
                existing['order_stamp'] = order_stamp
                existing['reason_cancellation'] = reason_cancellation

                print('--', existing, '--')

                new_order_id = mongo_order.insert({'orig_cl_ord_id': existing['orig_cl_ord_id'],
                                                   'user_id': existing['user_id'],
                                                   'product_id': existing['product_id'],
                                                   'side': existing['side'],
                                                   'price_instruction': existing['price_instruction'],
                                                   'ask_price': existing['ask_price'],
                                                   'total_qty': existing['total_qty'],
                                                   'order_qtydone': existing['order_qtydone'],
                                                   'LTP': existing['LTP'],
                                                   'order_stamp': existing['order_stamp'],
                                                   'reason_cancellation': existing['reason_cancellation'],
                                                   'state': '6',
                                                   'client': existing['client'],
                                                   'exchange_id': existing['exchange_id'],
                                                   'account': existing['account'],
                                                   'counter_party': existing['counter_party'],
                                                   'history': history})

                print('NEW = ', new_order_id)

                mongo_order.delete_one({'_id': objId})

                # mongo_order.update_one({'_id': objId}, {'$set': {'history': history} }, upsert=False)
                # mongo_order.update_one({'_id': objId}, {'$set': {'state': 3} }, upsert=False)
                # mongo_order.update_one({'_id': objId}, {'$set': {'order_stamp': order_stamp} }, upsert=False)
                # mongo_order.update_one({'_id': objId}, {'$set': {'reason_cancellation': reason_cancellation} }, upsert=False)

                # ack["success"] = True

                # new_order = mongo_order.find_one({'_id' : objId})		## new/updated/canceled order
                exec_ack = send_to_exec_link(existing, new_order_id, int(content['type']))
                if exec_ack['success']:
                    # mongo_order.update_one({'_id': new_order_id}, {'$set': {'state': 3} }, upsert=False) #cancelled order
                    ack['success'] = True


            elif int(content['type']) == 4:  # get order details
                user_id = int(content['user_id'])

                orders = []
                order_data = mongo_order.find({'user_id': user_id})

                fill_columns = [
                    {'id': 0, 'name': "OrderId", 'sortAsc': True},
                    {'id': 1, 'name': "QtyDone", 'sortAsc': True},
                    {'id': 2, 'name': "Exchange", 'sortAsc': True},
                    {'id': 3, 'name': "Stamp", 'sortAsc': True},
                    {'id': 4, 'name': "Price", 'sortAsc': True},
                    {'id': 5, 'name': "FillId", 'sortAsc': True}
                ]
                order_columns = [
                    {'id': 0, 'name': "Side", 'sortAsc': True},
                    {'id': 1, 'name': "State", 'sortAsc': True},
                    {'id': 2, 'name': "Symbol", 'sortAsc': True},
                    {'id': 3, 'name': "Client", 'sortAsc': True},
                    {'id': 4, 'name': "Size", 'sortAsc': True},
                    {'id': 5, 'name': "QtyDone", 'sortAsc': True},
                    {'id': 6, 'name': "QtyOpen", 'sortAsc': True},
                    {'id': 7, 'name': "OrderId", 'sortAsc': True},
                    {'id': 8, 'name': "PriceInstruction", 'sortAsc': True},
                    {'id': 9, 'name': "Exchange", 'sortAsc': True},
                    {'id': 10, 'name': "OrderStamp", 'sortAsc': True},
                    {'id': 11, 'name': "ProductType", 'sortAsc': True},
                    {'id': 12, 'name': "Ask", 'sortAsc': True},
                    {'id': 13, 'name': "Bid", 'sortAsc': True},
                    {'id': 14, 'name': "LTP", 'sortAsc': True},
                    {'id': 15, 'name': "Fills", 'sortAsc': True}
                ]

                data = []
                accounts = []
                i = 0
                for order in order_data:
                    order_table = []
                    order_table.append(side_dict[order['side']])
                    order_table.append(states_dict[order['state']])
                    order_table.append(order['product_id'])  # product_id = product_symbol
                    order_table.append(order['client'])

                    order_table.append(order['total_qty'])
                    order_table.append(order['order_qtydone'])
                    qtyopen = order['total_qty'] - order['order_qtydone']
                    order_table.append(qtyopen)

                    order_table.append(str(order['_id']))
                    order_table.append(order['price_instruction'])
                    order_table.append(order['exchange_id'])
                    order_table.append(order['order_stamp'])

                    prod = mongo_product.find_one({'product_id': order['product_id']})
                    try:
                        prod_type = prod['product_type']
                        order_table.append(prod_type)
                    except:
                        print("Product not in collection!")

                    order_table.append(order['ask_price'])
                    order_table.append(order['ask_price'])
                    order_table.append(order['LTP'])
                    accounts.append(order['account'])

                    # order_table['reason_cancellation'] = order['reason_cancellation']

                    fill_data = mongo_fill.find({'order_id': str(order['_id'])})
                    fill_table = []
                    fill_list = []

                    for record in fill_data:
                        fill_list = record['fills']
                        break

                    for fill in fill_list:
                        tmp_fill = []
                        tmp_fill.append(str(order['_id']))
                        tmp_fill.append(fill['qtydone'])

                        # exchange_data = mongo_exchange.find_one({'exchange_id':fill['exchange_id']})

                        tmp_fill.append(fill['exchange_id'])
                        tmp_fill.append(fill['exchange_stamp'])
                        tmp_fill.append(fill['price'])
                        # tmp_fill.append(fill['fill_id'])
                        # tmp_fill['exchange_id'] = fill['exchange_id']

                        fill_table.append(tmp_fill)

                    # order_table.append(fills)

                    data.append({'order_table': order_table, 'fill_table': fill_table, 'id': i})
                    i = i + 1

                Orders = {'order_columns': order_columns, 'fill_columns': fill_columns, 'data': data}
                ack = {'Orders': Orders, 'accounts': accounts}

                response = flask.jsonify(ack)
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Credentials', 'false')

                print(json.dumps(ack, sort_keys=True, indent=4))

                return response


            elif int(content['type']) == 5:
                print("type=5")
                symbols = content['symbols']
                ltps = {}
                clps = {}
                sps = {}

                for x in symbols:
                    orders = [str(y['_id']) for y in mongo_order.find({'product_id': x})]
                    # print(orders)
                    '''
                    for i in orders:
                        fill = mongo_fill.find({'order_id':i})
                        if i == 0:
                            fills =fill
                        else:
                            fills.union(fill)						
                    for fill in fills:
                        print(fills)'''
                    fills = mongo_fill.find({'order_id': {"$in": orders}})
                    new_fills = []
                    for i in fills:
                        # print(i)
                        if i == 0:
                            new_fills = i['fills']
                        else:
                            new_fills = new_fills + i['fills']
                    mytuple = []
                    for j in new_fills:
                        mytuple.append((j['exchange_stamp'].encode("utf-8").replace(" ", ""), j['price']))
                    today = datetime.date.today()
                    yesterday = today - datetime.timedelta(days=1)
                    today_string = today.strftime('%Y-%m-%d') + '*'
                    # yesterday_string = yesterday.strftime('%Y-%m-%d') +'*'
                    mytuple.sort(key=lambda y: y[0])
                    # y = re.compile(yesterday_string,re.UNICODE)
                    t = re.compile(today_string, re.UNICODE)
                    e_stamps = [y[0] for y in mytuple]
                    # print(e_stamps)
                    today = [str(y) for y in list(filter(t.search, e_stamps))]
                    # print(today)
                    today = sorted(today)
                    # print(today)
                    # yesterday =[str(y) for y in list(filter(y.match,e_stamps))]
                    # yesterday = sorted(yesterday,reverse = True)
                    ltp = mytuple[-1][1]
                    ltps[x] = ltp
                    # print("ltp",ltp)
                    # yesterday.sort(reverse=True)
                    # clp = list(filter(lambda y:y[0] == yesterday[0],mytuple))[0][1]
                    # clps[x] = clp
                    # print(mytuple)
                    # print(today)
                    # print("first",today[0])
                    sp = list(filter(lambda y: y[0] == today[0], mytuple))
                    print(sp)
                    sps[x] = sp[0][1]

                ack = {'ltps': ltps, 'sps': sps}
                response = flask.jsonify(ack)
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Credentials', 'false')

                print(json.dumps(ack, sort_keys=True, indent=4))

                return response

    # new_order = mongo_order.find_one({'order_id' : order_id_send})			## new/updated/canceled order
    # send_to_exec_link(new_order, content['type'])

    # return the data dictionary as a JSON response
    return flask.jsonify(ack)


# Following endpoint corresponds to execution_links() function defined below it.
# It can be called by client on 'http://localhost:5000/execution_endpoint' url.

@app.route("/execution_endpoint", methods=["POST"])
def execution_links():
    # initialize the ack dictionary that will be returned from the view
    ack = {"success": False}
    mongo_fill = mongo.db.fills
    mongo_order = mongo.db.orders  ##

    print('here')

    if flask.request.method == "POST":
        print('From exec', flask.request.data)
        if flask.request.is_json:
            content = flask.request.get_json()
            print('Content ', content)
            # print(flask.request.environ['REMOTE_ADDR'])
            # print('IP of sender : ', flask.request.remote_addr)

            ts = time.time()
            exchange_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

            order_status = content['OrdStatus']
            order_id = content['ClOrdID']
            objId = ObjectId(order_id)

            if order_status == '1' or order_status == '2':  # Partially filled / Filled
                price = content['LastPx']
                qtydone = content['CumQty']
                LTP = price  # Latest traded price

                fill = {'price': price, 'qtydone': qtydone, 'exchange_id': 'NSE', 'exchange_stamp': exchange_stamp}

                existing = mongo_fill.find_one({'order_id': order_id})
                print('<', existing, '>')

                if existing == None:  # If fills for this order_id do not exist, create new json with list of fills
                    mongo_fill.insert({'order_id': order_id, 'fills': [fill]})

                else:  # If fills for this order_id already exist, then append the new fill to list
                    existing_fills = existing['fills']
                    existing_fills.append(fill)
                    mongo_fill.update_one({'order_id': order_id}, {'$set': {'fills': existing_fills}}, upsert=False)

                mongo_order.update_one({'_id': objId}, {'$set': {'LTP': LTP}}, upsert=False)
                mongo_order.update_one({'_id': objId}, {'$inc': {'order_qtydone': qtydone}}, upsert=False)
                mongo_order.update_one({'_id': objId}, {'$set': {'state': order_status}}, upsert=False)

                order_send = mongo_order.find_one({'_id': objId})  ##
                fill_list_send = mongo_fill.find_one({'order_id': order_id})  ##
                send_to_trade_post(order_send, fill, fill_list_send)  ## send to trade post

            else:
                print("Order status ", order_status)
                mongo_order.update_one({'_id': objId}, {'$set': {'state': order_status}}, upsert=False)

            '''elif order_status == '0':		# New (Either Pending New to New OR Pending Replace to New)
                mongo_order.update_one( {'_id': objId}, {'$set': {'state': order_status} }, upsert=False )
                pass
                
            elif order_status == '4':		# Cancelled
                pass
                
            elif order_status == '8':		# Rejected
                pass'''

            '''
            fill = content['fill']			
            print(fill)
            
            fill['exchange_stamp'] = exchange_stamp
            print(fill)
            
            LTP = fill['price']		# Latest traded price
            qtydone = fill['qtydone']	

            existing = mongo_fill.find_one({'order_id' : order_id})
            print('<', existing, '>')
            
            if existing == None:		# If fills for this order_id do not exist, create new json with list of fills
                mongo_fill.insert({ 'order_id' : order_id, 'fills' : [fill] })
                
            else:				# If fills for this order_id already exist, then append the new fill to list
                existing_fills = existing['fills']
                existing_fills.append(fill)
                mongo_fill.update_one( {'order_id': order_id}, {'$set': {'fills': existing_fills} }, upsert=False)
            
            mongo_order.update_one( {'_id': objId}, {'$set': {'LTP': LTP} }, upsert=False )
            mongo_order.update_one( {'_id': objId}, {'$inc': {'order_qtydone': qtydone} }, upsert=False )'''

            # indicate that the request was a success
            ack["success"] = True

    return flask.jsonify(ack)


# if this is the main thread of execution first load the model and then start the server
if __name__ == "__main__":
    print(("* Flask starting server..."
           "Please wait until server has fully started"))
    app.run(debug=True, host='0.0.0.0')
