#
# DONG Shi, dongshi@mail.ustc.edu.cn
# BaseSolver.py, created: 2020.11.02
# last modified: 2020.11.04
#

from typing import Dict, Any, List, Set
from cplex import Cplex
from src.util.moipSol import CplexSolResult
from src.util.mooUtility import MOOUtility
from src.util.moipProb import MOIPProblem


class BaseSolver:
    def __init__(self, problem: MOIPProblem) -> None:
        """__init__ [summary] define members and add constraints,
        variables (from problem)into solver

        Args:
            problem (MOIPProblem): [description] moip (p)roblem
        """
        # store the problem
        self.problem = problem
        # the solver
        self.solver = Cplex()

        # instance variable: the solution set found by solver
        self.cplexSolutionSet: List[CplexSolResult] = []
        # instance variable: the solution map
        # the key is the solution obj values, the value is the solution
        self.cplexResultMap: Dict[str, CplexSolResult] = {}
        # instance variable: the map of the solutions in the pareto front
        self.cplexParetoSet: Set[Any] = set()

        # prepare the solver
        self.solver.set_results_stream(None)
        self.solver.set_warning_stream(None)
        self.solver.set_error_stream(None)
        self.solver.parameters.threads.set(1)
        self.solver.parameters.parallel.set(1)
        # add variables
        vars_num = problem.featureCount
        types = ['B'] * vars_num
        variables = ['x' + str(i) for i in range(vars_num)]
        self.solver.variables.add(obj=None, lb=None, ub=None,
                                  types=types, names=variables)
        # add constraints
        counter = 0
        for ineqlDic in problem.sparseInequationsMapList:
            rows = []
            vari = []
            coef = []
            rs = ineqlDic[vars_num]
            for key in ineqlDic:
                if key != vars_num:
                    vari.append('x' + str(key))
                    coef.append(ineqlDic[key])
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
        vars_num = self.problem.featureCount
        # add each constraint
        for name in constraints:
            ineqlDic = constraints[name]
            rows = []
            vari = []
            coef = []
            if vars_num in ineqlDic:
                rs = ineqlDic[vars_num]
            else:
                rs = 0
            for key in ineqlDic:
                if key != vars_num:
                    vari.append('x' + str(key))
                    coef.append(ineqlDic[key])
            rows.append([vari, coef])
            self.solver.linear_constraints.add(lin_expr=rows,
                                               senses='L',
                                               rhs=[rs],
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

    def solve(self) -> Dict[str, Any]:
        """solve [summary] solve the problem
        """
        self.solver.solve()
        status = self.solver.solution.get_status_string()
        if status.find("optimal") >= 0:
            # find the optimal solutions
            result_variables = self.solver.solution.get_values()
            cplex_result = CplexSolResult(result_variables,
                                          status, self.problem)
            # add into cplexResultMap
            if cplex_result.getResultID() not in self.cplexResultMap.keys():
                self.cplexSolutionSet.append(cplex_result)
                self.cplexResultMap[cplex_result.getResultID()] = cplex_result
            return {cplex_result.getResultID(): result_variables}
        else:
            return dict()

    def get_objective_value(self) -> Any:
        """get_objective_value [summary] get the objective value

        Returns:
            Any: [description] objective value
        """
        return self.solver.solution.get_objective_value()

    def build_pareto(self):
        """build_pareto [summary] build pareto from
        """
        inputPoints = [list(map(float, resultID.split('_')))
                       for resultID in self.cplexResultMap.keys()]
        if(len(inputPoints) == 0):
            self.cplexParetoSet = set()
        else:
            paretoPoints, dominatedPoints = \
                MOOUtility.simple_cull(inputPoints, MOOUtility.dominates)
            self.cplexParetoSet = paretoPoints

    def get_pareto(self):
        return self.cplexParetoSet
