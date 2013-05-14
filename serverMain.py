'''
Created on May 13, 2013

@author: snorre
'''
from easylogging.configLogger import getLoggerForStdOut
from server.server import Server
from tasks.task import StringTask

import asyncore
import random
import string


def create_random_strings():
    stringTasks = []
    for _ in xrange(1000000):
        stringTasks.append(StringTask(id_generator(random.randint(5, 40))))
    return stringTasks


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in xrange(size))



if __name__ == '__main__':
    mainLogger = getLoggerForStdOut('Main')
    tasks = create_random_strings()
    mainLogger.debug("Create " + str(len(tasks)) + " number of strings")
    server = Server(("", 9874), 100, tasks, 10)
    mainLogger.debug("Created server to listen on %s:%s" % 
                     server.address)
    mainLogger.debug("Start asyncore loop")
    asyncore.loop()
