# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# NRP.py, created: 2020.09.19        #
# Last Modified: 2020.09.21          #
# ################################## #

from typing import *
from config import *
from loaders import Loader
from moipProb import MOIPProblem
from copy import deepcopy
from functools import reduce

# Type 
CostType = Union[Dict[int, int], Dict[Tuple[int, int], int]]
ProfitType = Union[Dict[int, int], Dict[Tuple[int, int], int]]
DependenciesType = List[Tuple[int, int]]
RequestsType = List[Tuple[int, int]]
NRPType = Tuple[CostType, ProfitType, DependenciesType, RequestsType]

# describe a class provide an "universal" class 
# for recording next release problem
class NextReleaseProblem:
    # initialize
    def __init__(self, project_name : str):
        # prepare member variables
        self.__project : str = project_name;
        # profit, note that could be  requirement -> cost, customer -> cost
        # and even (requirement, customer/team) -> cost
        self.__cost : CostType = dict()
        # profit, note that could be customer -> profit, requirement -> profit
        # and even (requirement, customer/team) -> profit
        self.__profit : ProfitType = dict()
        # depdencies, describe dependencies among requirements
        # (x_i, x_j) denotes x_i -> x_j, x_i is precursor of x_j
        self.__dependencies : DependenciesType = []
        # request, customer -> requirement or team -> requirement
        self.__requests : RequestsType = []
        # load from file
        self.__load(project_name)
        # inventory
        assert self.inventory() == self.pattern()

    # load from file
    def __load(self, project_name : str) -> None:
        # employ a loader
        loader = Loader(project_name)
        self.__cost, self.__profit, self.__dependencies, self.__requests = loader.load()

    # check member variables status
    def inventory(self) -> Dict[str, str]:
        stats = dict()
        # check cost type
        assert self.__cost
        assert isinstance(self.__cost, dict)
        if isinstance(list(self.__cost.keys())[0], int):
            stats['cost'] = 'int'
        elif isinstance(list(self.__cost.keys())[0], tuple):
            assert len(list(self.__cost.keys())[0]) == 2
            stats['cost'] = 'tuple'
        else:
            assert False
        # check profit type
        assert self.__profit
        assert isinstance(self.__profit, dict)
        if isinstance(list(self.__profit.keys())[0], int):
            stats['profit'] = 'int'
        elif isinstance(list(self.__profit.keys())[0], tuple):
            assert len(list(self.__profit.keys())[0]) == 2
            stats['profit'] = 'tuple'
        else:
            assert False
        # check denpendencies
        if self.__dependencies:
            assert isinstance(self.__dependencies, list)
            assert isinstance(self.__dependencies[0], tuple)
            assert len(self.__dependencies[0]) == 2
            stats['dependencies'] = 'tuple'
        else:
            stats['dependencies'] = 'empty'
        # check requests
        if self.__requests:
            assert isinstance(self.__requests, list)
            assert isinstance(self.__requests[0], tuple)
            assert len(self.__requests[0]) == 2
            stats['requests'] = 'tuple'
        else:
            stats['requests'] = 'empty'
        # return
        return stats
    
    # what kind of pattern should a project has
    # compare with inventory
    def pattern(self) -> Dict[str, str]:
        if self.__project.startswith('classic'):
            return  {'cost':'int', 'profit':'int', 'dependencies':'tuple', 'requests':'tuple'}
        elif self.__project.startswith('realistic'):
            return {'cost':'int', 'profit':'int', 'dependencies':'empty', 'requests':'tuple'}
        elif self.__project.startswith('Motorola'):
            return {'cost':'int', 'profit':'int', 'dependencies':'empty', 'requests':'empty'}
        elif self.__project.startswith('RALIC'):
            return {'cost':'int', 'profit':'tuple', 'dependencies':'empty', 'requests':'empty'}
        elif self.__project.startswith('Baan'):
            return {'cost': 'tuple', 'profit':'int', 'dependencies':'empty', 'requests':'empty'}
        else:
            return None

    # get the content of NRP
    def content(self) -> NRPType:
        return self.__cost, self.__profit, self.__dependencies, self.__requests

    # find one requirement all precursors
    def __precursors(self, req_id : int) -> Set[int]:
        # find all depdency with right value as requst id input
        last_level = set([x[0] for x in self.__dependencies if x[1] == req_id])
        # check result
        if len(last_level) == 0:
            return last_level
        else:
            # find their dependecies each and merge their result
            # then convert then into set for dupicate elimination
            return last_level.union(set(reduce(lambda x, y: list(x)+list(y), map(self.__precursors, last_level))))

    # flatten dependencies, eliminate all dependencies between requirements
    def flatten(self) -> None:
        # of course depdencies should not be empty
        assert self.__dependencies
        # copy a new requests from self.requests
        neo_requests = deepcopy(self.__requests)
        # traverse requests
        for req in self.__requests:
            # find all real requests
            dependencies = list(self.__precursors(req[1]))
            # add into new requests
            for dep in dependencies:
                if (req[0], dep) not in neo_requests:
                    neo_requests.append((req[0], dep))
        # change requests and clear dependencies
        self.__requests = neo_requests
        self.__dependencies.clear()

    # moudling, convert NRP to certain MOIPProblem
    def mould(self, form : str) -> MOIPProblem:
        pass
        