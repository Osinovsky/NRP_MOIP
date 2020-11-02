#
# DONG Shi, dongshi@mail.ustc.edu.cn
# ABCSolver.py, created: 2020.11.02
# last modified: 2020.11.02
#

from abc import ABCMeta, abstractmethod


class ABCSolver(metaclass=ABCMeta):
    @abstractmethod
    def prepare(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def solutions(self):
        pass
