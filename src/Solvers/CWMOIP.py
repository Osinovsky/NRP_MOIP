#
# DONG Shi, dongshi@mail.ustc.edu.cn
# CWMOIP.py, created: 2020.11.04
# last modified: 2020.11.24
#

import math
from copy import deepcopy
from decimal import Decimal
from typing import List, Any, Tuple, Dict
from jmetal.core.solution import BinarySolution
from src.NRP import NRPProblem
from src.Solvers.BaseSolver import BaseSolver
from src.Solvers.ABCSolver import ABCSolver
from src.util.mooUtility import MOOUtility


class CWMOIP(ABCSolver):
    def __init__(self, problem: NRPProblem) -> None:
        """__init__ [summary] define members and add constraints,
        variables (from problem)into solver

        The method is just named as CWMOIP(), mentionend in
        Multi-Objective Integer Programming Approaches for Solving
        Optimal Feature Selection Problem, Yinxing Xue, Yan-Fu Li
        https://doi.org/10.1145/3180155.3180257

        Args:
            problem (NRPProblem): [description] nrp (p)roblem
        """
        # store the problem
        self.problem: NRPProblem = problem
        # solver
        self.solver: BaseSolver = BaseSolver(problem)
        # boundary solver
        self.boundary_solver: BaseSolver = BaseSolver(problem)

        # true boundary of objectives
        self.low: List[Any] = []
        self.up: List[Any] = []

    def calculte_boundary(self, obj: Dict[int, Any]) -> Tuple[Any, Any]:
        """calculte_boundary [summary] calculate
        the boundary of the objective

        Args:
            obj (Dict[int, Any]): [description] objective

        Returns:
            [type]: [description] lower bound, upper bound
        """
        # set minimize tag for lower boundary
        self.boundary_solver.set_objective(obj, minimize=True)
        self.boundary_solver.solve()
        low = self.boundary_solver.get_objective_value()
        # set maximize tag for upper boundary
        self.boundary_solver.set_objective(obj, minimize=False)
        self.boundary_solver.solve()
        up = self.boundary_solver.get_objective_value()
        # return
        return low, up

    def next_rhs(self, objective_index: int,
                 solutions: List[BinarySolution]) -> int:
        """next_rhs [summary] calculate max value on this objective

        Args:
            objective_index (int): [description] current objective
            solutions (List[BinarySolution]): [description] solutions we found

        Returns:
            int: [description] next rhs
        """
        return math.floor(max([solution.objectives[objective_index]
                               for solution in solutions]) + 0.5) - 1

    def recuse(self, level: int, up: List[Any]) -> Dict[str, BinarySolution]:
        """recuse [summary] recusively execute

        Args:
            level (int): [description] current objective
            up (List[Any]): [description] upper bound of each objective

        Returns:
            List[BinarySolution]: [description] solutions found so far
        """
        if level == 0:
            # solve
            return self.solver.solve()
        else:
            # prepare all solutions set
            all_solutions: Dict[str, BinarySolution] = {}
            # get the up bound
            rhs = math.ceil(up[level])
            constraint_name = 'obj_' + str(level)
            while True:
                # update rhs
                self.solver.set_rhs(constraint_name, rhs)
                solutions = self.recuse(level - 1, up)
                # cannot find solutions anymore
                if not solutions:
                    break
                # update next rhs
                rhs = self.next_rhs(level, list(solutions.values()))
                # update solutions
                all_solutions = {**all_solutions, **solutions}
            # end while
            return all_solutions

    def prepare(self) -> None:
        """prepare [summary] set objective and
        additional constraints
        """
        # prepare attribute and variable num
        objectives = self.problem.objectives
        k = len(self.problem.objectives)
        # calculate other boundraies
        self.low = [.0] * k
        self.up = [.0] * k
        for i in range(1, k):
            self.low[i], self.up[i] = self.calculte_boundary(objectives[i])
        # calculate weights
        w = Decimal(1.0)
        only_objective = deepcopy(objectives[0])
        for i in range(1, k):
            w = w / Decimal(MOOUtility.round(self.up[i] - self.low[i] + 1.0))
            only_objective = BaseSolver.objective_add(only_objective,
                                                      objectives[i],
                                                      float(w))
        # set objective
        self.solver.set_objective(only_objective, True)
        # prepare other objective's constraint
        obj_cst: Dict[str, Dict[Any, Any]] = dict()
        for i in range(1, k):
            obj_cst['obj_' + str(i)] = objectives[i]
        self.solver.add_constriants(obj_cst)

    def execute(self):
        """execute [summary] execute the algorithm
        """
        # solver
        k = len(self.problem.objectives)
        self.recuse(k - 1, self.up)

    def solutions(self) -> List[Any]:
        """solutions [summary] get solutions

        Returns:
            Any: [description] solutions
        """
        return self.solver.get_objectives()

    def variables(self) -> List[Any]:
        """variables [summary] get variables

        Returns:
            List[Any]: [description] variables
        """
        return self.solver.get_variables()
