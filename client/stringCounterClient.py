'''
Created on Apr 12, 2013

@author: snorre
'''

import asynchat
import socket
import configLogger
from time import sleep
import asyncore

from messaging.message import AuthMessage, AuthErrorMessage, \
    RequestMessage, ResultMessage, TaskMessage
from messaging.pickling import serialize_message, deserialize_message
from pickler import PicklingError, UnpicklingError


class StringCounterClient(asynchat.async_chat):

    '''Counts the length of strings received from server
    '''
    def __init__(self, address, programId, terminator):
        '''Constructor of StringCounterClient class
        '''
        asynchat.async_chat.__init__(self)

        self.logger = configLogger.getLoggerForStdOut("StringCounterClient")

        self.programId = "stringCounter"
        self.set_terminator("\n")
        self.receivedData = []

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4, TCP
        self.logger.debug('Connecting to %s, %s' % address)
        self.connect(address)
        return

    def handle_connect(self):
        '''Push command to server to authenticate
        '''
        self.logger.debug("Connected to server, push authentication data")
        authMessage = AuthMessage("Connecting", self.programId)
        self.send_message(authMessage)

    def collect_incoming_data(self, data):
        self.receivedData.append(data)
        self.logger.debug("Received data from server: " + data)

    def found_terminator(self):
        self.logger.debug("Found terminator from server socket")
        self.process_message()

    def process_message(self):
        receivedString = ''.join(self.receivedData)

        try:
            message = deserialize_message(receivedString)
        except UnpicklingError:
            self.logger.debug("Could not deserialize message")
        else:
            if isinstance(message, AuthMessage):
                self.send_task_request()
            elif isinstance(message, AuthErrorMessage):
                self.logger.debug("Could not authenticate with program id: " +
                                  self.programId + ". Closing client")
                self.close_when_done()
            elif isinstance(message, TaskMessage):
                length = self.process_task(message)
                self.send_task_result(length)

        self.receivedData = []

    def send_message(self, messageObj):
        '''Serialize message and send to server
        '''
        try:
            message = serialize_message(messageObj)
        except PicklingError:
            self.logger.debug("Could not serialize/pickle message")
            self.send_task_request()  # Ask for new task
        else:
            self.push(message + self.get_terminator())

    def send_task_request(self):
        '''Sends a task request message to server
        '''
        message = RequestMessage("Give task")
        self.send_message(message)

    def process_task(self, message):
        task = message.task
        length = len(task)
        return length

    def send_task_result(self, result):
        message = ResultMessage("Result", result)
        self.send_message(message)

if __name__ == '__main__':
    while True:
        address = ('localhost', 9876)
        try:
            client = StringCounterClient(address, "StringCounter", "</xml>")
            asyncore.loop()
            sleep(1)
        except socket.error:
            # Server probably busy
            sleep(20)
