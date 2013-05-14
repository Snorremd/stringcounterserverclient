from errors import NoSuchUserError
from collections import OrderedDict


class ScoreBoard(object):

    '''A class that keeps tab on a client's score.

    Properties:
        totalScore (int): the number of tasks completed in total
        scores (dict): a dictionary of each user's individual score
    '''

    def __init__(self):
        self.noOfExecutedTasks = 0
        self.scores = OrderedDict({})

    def increase_user_score(self, user, amount):
        '''Increases a user's score with given amount

        Args:
            user (str): the user who's score to increment
            amount (int): the amount with which to incrase score
        '''
        if user not in self.scores:
            self.scores[user] = amount
        else:
            self.scores[user] += amount

        self.noOfExecutedTasks += amount

    def get_user_score(self, user):
        '''Return score of named user

        Args:
            user (str): the name of the user

        Returns:
            the score of the user if user in scores dict.
            Raises NoSuchUserError if user not found.
        '''
        try:
            score = self.scores[user]
        except KeyError:
            raise NoSuchUserError("User not found", user)
        else:
            return score

    def get_user_ranks(self):
        '''Get the rank of all users

        Returns:
            Scores (OrderedDict) with user -> score mappings
        '''
        ## Sort the key-value-pairs according to score in descending order
        sorted(self.scores.items(),
               key=lambda item:
                                - item[1])
        return self.scores
