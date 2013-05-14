from collections import deque
from errors import NoTasksError
from datetime import datetime


class TaskOrganizer(object):

    '''Receive connections and establish handlers for each client
    '''

    def __init__(self, timeoutSeconds, tasks):
        '''Initialize StringCounterServer
        '''
        self.pendingTasks = deque(tasks)
        self.activeTasks = {}
        self.results = {}
        self.timeout = timeoutSeconds

    def add_tasks(self, tasks):
        '''Add all elements of tasks to pending tasks
        '''
        self.pendingTasks.extend(tasks)

    def get_task(self):
        '''Get first remaning Task if any

        Returns:
            A Task id and first available Task object.
            If none available, raise NoTasksError.
        '''
        try:
            Task = self.pendingTasks.popleft()
        except IndexError:
            raise NoTasksError("There are no remaning tasks in" + 
                               " pendingTasks deque")
        else:  # No exceptions raised
            taskId = self.make_task_active(Task)
            return taskId, Task

    def get_tasks(self, noOfTasks):
        '''Get n number of tasks from Task list

        Args:
            noOfTasks (int): number of tasks to get

        Returns:
            a dict containing taskId, Task pairs
        '''
        tasks = {}
        for _ in xrange(noOfTasks):
            try:
                taskId, Task = self.get_task()
            except NoTasksError:
                break
            else:
                tasks[taskId] = Task
        if not len(tasks) == 0:
            return tasks
        else:
            raise NoTasksError("There are no remaning tasks in" + 
                               " pendingTasks deque")

    def make_task_active(self, Task):
        '''Add a Task to the active jobs dictionary

        Args:
            Task (Task): The Task to make active

        Returns:
            currentTime (object) of when Task was created
        '''
        currentTime = datetime.now()
        self.activeTasks[currentTime] = Task
        return currentTime

    def check_active_tasks(self):
        '''Check active tasks for timeouts

        For each Task in active tasks, check if the
        Task has timed out, and if so reinsert into
        pendingTasks deque and remove from active tasks dict.
        '''
        currentTime = datetime.now()
        for timestamp in self.activeTasks.keys():
            difference = currentTime - timestamp
            if difference.seconds > self.timeout:
                self.pendingTasks.append(self.activeTasks[timestamp])
                del self.pendingTasks[timestamp]

    def task_active(self, taskId):
        '''Check if a Task is still active

        Args:
            taskId (object): the id of the Task to be checked

        Returns:
            True if Task still active, False if not
        '''
        if taskId in self.activeTasks:
            return True
        else:
            return False

    def finish_task(self, taskId, result):
        '''Finish Task

        Args:
            taskId (object): the idTaskthe task to finish
            result (Result): the finished result
        '''
        self.results[self.activeTasks[taskId]] = result
        del self.activeTasks[taskId]

    def finish_tasks(self, results):
        '''Finish the identified tasks with the given results

        Args:
            results (dict): taskIds (keys) and corresponding results (vals)
        '''
        for taskId, result in results.items():
            if self.task_active(taskId):
                self.finish_task(taskId, result)
