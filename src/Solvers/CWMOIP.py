#
# DONG Shi, dongshi@mail.ustc.edu.cn
# CWMOIP.py, created: 2020.11.04
# last modified: 2020.12.28
#

from decimal import Decimal
from typing import List, Any, Tuple, Dict
from jmetal.core.solution import BinarySolution
from src.NRP import NRPProblem
from src.Solvers.BaseSolver import BaseSolver
# from src.Solvers.LazyBaseSolver import LazyBaseSolver as BaseSolver
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

    def calculte_boundary(self, obj: Dict[int, Any]) -> Tuple[Any, Any]:
        """calculte_boundary [summary] calculate
        the boundary of the objective

        Args:
            obj (Dict[int, Any]): [description] objective

        Returns:
            [type]: [description] lower bound, upper bound
        """
        # set minimize tag for lower boundary
        self.solver.set_objective(obj, minimize=True)
        self.solver.solve()
        low = self.solver.get_objective_value()
        # set maximize tag for upper boundary
        self.solver.set_objective(obj, minimize=False)
        self.solver.solve()
        up = self.solver.get_objective_value()
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
        return max([BaseSolver.to_int(x.objectives[objective_index])
                    for x in solutions]) - 1

    def recuse(self, only_objective: Dict[int, Any],
               w: Decimal, objectives: List[Dict[int, Any]],
               level: int) -> Dict[str, BinarySolution]:
        """recuse [summary] recusively execute

        Args:
            only_objective (Dict[int, Any]): [description]
            w (Decimal): [description] weight
            objectives (List[Dict[int, Any]]) : [description]
            level (int): [description] current objective

        Returns:
            List[BinarySolution]: [description] solutions found so far
        """
        if level == 0:
            # solve
            self.solver.set_objective(only_objective, True)
            return self.solver.solve()
        else:
            # prepare all solutions set
            all_solutions: Dict[str, BinarySolution] = {}
            # solve boundaries
            low_f, up_f = self.calculte_boundary(objectives[level])
            if low_f is None or up_f is None:
                return all_solutions
            low = BaseSolver.to_int(low_f)
            up = BaseSolver.to_int(up_f)
            w_level = w / Decimal(MOOUtility.round(up - low + 1))
            the_objective = BaseSolver.objective_add(only_objective,
                                                     objectives[level],
                                                     float(w_level))
            constraint_name = 'obj' + str(level)
            # set constraint of objective
            self.solver.add_constriant(constraint_name, objectives[level])
            # initialize rhs
            rhs = up
            while True:
                # update rhs
                self.solver.set_rhs(constraint_name, rhs)
                solutions = \
                    self.recuse(the_objective, w_level, objectives, level - 1)
                # cannot find solutions anymore
                if not solutions:
                    break
                # update next rhs
                rhs = self.next_rhs(level, list(solutions.values()))
                # update solutions
                all_solutions = {**all_solutions, **solutions}
            # end while
            self.solver.delete_constraint(constraint_name)
            return all_solutions

    def prepare(self) -> None:
        pass

    def execute(self):
        """execute [summary] execute the algorithm
        """
        # solver
        objectives = self.problem.objectives
        k = len(objectives)
        self.recuse(objectives[0], Decimal(1.0), objectives, k - 1)

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
