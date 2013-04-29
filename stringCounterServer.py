'''
Created on Apr 12, 2013

@author: snorre
'''

import socket
import asynchat
import asyncore

from collections import deque
from configLogger import getLoggerForStdOut
from datetime import datetime
from os import linesep


class StringCounterServer(asyncore.dispatcher):
    '''Receive connections and establish handlers for each client
    '''

    def __init__(self, address, timeoutSeconds):
        '''Initialize StringCounterServer
        '''
        asyncore.dispatcher.__init__(self)
        self.programId = "StringCounter"
        self.timeoutSeconds = timeoutSeconds

        ## Make three collections, one with tasks,
        ## one with current jobs,
        ## and one with the results
        self.tasksDeque = deque(["This is my hearth", "You are cool", "Abcd", "lkajsdlkajds", "lk<jsdkljl<kjsdlakds", "kljlkajlkjdsakjald"])
        self.jobDict = {}
        self.resultDict = {}
        self.logger = getLoggerForStdOut("StringCounterServer")
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)  #IPv4, TCP
        self.bind(address)
        self.address = self.socket.getsockname()
        self.logger.debug("Created server socket at " + str(self.address))
        self.listen(100)
        return

    def handle_accept(self):
        '''Handle incoming calls from client
        '''
        clientInfo = self.accept()  # Should return socket and address
        self.logger.debug("Client with address %s connected to server socket" \
                          % str(clientInfo[1]))

        self.check_jobs()  # Check if any tasks timed out

        task = None
        if not len(self.tasksDeque) == 0:
            ## Task id is datetime object, string is task data
            task = (self.tasksDeque.popleft(), datetime.now())
            ## Use datetime object as key in dictionary
            self.jobDict[task[1]] = task[0]

            ClientHandler(clientInfo[0], self.programId, task,
                      self.jobDict, self.resultDict)
        else:
            task = None
            ClientHandler(clientInfo[0], self.programId, task,
                          None, None)

        self.logger.debug(str(self.tasksDeque) + str(self.jobDict))
        if len(self.tasksDeque) == 0 and len(self.jobDict) == 0:
            self.logger.debug("Currently no tasks to perform")
            self.logger.debug("Results: " + str(self.resultDict))
        return

    def handle_close(self):
        '''Close server socket
        '''
        self.logger.debug("Server closing server socket")
        self.logger.debug("Final results: " + str(self.resultDict))
        self.close()

    def check_jobs(self):
        '''Checks all ongoing jobs for timeouts

        If a task is timed out, it is appended to the
        task list for later consumption, and deleted from
        the job dictionary
        '''
        currentTime = datetime.now()
        for timestamp in self.jobDict.keys():  # Copy of keys list
            print timestamp
            difference = currentTime - timestamp
            if difference.seconds > self.timeoutSeconds:
                self.logger.debug("Task was removed from job dict back to task list")
                self.tasksDeque.append(self.jobDict[timestamp])
                del self.jobDict[timestamp]


class ClientHandler(asynchat.async_chat):
    '''Handle communication with single client socket
    '''
    ## Use default buffer size of 4096 bytes (4kb)
    def __init__(self, sock, programId, task, jobDict,
                 resultDict):
        self.programId = programId
        self.task = task
        self.jobDict = jobDict
        self.resultDict = resultDict
        self.receivedData = []
        self.logger = getLoggerForStdOut("ClientHandler")
        asynchat.async_chat.__init__(self, sock=sock)
        self.process_data = self.process_command
        self.set_terminator('</xml>')  # Break on </xml> or linesep
        return

    def collect_incoming_data(self, data):
        self.logger.debug("Read message from client socket and insert into incoming queue")
        self.receivedData.append(data)

    def found_terminator(self):
        '''Found the terminator in the input from the client
        '''
        self.logger.debug("Reached end of input (found terminator), process")
        self.process_data()

    def process_command(self):
        '''Received all command input from client. Send back data
        '''
        command = ''.join(self.receivedData)  # Complete data from client
        self.logger.debug('Process command: %s', command)
        try:
            programId = command
            if programId == self.programId:
                ## Everything is in order, send string
                if not self.task == None:
                    self.process_data = self.process_message  # Ready to receive count
                    self.receivedData = []  # Reset input queue
                    self.push(self.task[0] + self.get_terminator())
                else:
                    self.push("ERROR! There is currently no tasks to calculate." + 
                              self.get_terminator())
            else:
                self.logger.debug("A client tried to connect with the wrong program id")
                self.push("Connection not authorized" + linesep)
                self.close_when_done()  # Not a string counter script
        except ValueError:
            self.logger.debug("Caught ValueException. Wrong input: " + command)
            self.logger.debug("Close connection to client socket")
            self.push("Could not read command...", linesep)
            self.close_when_done()

    def process_message(self):
        '''Entire string count message read. Output to logger
        '''
        stringCount = ''.join(self.receivedData)
        try:
            count = int(stringCount)
            self.resultDict[self.task[0]] = count
            self.logger.debug("Client calculated string length")
            self.logger.debug("Inserted string length into dict: ")
            self.logger.debug("Dict now looks like:\n" + str(self.resultDict))
        except ValueError:
            self.stringsToProcess.append(self.stringToProcess)
            self.logger.debug("Client returned something other than an integer. Restore string to server")
        self.logger.debug("Close connection to client socket")
        self.close_when_done()


if __name__ == '__main__':
    mainLogger = getLoggerForStdOut('Main')
    strCountServer = StringCounterServer(("localhost", 9876), 100)
    mainLogger.debug("Created server to listen on %s:%s" % strCountServer.address)
    mainLogger.debug("Start asyncore loop")
    asyncore.loop()
