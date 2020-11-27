#
# DONG Shi, dongshi@mail.ustc.edu.cn
# BinSolver.py, created: 2020.11.27
# last modified: 2020.11.27
#

from typing import Dict, Any, List, Union, Tuple
from cplex import Cplex, SolutionInterface
from math import ceil, floor
from copy import deepcopy
from decimal import Decimal
from jmetal.util.archive import NonDominatedSolutionsArchive
from jmetal.core.solution import BinarySolution
from src.NRP import NRPProblem
from src.Solvers.ABCSolver import ABCSolver
from src.Solvers.BaseSolver import BaseSolver


class BinProblem:
    def __init__(self, problem: NRPProblem) -> None:
        self.problem = problem
        # prepare variables
        vars_num = len(problem.variables)
        self.types = ['B'] * vars_num
        self.variables = ['x' + str(i) for i in problem.variables]
        # prepare objective
        self.objective: Dict[int, Any] = {}
        # prepare inequations
        self.inequations = {}
        for index, inequ in enumerate(problem.inequations):
            self.inequations['c' + str(index)] = inequ

    def set_objective(self, w: float = None):
        self.objective = deepcopy(self.problem.objectives[0])
        if w:
            for k, v in self.problem.objectives[1].items():
                if k in self.objective:
                    self.objective[k] += w * v
                else:
                    self.objective[k] = w * v

    def set_rhs(self, rhs):
        var_num = len(self.variables)
        self.inequations['obj'] = deepcopy(self.problem.objectives[1])
        self.inequations['obj'][var_num] = rhs

    def solve(self):
        solver = Cplex()
        solver.set_results_stream(None)
        solver.set_warning_stream(None)
        solver.set_error_stream(None)
        solver.parameters.threads.set(1)
        solver.parameters.parallel.set(1)
        solver.variables.add(obj=None, lb=None, ub=None,
                             types=self.types, names=self.variables)
        vars_num = len(self.variables)
        for name, inequation in self.inequations.items():
            rows = []
            vari = []
            coef = []
            if vars_num in inequation:
                rs = inequation[vars_num]
            else:
                rs = 0
            for key in inequation:
                if key != vars_num:
                    vari.append('x' + str(key))
                    coef.append(inequation[key])
            rows.append([vari, coef])
            solver.linear_constraints.add(lin_expr=rows,
                                          senses='L',
                                          rhs=[rs],
                                          names=[name])
        # set objective
        pairs: List[Tuple[str, Any]] = \
            [('x' + str(k), v) for k, v in self.objective.items()]
        # set objective
        solver.objective.set_linear(pairs)
        # set sense
        solver.objective.set_sense(solver.objective.sense.minimize)
        # solve
        solver.solve()
        solution = self.jmetal_solution(solver.solution)
        del solver
        return solution

    def jmetal_solution(self, cplex_soltuion: SolutionInterface
                        ) -> Union[BinarySolution, None]:
        # create a new binary solution
        solution = BinarySolution(
            len(self.problem.variables),
            len(self.problem.objectives),
            len(self.problem.inequations)
        )
        # get status, variables from cplex_solution
        status = cplex_soltuion.get_status_string()
        if 'optimal' not in status:
            return None
        variables: Dict[int, Any] = {}
        for var_id in self.problem.variables:
            value = cplex_soltuion.get_values('x'+str(var_id))
            variables[var_id] = BaseSolver.bool_float(value)
        # check
        assert len(variables) == len(self.problem.variables)
        # set variables
        solution.variables = variables
        # calculate objectives
        solution.objectives = [0.0] * len(self.problem.objectives)
        constant_id = len(self.problem.variables)
        for index, objective in enumerate(self.problem.objectives):
            if constant_id in objective:
                rhs = float(objective[constant_id])
            else:
                rhs = 0.0
            for var in objective:
                if solution.variables[var]:
                    rhs += objective[var]
            solution.objectives[index] = rhs
        # check constraints
        for cst in self.problem.inequations:
            cst_val = 0
            for var, coef in cst.items():
                if var == len(variables):
                    cst_val += coef
                else:
                    if variables[var]:
                        cst_val -= coef
            if cst_val < -1e-6:
                print(cst_val, solution.objectives)
            assert cst_val >= -1e-6
        return solution


class EConstraint(ABCSolver):
    def __init__(self, problem: NRPProblem) -> None:
        # store the problem
        self.problem = BinProblem(problem)
        # Non-Dominated Solutions Archive
        self.archive: NonDominatedSolutionsArchive = \
            NonDominatedSolutionsArchive()
        # solution tmp list
        self.solution_list: List[BinarySolution] = []

    @staticmethod
    def to_int(f: float) -> int:
        f_floor = floor(f)
        f_ceil = ceil(f)
        if f >= f_floor - 1e-6 and f <= f_floor + 1e-6:
            return f_floor
        if f >= f_ceil - 1e-6 and f <= f_ceil + 1e-6:
            return f_ceil
        assert False

    def calculte_boundary(self, obj: Dict[int, Any]) -> Tuple[Any, Any]:
        ub = 0.0
        lb = 0.0
        for value in obj.values():
            if value > 0:
                ub = ub + value
            else:
                lb = lb + value
        return lb, ub

    def prepare(self):
        pass

    def execute(self):
        # main loop
        low, up = self.calculte_boundary(self.problem.problem.objectives[1])
        low = floor(low)
        up = ceil(up)
        # set objective
        self.problem.set_objective()
        for rhs in range(up, low - 1, -1):
            # set rhs
            self.problem.set_rhs(rhs)
            solution = self.problem.solve()
            if not solution:
                break
            self.solution_list.append(solution)
        # end for

    def solutions(self) -> List[Tuple[float, ...]]:
        # from solution list to archive
        if self.archive.size() == 0:
            for solution in self.solution_list:
                self.archive.add(solution)
        # convert objectives
        objectives = []
        for solution in self.archive.solution_list:
            objectives.append(tuple(solution.objectives))
        return objectives

    def variables(self) -> List[Tuple[bool, ...]]:
        # from solution list to archive
        if self.archive.size() == 0:
            for solution in self.solution_list:
                self.archive.add(solution)
        variables = []
        for solution in self.archive.solution_list:
            vars_list: List[bool] = []
            for var in range(len(solution.variables)):
                vars_list.append(solution.variables[var])
            variables.append(tuple(vars_list))
        return variables


class CWMOIP(EConstraint):
    def execute(self):
        # main loop
        low, up = self.calculte_boundary(self.problem.problem.objectives[1])
        low = floor(low)
        up = ceil(up)
        # set objective
        w = float(Decimal(1.0) / Decimal(up - low + 1))
        self.problem.set_objective(w)
        rhs = up
        while True:
            # set rhs
            self.problem.set_rhs(rhs)
            solution = self.problem.solve()
            if not solution:
                break
            self.solution_list.append(solution)
            rhs = self.to_int(solution.objectives[1]) - 1
        # end for
