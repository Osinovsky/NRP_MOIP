# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# loaders.py, created: 2020.08.31    #
# Last Modified: 2020.09.03          #
# ################################## #

from typing import *
from config import *
from functools import reduce
from loaders import XuanLoader, MotorolaLoader, RALICLoader
from copy import deepcopy
import os
from moipProb import MOIPProblem 

# Type 
NRPContent = Tuple[Dict[int, int], Dict[int, int], List[Tuple[int, int]], List[Tuple[int, int]]]

# describe a class provide an universe class 
# for recording next release problem
class NextReleaseProblem:
    # initialize
    def __init__(self):
        # requirement cost, requirement -> cost
        self.__cost : Dict[int, int] = dict()
        # customer profit, customer -> profit
        self.__profit : Dict[int, int] = dict()
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
    def content(self) -> NRPContent:
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
                # we convert cost as a int for generalizing
                self.__cost[cost_pair[0]] = int(cost_pair[1])
        # then, the customers' profit and the requirement pair list
        for customer in customers:
            # parse the tuple
            customer_id = customer[0]
            customer_requirement = customer[2]
            # add profit into self profit
            assert customer_id not in self.__profit
            self.__profit[customer_id] = int(customer[1])
            # construct (requirer, requiree) pairs and store
            assert customer_requirement # non-empty check
            for req in customer_requirement:
                self.__requirements.append(tuple((customer_id, req)))
        # now we copy the dependencies
        self.__dependencies = deepcopy(dependencies)
        # don't forget have a check of all member
        # assert self.__check()

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
        # assert self.__flatten_check(neo_requirements)
        # 毋忘在莒
        self.__requirements = neo_requirements
        self.__dependencies : List[Tuple[int, int]]  = []

    # compact encoding check
    def __if_compact_encoding(self, l : List[int]) -> bool:
        return (max(l)-min(l)+1) == len(l)

    # compact encoding check
    def __unique_and_compact_reenconde_check(self,  \
        neo_content : NRPContent,                   \
        customer_rename : Dict[int, int],           \
        requirement_rename : Dict[int, int]) -> bool:
        # unpack the neo_content
        neo_cost : Dict[int, int] = neo_content[0]
        neo_profit : Dict[int, int] = neo_content[1]
        neo_dependencies : List[Tuple[int, int]] = neo_content[2]
        neo_requirements : List[Tuple[int, int]] = neo_content[3]
        # check if compact
        if not self.__if_compact_encoding(list(neo_cost.keys())+list(neo_profit.keys())):
            print("encoding is not compact")
            return False
        # check rename if one-to-one mapping
        if not len(customer_rename.keys()) == len(set(customer_rename.values())):
            print("customner rename dict is not a one-to-one mapping")
            return False
        if not len(requirement_rename.keys()) == len(set(requirement_rename.values())):
            print("requirement rename dict is not a one-to-one mapping")
            return False
        # check length
        if not len(neo_cost) == len(self.__cost):
            print("cost length not match")
            return False
        if not len(neo_profit) == len(self.__profit):
            print("profit length not match")
            return False
        if not len(neo_dependencies) == len(self.__dependencies):
            print("dependencies length not match")
            return False
        if not len(neo_requirements) == len(self.__requirements):
            print("requirements length not match")
            return False
        # check rename correctness
        # profit
        for old_id, new_id in customer_rename.items():
            if abs(self.__profit[old_id] - neo_profit[new_id]) > 1e-6:
                print("profit not match")
                return False
        # cost
        for old_id, new_id in requirement_rename.items():
            if abs(self.__cost[old_id] - neo_cost[new_id]) > 1e-6:
                print("cost not match")
                return False
        # dependency
        for old_left, new_left in requirement_rename.items():
            for old_right, new_right in requirement_rename.items():
                if not (((old_left, old_right) in self.__dependencies) == ((new_left, new_right) in neo_dependencies)):
                    print("dependency not match")
                    return False
        # requirements
        for old_left, new_left in customer_rename.items():
            for old_right, new_right in requirement_rename.items():
                if not (((old_left, old_right) in self.__requirements) == ((new_left, new_right) in neo_requirements)):
                    print("requirement not match")
                    return False
        # till here, all passed
        return True

    # re-encode the customer and requirement 
    # after this, each customer and requirement has unique encoding
    # note that, no customer id and requirement id is same
    # ... and there won't be a number smaller than a certain id but is not used(>=1)
    # if customer_first then c_1, ..., c_m, r_m+1, ..., r_m+n
    # else r_1, ..., r_n, c_n+1, ..., c_n+m
    def unique_and_compact_reenconde(self, customer_first : bool) -> NRPContent:
        # rename map record
        customer_rename : Dict[int, int] = {}
        requirement_rename : Dict[int, int] = {}
        # prepare an encoder first, from 1
        encoder = 1
        # clearify the order
        if customer_first:
            # re-encode the customers
            for c_id, _ in self.__profit.items():
                customer_rename[c_id] = encoder
                encoder += 1
            # re-encode the requirements
            for r_id, _ in self.__cost.items():
                requirement_rename[r_id] = encoder
                encoder += 1
        else:
            # re-encode the requirements
            for r_id, _ in self.__cost.items():
                requirement_rename[r_id] = encoder
                encoder += 1
            # re-encode the customers
            for c_id, _ in self.__profit.items():
                customer_rename[c_id] = encoder
                encoder += 1
        # self check
        # rename
        neo_cost : Dict[int, int] = \
            {requirement_rename[x[0]]:x[1] for x in self.__cost.items()}
        neo_profit : Dict[int, int] = \
            {customer_rename[x[0]]:x[1] for x in self.__profit.items()}
        neo_dependencies : List[Tuple[int, int]] = \
            [tuple((requirement_rename[x[0]], requirement_rename[x[1]])) for x in self.__dependencies]
        neo_requirements : List[Tuple[int, int]] = \
            [tuple((customer_rename[x[0]], requirement_rename[x[1]])) for x in self.__requirements]
        # pack up
        neo_content = tuple((neo_cost, neo_profit, neo_dependencies, neo_requirements))
        # check
        # assert self.__unique_and_compact_reenconde_check(neo_content, customer_rename, requirement_rename)
        return neo_content

    # convert to MOIPProbelm general Format TODO: return value
    def to_general_MOIP(self, b : float):
        # requirement dependencies should be eliminated
        assert not self.__dependencies
        # prepare the "variables"
        neo_content = self.unique_and_compact_reenconde(True) # customer + requirement
        neo_cost, neo_profit, neo_dependencies, neo_requirements = neo_content
        # prepare variables
        variables = neo_profit.keys() + neo_cost.keys()
        # prepare objective coefs
        objectives : List[Dict[int, int]] = [neo_profit]
        # prepare the atrribute matrix
        inequations : List[Dict[int, int]] = []
        inequations_operators : List[str] = []
        # don't forget encode the constant, it always be MAX_CODE + 1
        constant_id = len(variables)
        assert constant_id not in neo_cost.keys()
        assert constant_id not in neo_profit.keys()
        # convert requirements
        # use requirements, y <= x
        for req in neo_requirements:
            # custom req[0] need requirement req[1]
            # req[0] <= req[1] <=> req[0] - req[1] <= 0
            inequations.append({req[0]:1, req[1]:-1, constant_id:0})
            # 'L' for <= and 'G' for >=, we can just convert every inequations into <= format
            inequations_operators.append('L')
        # use sum cost_i x_i < b sum(cost)
        cost_sum = sum(neo_cost.values())
        tmp_inequation = neo_cost
        tmp_inequation[constant_id] = int(cost_sum * b)
        inequations.append(tmp_inequation)
        inequations_operators.append('L')
        # TODO: 0 <= x, y <= 1
        # construct Problem 
        # return NextReleaseProblem.to_MOIP(variables, objectives, inequations, inequations_operators)
    
    # to MOIP, construct from some already content
    # @staticmethod
    # def to_MOIP(variables : List[int], \
    #     objectives : List[Dict[int, int]], \
    #     inequations : List[Dict[int, int]], \
    #     inequations_operators : List[str] \
    # ) -> MOIPProblem:
    #     # construct MOIP
    #     MOIP = MOIPProblem(len(objectives), len(variables), 0)
    #     # use objectives make attribute matrix
    #     for objective in objectives:
    #         line = [0] * (len(variables)+1)
    #         for key, value in objective.items():
    #             line[key] = value
    #         # now the constant, constant id is MAX_VARIABLE_ID + 1
    #         if len(variables) in objective:
    #             line[len(variables)] = objective[len(variables)]
        # TODO: convert to MOIP

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
    # lets run all Xuan datasets
    # classic instances
    for classic_nrp in CLASSIC_NRPS:
        print("start " + classic_nrp)
        loader = XuanLoader()
        file_name = os.path.join(CLASSIC_NRP_PATH, classic_nrp)
        loader.load(file_name)
        nrp = NextReleaseProblem()
        nrp.construct_from_XuanLoader(loader)
        nrp.flatten()
        nrp.unique_and_compact_reenconde(True)
        # nrp.to_geneneral_MOIP(0.5)
    # realistic instances
    for realistic_nrp in REALISTIC_NRPS:
        print("start " + realistic_nrp)
        loader = XuanLoader()
        file_name = os.path.join(REALISTIC_NRP_PATH, realistic_nrp)
        loader.load(file_name)
        nrp = NextReleaseProblem()
        nrp.construct_from_XuanLoader(loader)
        # nrp.flatten()
        nrp.unique_and_compact_reenconde(True)
        # nrp.to_geneneral_MOIP(0.5)