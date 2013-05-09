'''
Created on May 9, 2013

@author: snorre
'''

from messaging.pickling import serialize_message, deserialize_message
from messaging.message import Message

if __name__ == '__main__':
    message = Message("This is message")
    serialized = serialize_message(message)
    print serialized
    received = deserialize_message(serialized)
    print received