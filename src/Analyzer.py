#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Analyzer.py, created: 2020.11.10
# last modified: 2020.11.11
#

from typing import Dict, List
import matplotlib.pyplot as plt
from jmetal.core.solution import BinarySolution
from jmetal.util.archive import NonDominatedSolutionsArchive
from src.Indicator import Indicator
from src.Config import Config
from src.Result import Result, ResultEntry


class Comparator:
    def __init__(self, result_folder: str) -> None:
        """__init__ [summary] Comparator, load results,
        give indicators scores and compare

        Args:
            result_folder (str): [description] result root folder
        """
        # result files management
        self.result_manager = Result(result_folder)
        # comparison results, in each project, last on in list is
        # for whole method pareto fron
        self.comparison: Dict[str, Dict[str, List[ResultEntry]]] = {}
        # pareto fronts for each project
        self.fronts: Dict[str, NonDominatedSolutionsArchive] = {}

    def compare(self, projects: List[str] = [], methods: List[str] = [],
                indicators: List[str] = [], on_front: bool = True) -> None:
        """compare [summary] compare methods with indicators on given projects,
        if on_front is true, all info will be relative with their front
        solutions, either, it will work on all solutions that it found

        NOTE that projects names and methods names do not need to
        be specific when there's no same problem with different modelling,
        or same methods with different parameters

        Args:
            projects (List[str], optional): [description]. Defaults to [].
            methods (List[str], optional): [description]. Defaults to [].
            indicators (List[str], optional): [description]. Defaults to [].
            on_front (bool, optional): [description]. Defaults to True.
        """
        if not projects:
            projects = self.result_manager.projects
        else:
            projects = \
                [self.result_manager.project_name(x) for x in projects]
        if not methods:
            methods = self.result_manager.methods
        else:
            methods = \
                [self.result_manager.method_name(x) for x in methods]
        if not indicators:
            config = Config()
            indicators = config.indicators
        for project in projects:
            self.comparison[project] = {}
            self.__compare(project, methods, indicators, on_front)

    def __compare(self, project: str, methods: List[str],
                  indicators: List[str], on_front: bool
                  ) -> None:
        """__compare [summary] compare on a certain project

        Args:
            project (str): [description]
            methods (List[str]): [description]
            indicators (List[str]): [description]
            on_front (bool): [description]
        """
        # build paretos
        self.fronts[project] = self.__build_pareto(project, methods)
        # employ an indicator
        indicator = Indicator(self.comparison[project], self.fronts[project],
                              methods, self.result_manager.iterations)
        # for each indicator
        for indicator_name in indicators:
            self.comparison[project] = \
                indicator.compute(indicator_name, on_front)

    def __build_pareto(self, project: str, methods: List[str]
                       ) -> NonDominatedSolutionsArchive:
        """__build_pareto [summary] build pareto from
        variables/objectives files for each iteration
        and for all iterations

        Args:
            project (str): [description]
            methods (List[str]): [description]

        Returns:
            NonDominatedSolutionsArchive: [description]
            The pareto front for this project
        """
        # project archive
        archive = NonDominatedSolutionsArchive()
        # for each iteration and method
        for method in methods:
            self.comparison[project][method] = []
            method_front = ResultEntry()
            for index in range(self.result_manager.iterations):
                # entry for this iteration
                entry = ResultEntry()
                # make solution
                solutions = Result.load_solutions(
                    self.result_manager.s(project, method, index),
                    self.result_manager.v(project, method, index)
                )
                # load solutions in entry
                for solution in solutions:
                    entry.found.add(solution)
                    method_front.found.add(solution)
                    archive.add(solution)
                # load elapsed time and solutions found num
                info = Result.load_json(
                    self.result_manager.i(project, method, index)
                )
                entry.time = info['elapsed time']
                method_front.time += entry.time
                # add into result list
                self.comparison[project][method].append(entry)
            # end index loop
            self.comparison[project][method].append(method_front)

        # end nest for
        # check for each method/iteration,
        # how many solutions are still in the front(archive)
        for method in methods:
            for index in range(self.result_manager.iterations + 1):
                solutions = self.comparison[project][method][index]\
                                           .found.solution_list
                for solution in solutions:
                    if solution in archive.solution_list:
                        self.comparison[project][method][index] \
                                       .front.add(solution)
        # end nest for
        return archive


