# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# loaders.py, created: 2020.08.31    #
# Last Modified: 2020.09.01          #
# ################################## #

from typing import *
from config import *
from functools import reduce
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

    # find all dependened requirement
    def __all_precursors(self, req_id : int) -> Set[int]:
        # find all dependency with right value as req_id
        one_level = set([x[0] for x in self.__dependencies if x[1] == req_id])
        # check result length
        if len(one_level) == 0:
            return one_level
        elif len(one_level) == 1:
            return one_level.union(self.__all_precursors(list(one_level)[0]))
        else:
            # find their dependecies each and merge their result
            # then convert then into set for dupicate elimination
            return one_level.union(set(reduce(lambda x, y: list(x)+list(y), map(self.__all_precursors, one_level))))

    # sub function of flatten check
    def __flatten_check_sub(self, c_id : int, r_id : int, neo_requirements : List[Tuple[int, int]]) -> bool:
        next_level = set()
        for dep in self.__dependencies:
            if dep[1] == r_id:
                next_level.add(dep[0])
                if (c_id, dep[0]) not in neo_requirements:
                    print(str((c_id, dep[0])) + " is not in new requirements")
                    return False
        if next_level:
            for n_r in next_level:
                if not self.__flatten_check_sub(c_id, n_r, neo_requirements):
                    return False
        return True

    # check if there a precursor named as target id
    def __is_your_precursor(self, r_id : int, target : int) -> bool:
        if (target, r_id) in self.__dependencies or r_id == target:
            return True
        else:
            for dep in self.__dependencies:
                if not dep[1] == r_id:
                    continue
                if self.__is_your_precursor(dep[0], target):
                    return True
            return False

    # check if customer require this requirement
    def __is_your_requirement(self, c_id : int, r_id : int) -> bool:
        if (c_id, r_id) in self.__requirements:
            return True
        for req in self.__requirements:
            if req[0] == c_id and self.__is_your_precursor(req[1], r_id):
                return True
        return False

    # check if dependency is correctly converted
    def __flatten_check(self, neo_requirements : List[Tuple[int, int]]) -> bool:
        # self.req => neo_req
        for req in self.__requirements:
            c_id = req[0]
            r_id = req[1]
            if req not in neo_requirements:
                print("old requirement missed")
                return False
            if not self.__flatten_check_sub(c_id, r_id, neo_requirements):
                return False
        # neo_req => self.req
        for req in neo_requirements:
            if not self.__is_your_requirement(req[0], req[1]):
                return False
        return True
            

    # eliminate requirement level dependency
    # after this process, there should be only one level
    def flatten(self) -> None:
        assert self.__dependencies
        # employ another list to record the temporary requirements
        neo_requirements = deepcopy(self.__requirements)
        # traverse requirement pair
        for req in self.__requirements:
            customer_id = req[0]
            # find all real requirements
            dependecies = list(self.__all_precursors(req[1]))
            # add into requirements
            for dep in dependecies:
                if (customer_id, dep) not in neo_requirements:
                    neo_requirements.append((customer_id, dep))
        # self check
        # print(self.__requirements)
        # print(self.__dependencies)
        # print(neo_requirements)
        assert self.__flatten_check(neo_requirements)
        # 毋忘在莒
        self.__requirements = neo_requirements
        self.__dependencies : List[Tuple[int, int]]  = []

    # convert to MOIPProbelm Format
    def to_MOIP(self) -> MOIPProblem:
        pass # TODO:
        
# just a main for testing
if __name__ == '__main__':
    pass
    # l1 = XuanLoader()
    # classic_1 = os.path.join(CLASSIC_NRP_PATH, CLASSIC_NRPS[0])
    # l1.load(classic_1)
    # nrp = NextReleaseProblem()
    # nrp.construct_from_XuanLoader(l1)
    # nrp.flatten()
    # res = nrp.content()
    # print(res[0])
    # print(res[1])
    # print(res[2])
    # print(res[3])
