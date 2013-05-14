'''
Created on May 13, 2013

@author: snorre
'''
from tasks.task import Task
from tasks.errors import TaskExecutionError


def execute_tasks(tasks):
    '''Return results for tasks dict

    Args:
        tasks (dict): taskids mapping to tasks

    Returns:
        a dict containing taskids and corresponding results

    Raises:
        TaskExecutionError if task value is of wrong type

    '''
    try:
        results = {}
        for (taskId, task) in tasks.items():
            results[taskId] = execute_task(task)
        return results
    except TaskExecutionError:
        raise

def execute_task(task):
    '''Executes a task and returns the given result

    Args:
        task (Task): the task to execute

    Returns:
        result from of executing task

    Raises:
        TypeError if task value is not of type Task (or subclass)
    '''
    if hasattr(task, "execute"):
        return task.execute()
    else:
        raise TaskExecutionError("task has to have execution " + \
                                 "method", task)
