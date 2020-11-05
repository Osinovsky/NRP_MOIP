#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Solver.py, created: 2020.11.02
# last modified: 2020.11.04
#

from typing import Dict, Any, Set, Union
from src.Config import Config
from src.util.moipProb import MOIPProblem
from src.Solvers.ABCSolver import ABCSolver
from src.Solvers.EConstraint import EConstraint
from src.Solvers.CWMOIP import CWMOIP
from src.Solvers.JarSolver import JarSolver


class Solver:
    def __init__(self,
                 method: str,
                 method_option: Dict[str, Any],
                 problem: Union[MOIPProblem, str]) -> None:
        """__init__ [summary] define members

        Args:
            method (str): [description] which method to solve
            method_option (Dict[str, Any]): method option
            problem (Union[MOIPProblem, str]): problem or dumpped problem file
        """
        # store
        self.method = method
        self.method_option = method_option
        self.problem = problem
        # get config
        config = Config()
        assert method in config.method
        self.solver: ABCSolver = None
        getattr(self, 'employ_{}'.format(method))(problem, method_option)

    def prepare(self):
        self.solver.prepare()

    def execute(self):
        self.solver.execute()

    def solutions(self) -> Set[Any]:
        return self.solver.solutions()

    def employ_epsilon(self,
                       problem: MOIPProblem,
                       option: Dict[str, Any] = None
                       ) -> None:
        self.solver = EConstraint(problem)

    def employ_cwmoip(self,
                      problem: MOIPProblem,
                      option: Dict[str, Any] = None
                      ) -> None:
        self.solver = CWMOIP(problem)

    def employ_NSGAII(self,
                      problem: str,
                      option: Dict[str, Any] = None
                      ) -> None:
        self.solver = JarSolver('NSGAII', option, problem)
