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


class EConstraint(ABCSolver):
    def __init__(self, problem: NRPProblem) -> None:
        # store the problem
        self.problem = problem
        # the solver
        self.solver = Cplex()
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
        return solution

    def prepare(self):
        problem = self.problem
        # prepare the solver
        self.solver.set_results_stream(None)
        self.solver.set_warning_stream(None)
        self.solver.set_error_stream(None)
        self.solver.parameters.threads.set(1)
        self.solver.parameters.parallel.set(1)
        # add variables
        vars_num = len(problem.variables)
        types = ['B'] * vars_num
        variables = ['x' + str(i) for i in problem.variables]
        self.solver.variables.add(obj=None, lb=None, ub=None,
                                  types=types, names=variables)
        # add constraints
        counter = 0
        for inequation in problem.inequations:
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
            self.solver.linear_constraints.add(lin_expr=rows,
                                               senses='L',
                                               rhs=[rs],
                                               names=['c' + str(counter)])
            counter += 1
        # calculate boundary of that objective
        _, up = self.calculte_boundary(problem.objectives[1])
        # add objective
        rows = []
        vari = []
        coef = []
        rs = up
        for key in problem.objectives[1]:
            if key != vars_num:
                vari.append('x' + str(key))
                coef.append(problem.objectives[1][key])
        rows.append([vari, coef])
        self.solver.linear_constraints.add(lin_expr=rows,
                                           senses='L',
                                           rhs=[rs],
                                           names=['obj'])

    def execute(self):
        # add objective
        pairs: List[Tuple[str, Any]] = \
            [('x' + str(k), v) for k, v in self.problem.objectives[0].items()]
        # set objective
        self.solver.objective.set_linear(pairs)
        # set sense
        self.solver.objective.set_sense(self.solver.objective.sense.minimize)
        # main loop
        low, up = self.calculte_boundary(self.problem.objectives[1])
        low = floor(low)
        up = ceil(up)
        for rhs in range(up, low - 1, -1):
            self.solver.linear_constraints.set_rhs('obj', rhs)
            self.solver.solve()
            solution = self.jmetal_solution(self.solver.solution)
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
        # prepare the objective
        low, up = self.calculte_boundary(self.problem.objectives[1])
        w = Decimal(1.0) / Decimal(self.to_int(up) - self.to_int(low) + 1)
        only_objective = deepcopy(self.problem.objectives[0])
        for var, val in self.problem.objectives[1].items():
            if var in only_objective:
                only_objective[var] += float(w) * val
            else:
                only_objective[var] = float(w) * val
        # add objective
        pairs: List[Tuple[str, Any]] = \
            [('x' + str(k), v) for k, v in only_objective.items()]
        # set objective
        self.solver.objective.set_linear(pairs)
        # set sense
        self.solver.objective.set_sense(self.solver.objective.sense.minimize)
        # main loop
        rhs = self.to_int(up)
        while True:
            self.solver.linear_constraints.set_rhs('obj', rhs)
            self.solver.solve()
            solution = self.jmetal_solution(self.solver.solution)
            if not solution:
                break
            self.solution_list.append(solution)
            rhs = int(solution.objectives[1]) - 1
        # end for
