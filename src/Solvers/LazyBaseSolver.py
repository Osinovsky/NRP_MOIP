#
# DONG Shi, dongshi@mail.ustc.edu.cn
# LazyBaseSolver.py, created: 2020.11.26
# last modified: 2020.11.26
#

from typing import Dict, Any, List, Union, Tuple
from cplex import SolutionInterface
from jmetal.util.archive import NonDominatedSolutionsArchive
from jmetal.core.solution import BinarySolution
from src.NRP import NRPProblem
from src.Solvers.BaseSolver import BaseSolver


class LazyBaseSolver:
    def __init__(self, problem: NRPProblem) -> None:
        """__init__ [summary] define members and add constraints,
        variables (from problem)into solver

        Args:
            problem (NRPProblem): [description] nrp (p)roblem
        """
        print('LazyBaseSolver used')
        # solver
        self.solver = BaseSolver(problem)
        # store the problem
        self.problem = problem
        # Non-Dominated Solutions Archive
        self.archive: NonDominatedSolutionsArchive = \
            NonDominatedSolutionsArchive()
        # constraints
        self.new_constraints: Dict[str, Dict[int, Any]] = {}
        # objective
        self.objective: Dict[int, Any] = {}
        self.minimize = True
        # rhs set list
        self.rhs_dict: Dict[str, Any] = {}
        # solution tmp list
        self.solution_list: List[BinarySolution] = []

    def add_constriants(self,
                        constraints: Dict[str, Dict[int, Any]]) -> None:
        self.new_constraints = {**self.new_constraints, **constraints}

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
        self.objective = objective
        self.minimize = minimize

    def set_rhs(self, name: str, rhs: Any) -> None:
        self.rhs_dict[name] = rhs

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
            assert False

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
        self.solver = BaseSolver(self.problem)
        # set constraints
        self.solver.add_constriants(self.new_constraints)
        # set rhs
        for name in self.rhs_dict:
            self.solver.set_rhs(name, self.rhs_dict[name])
        # set objective
        self.solver.set_objective(self.objective, self.minimize)
        solutions = self.solver.solve()
        for solution in solutions.values():
            self.solution_list.append(solution)
        return solutions

    def get_objective_value(self) -> Any:
        """get_objective_value [summary] get the objective value

        Returns:
            Any: [description] objective value
        """
        return self.solver.get_objective_value()

    def get_objectives(self) -> List[Tuple[float, ...]]:
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
