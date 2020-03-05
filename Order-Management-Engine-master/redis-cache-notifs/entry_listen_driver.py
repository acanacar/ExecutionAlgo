from settings import r
import sys
#one channel for order execution, one channel for order entry
#we need our redis server to subscribe to both channels
#if there is a order request, find out on pubsub.listen() somehow store in cache the order number and add the user 
#if there is an update on order, access the cache mentioned above and send order details 
def main():    
    entry_send_channel = "entry_send"
    entry_pubsub = r.pubsub()
    entry_pubsub.subscribe(entry_send_channel)
    print 'Welcome to {entry_send_channel}'.format(**locals())
    while True:
        for item in entry_pubsub.listen():
            print item['data']
            break

if __name__ == '__main__':
    main()
