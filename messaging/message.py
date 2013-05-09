class Message(object):

    '''Base class for message that can be sent between server and client
    '''

    def __init__(self, message):
        self.message = message


class TaskMessage(Message):

    '''Message containing task to execute
    '''
    def __init__(self, message, taskId, task):
        Message.__init__(message)
        self.taskId = taskId
        self.task = task


class ResultMessage(Message):

    '''Message containing results from client
    '''
    def __init__(self, message, taskId, result):
        Message.__init__(message)
        self.taskId = taskId
        self.result = result


class AuthMessage(Message):

    '''Message containing authentication data
    '''
    def __init__(self, message, authData):
        Message.__init__(message)
        self.authData = authData


class AuthErrorMessage(AuthMessage):

    ''' Message containing auth error data
    '''

    def __init__(self, message, authData, error):
            AuthMessage.__init(message, authData)
            self.error = error


class RequestMessage(Message):

    '''Message containing a task request
    '''
    def __init__(self, message):
        Message.__init__(message)


class ErrorMessage(Message):

    '''Message containing error message
    '''
    def __init__(self, message, error):
        Message.__init__(message)
        self.error = error