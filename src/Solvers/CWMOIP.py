#
# DONG Shi, dongshi@mail.ustc.edu.cn
# CWMOIP.py, created: 2020.11.04
# last modified: 2020.11.04
#

import math
import numpy as np
from decimal import Decimal
from typing import List, Any, Tuple, Dict, Set
from src.Solvers.BaseSolver import BaseSolver
from src.util.moipProb import MOIPProblem
from src.util.mooUtility import MOOUtility
from src.Solvers.ABCSolver import ABCSolver


class CWMOIP(ABCSolver):
    def __init__(self, problem: MOIPProblem) -> None:
        """__init__ [summary] define members and add constraints,
        variables (from problem)into solver

        The method is just named as CWMOIP(), mentionend in
        Multi-Objective Integer Programming Approaches for Solving
        Optimal Feature Selection Problem, Yinxing Xue, Yan-Fu Li
        https://doi.org/10.1145/3180155.3180257

        Args:
            problem (MOIPProblem): [description] moip (p)roblem
        """
        # store the problem
        self.problem: MOIPProblem = problem
        # solver
        self.solver: BaseSolver = BaseSolver(problem)
        # boundary solver
        self.boundary_solver: BaseSolver = BaseSolver(problem)

        # true boundary of objectives
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
        # set minimize tag for lower boundary
        self.boundary_solver.set_objective(obj, minimize=False)
        self.boundary_solver.solve()
        low = self.boundary_solver.get_objective_value()
        # set maximize tag for upper boundary
        self.boundary_solver.set_objective(obj, minimize=True)
        self.boundary_solver.solve()
        up = self.boundary_solver.get_objective_value()
        # return
        return low, up

    def next_rhs(self, objective: List[Any], solutions: Dict[str, Any]) -> int:
        """next_rhs [summary] calculate maax value on this objective

        Args:
            objective (List[Any]): [description] current objective
            solutions (Dict[str, Any]): [description] solutions we found

        Returns:
            int: [description] next rhs
        """
        values = [float("-inf")]
        array1 = np.array(objective)
        for key in solutions:
            new_solution = solutions[key]
            array2 = np.array(new_solution)
            values.append(float(np.dot(array1, array2)))
        result = MOOUtility.round(max(values))
        return result - 1

    def recuse(self, level: int,
               up: List[Any],
               attribute: List[List[Any]]) -> Dict[str, Any]:
        """recuse [summary] recusively execute

        Args:
            level (int): [description] current objective
            up (List[Any]): [description] upper bound of each objective
            attribute (List[List[Any]]): [description] original objectives

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
            # get the up bound
            rhs = math.ceil(up[level])
            constraint_name = 'obj_' + str(level)
            while True:
                # update rhs
                self.solver.set_rhs(constraint_name, rhs)
                solutions = self.recuse(level - 1, up, attribute)
                # cannot find solutions anymore
                if not solutions:
                    break
                # update next rhs
                rhs = self.next_rhs(attribute[level], solutions)
                # update solutions
                all_solutions = {**all_solutions, **solutions}
            # end while
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
        # calculate weights
        w = Decimal(1.0)
        only_objective = attribute_np[0]
        for i in range(1, k):
            w = w / Decimal(MOOUtility.round(self.up[i] - self.low[i] + 1.0))
            only_objective = only_objective + float(w) * attribute_np[1]
        # set objective
        self.solver.set_objective(only_objective.tolist(), True)
        # prepare other objective's constraint
        obj_cst: Dict[str, Dict[Any, Any]] = dict()
        for i in range(1, k):
            obj_cst['obj_' + str(i)] = objectives[i]
        self.solver.add_constriants(obj_cst)

    def execute(self):
        """execute [summary] execute the algorithm
        """
        # solver
        k = len(self.problem.attributeMatrix)
        self.recuse(k - 1, self.low, self.problem.attributeMatrix)
        # build pareto
        self.solver.build_pareto()

    def solutions(self) -> Set[Any]:
        """solutions [summary] get solutions

        Returns:
            Any: [description] solutions
        """
        return self.solver.get_pareto()