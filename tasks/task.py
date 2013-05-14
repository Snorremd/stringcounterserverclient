from datetime import datetime


class Task(object):

    '''Class modelling one Task to execute.
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

    def execute(self):
        return None


class StringTask(Task):

    '''A simple class to find lenghts of strings
    '''

    def __init__(self, workItem):
        Task.__init__(self, workItem)

    def execute(self):
        result = len(self.workItem)
        return result
