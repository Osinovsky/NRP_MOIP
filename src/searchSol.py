# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# searchSol.py, created: 2020.10.18  #
# Last Modified: 2020.10.19          #
# ################################## #

from sortedcontainers import SortedList
from typing import Set, List, Tuple
from config import *
from NRP import NextReleaseProblem

NonDominated = 1
Equal = 0
Dominate = -1
Dominated = -2

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

# naive search based solver
class SearchSol:
    # dominate test, return if x dominate y
    # dominate = lambda x, y : x[0] <= y[0] and x[1] <= y[1]

    # initialize 
    def __init__(self, problem):
        # load problem
        self.__cost, self.__profit, _, self.__requests = problem
        # history visited state
        self.__history = set()
        # pareto front, ordered by sum profit
        self.__pareto = dict()

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
        # sort ND and DD
        for y_profit in profit_order:
            pass

    # test dominated
    @staticmethod
    def dominate(left : State, right : State) -> int:
        if left.p > right.p:
            if left.c < right.c:
                return Dominate # (D, D) -> Dominate
            elif left.c > right.c:
                return NonDominated # (D, ND) -> NonDominated
            else:
                return Dominate # (D, E) -> Dominate
        elif left.p < right.p:
            if left.c < right.c:
                return NonDominated # (ND, D) -> NonDominated
            elif left.c > right.c:
                return Dominated # (ND, ND) -> Dominated
            else:
                return Dominated # (ND, E) -> Dominated
        else:
            if left.c < right.c:
                return Dominate # (E, D) -> Dominate
            elif left.c > right.c:
                return Dominated # (E, ND) -> Dominated
            else:
                return Equal # (E, E) -> Equal

    # nd sort, return (ND, DD)
    @staticmethod
    def dominated_sort(input_set : Set[State]) -> Tuple[Set[State], Set[State]]:
        pass