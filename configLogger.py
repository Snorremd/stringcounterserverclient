'''
Created on Apr 12, 2013

@author: snorre
'''

import logging
import sys
import time


def getLoggerForStdOut(nameForLogger):
    logger = logging.getLogger(nameForLogger + str(time.time()))
    logger.level = logging.DEBUG
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    return logger
