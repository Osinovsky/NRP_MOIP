#
# DONG Shi, dongshi@mail.ustc.edu.cn
# ABCSolver.py, created: 2020.11.02
# last modified: 2020.11.09
#

from abc import ABCMeta, abstractmethod
from src.NRP import NRPProblem


class ABCSolver(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, problem: NRPProblem):
        pass

    @abstractmethod
    def prepare(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def solutions(self):
        pass

    @abstractmethod
    def variables(self):
        pass