class Analyzer:
    def __init__(self, result_folder: str) -> None:
        """__init__ [summary] Analyzer is used for visualize
        results from Comparator

        Args:
            result_folder (str): [description] result root folder
        """
        # employ an comparator
        self.comparator = Comparator(result_folder)

        # compute all scores and infomations in comparator
        self.comparator.compare()

    @staticmethod
    def tabulate(file_name: str,
                 sheet: List[List[str]]) -> None:
        """tabulate [summary] turn a sheet into csv file

        Args:
            file_name (str): [description] *.csv file name
            sheet (List[List[str]]): [description] the sheet
        """
        with open(file_name, 'w+') as fout:
            for line in sheet:
                line_str = ''
                for index, element in enumerate(line):
                    if index > 0:
                        line_str += ', '
                    else:
                        line_str += element
                fout.write(line_str + '\n')
            fout.close()

    def make_sheet(self,
                   projects: List[str] = [],
                   methods: List[str] = [],
                   indicators: List[str] = [],
                   tab_iteration: bool = False
                   ) -> List[List[str]]:
        if not projects:
            projects = self.comparator.result_manager.projects
        else:
            projects = \
                [self.comparator.result_manager.project_name(x)
                 for x in projects]
        if not methods:
            methods = self.comparator.result_manager.methods
        else:
            methods = \
                [self.comparator.result_manager.method_name(x)
                 for x in methods]
        if not indicators:
            config = Config()
            indicators = config.indicators
        if tab_iteration:
            return self.make_iteration_sheet(
                projects, methods, indicators
            )
        else:
            return self.make_method_sheet(
                projects, methods, indicators
            )

    def make_iteration_sheet(self,
                             projects: List[str],
                             methods: List[str],
                             indicators: List[str],
                             ) -> List[List[str]]:
        """make_iteration_sheet [summary] make sheets for
        each iteration

        Args:
            projects (List[str]): [description]
            methods (List[str]): [description]

        Returns:
            List[List[str]]: [description] sheet
        """
        sheet: List[List[str]] = []
        iteration_num = self.comparator.result_manager.iterations
        for project in projects:
            # project, ...
            project_line = [project] + [''] * iteration_num
            sheet.append(project_line)
            for indicator in indicators:
                # indicator, itr1, itr2, ...
                header = [indicator] + \
                    ['itr' + str(x+1) for x in range(iteration_num)]
                sheet.append(header)
                for method in methods:
                    # method: score1, score2, ...
                    line = [method] + \
                        [str(round(x.score[indicator], 6)) for x in
                         self.comparator.comparison[project][method]]
                    sheet.append(line)
            # elapsed time
            header = ['time'] + \
                     ['itr' + str(x+1) for x in range(iteration_num)]
            for method in methods:
                # method: time1, time2, ...
                line = [method] + \
                    [str(round(x.time, 6)) for x in
                     self.comparator.comparison[project][method]]
                sheet.append(line)
            # solutions found
            header = ['found'] + \
                     ['itr' + str(x+1) for x in range(iteration_num)]
            for method in methods:
                # method: found1, found2, ...
                line = [method] + \
                    [str(len(x.found)) for x in
                     self.comparator.comparison[project][method]]
                sheet.append(line)
            # solutions on the front
            header = ['front'] + \
                     ['itr' + str(x+1) for x in range(iteration_num)]
            for method in methods:
                # method: front1, front2, ...
                line = [method] + \
                    [str(len(x.front)) for x in
                     self.comparator.comparison[project][method]]
                sheet.append(line)
        # end nest for
        return sheet

    def make_method_sheet(self,
                          projects: List[str],
                          methods: List[str],
                          indicators: List[str],
                          ) -> List[List[str]]:
        """make_method_sheet [summary] make sheet for
        each method, without specific iterations

        Args:
            projects (List[str]): [description]
            methods (List[str]): [description]
            indicators (List[str]): [description]

        Returns:
            List[List[str]]: [description] sheet
        """
        sheet: List[List[str]] = []
        iteration_num = self.comparator.result_manager.iterations
        for project in projects:
            # project, time, found, front, indicator1, indicator2, ...
            project_line = [project] + ['time', 'found', 'front'] + indicators
            sheet.append(project_line)
            for method in methods:
                scores = \
                    self.comparator.comparison[project][method][iteration_num]
                # method, time, solutions found, solutions on front, score1, ..
                method_line = [method] \
                    + [str(round(scores.time, 2))] \
                    + [str(len(scores.found))] \
                    + [str(len(scores.front))] \
                    + [str(round(scores.score[indicator], 6))
                       for indicator in indicators]
                sheet.append(method_line)
        # end for
        return sheet

    @staticmethod
    def get_objectives(solutions: List[BinarySolution]
                       ) -> List[List[float]]:
        """get_objectives [summary] convert list of solutions
        to objectives lists

        Args:
            solutions (List[BinarySolution]): [description]

        Returns:
            Tuple[List[float], List[float]]: [description] objectives lists
        """
        width = len(solutions[0].objectives)
        objectives: List[List[float]] = []
        for i in range(width):
            objectives.append([])
        for solution in solutions:
            for i in range(width):
                objectives[i].append(solution.objectives[i])
        return objectives

    def plot_2D_pareto(self, project: str, methods: List[str] = [],
                       file_name: str = None) -> None:
        """plot_2D_pareto [summary] plot 2D pareto figure

        Args:
            project (str): [description] 
            methods (List[str]): [description]
        """
        project = self.comparator.result_manager.project_name(project)
        if not methods:
            methods = self.comparator.result_manager.methods
        else:
            methods = \
                [self.comparator.result_manager.method_name(x)
                 for x in methods]
        iteration = self.comparator.result_manager.iterations
        handles = []
        labels = []
        for method in methods:
            objectives = \
                self.get_objectives(self.comparator
                                        .comparison[project][method][iteration]
                                        .front.solution_list)
            handle = \
                plt.scatter(objectives[0], objectives[1], label=method, alpha=0.5)
            handles.append(handle)
            labels.append(method)
        if file_name:
            plt.savefig(file_name)
        else:
            plt.legend(handles, labels)
            plt.show()
