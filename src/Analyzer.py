#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Analyzer.py, created: 2020.11.10
# last modified: 2021.01.18
#

from typing import Any, Dict, List, Tuple
import matplotlib.pyplot as plt
from jmetal.core.solution import BinarySolution
from src.Indicator import Indicator
from src.Config import Config
from src.Result import Result


class Analyzer:
    def __init__(self, result_folder: str, result: Result = None) -> None:
        """__init__ [summary] Analyzer is used for analyzing
        results from Result

        Args:
            result_folder (str): [description] result root folder
            result (Result): [description]
        """
        # employ a Result to manage results
        if not result:
            self.result = Result(result_folder)
        else:
            self.result = result

        # prepare store scores
        self.scores: Dict[Tuple[str, str], Dict[str, Any]] = {}

    @staticmethod
    def prefix_list(raw_list: List[str],
                    prefix: List[str]) -> List[str]:
        """ filter raw_list with give prefix
        """
        result: List[str] = []
        for raw_str in raw_list:
            for pre_str in prefix:
                if raw_str.startswith(pre_str):
                    result.append(raw_str)
                    break
        return result

    def metric(self, projects: List[str], methods: List[str],
               indicators: List[str] = []) -> None:
        """metric [summary] give score on each front
        Args:
            projects (List[str]): [description]
            methods (List[str]): [description]
            indicators (List[str], optional): [description]. [] mean all.
        """
        # load config
        config = Config()
        if not indicators:
            indicators = config.indicators
        # for each project and method
        ps = Analyzer.prefix_list(self.result.projects, projects)
        for p in ps:
            true_front = self.result.project_fronts[p]
            ms = Analyzer.prefix_list(self.result.methods[p], methods)
            for m in ms:
                method_front = self.result.method_fronts[(p, m)]
                self.scores[(p, m)] = \
                    Indicator.compute(indicators, method_front, true_front)
        # end nest for

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
                    line_str += element
                fout.write(line_str + '\n')
            fout.close()

    def make_sheet(self, indicators: List[str] = []) -> List[List[str]]:
        """make_sheet [summary] make sheet for each method

        Args:
            indicators (List[str]): [description]

        Returns:
            List[List[str]]: [description] sheet
        """
        config = Config()
        if not indicators:
            indicators = config.indicators
        sheet: List[List[str]] = []
        for project in self.result.projects:
            # project, time, found, front, indicator1, indicator2, ...
            project_line = [project] + ['time', 'found', 'front'] + indicators
            sheet.append(project_line)
            for method in self.result.methods[project]:
                key = (project, method)
                # calculate indicator scores
                scores = \
                    Indicator.compute(indicators,
                                      self.result.method_fronts[key],
                                      self.result.project_fronts[project])
                # method, time, solutions found, solutions on front, score1, ..
                method_front = self.result.method_fronts[key].solution_list
                method_line = [method] \
                    + [str(round(self.result.info[key]['time'], 2))] \
                    + [str(self.result.info[key]['found'])] \
                    + [str(len(method_front))] \
                    + [str(round(scores[ind], 6)) for ind in indicators]
                sheet.append(method_line)
        # end for
        return sheet

    def make_better_sheet(self, methods: List[str] = [],
                          indicators: List[str] = []) -> List[List[str]]:
        """make_better_sheet [summary] make better sheet for each method

        Args:
            indicators (List[str]): [description]

        Returns:
            List[List[str]]: [description] sheet
        """
        config = Config()
        if not indicators:
            indicators = config.indicators
        if not methods:
            for project in self.result.projects:
                for method in self.result.methods[project]:
                    methods.append(method.split('-')[0])
        # prepare the header
        header = ['datasets'] \
            + [m + '-front' for m in methods] \
            + [m + '-time' for m in methods]
        for indicator in indicators:
            for method in methods:
                header.append(method + '-' + indicator)
        # prepare the sheet
        sheet: List[List[str]] = [header]
        for project in self.result.projects:
            # prepare the method order according to input
            real_methods = [''] * len(methods)
            for method in self.result.methods[project]:
                for index, short_name in enumerate(methods):
                    if method.startswith(short_name):
                        real_methods[index] = method
            # collect each method line
            method_lines = []
            for method in real_methods:
                key = (project, method)
                # calculate indicator scores
                scores = \
                    Indicator.compute(indicators,
                                      self.result.method_fronts[key],
                                      self.result.project_fronts[project])
                # method, solutions on front, time, score1, ..
                method_front = self.result.method_fronts[key].solution_list
                method_line = [str(len(method_front))] \
                    + [str(round(self.result.info[key]['time'], 2))] \
                    + [str(round(scores[ind], 6)) for ind in indicators]
                method_lines.append(method_line)
            # prepare project line
            line = [project]
            for index in range(len(method_lines[0])):
                for method_line in method_lines:
                    line.append(method_line[index])
            sheet.append(line)
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
        project = self.result.project_name(project)
        if not methods:
            methods = self.result.methods[project]
        else:
            methods = \
                [self.result.method_name(project, x) for x in methods]
        handles = []
        labels = []
        fig, ax = plt.subplots()
        for method in methods:
            key = (project, method)
            solution_list = self.result.method_fronts[key].solution_list
            objectives = self.get_objectives(solution_list)
            handle = \
                ax.scatter(objectives[0], objectives[1],
                           label=method, alpha=0.5)
            handles.append(handle)
            labels.append(method)
        if file_name:
            fig.savefig(file_name, dpi=300)
            plt.close(fig)
        else:
            plt.legend(handles, labels)
            plt.show()
