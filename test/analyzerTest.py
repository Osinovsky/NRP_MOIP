# #################################### #
# DONG Shi, dongshi@mail.ustc.edu.cn   #
# analyzerTest.py, created: 2020.09.23 #
# Last Modified: 2020.09.24            #
# #################################### #

import unittest
from copy import deepcopy
import os
import random
import numpy
import sys
sys.path.append("C:\\Users\\osino\\Desktop\\dev\\prototype\\NRP_MOIP\\src")
from config import *
from runner import Runner
from analyzer import ResultHandler, Analyzer, Comparator

# test analyzer.py
class analyzerTest(unittest.TestCase):
    # RESULTHANDLER TESTS
    # test to jmetal solution conversion
    def test_jmetal_solution_conversion(self):
        for i in range(100):
            width = random.randint(1,10)
            solution = []
            for k in range(width):
                solution.append(random.uniform(-100.9, 100.9))
            solution = tuple(solution)
            # solution with round
            round_solution = [round(float(x), 2) for x in solution]
            # conversion
            jmetal_solution = ResultHandler.to_jmetal_solution(solution)
            # test
            assert round_solution == jmetal_solution.objectives

    # test to numpy array
    def test_numpy_array_conversion(self):
        for i in range(100):
            length = random.randint(1, 3)
            solutions = []
            round_solutions = []
            for j in range(length):
                width = random.randint(1,10)
                solution = []
                for k in range(width):
                    solution.append(random.uniform(-100.9, 100.9))
                round_solutions.append(tuple([round(float(b), 2) for b in deepcopy(solution)]))
                solutions.append(ResultHandler.to_jmetal_solution(tuple(solution)))
            # conversion
            array_solutions = ResultHandler.to_numpy_array(solutions)
            # convert back
            back_solutions = [tuple(a) for a in array_solutions.tolist()]
            # test
            # print(back_solutions)
            assert back_solutions == round_solutions
    # ANALYZER TESTS

    # COMPARATOR TESTS
    # test parse names
    def test_parse(self):
        configs = []
        for project, _ in ALL_FILES_DICT.items():
            configs.append((project, 'xxxxx', 'yyyyy'))
        names = []
        for config in configs:
            names.append(Runner.name(*config))
        # get dicts
        which_names, which_project = Comparator.parse_names(names)
        # test
        for name in names:
            project = Runner.dename(name)['project']
            assert name in which_names[project]
            assert which_project[name] == project

# run tests
if __name__ == '__main__':
    unittest.main()