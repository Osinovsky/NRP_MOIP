#
# DONG Shi, dongshi@mail.ustc.edu.cn
# NCGOPSolver.py, created: 2020.12.24
# last modified: 2020.12.24
#

from src.util.ObjectiveSpace import ObjectiveSpace3D
from src.Solvers.ABCSolver import ABCSolver
from src.Solvers.BaseSolver import BaseSolver
from src.NRP import NRPProblem


class NCGOPSolver(ABCSolver, BaseSolver):
    def __init__(self, problem: NRPProblem) -> None:
        super().__init__(problem)
        self.space = ObjectiveSpace3D(problem)
