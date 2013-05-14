'''
Created on May 13, 2013

@author: snorre
'''

from easylogging.configLogger import getLoggerForStdOut
from client.client import Client
import asyncore
import socket
from time import sleep
import sys


if __name__ == '__main__':
        mainLogger = getLoggerForStdOut("Main")
        address = ('microbrewit.thunemedia.no', 9874)
        client = None
        try:
            client = Client(address, "StringCounter", "snorremac!")
            asyncore.loop()
            sleep(1)
        except socket.error:
            # Server probably busy
            mainLogger.debug("Could not connect to server, restart script")
        except KeyboardInterrupt:
            try:
                if not client == None:
                    mainLogger.debug("Attempting to disconnect from server.\n" + \
                                     "Press ctrl + C again to force close script.")
                    client.disconnect("User cancelled script")
            except KeyboardInterrupt:
                sys.exit(0)
