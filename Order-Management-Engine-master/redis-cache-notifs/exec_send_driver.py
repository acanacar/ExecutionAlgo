from settings import r
import sys

if __name__ == '__main__':
    channel = "execution" 

    print 'Welcome to {channel}'.format(**locals())

    while True:
        message = raw_input('Enter a message: ')

        if message.lower() == 'exit':
            break

        message = '{message}'.format(**locals())

        r.publish(channel, message)

