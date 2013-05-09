from errors import NoSuchUserError


class ScoreBoard(object):

    '''A class that keeps tab on a client's score.

    Properties:
        totalScore (int): the number of tasks completed in total
        scores (dict): a dictionary of each user's individual score
    '''

    def __init__(self):
        self.totalScore = 0
        self.scores = {}
        self.ranks = 

    def increment_user_score(self, user):
        '''Increments a user's score with 1

        Args:
            user (str): the user who's score to increment
        '''
        if user not in self.scores:
            self.scores[user] = 1
        else:
            self.scores[user] += 1

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
