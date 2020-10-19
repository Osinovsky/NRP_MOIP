# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# searchTest.py, created: 2020.10.19 #
# Last Modified: 2020.10.19          #
# ################################## #

import unittest
import sys
sys.path.append("C:\\Users\\osino\\Desktop\\dev\\prototype\\NRP_MOIP\\src")
from searchSol import SearchSol
from config import *

class searchTest(unittest.TestCase): 
    # test init rest
    def test_init_rest(self):
        profit = {1:10, 2:5, 3:3, 4:6}
        cost = {5:2, 6:3, 7:6, 8:5, 9:4, 10:1}
        dependencies = None
        requests = [(1,5), (1,7), (2,6), (2,7), (2,9), (3,8), (4,9), (4,10)]

        problem = (cost, profit, dependencies, requests)
        solver = SearchSol(problem)
        solver.test_rest_init()

if __name__ == '__main__':
    unittest.main()
