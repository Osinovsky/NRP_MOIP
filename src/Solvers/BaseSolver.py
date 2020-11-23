#
# DONG Shi, dongshi@mail.ustc.edu.cn
# BaseSolver.py, created: 2020.11.02
# last modified: 2020.11.18
#

from typing import Dict, Any, List, Union, Tuple
from cplex import Cplex, SolutionInterface
from jmetal.util.archive import NonDominatedSolutionsArchive
from jmetal.core.solution import BinarySolution
from src.NRP import NRPProblem


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

    def add_constriants(self,
                        constraints: Dict[str, Dict[int, Any]]) -> None:
        """add_constriants [summary] add addtional constraints

        Args:
            constraints (Dict[str, Dict[int, Any]]): [description]
            constraints, name mapping to constraint
        """
        # get the num of variables
        vars_num = len(self.problem.variables)
        # add each constraint
        for name in constraints:
            constraint = constraints[name]
            rows = []
            vari = []
            coef = []
            if vars_num in constraint:
                rs = constraint[vars_num]
            else:
                rs = 0
            for key in constraint:
                if key != vars_num:
                    vari.append('x' + str(key))
                    coef.append(float(constraint[key]))
            rows.append([vari, coef])
            self.solver.linear_constraints.add(lin_expr=rows,
                                               senses='L',
                                               rhs=[float(rs)],
                                               names=[name])

    def set_objective(self,
                      objective: List[Any],
                      minimize: bool) -> None:
        """set_objective [summary] set the objective

        Args:
            objective (List[Any]): [description] objective is a
            list of each variables' coefficient
            minimize (bool): [description] True -> minimize, False -> maximize
        """
        var_len = len(objective)
        # set objective
        self.solver.objective.set_linear(zip(list(range(var_len)), objective))
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
        variables = cplex_soltuion.get_values()
        # check
        assert len(variables) == len(self.problem.variables)
        # set variables
        solution.variables = [[BaseSolver.bool_float(x) for x in variables]]
        # calculate objectives
        solution.objectives = [0.0] * len(self.problem.objectives)
        constant_id = len(self.problem.variables)
        for index, objective in enumerate(self.problem.objectives):
            if constant_id in objective:
                rhs = float(objective[constant_id])
            else:
                rhs = 0.0
            for var in objective:
                if solution.variables[0][var]:
                    rhs += objective[var]
            solution.objectives[index] = rhs
        return solution

    @staticmethod
    def objectives_str(solution: BinarySolution) -> str:
        obj_str = str(int(solution.objectives[0]))
        for i in range(1, len(solution.objectives)):
            obj_str += '_'
            obj_str += str(int(solution.objectives[i]))
        return obj_str

    def solve(self) -> Dict[str, BinarySolution]:
        """solve [summary] solve the problem
        """
        # solve
        self.solver.solve()
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
        # from tmp list to archive
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
        variables = []
        for solution in self.archive.solution_list:
            variables.append(tuple(solution.variables[0]))
        return variables
