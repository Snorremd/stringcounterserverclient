'''
Created on Apr 12, 2013

@author: snorre
'''

import asynchat
import socket
import configLogger
from time import sleep
import asyncore


class StringCounterClient(asynchat.async_chat):
    '''Counts the length of strings received from server
    '''
    def __init__(self, address, programId, terminator):
        '''Constructor of StringCounterClient class
        '''
        self.programId = programId
        self.set_terminator(terminator)
        self.receivedData = []
        self.logger = configLogger.getLoggerForStdOut("StringCounterClient")
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4, TCP
        self.logger.debug('Connecting to %s, %s' % address)
        self.connect(address)
        return

    def handle_connect(self):
        '''Push command to server to authenticate
        '''
        self.logger.debug("Connected to server, push authentication data")
        self.push(self.programId + self.get_terminator())

    def collect_incoming_data(self, data):
        self.receivedData.append(data)
        self.logger.debug("Received data from server: " + data)

    def found_terminator(self):
        self.logger.debug("Found terminator from server socket")
        self.process_message()

    def process_message(self):
        receivedMessage = ''.join(self.receivedData)
        if receivedMessage.startswith("ERROR!"):
            self.logger.debug(receivedMessage)
            self.close()
        else:
            stringLength = len(receivedMessage)
            self.logger.debug("Received string " + receivedMessage + " of length " + str(stringLength))
            self.logger.debug("Attempt to push data to server")
            self.push(str(stringLength) + self.get_terminator())
            self.close_when_done()
        self.logger.debug("Disconnected from server")
        

if __name__ == '__main__':
    while True:
        address = ('localhost', 9876)
        try:
            client = StringCounterClient(address, "StringCounter", "</xml>")
            asyncore.loop()
            sleep(1)
        except socket.error:
            ## Server probably busy, sleep a bit longer to avoid too much traffic
            sleep(20)
