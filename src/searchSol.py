# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# searchSol.py, created: 2020.10.18  #
# Last Modified: 2020.10.19          #
# ################################## #

from sortedcontainers import SortedList
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

    def __hash__(self):
        return hash((self.y, hash(tuple(self.x)), self.p, self.c))

    def __eq__(self, other):
        return  self.y == other.y \
            and self.p == other.p \
            and self.c == other.c \
            and self.x == other.x

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
        # rest y set, manage states as p order
        self.__rest = dict()
        self.__rest_min = None
        # history visited state
        self.__history = set()
        # pareto front, ordered by sum profit
        self.__pareto = dict()
        # current selecting ys
        self.ys = SortedList()
        # current profit of all
        self.yp = 0
        # current cost of all
        self.yc = 0

        # make y rest set
        self.init_rest()

    # make y rest set
    def init_rest(self) -> None:
        # gathering the request by y
        y_request = dict()
        for request in self.__requests:
            if request[0] not in y_request:
                y_request[request[0]] = [request[1]]
            else:
                y_request[request[0]].append(request[1])
        # use gathered request to construct self.rest
        # prepare a tmp rest and rest_min
        rest = dict()
        profit_set = set()
        # traverse all requests
        for y_id, request_list in y_request.items():
            # calculate cost of y
            y_cost = sum([self.__cost[x] for x in request_list])
            # get the profit of y
            y_profit = self.__profit[y_id]
            profit_set.add(y_profit)
            # construct a state
            new_state = State(y_id, set(request_list), y_profit, y_cost)
            if y_id not in rest:
                rest[y_profit] = {new_state}
            else:
                rest[y_profit].add(new_state)
        # ordered y_profit and add to self.rest
        profit_order = sorted(list(profit_set), reverse=True)
        # add to self.rest with profit from big to small
        for y_profit in profit_order:
            self.__rest[y_profit] = rest[y_profit]
        # find the max profit min cost state
        max_profit = profit_order[0]
        self.__rest_min = min(self.__rest[max_profit], key=lambda x : x.c)
        # remove it from rest
        self.__rest[max_profit].remove(self.__rest_min)

    # pick a state
    def pick_state(self) -> State:
        # pick max profit and min cost state
        max_profit = next(iter(self.__rest))
        choosen = self.__rest_min[max_profit]
        # update rest and rest min


    # next state
    def next_state(self) -> None:
        # pick a state as next state
        pass

    # execute
    def execute(self) -> None:
        pass

    # DFS search
    def DFS(self, ) -> None:
        pass