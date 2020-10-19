# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# searchTest.py, created: 2020.10.19 #
# Last Modified: 2020.10.19          #
# ################################## #

import unittest
import sys
import random
from copy import deepcopy
sys.path.append("C:\\Users\\osino\\Desktop\\dev\\prototype\\NRP_MOIP\\src")
from searchSol import SearchSol, State, Dominate, Dominated, NonDominated, Equal
from config import *

class searchTest(unittest.TestCase): 
    # test dominate judge
    def test_dominate(self):
        for _ in range(300):
            left = State(1, {2}, random.randint(1, 10), random.randint(1, 10))
            right = deepcopy(left)
            assert SearchSol.dominate(left, right) == Equal
            assert SearchSol.dominate(right, left) == Equal
            right = deepcopy(left)
            right.p += random.randint(1, 10)
            assert SearchSol.dominate(left, right) == Dominated
            assert SearchSol.dominate(right, left) == Dominate
            right = deepcopy(left)
            right.p -= random.randint(1, 10)
            assert SearchSol.dominate(left, right) == Dominate
            assert SearchSol.dominate(right, left) == Dominated
            right = deepcopy(left)
            right.c -= random.randint(1, 10)
            assert SearchSol.dominate(left, right) == Dominated
            assert SearchSol.dominate(right, left) == Dominate
            right = deepcopy(left)
            right.c += random.randint(1, 10)
            assert SearchSol.dominate(left, right) == Dominate
            assert SearchSol.dominate(right, left) == Dominated
            right = deepcopy(left)
            right.p -= random.randint(1, 10)
            right.c -= random.randint(1, 10)
            assert SearchSol.dominate(left, right) == NonDominated
            assert SearchSol.dominate(right, left) == NonDominated
            right = deepcopy(left)
            right.p += random.randint(1, 10)
            right.c += random.randint(1, 10)
            assert SearchSol.dominate(left, right) == NonDominated
            assert SearchSol.dominate(right, left) == NonDominated
            right = deepcopy(left)
            right.p += random.randint(1, 10)
            right.c -= random.randint(1, 10)
            assert SearchSol.dominate(left, right) == Dominated
            assert SearchSol.dominate(right, left) == Dominate
            right = deepcopy(left)
            right.p -= random.randint(1, 10)
            right.c += random.randint(1, 10)
            assert SearchSol.dominate(left, right) == Dominate
            assert SearchSol.dominate(right, left) == Dominated

    # test init rest
    # def test_init_rest(self):
    #     profit = {1:10, 2:5, 3:3, 4:6}
    #     cost = {5:2, 6:3, 7:6, 8:5, 9:4, 10:1}
    #     dependencies = None
    #     requests = [(1,5), (1,7), (2,6), (2,7), (2,9), (3,8), (4,9), (4,10)]

    #     problem = (cost, profit, dependencies, requests)
    #     solver = SearchSol(problem)
    #     solver.test_rest_init()

if __name__ == '__main__':
    unittest.main()
