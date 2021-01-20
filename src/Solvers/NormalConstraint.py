#
# DONG Shi, dongshi@mail.ustc.edu.cn
# NormalConstraint.py, created: 2020.12.26
# last modified: 2021.01.20
#

from typing import Dict, Any
from src.util.ObjectiveSpace import RPObjectiveSpace
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
        self.space = RPObjectiveSpace(problem)
        # prepare the solver
        self.solver = BaseSolver(problem)
        # get the sampling size
        self.sampling_size = option['size']

    def prepare(self):
        # add first two objectives as constraints
        self.solver.add_constriant('obj0', self.problem.objectives[0])
        self.solver.add_constriant('obj1', self.problem.objectives[1])
        # set third objective as objective
        self.solver.set_objective(self.problem.objectives[2], True)

    def execute(self):
        # sampling from ObjectiveSpace
        points = self.space.uniform_sampling(self.sampling_size)
        # set each point as objective bound and solve
        for point in points:
            self.solver.set_rhs('obj0', point[0])
            self.solver.set_rhs('obj1', point[1])
            self.solver.solve()

    def solutions(self):
        return self.solver.get_objectives()

    def variables(self):
        return self.solver.get_variables()
