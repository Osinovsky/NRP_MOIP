# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# loaders.py, created: 2020.09.19    #
# Last Modified: 2020.09.19          #
# ################################## #

from typing import *
from config import *
from functools import reduce
from loaders import Loader
from copy import deepcopy
import os
from moipProb import MOIPProblem 

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
        # load from file, TODO:

    # load from file
    @staticmethod
    def __load(self, project_name : str):
        # TODO:
        pass
        