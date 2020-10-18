# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# searchSol.py, created: 2020.10.18  #
# Last Modified: 2020.10.18          #
# ################################## #

from typing import Set, List
from config import *
from NRP import NextReleaseProblem

# state
class State:
    # define members
    def __init__(self, y : int, x : Set[int], p : int, c : int):
        self.y = y
        self.x = x
        self.p = p
        self.c = c

    # remove a x
    def update(self, xs_remove : List[int], c_diff : int):
        for x_remove in xs_remove:
            if x_remove in self.x:
                self.x.remove(x_remove)
        self.c -= c_diff

# naive search based solver
class SearchSol:
    # dominate test, return if x dominate y
    dominate = lambda x, y : x[0] <= y[0] and x[1] <= y[1]

    # initialize 
    def __init__(self, problem):
        # load problem
        self.__cost, self.__profit, _, self.__requests = problem
        # make rest y "set"
        # rest y set, manage states as p order
        self.__rest = dict()
        # gathering the request by y
        y_request = dict()
        for request in self.__requests:
            if request[0] not in y_request:
                y_request[request[0]] = [request[1]]
            else:
                y_request[request[0]].append(request[1])
        # use gathered request to construct self.rest
        for y_id, request_list in y_request.items():
            # calculate cost of y
            y_cost = sum([self.__cost[x] for x in request_list])
            # construct a state
            new_state = State(y_id, set(request_list), self.__profit[y_id], y_cost)
            if y_id not in self.__rest:
                self.__rest[y_id] = [new_state]
            else:
                self.__rest[y_id].append(new_state)

    # next state