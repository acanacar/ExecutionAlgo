from settings import r
import sys
import json
#from common.redis_client import get_redis_client

#one channel for order execution, one channel for order entry
#we need our redis server to subscribe to both channels
#if there is a order request, find out on pubsub.listen() somehow store in cache the order number and add the user 
#if there is an update on order, access the cache mentioned above and send order details 
def json_cache(loaded_json, cache):
    if loaded_json['order_id'] in cache:
        cache[loaded_json['order_id']].append(loaded_json['user_id'])
    else:
        cache[loaded_json['order_id']] = [loaded_json['user_id']]
    print cache
    return


def main():
    cache = dict()
    exec_channel = "execution"
    entry_channel = "entry"
    entry_send_channel = "entry_send"
    pubsub = r.pubsub()
    pubsub.subscribe(entry_channel, exec_channel)
    #print 'Listening to {channel}'.format(**locals())
    while True:
        for item in pubsub.listen():
            if item['data'] == 1L or item['data'] == 2L:
                continue
            if item['channel'] == "entry":
                print item['data'],"sent by order entry and cached"
                loaded_json = json.loads(item['data'].replace("\'", '"')) 
                json_cache(loaded_json, cache) 

            if item['channel'] == "execution":
                print item['data']," sent by execution links"
                loaded_json = json.loads(item['data'].replace("\'", '"')) 
                if loaded_json['order_id'] in cache:
                    r.publish(entry_send_channel, str(cache[loaded_json['order_id']]))
                else:
                    r.publish(entry_send_channel, "not found")




if __name__ == '__main__':
    main()
