class Message(object):

    '''Base class for message that can be sent between server and client
    '''

    def __init__(self, message):
        self.message = message


class AuthenticationMessage(Message):

    '''Message containing authentication data
    '''
    def __init__(self, message, authData):
        Message.__init__(self, message)
        self.authData = authData


class AuthErrorMessage(AuthenticationMessage):

    ''' Message containing auth error data
    '''

    def __init__(self, message, authData, error):
            AuthenticationMessage.__init__(self, message, authData)
            self.error = error


class TaskMessage(Message):

    '''Message containing task to execute
    '''
    def __init__(self, message, tasks):
        Message.__init__(self, message)
        self.tasks = tasks


class NoTasksMessage(Message):

    '''Message containing no task info
    '''
    def __init__(self, message, noTasksInfo):
        Message.__init__(self, message)
        self.noTasksInfo = noTasksInfo


class TaskAuthenticationError(Message):

    '''Message containing task auth error
    '''
    def __init__(self, message, taskIds):
        Message.__init__(self, message)
        self.taskids = taskIds


class ResultMessage(Message):

    '''Message containing results from client
    '''
    def __init__(self, message, results):
        Message.__init__(self, message)
        self.results = results


class RequestMessage(Message):

    '''Message containing a task request
    '''
    def __init__(self, message):
        Message.__init__(self, message)


class ErrorMessage(Message):

    '''Message containing error message
    '''
    def __init__(self, message, error):
        Message.__init__(self, message)
        self.error = error


class DisconnectMessage(Message):

    '''Disconnection message for client or server
    '''
    def __init__(self, message, disconnectInfo):
        Message.__init__(self, message)
        self.disconnectInfo = disconnectInfo
