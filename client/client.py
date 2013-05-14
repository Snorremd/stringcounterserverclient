'''
Created on Apr 12, 2013

@author: snorre
'''

import asynchat
import socket

from easylogging.configLogger import getLoggerForStdOut
from time import sleep

from tasks import taskExecutor
from tasks.errors import TaskExecutionError

from messaging.message import *
from messaging.pickling import serialize_message, deserialize_message
from pickle import PickleError


class Client(asynchat.async_chat):

    '''Counts the length of strings received from server
    '''
    def __init__(self, address, programId, username):
        '''Constructor of Client class
        '''
        asynchat.async_chat.__init__(self)

        self.logger = getLoggerForStdOut("Client")

        self.programId = "StringCounter"
        self.username = username
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
        authMessage = AuthenticationMessage("Connecting", self.programId,
                                            self.username)
        self.send_message(authMessage)
        return

    def disconnect(self, disconnectInfo):
        '''Disconnect from server and close connection
        '''
        message = DisconnectMessage("Client disconnected",
                                    disconnectInfo)
        self.send_message(message)
        self.close_when_done()
        self.logger.debug("Disconnected from server")

    def collect_incoming_data(self, data):
        self.receivedData.append(data)

    def found_terminator(self):
        self.process_message()

    def process_message(self):
        receivedString = ''.join(self.receivedData)
        try:
            message = deserialize_message(receivedString)
        except PickleError:
            self.logger.debug("Could not deserialize message")
        else:
            if isinstance(message, TaskMessage):
                self.process_tasks(message.tasks)
            elif isinstance(message, NoTasksMessage):
                self.logger.debug("Server returned NoTasksError " + \
                                  "with reason:\n" + message.noTasksInfo)
                sleep(10)
                self.send_task_request()
            elif isinstance(message, ScoreMessage):
                self.logger.debug("Received scores")
                self.output_scores(message)
                self.send_task_request()
            elif isinstance(message, AuthErrorMessage):
                self.logger.debug("Server returned AuthErrorMessage " + \
                                  "for tasks:\n" + str(message.taskIds))
                self.logger.debug("Could not authenticate with program id: " + 
                                  self.programId + ". Closing client")
                self.close_when_done()
            elif isinstance(message, AuthenticationMessage):
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
            self.send_task_request()  # Ask for new Task
        else:
            self.push(message + self.get_terminator())

    def send_task_request(self):
        '''Sends a Task request message to server
        '''
        message = RequestMessage("Request Task")
        self.send_message(message)

    def process_tasks(self, tasks):
        '''Process n tasks and sends a results message to server

        Args:
            tasks (dict): a map of taskIds and task objects

        '''
        try:
            results = taskExecutor.execute_tasks(tasks)
        except TaskExecutionError as error:
            self.logger.debug("Could not execute task: " + \
                              str(error.task))

            self.disconnect("Could not execute tasks")
            self.logger.debug("Client disconnected from the server as " + \
                              "it could not execute given tasks.")
        else:
            self.send_task_results(results)
            self.noOfCompletedTasks += len(results)
            self.send_task_request()
        sleep(5)

    def send_task_results(self, results):
        '''Sends task results to the server

        Args:
            results (dict): a map of taskIds and results
        '''
        message = ResultMessage("Result", results)
        self.send_message(message)

    def output_scores(self, scoreMessage):
        '''Outputs scores to the logger defined in self
        '''
        scoreOutput = "\n#####################################\n" + \
        "Your score: " + str(scoreMessage.userScore) + "\n" + \
        "-----------\n" + \
        self.get_scoreboard_string(scoreMessage.topScores)
        self.logger.debug(scoreOutput)

    def get_scoreboard_string(self, topScores):
        noOfScores = len(topScores)
        scoreBoardString = "Top " + str(noOfScores) + " users:\n"
        for user, score in topScores:
            scoreBoardString += "{0:15} : {1}\n".format(user, score)
        return scoreBoardString
