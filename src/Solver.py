#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Solver.py, created: 2020.11.02
# last modified: 2020.11.02
#

from src.Config import Config
from src.util.moipProb import MOIPProblem
from src.Solvers.ABCSolver import ABCSolver
from src.Solvers.EConstraint import EConstraint


class Solver:
    def __init__(self, method: str, problem: MOIPProblem) -> None:
        """__init__ [summary] define members

        Args:
            method (str): [description] which method to solve
        """
        # store
        self.method = method
        self.problem = problem
        # get config
        config = Config()
        assert method in config.method
        self.solver: ABCSolver = None
        getattr(self, 'employ_{}'.format(method))(problem)

    def prepare(self):
        self.solver.prepare()

    def execute(self):
        self.solver.execute()

    def solutions(self):
        return self.solver.solutions()

    def employ_epsilon(self, problem: MOIPProblem) -> EConstraint:
        self.solver = EConstraint(problem)
