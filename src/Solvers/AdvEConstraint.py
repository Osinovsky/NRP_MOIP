#
# DONG Shi, dongshi@mail.ustc.edu.cn
# AdvEConstraint.py, created: 2020.12.10
# last modified: 2020.12.10
#

from typing import Dict, Any, List
import math
from src.Solvers.EConstraint import EConstraint
from jmetal.core.solution import BinarySolution


class AdvEConstraint(EConstraint):
    """AdvEConstraint [summary]
    Inspired by CWMOIP, we developed another AdvConstraint with update rhs
    without fixed step. Meanwhile, unlike CWMOIP, we still use the same
    objective with EConstraint, in case of reducing the time as it's solved
    in practice.
    """
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

    def recuse(self, level: int,
               low: List[Any], up: List[Any]) -> Dict[str, BinarySolution]:
        """recuse [summary] recusively execute

        Args:
            level (int): [description] current objective
            low (List[Any]): [description] lower bound of each objective
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
            # get the upper bound
            rhs = math.ceil(up[level])
            constraint_name = 'obj' + str(level)
            while True:
                # update rhs
                self.solver.set_rhs(constraint_name, rhs)
                solutions = self.recuse(level - 1, low, up)
                if not solutions:
                    break
                rhs = self.next_rhs(level, list(solutions.values()))
                all_solutions = {**all_solutions, **solutions}
            # end for
            return all_solutions
