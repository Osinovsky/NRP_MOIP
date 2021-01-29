#
# DONG Shi, dongshi@mail.ustc.edu.cn
# NormalConstraint.py, created: 2020.12.26
# last modified: 2021.01.20
#

from typing import Dict, Any, List
from copy import deepcopy
from src.util.ObjectiveSpace import ObjectiveSpace3D
from src.Solvers.ABCSolver import ABCSolver
from src.Solvers.BaseSolver import BaseSolver
from src.NRP import NRPProblem


class NormalConstraint(ABCSolver):
    def __init__(self, problem: NRPProblem, option: Dict[str, Any]) -> None:
        """__init__ [summary] only support ReleasePlanner datasets
        """
        # store the problem
        self.problem = problem
        # prepare Objective Space
        self.space = ObjectiveSpace3D(problem)
        # prepare the solver
        self.solver = BaseSolver(problem)
        # get the sampling size
        self.sampling_size = option['size']

    @staticmethod
    def simple_sum_up(objectives: List[Dict[int, Any]]) -> Dict[int, Any]:
        the_objective = deepcopy(objectives[0])
        factor = (abs(sum(objectives[2])) + 1.0)
        for key, val in objectives[2].items():
            if key in the_objective:
                the_objective[key] += (val / factor)
            else:
                the_objective[key] = (val / factor)
        factor *= (abs(sum(objectives[1])) + 1.0)
        for key, val in objectives[1].items():
            if key in the_objective:
                the_objective[key] += (val / factor)
            else:
                the_objective[key] = (val / factor)
        return the_objective

    def prepare(self):
        # add first two objectives as constraints
        self.solver.add_constriant('obj0', self.problem.objectives[0])
        self.solver.add_constriant('obj1', self.problem.objectives[1])
        # set third objective as objective
        # obj2 + w1obj1 + w1w0obj0
        the_objective = NormalConstraint.simple_sum_up(self.problem.objectives)
        self.solver.set_objective(the_objective, True)

    def execute(self):
        # sampling from ObjectiveSpace
        points = self.space.uniform_sampling(self.sampling_size)
        # set each point as objective bound and solve
        last_solution = None
        for point in points:
            if last_solution \
                and point[0] <= last_solution[0] \
                    and point[1] <= last_solution[1]:
                continue
            self.solver.set_rhs('obj0', point[0])
            self.solver.set_rhs('obj1', point[1])
            # self.solver.solve()
            solution = self.solver.solve()
            if not solution:
                continue
            if not last_solution:
                last_solution = list(solution.values())[0].objectives[:2]

    def solutions(self):
        return self.solver.get_objectives()

    def variables(self):
        return self.solver.get_variables()
