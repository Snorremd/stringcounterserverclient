from datetime import datetime


class task(object):

    '''Class modelling one task to execute.
    '''

    def __init__(self, workItem):
        self.timestamp = datetime.now()
        self.workItem = workItem

    def is_timed_out(self, timeoutInSeconds):
        currentTime = datetime.now()
        timeDifference = currentTime - self.timestamp
        if timeDifference.seconds > timeoutInSeconds:
            return True
        else:
            return False
