# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# solvers.py, created: 2020.09.22    #
# Last Modified: 2020.10.20          #
# ################################## #

from typing import *
import time
from NRP import NextReleaseProblem, ProblemType
from moipProb import MOIPProblem
# from naiveSol import NaiveSol
from moipSol import BaseSol
# from cwmoipSol import CwmoipSol
from altSol import NaiveSol, CwmoipSol
from ncgopSol import NcgopSol
from config import *

from JNRP import JNRP
from jmetal.core.solution import BinarySolution
from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.algorithm.multiobjective.ibea import IBEA
from jmetal.algorithm.multiobjective.hype import HYPE
from jmetal.algorithm.multiobjective.spea2 import SPEA2
from jmetal.operator import BitFlipMutation, SPXCrossover
from jmetal.util.termination_criterion import TerminationCriterion, StoppingByEvaluations
from jmetal.util.archive import NonDominatedSolutionsArchive

# termination criterion by solution update
class Terminator(TerminationCriterion):
    # initialize
    def __init__(self, tolerance, max_evaluation):
        super().__init__()
        # store the parameters
        self.max_evaluation = max_evaluation
        # self.timeout = timeout
        self.tolerance = tolerance
        # prepare members
        self.evaluations = 0
        # self.seconds = 0.0
        self.counter = 0
        self.front = NonDominatedSolutionsArchive()
        self.last_violation = None
        self.last_front_size = None

    # check violation
    def violation_count(self, solutions):
        count = 0
        for solution in solutions:
            if not all([c >= 0.0 for c in solution.constraints]):
                count += 1
        return count

    # update the front
    def update_front(self, solutions):
        new_solution_num = 0
        for solution in solutions:
            # solution.objectives = [round(o, 0) for o in solution.objectives]
            if self.front.add(solution):
                new_solution_num += 1
        return new_solution_num

    # update
    def update(self, *args, **kwargs):
        self.evaluations = kwargs['EVALUATIONS']
        if self.evaluations % 500 == 0:
            print(self.evaluations)
        # self.seconds = kwargs['COMPUTING_TIME']
        solutions = kwargs['SOLUTIONS']
        # check 
        front_size = self.update_front(solutions)
        violation = self.violation_count(solutions)
        if self.last_front_size == self.front.size() and self.last_violation == violation:
            self.counter += 1
        else:
            self.counter = 0
        # update
        self.last_front_size = self.front.size()
        self.last_violation = violation
        print('counter: ', self.counter, ' front_size: ', self.front.size(), ' violation: ', violation)
        # print(self.violation_count(solutions))

    # finish condition
    @property
    def is_met(self):
        # if self.evaluations >= self.max_evaluation:
        #     return True
        # return self.seconds >= self.timeout or self.counter >= self.tolerance
        return self.front.size() == POPULATION_SIZE and self.counter >= self.tolerance

# construct a wrapper for solvers
class Solver:
    # initialize
    def __init__(self, method : str, option : Dict[str, Any] = None):
        # check method
        assert method in SOLVING_METHOD
        # record method
        self.__method = method
        # record the problem
        self.__problem = None
        # employ the solver
        self.__solver = None
        # save option
        self.__option = option

    # load problem
    def load(self, problem : ProblemType) -> None:
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
        # elif self.__method == 'IBEA':
        #     self.__IBEA()
        elif self.__method == 'HYPE':
            self.__HYPE()
        elif self.__method == 'SPEA2':
            self.__SPEA2()

    # execute
    def execute(self) -> Set[Any]:
        if self.__method in DEFAULT_METHOD :
            self.__solver.prepare()
            self.__solver.execute()
        elif self.__method in MOEA_METHOD:
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
        if self.__method in DEFAULT_METHOD:
            return self.__solver.cplexParetoSet
        elif self.__method in MOEA_METHOD:
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
        assert 'mutation' in self.__option
        assert 'crossover' in self.__option
        assert 'max_evaluation' in self.__option
        assert 'tolerance' in self.__option
        self.__solver = NSGAII(
            problem=self.__problem,
            population_size=POPULATION_SIZE,
            offspring_population_size=OFFSPRING_SIZE,
            # mutation=BitFlipMutation(probability=1.0/self.__problem.number_of_variables),
            mutation=BitFlipMutation(probability=self.__option['mutation']),
            crossover=SPXCrossover(probability=self.__option['crossover']),
            termination_criterion=StoppingByEvaluations(max_evaluations=MAX_EVALUATION)
            # termination_criterion=Terminator(max_evaluation=self.__option['max_evaluation'], tolerance=self.__option['tolerance'])
        )

    # wrap IBEA
    # NOTE: IBEA could hardly handle constraints
    # def __IBEA(self) -> None:
    #     self.__solver = IBEA(
    #         problem=self.__problem,
    #         kappa=1.,
    #         population_size=POPULATION_SIZE,
    #         offspring_population_size=OFFSPRING_SIZE,
    #         mutation=BitFlipMutation(probability=1.0/self.__problem.number_of_variables),
    #         crossover=SPXCrossover(probability=1.0),
    #         termination_criterion=StoppingByEvaluations(max_evaluations=MAX_EVALUATION)
    #     )

    # wrap HYPE
    def __HYPE(self) -> None:
        reference_point = BinarySolution(self.__problem.number_of_variables, self.__problem.number_of_objectives, self.__problem.number_of_constraints)
        reference_point.objectives = [1.0 for _ in range(self.__problem.number_of_objectives)]
        self.__solver = HYPE(
            problem=self.__problem,
            reference_point=reference_point,
            population_size=POPULATION_SIZE,
            offspring_population_size=OFFSPRING_SIZE,
            #mutation=BitFlipMutation(probability=1.0/self.__problem.number_of_variables),
            mutation=BitFlipMutation(probability=0.035),
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