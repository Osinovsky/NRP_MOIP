#
# DONG Shi, dongshi@mail.ustc.edu.cn
# BaseSolverTest.py, created: 2020.11.24
# last modified: 2020.11.24
#

import unittest
from random import randint
from src.Solvers.BaseSolver import BaseSolver


class BaseSolverTest(unittest.TestCase):
    def random_objective(self, var_len, size):
        objective = {}
        for _ in range(size):
            key = randint(0, var_len-1)
            objective[key] = randint(-1000, 1000)
        return objective

    def test_objective_add(self):
        for _ in range(100):
            o1 = self.random_objective(100, 50)
            o2 = self.random_objective(100, 50)
            coef = float(randint(1, 100))/100.0

            sum_o = BaseSolver.objective_add(o1, o2, coef)

            assert set(sum_o.keys()) == set(o1.keys()).union(o2.keys())

            for k, v in sum_o.items():
                assert k in o1 or k in o2
                if k in o1:
                    o1v = o1[k]
                else:
                    o1v = 0.0
                if k in o2:
                    o2v = coef * o2[k]
                else:
                    o2v = 0.0
                assert o1v + o2v <= v + 1e-6 and o1v + o2v >= v - 1e-6


if __name__ == "__main__":
    unittest.main()
