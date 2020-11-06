#
# DONG Shi, dongshi@mail.ustc.edu.cn
# EConstraint.py, created: 2020.11.02
# last modified: 2020.11.06
#

import math
from typing import Dict, List, Any, Tuple, Set
import numpy as np
from src.Solvers.BaseSolver import BaseSolver
from src.util.moipProb import MOIPProblem
from src.Solvers.ABCSolver import ABCSolver


class EConstraint(ABCSolver):
    def __init__(self, problem: MOIPProblem) -> None:
        """__init__ [summary] define members and add constraints,
        variables (from problem)into solver

        The method short for epsilon-constraint, mentioned in
        An Integer Linear Programming approach to the single
        and bi-objective Next Release Problem, NadarajenVeerapen
        https://doi.org/10.1016/j.infsof.2015.03.008

        Args:
            problem (MOIPProblem): [description] moip (p)roblem
        """
        # store the problem
        self.problem: MOIPProblem = problem
        # solver
        self.solver: BaseSolver = BaseSolver(problem)
        # solutions
        self.__solutions: Dict[Any, Any] = {}

        # boundary of objectives
        self.low: List[Any] = []
        self.up: List[Any] = []

    def calculte_boundary(self, obj: List[Any]) -> Tuple[Any, Any]:
        """calculte_boundary [summary] calculate
        the boundary of the objective

        Args:
            obj (List[Any]): [description] objective

        Returns:
            [type]: [description] lower bound, upper bound
        """
        ub = 0.0
        lb = 0.0
        for value in obj:
            if value > 0:
                ub = ub + value
            else:
                lb = lb + value
        return lb, ub

    def recuse(self, level: int,
               low: List[Any], up: List[Any]) -> Dict[str, Any]:
        """recuse [summary] recusively execute

        Args:
            level (int): [description] current objective
            low (List[Any]): [description] lower bound of each objective
            up (List[Any]): [description] upper bound of each objective

        Returns:
            Dict[str, Any]: [description] results found so far through this
            search path
        """
        if level == 0:
            # solve
            return self.solver.solve()
        else:
            # prepare all solutions set
            all_solutions: Dict[str, Any] = dict()
            # get the up and low bound
            relaxed_up = math.ceil(up[level])
            relaxed_low = math.ceil(low[level])
            constraint_name = 'obj_' + str(level)
            for rhs in range(relaxed_up, relaxed_low - 1, -1):
                # update rhs
                self.solver.set_rhs(constraint_name, rhs)
                solutions = self.recuse(level - 1, low, up)
                all_solutions = {**all_solutions, **solutions}
            # end for
            return all_solutions

    def prepare(self) -> None:
        """prepare [summary] set objective and
        additional constraints
        """
        # prepare attribute and variable num
        objectives = self.problem.objectiveSparseMapList
        attribute = self.problem.attributeMatrix
        attribute_np = np.array(attribute)
        k = len(attribute)
        # calculate other boundraies
        self.low = [.0] * k
        self.up = [.0] * k
        for i in range(1, k):
            self.low[i], self.up[i] = self.calculte_boundary(attribute[i])
        # prepare the objective
        only_objective = attribute_np[0].tolist()
        self.solver.set_objective(only_objective, True)
        # prepare other objective's constraint
        obj_cst: Dict[str, Dict[Any, Any]] = dict()
        for i in range(1, k):
            obj_cst['obj_' + str(i)] = objectives[i]
        self.solver.add_constriants(obj_cst)

    def execute(self) -> None:
        """execute [summary] execute the algorithm
        """
        # solver
        k = len(self.problem.attributeMatrix)
        self.__solutions = self.recuse(k - 1, self.low, self.up)
        # build pareto
        self.solver.build_pareto()

    def solutions(self) -> Set[Any]:
        """solutions [summary] get solutions

        Returns:
            Any: [description] solutions
        """
        return self.solver.get_pareto()

    def variables(self) -> Set[Any]:
        """variables [summary] get variables

        Returns:
            Set[Any]: [description] variables
        """
        variables = set()
        for solution in self.__solutions.values():
            solution_var = tuple([int(x) for x in solution])
            variables.add(solution_var)
        return variables
