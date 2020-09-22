# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# solvers.py, created: 2020.09.22    #
# Last Modified: 2020.09.22          #
# ################################## #

from typing import *
import time
from NRP import NextReleaseProblem
from moipProb import MOIPProblem
from naiveSol import NaiveSol
from moipSol import BaseSol
from config import *

SolverType = Union[BaseSol, NaiveSol]

# construct a wrapper for solvers
class Solver:
    # initialize
    def __init__(self, method : str):
        # check method
        assert method in SOLVING_METHOD
        # record method
        self.__method = method
        # record the problem
        self.__problem = None
        # employ the solver
        self.__solver = None
    
    # load problem
    def load(self, problem : MOIPProblem) -> None:
        # load problem
        assert problem
        self.__problem = problem
        # initialize solver
        if self.__method == 'single':
            self.__BaseSol()
        elif self.__method == 'epsilon':
            self.__NaiveSol()

    # execute
    def execute(self) -> Set[Any]:
        if self.__method == 'single':
            self.__BaseSol_prepare()
            self.__BaseSol_execute()
        elif self.__method == 'epsilon':
            self.__NaiveSol_prepare()
            self.__NaiveSol_execute()
        return self.solutions()
    
    # get results
    def solutions(self) -> Set[Any]:
        return self.__solver.cplexParetoSet

    # wrap BaseSol
    # initialize
    def __BaseSol(self) -> None:
        self.__solver = BaseSol(self.__problem)
    # prepare
    def __BaseSol_prepare(self) -> None:
        self.__solver.prepare()
    # execute
    def __BaseSol_execute(self) -> None:
        self.__solver.execute()

    # wrap NaiveSol
    # initialize
    def __NaiveSol(self) -> None:
        self.__solver = NaiveSol(self.__problem)
    # prepare
    def __NaiveSol_prepare(self) -> None:
        self.__solver.prepare()
    # execute
    def __NaiveSol_execute(self) -> None:
        self.__solver.execute()
