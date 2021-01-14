#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Solver.py, created: 2020.11.02
# last modified: 2020.12.29
#

from typing import Dict, Any, List, Union
from src.NRP import NRPProblem
from src.Config import Config
from src.Solvers.EConstraint import EConstraint
from src.Solvers.ImprovedEC import ImprovedEC
from src.Solvers.CWMOIP import CWMOIP
from src.Solvers.NormalConstraint import NormalConstraint
from src.Solvers.JarSolver import JarSolver

# type
SolverType = Union[EConstraint, CWMOIP, NormalConstraint, JarSolver]


class Solver:
    def __init__(self,
                 method: str,
                 method_option: Dict[str, Any],
                 problem: Union[NRPProblem, str]) -> None:
        """__init__ [summary] define members

        Args:
            method (str): [description] which method to solve
            method_option (Dict[str, Any]): method option
            problem (Union[NRPProblem, str]): problem or dumpped problem file
        """
        # store
        self.method = method
        self.method_option = method_option
        self.problem = problem
        # get config
        config = Config()
        assert method in config.method
        self.solver: SolverType
        getattr(self, 'employ_{}'.format(method))(problem, method_option)

    def prepare(self):
        self.solver.prepare()

    def execute(self):
        self.solver.execute()

    def solutions(self) -> List[Any]:
        return self.solver.solutions()

    def variables(self) -> List[Any]:
        return self.solver.variables()

    def employ_epsilon(self,
                       problem: NRPProblem,
                       option: Dict[str, Any] = None
                       ) -> None:
        self.solver = EConstraint(problem)

    def employ_imprec(self,
                      problem: NRPProblem,
                      option: Dict[str, Any] = None
                      ) -> None:
        self.solver = ImprovedEC(problem)

    def employ_cwmoip(self,
                      problem: NRPProblem,
                      option: Dict[str, Any] = None
                      ) -> None:
        self.solver = CWMOIP(problem)

    def employ_normal(self,
                      problem: NRPProblem,
                      option: Dict[str, Any] = None
                      ) -> None:
        self.solver = NormalConstraint(problem)

    def employ_NSGAII(self,
                      problem: str,
                      option: Dict[str, Any] = {}
                      ) -> None:
        self.solver = JarSolver('NSGAII', option)

    def employ_IBEA(self,
                    problem: str,
                    option: Dict[str, Any] = {}
                    ) -> None:
        self.solver = JarSolver('IBEA', option)
