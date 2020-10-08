# #################################### #
# DONG Shi, dongshi@mail.ustc.edu.cn   #
# solverTest.py, created: 2020.10.07   #
# Last Modified: 2020.10.08            #
# #################################### #

import unittest
import sys
import random
sys.path.append("C:\\Users\\osino\\Desktop\\dev\\prototype\\NRP_MOIP\\src")
from config import *
from JNRP import JNRP
from NRP import NextReleaseProblem
from solvers import Solver

class SolverTest(unittest.TestCase):
    single_solver = ['single', 'SPEA2']
    binary_solver = ['epsilon','SPEA2']

    # display solutions
    def display_all(self, solutions):
        for solution in solutions:
            print(solution)

    # randomly choose some solution for displaying
    def display(self, solutions, num):
        if len(solutions) <= num:
            self.display_all(list(solutions))
        else:
            choosen = random.sample(list(solutions), num)
            self.display_all(choosen)

    def dpl(self, solutions):
        for solution in solutions:
            print(solution.variables, solution.constraints, solution.objectives)

    # Test cases are just for running
    # do not check the result, just check wether the code could run
    # unconstrainted single objective case
    def test_case_1(self):
        # prepare raw problem
        variables = [0, 1, 2]
        objectives = [
            {0:-10, 1:-5, 2:-1}
        ]
        constraints = dict()
        # prepare solvers
        for solver_name in self.single_solver:
            if solver_name == 'single':
                problem = NextReleaseProblem.MOIP( \
                    variables, objectives, constraints,  \
                    dict(), dict() \
                )
            else:
                constraints = JNRP.regularize_constraints(constraints, len(variables))
                problem = JNRP(variables, objectives, constraints)
            solver = Solver(solver_name)
            # prepare and solve
            solver.load(problem)
            solver.execute()
            # get the solutions
            solutions = solver.solutions()
            print(solver_name + '\t\t' + str(len(solutions)))
            self.display(solutions, 5)

    # constrainted single objective case
    def test_case_2(self):
        # prepare raw problem
        variables = [0, 1, 2, 3]
        objectives = [
            {0:-10, 1:-5, 2:-1, 3:5}
        ]
        constraints = [
            {2:1, 4:0},
            {0:1, 3:-1, 4:0}
        ]
        # prepare solvers
        for solver_name in self.single_solver:
            if solver_name == 'single':
                problem = NextReleaseProblem.MOIP( \
                    variables, objectives, constraints,  \
                    ['L' for _ in range(len(constraints))], dict() \
                )
            else:
                constraints = JNRP.regularize_constraints(constraints, len(variables))
                problem = JNRP(variables, objectives, constraints)
            solver = Solver(solver_name)
            # prepare and solve
            solver.load(problem)
            solver.execute()
            # get the solutions
            solutions = solver.solutions()
            print(solver_name + '\t\t' + str(len(solutions)))
            self.display(solutions, 5)

    # unconstrainted binary objectives case
    def test_case_3(self):
        # prepare raw problem
        variables = [0, 1, 2, 3]
        objectives = [
            {0:-10, 1:-5, 2:-1, 3:-5},
            {0:3, 1:2, 2:3, 3:0}
        ]
        constraints = dict()
        # prepare solvers
        for solver_name in self.binary_solver:
            if solver_name == 'epsilon':
                problem = NextReleaseProblem.MOIP( \
                    variables, objectives, constraints,  \
                    dict(), dict() \
                )
            else:
                constraints = JNRP.regularize_constraints(constraints, len(variables))
                problem = JNRP(variables, objectives, constraints)
            solver = Solver(solver_name)
            # prepare and solve
            solver.load(problem)
            solver.execute()
            # get the solutions
            solutions = solver.solutions()
            print(solver_name + '\t\t' + str(len(solutions)))
            self.display(solutions, 5)

    # constrainted binary objectives case
    def test_case_4(self):
        # prepare raw problem
        variables = [0, 1, 2, 3]
        objectives = [
            {0:-10, 1:-5, 2:-1, 3:-5},
            {0:3, 1:2, 2:3, 3:0}
        ]
        constraints = [
            {2:-1, 4:-1},
            {0:1, 3:-1, 4:0}
        ]
        # prepare solvers
        for solver_name in self.binary_solver:
            if solver_name == 'epsilon':
                problem = NextReleaseProblem.MOIP( \
                    variables, objectives, constraints,  \
                    ['L' for _ in range(len(constraints))], None \
                )
            else:
                constraints = JNRP.regularize_constraints(constraints, len(variables))
                problem = JNRP(variables, objectives, constraints)
            solver = Solver(solver_name)
            # prepare and solve
            solver.load(problem)
            solver.execute()
            # get the solutions
            solutions = solver.solutions()
            print(solver_name + '\t\t' + str(len(solutions)))
            self.display(solutions, 5)

if __name__ == '__main__':
    unittest.main()