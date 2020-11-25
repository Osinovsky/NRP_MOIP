import math
from typing import Dict, List, Any
from src.NRP import NRPProblem
from src.Solvers.EConstraint import EConstraint
from jmetal.core.solution import BinarySolution


class CWMOIP(EConstraint):
    def __init__(self, problem: NRPProblem) -> None:
        super().__init__(problem)
        print('Alt CWMOIP used')

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
            # get the up and low bound
            rhs = math.ceil(up[level])
            # relaxed_low = math.floor(low[level])
            constraint_name = 'obj_' + str(level)
            while True:
                # update rhs
                fout = open('cwmoip_rhs.txt', 'a')
                fout.write(str(rhs) + '\n')
                fout.close()
                self.solver.set_rhs(constraint_name, rhs)
                solutions = self.recuse(level - 1, low, up)
                if not solutions:
                    break
                rhs = self.next_rhs(level, list(solutions.values()))
                all_solutions = {**all_solutions, **solutions}
            # end for
            return all_solutions
