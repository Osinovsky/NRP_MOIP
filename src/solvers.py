# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# solvers.py, created: 2020.09.22    #
# Last Modified: 2020.10.07          #
# ################################## #

from typing import *
import time
from NRP import NextReleaseProblem
from moipProb import MOIPProblem
from naiveSol import NaiveSol
from moipSol import BaseSol
from cwmoipSol import CwmoipSol
from ncgopSol import NcgopSol
from config import *

from JNRP import JNRP
from jmetal.core.solution import BinarySolution
from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.algorithm.multiobjective.ibea import IBEA
from jmetal.algorithm.multiobjective.hype import HYPE
from jmetal.algorithm.multiobjective.spea2 import SPEA2
from jmetal.operator import BitFlipMutation, SPXCrossover
from jmetal.util.termination_criterion import StoppingByEvaluations

Problem = Union[MOIPProblem, JNRP]

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
    def load(self, problem : Problem) -> None:
        # load problem
        assert problem
        self.__problem = problem
        # initialize solver
        if self.__method == 'single':
            self.__BaseSol()
        elif self.__method == 'epsilon':
            self.__NaiveSol()
        elif self.__method == 'cwmoip':
            self.__CwmoipSol()
        elif self.__method == 'ncgop':
            self.__NcgopSol()
        elif self.__method == 'NSGAII':
            self.__NSGAII()
        elif self.__method == 'IBEA':
            self.__IBEA()
        elif self.__method == 'HYPE':
            self.__HYPE()
        elif self.__method == 'SPEA2':
            self.__SPEA2()

    # execute
    def execute(self) -> Set[Any]:
        if self.__method in ['single', 'epsilon', 'cwmoip', 'ncgop']:
            self.__solver.prepare()
            self.__solver.execute()
        elif self.__method in ['NSGAII', 'IBEA', 'HYPE', 'SPEA2']:
            self.__solver.run()
    
    # no negative element in list
    @staticmethod
    def forall_ge0(l : List[int]) -> bool:
        if l:
            return all([e >= 0 for e in l])
        else:
            return True

    # get results
    def solutions(self) -> Set[Any]:
        if self.__method in ['single', 'epsilon', 'cwmoip', 'ncgop']:
            return self.__solver.cplexParetoSet
        elif self.__method in ['NSGAII', 'IBEA', 'HYPE', 'SPEA2']:
            results : List[BinarySolution] = self.__solver.get_result()
            # remove infeasible solution
            return set([tuple(s.objectives) for s in results if Solver.forall_ge0(s.constraints)])

    # get raw results, for MOEA
    def moea_solutions(self) -> Any:
        return self.__solver.get_result()

    # wrap BaseSol
    def __BaseSol(self) -> None:
        self.__solver = BaseSol(self.__problem)

    # wrap NaiveSol
    def __NaiveSol(self) -> None:
        self.__solver = NaiveSol(self.__problem)

    # wrap CwmoipSol Solver
    def __CwmoipSol(self) -> None:
        self.__solver = CwmoipSol(self.__problem)
    
    # wrap NcgopSol Solver
    def __NcgopSol(self) -> None:
        self.__solver = NcgopSol(self.__problem)

    # wrap NSGAII
    def __NSGAII(self) -> None:
        self.__solver = NSGAII(
            problem=self.__problem,
            population_size=POPULATION_SIZE,
            offspring_population_size=OFFSPRING_SIZE,
            mutation=BitFlipMutation(probability=1.0/self.__problem.number_of_variables),
            crossover=SPXCrossover(probability=1.0),
            termination_criterion=StoppingByEvaluations(max_evaluations=MAX_EVALUATION)
        )

    # wrap IBEA
    # NOTE: IBEA could hardly handle constraints
    def __IBEA(self) -> None:
        self.__solver = IBEA(
            problem=self.__problem,
            kappa=1.,
            population_size=POPULATION_SIZE,
            offspring_population_size=OFFSPRING_SIZE,
            mutation=BitFlipMutation(probability=1.0/self.__problem.number_of_variables),
            crossover=SPXCrossover(probability=1.0),
            termination_criterion=StoppingByEvaluations(max_evaluations=MAX_EVALUATION)
        )

    # wrap HYPE
    def __HYPE(self) -> None:
        reference_point = BinarySolution(self.__problem.number_of_variables, self.__problem.number_of_objectives, self.__problem.number_of_constraints)
        reference_point.objectives = [1.0 for _ in range(self.__problem.number_of_objectives)]
        self.__solver = HYPE(
            problem=self.__problem,
            reference_point=reference_point,
            population_size=POPULATION_SIZE,
            offspring_population_size=OFFSPRING_SIZE,
            mutation=BitFlipMutation(probability=1.0/self.__problem.number_of_variables),
            crossover=SPXCrossover(probability=1.0),
            termination_criterion=StoppingByEvaluations(max_evaluations=MAX_EVALUATION)
        )
    
    # wrap SPEA2
    def __SPEA2(self) -> None:
        self.__solver = SPEA2(
            problem=self.__problem,
            population_size=POPULATION_SIZE,
            offspring_population_size=OFFSPRING_SIZE,
            mutation=BitFlipMutation(probability=1.0/self.__problem.number_of_variables),
            crossover=SPXCrossover(probability=1.0),
            termination_criterion=StoppingByEvaluations(max_evaluations=MAX_EVALUATION)
        )
