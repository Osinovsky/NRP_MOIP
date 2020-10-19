# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# searchSol.py, created: 2020.10.18  #
# Last Modified: 2020.10.19          #
# ################################## #

from sortedcontainers import SortedList
from typing import Set, List, Tuple
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
        profit_max = profit_order[0]
        self.__rest_min = min(self.__rest[profit_max], key=lambda x : x.c)
        # remove it from rest
        self.__rest[profit_max].remove(self.__rest_min)
        if not self.__rest[profit_max]:
            del self.__rest[profit_max]

    # pick a state
    def pick_state(self) -> Tuple[State, Set[State]]:
        # just pick rest min as choosen one
        choosen_state = self.__rest_min
        # update the rest
        # prepare extendable state set
        extendable = set()
        # update rest state c and x
        remove_xs = choosen_state.x
        for y_profit in self.__rest:
            tmp_set = set()
            # for each state, x \ remove_xs, cost -= sum cost(remove_xs)
            for state in self.__rest[y_profit]:
                # remove x and update c
                for remove_x in remove_xs:
                    if remove_x in state.x:
                        state.x.remove(remove_x)
                        state.c -= self.__cost[remove_x]
                # end for
                # add to extendable if empty x
                if state.x:
                    extendable.add(state)
                else:
                    tmp_set.add(state)
            # end for
            if tmp_set:
                self.__rest = tmp_set
            else:
                del self.__rest[y_profit]
        # end for
        # pick max profit and min cost state
        profit_max = next(iter(self.__rest))
        # find new rest min
        self.__rest_min = min(self.__rest[profit_max], key=lambda x : x.c)
        # delete from rest
        self.__rest[profit_max].remove(self.__rest_min)
        # return choosen state and extendable
        return (choosen_state, extendable)

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

    # for test methods
    # test rest construct
    def test_rest_init(self) -> None:
        # rest => problem
        last_profit = None
        for y_profit, states in self.__rest.items():
            for state in states:
                assert self.__profit[state.y] == state.p and state.p == y_profit
                assert sum([self.__cost[xx] for xx in state.x]) == state.c
                assert all([(state.y, xx) in self.__requests for xx in state.x])
            # check profit order
            if last_profit:
                assert last_profit > y_profit
            last_profit = y_profit
        # check rest min
        state = self.__rest_min
        assert self.__profit[state.y] == state.p
        assert sum([self.__cost[xx] for xx in state.x]) == state.c
        assert all([(state.y, xx) in self.__requests for xx in state.x])
        # check if rest min is min
        if self.__rest_min.p in self.__rest:
            for state in self.__rest[self.__rest_min.p]:
                assert state.y != self.__rest_min.y
                assert state.c >= self.__rest_min.c

    # test state pick
    def test_state_pick(self, current_state, choosen_state, extendable):
        pass
