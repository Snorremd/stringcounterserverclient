'''
Created on Apr 12, 2013

@author: snorre
'''

import socket
import asynchat
import asyncore

import string
import random
from pickle import PickleError

from easylogging.configLogger import getLoggerForStdOut
from datetime import datetime

from tasks.taskOrganizer import TaskOrganizer
from tasks.errors import NoTasksError
from messaging.message import *
'''AuthMessage, ErrorMessage, \
    TaskMessage, RequestMessage, ResultMessage, AuthErrorMessage
'''
from messaging.pickling import serialize_message, deserialize_message


class StringCounterServer(asyncore.dispatcher):

    '''Receive connections and establish handlers for each client
    '''

    def __init__(self, address, timeoutSeconds, tasks):
        '''Initialize StringCounterServer
        '''
        asyncore.dispatcher.__init__(self)

        self.logger = getLoggerForStdOut("StringCounterServer")

        self.programId = "StringCounter"
        self.timeoutSeconds = timeoutSeconds
        self.clientSockets = {}

        self.taskOrganizer = TaskOrganizer(timeoutSeconds, tasks)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4, TCP
        self.bind(address)
        self.address = self.socket.getsockname()
        self.logger.debug("Created server socket at " + str(self.address))
        self.listen(100)
        return

    def handle_accept(self):
        '''Handle incoming calls from client
        '''
        clientInfo = self.accept()  # Should return socket and address
        '''
        self.logger.debug("Client with address %s connected to server socket"
                          % str(clientInfo[1]))
        '''
        if len(self.taskOrganizer.results) == len(tasks):
            self.logger.debug("Completed all tasks")
            for string, length in self.taskOrganizer.results:
                print string, ": ", length
            self.close()
        client = ClientHandler(clientInfo[0], self.programId,
                               self, self.taskOrganizer)
        self.clientSockets[client.clientId] = client  # Add with unique id

    def handle_close(self):
        '''Close server socket
        '''
        self.logger.debug("Server closing server socket")
        self.close()

    def remove_client(self, clientId):
        '''Removed the identified client from the list
        '''
        del self.clientSockets[clientId]


class ClientHandler(asynchat.async_chat):

    '''Handle communication with single client socket
    '''
    # Use default buffer size of 4096 bytes (4kb)
    def __init__(self, sock, programId, serverSocket, taskOrganizer):
        self.logger = getLoggerForStdOut("ClientHandler")
        asynchat.async_chat.__init__(self, sock=sock)

        self.clientId = datetime.now()
        self.programId = programId
        self.serverSocket = serverSocket

        self.taskOrganizer = taskOrganizer
        self.taskId = None

        self.authorized = False

        self.receivedData = []  # String data from client

        self.set_terminator('</' + programId + '>')  # Break on </xml> or linesep
        return

    def collect_incoming_data(self, data):
        self.receivedData.append(data)

    def found_terminator(self):
        '''Found the terminator in the input from the client
        '''
        self.process_message()

    def process_message(self):
        '''Received all command input from client. Send back data
        '''
        stringInput = ''.join(self.receivedData)  # Complete data from client
        # self.logger.debug('Process command: %s', command)
        try:
            message = deserialize_message(stringInput)
        except PickleError:
            errorMessage = ErrorMessage("Could not deserialize message",
                                        "Deserialization error")
            self.send_message(errorMessage)
        else:
            if isinstance(message, AuthMessage):
                self.authorize_client(message)
            elif isinstance(message, RequestMessage):
                self.send_client_task()
            elif isinstance(message, ResultMessage):
                self.handle_client_result(message)
        self.receivedData = []

    def send_message(self, message):
        '''Sends a message object to a client
        '''
        pickledMessage = serialize_message(message)
        self.push(pickledMessage + self.get_terminator())

    def authorize_client(self, messageObj):
        if messageObj.authData == self.programId:
            self.authorized = True
            authMessage = AuthMessage("Authentification suceeded",
                                      "Authentification data was correct")
            self.send_message(authMessage)

        else:
            errorMessage = AuthErrorMessage("Authentification failed",
                                            messageObj.authData,
                                            "Auth data was not correct")
            self.send_message(errorMessage)
            self.serverSocket.remove_client(self.clientId)
            self.close_when_done()

    def send_client_task(self):
        try:
            self.taskId, task = self.taskOrganizer.get_task()
        except NoTasksError:
            errorMessage = ErrorMessage("No tasks",
                                        "No tasks error")
            self.send_message(errorMessage)
        else:
            taskMessage = TaskMessage("Task:", self.taskId, task)
            self.send_message(taskMessage)

    def handle_client_result(self, resultMessage):
        result = resultMessage.result
        taskId = resultMessage.taskId

        if self.taskId == taskId and self.taskOrganizer.task_active(taskId):
            self.taskOrganizer.finish_task(taskId, result)
        else:
            errorMessage = ErrorMessage("Could not validate task result",
                                        "Invalid result error")
            self.send_message(errorMessage)


def create_random_strings():
    strings = []
    for _ in xrange(100000):
        strings.append(id_generator(random.randint(5, 40)))
    return strings


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in xrange(size))


if __name__ == '__main__':
    mainLogger = getLoggerForStdOut('Main')
    tasks = create_random_strings()
    mainLogger.debug("Create " + str(len(tasks)) + " number of strings")
    strCountServer = StringCounterServer(("localhost", 9876), 100, tasks)
    mainLogger.debug("Created server to listen on %s:%s" %
                     strCountServer.address)
    mainLogger.debug("Start asyncore loop")
    asyncore.loop()
