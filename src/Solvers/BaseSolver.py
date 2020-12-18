#
# DONG Shi, dongshi@mail.ustc.edu.cn
# BaseSolver.py, created: 2020.11.02
# last modified: 2020.12.14
#

from math import ceil, floor
from typing import Dict, Any, List, Union, Tuple
from cplex import Cplex, SolutionInterface
from jmetal.util.archive import NonDominatedSolutionsArchive
from jmetal.core.solution import BinarySolution
from src.Config import Config
from src.NRP import NRPProblem

# from time import time


class BaseSolver:
    def __init__(self, problem: NRPProblem) -> None:
        """__init__ [summary] define members and add constraints,
        variables (from problem)into solver

        Args:
            problem (NRPProblem): [description] nrp (p)roblem
        """
        # store the problem
        self.problem = problem
        # the solver
        self.solver = Cplex()
        # Non-Dominated Solutions Archive
        self.archive: NonDominatedSolutionsArchive = \
            NonDominatedSolutionsArchive()

        # solution tmp list
        self.solution_list: List[BinarySolution] = []

        # load config
        config = Config()

        # prepare the solver
        self.solver.set_results_stream(None)
        self.solver.set_warning_stream(None)
        self.solver.set_error_stream(None)
        self.solver.parameters.threads.set(config.threads)
        # self.solver.parameters.parallel.set(0)
        self.solver.parameters.emphasis.mip.set(0)
        self.solver.parameters.mip.tolerances.absmipgap.set(0.0)
        self.solver.parameters.mip.tolerances.mipgap.set(0.0)
        # add variables
        vars_num = len(problem.variables)
        types = ['B'] * vars_num
        variables = ['x' + str(i) for i in problem.variables]
        self.solver.variables.add(obj=None, lb=None, ub=None,
                                  types=types, names=variables)
        # add constraints
        for index, inequation in enumerate(problem.inequations):
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
                                               names=['c' + str(index)])

    def add_constriant(self, name: str,
                       constraint: Dict[int, Any]) -> None:
        """add_constriant [summary] add one constraint

        Args:
            name (str): [description]
            constraint (Dict[int, Any]): [description]
        """
        # get the num of variables
        vars_num = len(self.problem.variables)
        rows = []
        vari = []
        coef = []
        if vars_num in constraint:
            rs = float(constraint[vars_num])
        else:
            rs = 0.0
        for key in constraint:
            if key != vars_num:
                vari.append('x' + str(key))
                coef.append(float(constraint[key]))
        rows.append([vari, coef])
        self.solver.linear_constraints.add(lin_expr=rows, senses='L',
                                           rhs=[rs], names=[name])

    def delete_constraint(self, name: str) -> None:
        """delete_constraint [summary] remove one constraint

        Args:
            name (str): [description]
        """
        self.solver.linear_constraints.delete(name)

    def add_constriants(self,
                        constraints: Dict[str, Dict[int, Any]]) -> None:
        """add_constriants [summary] add addtional constraints

        Args:
            constraints (Dict[str, Dict[int, Any]]): [description]
            constraints, name mapping to constraint
        """
        # add each constraint
        for name, constraint in constraints.items():
            self.add_constriant(name, constraint)

    @staticmethod
    def objective_add(left: Dict[int, Any],
                      right: Dict[int, Any],
                      coef: float
                      ) -> Dict[int, Any]:
        """objective_add [summary] add up two objectives(map)

        Args:
            left (Dict[int, Any]): [description]
            right (Dict[int, Any]): [description]
            coef (float): [description] weight of right objective

        Returns:
            Dict[int, Any]: [description] merged objective
        """
        sum_obj: Dict[int, Any] = {}
        # see left objective
        for k in left:
            if k in sum_obj:
                sum_obj[k] += left[k]
            else:
                sum_obj[k] = left[k]
        # see right objective
        for k in right:
            if k in sum_obj:
                sum_obj[k] += coef * right[k]
            else:
                sum_obj[k] = coef * right[k]
        # end for
        return sum_obj

    def set_objective(self,
                      objective: Dict[int, Any],
                      minimize: bool) -> None:
        """set_objective [summary] set the objective

        Args:
            objective (Dict[int, Any]): [description] objective is a
            map of each variables' coefficients, note that there should not
            be constant number
            minimize (bool): [description] True -> minimize, False -> maximize
        """
        # prepare pairs for setting objectives
        pairs: List[Tuple[str, Any]] = \
            [('x' + str(k), v) for k, v in objective.items()]
        # set objective
        self.solver.objective.set_linear(pairs)
        # set sense
        sense = None
        if minimize:
            sense = self.solver.objective.sense.minimize
        else:
            sense = self.solver.objective.sense.maximize
        self.solver.objective.set_sense(sense)

    def set_rhs(self, name: str, rhs: Any) -> None:
        """set_rhs [summary] set a constraint rhs

        Args:
            name (str): [description] constraint name
            rhs (Any): [description] rhs
        """
        self.solver.linear_constraints.set_rhs(name, rhs)

    @staticmethod
    def around(f: float, mid: float) -> bool:
        left = mid - 1e-6
        right = mid + 1e-6
        return f >= left and f <= right

    @staticmethod
    def bool_float(f: float) -> bool:
        if BaseSolver.around(f, 0.0):
            return False
        elif BaseSolver.around(f, 1.0):
            return True
        else:
            result = False
            if f > 0.5:
                result = True
            print(str(f) + 'converted to' + str(result))
            return result

    @staticmethod
    def to_int(f: float) -> int:
        diff_ceil = float(ceil(f)) - f
        diff_floor = f - float(floor(f))
        if diff_ceil < diff_floor:
            return ceil(f)
        else:
            return floor(f)

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

    def fake_jmetal_solution(self, vars_list):
        solution = BinarySolution(
            len(self.problem.variables),
            len(self.problem.objectives),
            len(self.problem.inequations)
        )
        solution.variables = vars_list
        # calculate objectives
        solution.objectives = [0.0] * len(self.problem.objectives)
        constant_id = len(self.problem.variables)
        for index, objective in enumerate(self.problem.objectives):
            if constant_id in objective:
                rhs = float(objective[constant_id])
            else:
                rhs = 0.0
            for var in objective:
                if var >= len(solution.variables):
                    print(objective)
                    print(var)
                    input()
                if solution.variables[var]:
                    rhs += objective[var]
            solution.objectives[index] = rhs
        return solution

    @staticmethod
    def objectives_str(solution: BinarySolution) -> str:
        obj_str = str(round(solution.objectives[0], 2))
        for i in range(1, len(solution.objectives)):
            obj_str += '_'
            obj_str += str(round(solution.objectives[i], 2))
        return obj_str

    def solve(self) -> Dict[str, BinarySolution]:
        """solve [summary] solve the problem
        """
        # solve
        # start = time()
        self.solver.solve()
        # end = time()
        # print('cplex time:', end - start)
        # get solution
        solution = self.jmetal_solution(self.solver.solution)
        if solution:
            # add into archive
            # self.archive.add(solution)
            self.solution_list.append(solution)
            return {BaseSolver.objectives_str(solution): solution}
        else:
            # no solution
            return {}

    def get_objective_value(self) -> Any:
        """get_objective_value [summary] get the objective value

        Returns:
            Any: [description] objective value
        """
        return self.solver.solution.get_objective_value()

    def get_objectives(self) -> List[Tuple[float, ...]]:
        """get_objectives [summary] get the pareto solutions objectives

        Returns:
            List[Tuple[float, ...]]: [description] list of objectives tuple
        """
        # from solution list to archive
        if self.archive.size() == 0:
            for solution in self.solution_list:
                self.archive.add(solution)
        # convert objectives
        objectives = []
        for solution in self.archive.solution_list:
            objectives.append(tuple(solution.objectives))
        return objectives

    def get_variables(self) -> List[Tuple[bool, ...]]:
        """get_variables [summary] get the pareto solutions variables

        Returns:
            List[Tuple[bool, ...]]: [description] list of variables tuple
        """
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
