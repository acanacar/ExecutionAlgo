from settings import r
import sys
#one channel for order execution, one channel for order entry
#we need our redis server to subscribe to both channels
#if there is a order request, find out on pubsub.listen() somehow store in cache the order number and add the user 
#if there is an update on order, access the cache mentioned above and send order details 
def main():    
    channel = "entry"
    print 'Welcome to {channel}'.format(**locals())
    while True:
        message = raw_input('Enter a message: ')
        message = '{message}'.format(**locals())
        if message.lower() == 'exit':
        	break
        r.publish(channel, message)

if __name__ == '__main__':
    main()
