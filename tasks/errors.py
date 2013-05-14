class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class NoTasksError(Error):

    '''Exception raised for errors in the input.
    Attributes:
        msg  -- explanation of the error
    '''
    def __init__(self, msg):
        Error.__init__(self, msg)


class TaskExecutionError(Error):

    '''Exception raised if task execution errors
    occurs
    '''
    def __init__(self, msg, task):
        Error.__init__(self, msg)
        self.task = task
