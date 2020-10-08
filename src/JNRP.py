# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# JNRP.py, created: 2020.10.05       #
# Last Modified: 2020.10.06          #
# ################################## #

from typing import *
from config import *
import random
from jmetal.core.problem import BinarySolution, BinaryProblem

# JMetal MOIProblem
class JNRP(BinaryProblem):
    # initialize
    # NOTE that every inequation should be format as x ... >= 0.0
    # What's more, there are no equations
    def __init__(self,
        variables : List[int], \
        objectives : List[Dict[int, int]], \
        constraints : List[Dict[int, int]] \
    ):  
        super().__init__()
        
        self.number_of_variables = len(variables)
        self.number_of_objectives = len(objectives)
        self.number_of_constraints = len(constraints)

        # use some members to record all input
        self.my_variables = variables
        self.my_objectives = objectives
        self.my_constraints = constraints

    # create a solution
    def create_solution(self) -> BinaryProblem:
        new_solution = BinarySolution( \
            # upper_bound=[1 for _ in range(len(self.my_variables))], \
            # lower_bound=[0 for _ in range(len(self.my_variables))], \
            number_of_variables=len(self.my_variables), \
            number_of_objectives=len(self.my_objectives), \
            number_of_constraints=len(self.my_constraints))
        #new solution
        new_solution.variables[0] = [True if random.randint(0, 1) == 0 else False for _ in range(len(self.my_variables))]
        return new_solution

    # evaluate
    def evaluate(self, solution : BinarySolution) -> BinarySolution:
        for obj_ind in range(len(self.my_objectives)):
            # get the current objective
            objective = self.my_objectives[obj_ind]
            # initialize objectives in a solution
            solution.objectives[obj_ind] = 0.0
            # for all variables
            for index, value in enumerate(solution.variables[0]):
                if index in objective and value:
                    solution.objectives[obj_ind] += objective[index]
            # end for
        # end for
        # update constraints
        self.__evaluate_constraints(solution)
        # return
        return solution

    # evaluate constraints
    def __evaluate_constraints(self, solution : BinarySolution) -> None:
        # prepare to calculate constraints
        constraints = [0.0 for _ in range(len(self.my_constraints))]
        # for each constraint
        for cst_ind, constraint in enumerate(self.my_constraints):
            # for each variable
            for index, value in enumerate(solution.variables[0]):
                if index not in constraint:
                    continue # ignore zero coef variables
                if value:
                    constraints[cst_ind] += constraint[index]
                else:
                    constraints[cst_ind] -= constraint[index]
            # end for
            # for the constant
            constant_id = len(self.my_variables)
            if constant_id in constraint:
                # NOTE constant should be moved to left side but not a rhs
                constraints[cst_ind] += constraint[constant_id]
        # update constraints in solution
        solution.constraints = constraints
        # print(solution.variables, solution.constraints)

    # name 
    def get_name(self) -> str:
        return 'jMetal NRP'

    # convert MOIP form inequations to jMetal form
    # Input constraints: lhs <= rhs, the rhs == constant_id is always a constant
    # Output constraints: lhs' >= 0.0, lhs ' = rhs - lhs 
    @staticmethod
    def regularize_constraints(raw_constraints : List[Dict[int, int]], constant_id : int) -> List[Dict[int, int]]:
        constraints = []
        # for each constraint
        for raw_constraint in raw_constraints:
            # - lhs - rhs
            constraint = {k:-v for k,v in raw_constraint.items()}
            # - lhs + rhs
            if constant_id in constraint:
                constraint[constant_id] = -constraint[constant_id]
            constraints.append(constraint)
        # end for
        return constraints