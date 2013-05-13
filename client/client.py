'''
Created on Apr 12, 2013

@author: snorre
'''

import asynchat
import socket

from easylogging.configLogger import getLoggerForStdOut
from time import sleep

from messaging.message import *
from messaging.pickling import serialize_message, deserialize_message
from pickle import PickleError


class StringCounterClient(asynchat.async_chat):

    '''Counts the length of strings received from server
    '''
    def __init__(self, address, programId):
        '''Constructor of StringCounterClient class
        '''
        asynchat.async_chat.__init__(self)

        self.logger = getLoggerForStdOut("StringCounterClient")

        self.programId = "StringCounter"
        self.set_terminator('</' + programId + '>')
        self.receivedData = []
        self.noOfCompletedTasks = 0

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
        return

    def collect_incoming_data(self, data):
        self.receivedData.append(data)
        self.logger.debug("Received data")

    def found_terminator(self):
        self.logger.debug("Found terminator from server socket")
        self.process_message()

    def process_message(self):
        receivedString = ''.join(self.receivedData)
        self.logger.debug("Process message")

        try:
            message = deserialize_message(receivedString)
        except PickleError:
            self.logger.debug("Could not deserialize message")
        else:
            if isinstance(message, TaskMessage):
                results = self.process_tasks(message.tasks)
                self.send_task_results(results)
                self.noOfCompletedTasks += len(results)
                self.send_task_request()
                self.logger.debug(str(self.noOfCompletedTasks) + " number of tasks completed")
            elif isinstance(message, ErrorMessage):
                sleep(10)
                self.send_task_request()
            elif isinstance(message, AuthErrorMessage):
                self.logger.debug("Is instance of AuthErrorMessage")
                self.logger.debug("Could not authenticate with program id: " + 
                                  self.programId + ". Closing client")
                self.close_when_done()
            elif isinstance(message, AuthMessage):
                self.logger.debug("Successfully authenticated")
                self.send_task_request()

        self.receivedData = []

    def send_message(self, messageObj):
        '''Serialize message and send to server
        '''
        try:
            message = serialize_message(messageObj)
        except PickleError:
            self.logger.debug("Could not serialize/pickle message")
            self.send_task_request()  # Ask for new task
        else:
            self.push(message + self.get_terminator())

    def send_task_request(self):
        '''Sends a task request message to server
        '''
        message = RequestMessage("Give task")
        self.send_message(message)

    def process_tasks(self, tasks):
        '''Process n tasks and return results
        '''
        results = {}
        for taskId, task in tasks.items():
            result = self.process_task(task)
            results[taskId] = result
        return results

    def process_task(self, task):
        length = len(task)
        return length

    def send_task_results(self, results):
        message = ResultMessage("Result", results)
        self.send_message(message)
