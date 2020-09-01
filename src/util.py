# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# loaders.py, created: 2020.08.31    #
# Last Modified: 2020.09.01          #
# ################################## #

from typing import *
from config import *
from loaders import XuanLoader, MotorolaLoader, RALICLoader
from copy import deepcopy
import os
from moipProb import MOIPProblem 

# describe a class provide an universe class 
# for recording next release problem
class NextReleaseProblem:
    # initialize
    def __init__(self):
        # requirement cost, requirement -> cost
        self.__cost : Dict[int, float] = dict()
        # customer profit, customer -> profit
        self.__profit : Dict[int, float] = dict()
        # requirement dependency, requirement -> requirement
        self.__dependencies : List[Tuple[int, int]] = []
        # requirements (customer, requirement)
        self.__requirements : List[Tuple[int, int]] = []

    # self check 
    def __check(self) -> bool :
        # all requirements
        req_list = list(self.__cost.keys())
        # dependency pairs' lefts and rights should be in cost(requirement id)
        for dep in self.__dependencies:
            if dep[0] not in req_list or dep[1] not in req_list:
                print(str(dep) + ' is not a legal dependency')
                return False
        # all customers
        customer_list = list(self.__profit.keys())
        for req in self.__requirements:
            if req[0] not in customer_list:
                print(str(req[0]) + ' is not a legal customer')
                return False
            if req[1] not in req_list:
                print(str(req[1]) + ' is not a legal requirement')
                return False
        # all clear!
        return True

    # content access
    def content(self) -> Tuple[Dict[int, float], Dict[int, float], List[Tuple[int, int]], List[Tuple[int, int]]]:
        return (self.__cost, self.__profit, self.__dependencies, self.__requirements)
    
    # convert from XuanLoader
    def construct_from_XuanLoader(self, loader : XuanLoader) -> None:
        # get the content from loader
        cost, dependencies, customers = loader.content()
        # there are many level in cost, we should collect them up
        for cost_line in cost:
            # iterate each element in this line
            for cost_pair in cost_line:
                # the key should be unique
                assert cost_pair[0] not in self.__cost
                # we convert cost as a float for generalizing
                self.__cost[cost_pair[0]] = float(cost_pair[1])
        # then, the customers' profit and the requirement pair list
        for customer in customers:
            # parse the tuple
            customer_id = customer[0]
            customer_requirement = customer[2]
            # add profit into self profit
            assert customer_id not in self.__profit
            self.__profit[customer_id] = float(customer[1])
            # construct (requirer, requiree) pairs and store
            assert customer_requirement # non-empty check
            for req in customer_requirement:
                self.__requirements.append(tuple((customer_id, req)))
        # now we copy the dependencies
        self.__dependencies = deepcopy(dependencies)
        # don't forget have a check of all member
        assert self.__check()

    # convert to MOIPProbelm Format
    def to_MOIP(self) -> MOIPProblem:
        pass # TODO:
        
# just a main for testing
if __name__ == '__main__':
    pass
    # l1 = XuanLoader()
    # classic_2 = os.path.join(CLASSIC_NRP_PATH, CLASSIC_NRPS[2])
    # l1.load(classic_2)
    # nrp = NextReleaseProblem()
    # nrp.construct_from_XuanLoader(l1)
    # res = nrp.content()
    # print(res[0])
    # print(res[1])
    # print(res[2])
    # print(res[3])
