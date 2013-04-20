'''
Created on Apr 12, 2013

@author: snorre
'''

import asyncore
import logging
import socket
import sys
from configLogger import getLoggerForStdOut
import asynchat


class StringCounterServer(asyncore.dispatcher):
    '''Receive connections and establish handlers for each client
    '''

    def __init__(self, address):
        '''Initialize StringCounterServer
        '''
        asyncore.dispatcher.__init__(self)
        self.programId = "StringCounter"
        self.stringsToProcess = ["This is my hearth", "You are cool", "Abcd"]
        self.logger = getLoggerForStdOut("StringCounterServer")
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)  #IPv4, TCP
        self.bind(address)
        self.address = self.socket.getsockname()
        self.logger.debug("Created server socket at " + str(self.address))
        self.listen(10)
        return

    def handle_accept(self):
        '''Handle incoming calls from client
        '''
        clientInfo = self.accept()  # Should return socket and address
        self.logger.debug("Client with address %s connected to server socket" % str(clientInfo[1]))
        ClientHandler(clientInfo[0], self.programId, self.stringsToProcess.pop())
        ## self.handle_close()
        return

    def handle_close(self):
        '''Close server socket
        '''
        self.logger.debug("Server closing server socket")
        self.close()



class ClientHandler(asynchat.async_chat):
    '''Handle communication with single client socket
    '''
    ## Use default buffer size of 4096 bytes (4kb)
    def __init__(self, sock, programId, stringToProcess):
        self.programId = programId
        self.stringToProcess = stringToProcess
        self.receivedData = []
        self.logger = getLoggerForStdOut("ClientHandler")
        asynchat.async_chat.__init__(self, sock=sock)
        self.process_data = self.process_command
        self.set_terminator('\n')
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
            programId, terminator = command.strip().split()
            if programId == self.programId and len(terminator) > 0:
                ## Everything is in order, send string
                self.set_terminator(terminator)  # Client's reported length
                self.process_data = self.process_message  # Ready to receive count
                self.receivedData = []  # Reset input queue
            else:
                self.logger.debug("A client tried to connect with the wrong program id")
                self.close_when_done()  # Not a string counter script
        except ValueError:
            self.logger.debug("Caught ValueException. Wrong input: " + command)
            self.close_when_done()

    def process_message(self):
        '''Entire string count message read. Output to logger
        '''
        stringCount = ''.join(self.receivedData)
        self.logger.debug(self.stringToProcess + " is " + stringCount + " characters long")
        self.close_when_done()


if __name__ == '__main__':
    mainLogger = getLoggerForStdOut('Main')
    strCountServer = StringCounterServer(("localhost", 9876))
    mainLogger.debug("Created server to listen on %s:%s" % strCountServer.address)
    mainLogger.debug("Start asyncore loop")
    asyncore.loop()
