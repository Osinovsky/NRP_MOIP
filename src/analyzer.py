# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# analyzer.py, created: 2020.09.24   #
# Last Modified: 2020.09.25          #
# ################################## #

from typing import *
import json
import os
import sys
from copy import deepcopy
from ast import literal_eval as to_tuple
from jmetal.core.solution import FloatSolution, Solution
from jmetal.util.archive import NonDominatedSolutionsArchive, Archive
from jmetal.core.quality_indicator import InvertedGenerationalDistance, HyperVolume
import numpy as np
from config import *
from evenness_indicator import EvennessIndicator
from runner import Runner

# result handling class
class ResultHandler:
    # members
    def __init__(self, result_path : str, names : List[str], ite_num : int = 1):
        # recording
        self.out_path = result_path
        self.names = names
        self.ite_num = ite_num
        # prepare content, whether be analysis or comparison
        self.content = dict()
        # store result(checklist)
        self.result = ResultHandler.load_checklist(result_path)
        # load solutions to self.result
        self.load_solutions()
        # load_result_to_content
        self.load_result_to_content()
    
    # load result(result_path/checklist.json)
    @staticmethod
    def load_checklist(result_path : str) -> Dict[str, Any]:
        # check file path and file
        assert os.path.exists(result_path)
        file_name = os.path.join(result_path, 'checklist.json')
        assert os.path.isfile(file_name)
        # load
        checklist_file = open(file_name, 'r')
        checklist = json.load(checklist_file)
        checklist_file.close()
        # return it
        return checklist

    # load a solution set
    @staticmethod
    def load_solution_set(file_name : str) -> Set[Any]:
        # check file exist
        assert os.path.isfile(file_name)
        # prepare an empty set
        solution_set = set()
        # read file
        file_in = open(file_name, 'r')
        for line in file_in.readlines():
            line = line.strip('\n\r')
            tmp_tuple = to_tuple(line)
            solution_set.add(tmp_tuple)
        file_in.close()
        # return it
        return solution_set

    # load a solution as jmetal solution list
    @staticmethod
    def load_jmetal_solution_list(file_name : str) -> List[Solution]:
        # load result set
        solution_set = ResultHandler.load_solution_set(file_name)
        # convert them to jmetal solution
        solutions = []
        for solution in list(solution_set):
            jmetal_solution = ResultHandler.to_jmetal_solution(solution)
            solutions.append(jmetal_solution)
        # return it
        return solutions

    # convert tuple solution to jmetal Solution
    @staticmethod
    def to_jmetal_solution(tuple_solution) -> FloatSolution:
        vector = [round(float(x), 2) for x in tuple_solution]
        solution = FloatSolution([], [], len(vector))
        solution.objectives = vector
        return solution

    # convert tuple solution set to jmetal Solution list
    @staticmethod
    def to_jmetal_solution_list(tuple_solutions) -> List[FloatSolution]:
        solutions = []
        for tuple_solution in list(tuple_solutions):
            solutions.append(ResultHandler.to_jmetal_solution(tuple_solution))
        return solutions
    
    # build true front and str mapping
    @staticmethod
    def build_true_front(\
        true_front : NonDominatedSolutionsArchive, \
        true_front_map : Dict[str, Solution], \
        solution_list : List[Solution]) -> Tuple[NonDominatedSolutionsArchive, Dict[str, Solution]]:
        # make true front
        for solution in solution_list:
            true_front.add(solution)
            true_front_map[str(solution.objectives)] = solution
        # return them
        return true_front, true_front_map

    # convert solution list to numpy array
    @staticmethod
    def to_numpy_array(solutions : List[Solution]) -> np.array :
        return np.array([solutions[i].objectives for i in range(len(solutions))])

    # find reference points
    @staticmethod
    def find_reference_point(solutions: List[Solution]) -> List[float]:
        # get solution widths
        width = len(solutions[0].objectives)
        # prepare result list
        reference_point = []
        for ite in range(width):
            reference_point.append(max([solutions[i].objectives[ite] for i in range(len(solutions))])+1.0)
        # return it
        return reference_point

    # Hyper Volume indicator
    @staticmethod
    def hv(true_front : NonDominatedSolutionsArchive, solution_list : List[Solution]) -> float:
        # prepare reference point and indicator
        reference_point = ResultHandler.find_reference_point(true_front.solution_list)
        indicator = HyperVolume(reference_point)
        mod = np.prod(reference_point)
        # prepare solution list in numpy array
        solutions = ResultHandler.to_numpy_array(solution_list)
        # calculate
        return indicator.compute(solutions)/mod
    
    # Inverted Generational Distance
    @staticmethod
    def igd(true_front : NonDominatedSolutionsArchive, solution_list : List[Solution]) -> float:
        # prepare indicator
        array_true_front = ResultHandler.to_numpy_array(true_front.solution_list)
        indicator = InvertedGenerationalDistance(array_true_front)
        # calculate
        solutions = ResultHandler.to_numpy_array(solution_list)
        return indicator.compute(solutions)
    
    # Evenness
    @staticmethod
    def evenness(true_front : NonDominatedSolutionsArchive, solution_list : List[Solution]) -> float:
        # prepare reference point and indicator
        reference_point = ResultHandler.find_reference_point(true_front.solution_list)
        indicator = EvennessIndicator(reference_point)
        # calculate
        return indicator.compute(solution_list)

    # load solutions into self result
    def load_solutions(self) -> None:
        for name in self.names:
            # prepare path
            file_path = os.path.join(self.out_path, name)
            for ite in range(self.ite_num):
                file_name = os.path.join(file_path, str(ite)+'.txt')
                self.result[name][str(ite)]['solutions'] = ResultHandler.load_jmetal_solution_list(file_name)

    # load things from results to content
    def load_result_to_content(self) -> None:
        for name in self.names:
            self.content[name] = dict()
            self.content[name]['all'] = dict()
            # count runtime and solution number
            runtime = .0
            solution_number = 0
            for ite in range(self.ite_num):
                self.content[name][str(ite)] = dict()
                solution_number += self.result[name][str(ite)]['solution number']
                runtime += self.result[name][str(ite)]['runtime']
                self.content[name][str(ite)]['solution number'] = \
                    self.result[name][str(ite)]['solution number']
                self.content[name][str(ite)]['runtime'] = \
                    self.result[name][str(ite)]['runtime']
            # assign to 'all'
            self.content[name]['all']['solution number'] = solution_number
            self.content[name]['all']['runtime'] = runtime

    # get content
    def get_content(self) -> Dict[str, Any]:
        return self.content

    # dump content
    def dump(self, file_name : str = 'content.json') -> None:
        content_file = open(os.path.join(self.out_path, file_name), 'w+')
        json_object = json.dumps(self.content, indent = 4)
        content_file.write(json_object)
        content_file.close()

    # read content, do not store in self.content but return
    @staticmethod
    def load(path_name : str, file_name : str = 'content.json') -> Dict[str, Any]:
        content_file = open(os.path.join(path_name, file_name), 'r')
        json_object = json.load(content_file)
        content_file.close()
        return json_object

# analyzer, used to calculate non-dominated solutions, and some indicators scores
# such as IGD, HV, Evenness
class Analyzer(ResultHandler):
    # initialize
    def __init__(self, result_path : str, names : List[str], ite_num : int = 1):
        # super initialization will load the checklist as result
        # and load solutions as jmetal solution list in self.result
        # and load runtime, solution number to content
        # in this class, we see content as our analysis result
        super().__init__(result_path, names, ite_num)
        # prepare members
        self.__true_front = dict()
        self.__true_front_map = dict()
        self.__pareto = dict()
        # build true front
        for name in names:
            # build true front
            self.build_each_true_front(name)
            # sort non-dominated solutions
            self.sort_each_non_dominated_solutions(name)
            # caculate indicators
            self.content[name]['all']['igd'] = \
                self.igd(self.__true_front[name], self.__pareto[name])
            self.content[name]['all']['hv'] = \
                self.hv(self.__true_front[name], self.__pareto[name])
            self.content[name]['all']['evenness'] = \
                self.evenness(self.__true_front[name], self.__pareto[name])
            # dump
            self.dump('analysis.json')

    # build true front for each name
    def build_each_true_front(self, name : str) -> None:
        self.__true_front[name] = NonDominatedSolutionsArchive()
        self.__true_front_map[name] = dict()
        for ite in range(self.ite_num):
            solutions = self.result[name][str(ite)]['solutions']
            self.__true_front[name], self.__true_front_map[name] = \
                    self.build_true_front(self.__true_front[name], self.__true_front_map[name], solutions)

    # sort non dominated solutions for each name
    def sort_each_non_dominated_solutions(self, name : str) -> None:
        contained : Set[str] = set()
        self.__pareto[name] = []
        for ite in range(self.ite_num):
            self.content[name][str(ite)]['nd'] = 0
            solution_list = self.result[name][str(ite)]['solutions']
            for slt in solution_list:
                slt_key = str(slt.objectives)
                if slt_key in self.__true_front_map[name]:
                    self.content[name][str(ite)]['nd'] += 1
                    if slt_key not in contained:
                        self.__pareto[name].append(slt)
                        contained.add(slt_key)
                    # indicate no else statement here
                else:
                    assert not self.__true_front[name].add(slt)
        self.content[name]['all']['nd'] = len(self.__pareto[name])

# comparator, used to compare multipule solutions sets
# calculate non-dominated solutions, and some indicators scores
# such as IGD, HV, Evenness
class Comparator(ResultHandler):
    # initialize
    # Comparator will read out_path/checklist.json automaticly
    # and find the results you want to compare inside this folder
    def __init__(self, out_path : str, names : List[str], ite_num : int = 1):
        # super initialization will load the checklist as result
        # and load solutions as jmetal solution list in self.result
        # and load runtime, solution number to content
        # in this class, we see content as our comparison result
        super().__init__(out_path, names, ite_num)
        # prepare true front 
        self.__true_front = dict()
        self.__true_front_map = dict()
        self.__pareto = dict()
        # parser the names and classify them by project name
        self.which_names, self.which_project = self.parse_names(names)
        # convert content to project ordered format
        self.convert_content()
        # build true front
        self.build_all_true_front()
        # sort all non dominated solutions
        self.sort_all_non_dominated_solutions()
        # calculate scores
        self.evaluate_all()

    # parse names
    @staticmethod
    def parse_names(names : List[str]) -> Tuple[Dict[str, List[str]], Dict[str, str]]:
        # prepare project order and name order dict
        which_names = dict()
        which_project = dict()
        # parse
        for name in names:
            project_name = Runner.dename(name)['project']
            if project_name in which_names:
                which_names[project_name].append(name)
            else:
                which_names[project_name] = [name]
            which_project[name] = project_name
        return which_names, which_project

    # convert content to project ordered format
    def convert_content(self) -> None:
        neo_content = dict()
        for project_name, name_list in self.which_names.items():
            neo_content[project_name] = dict()
            for name in name_list:
                neo_content[project_name][name] = deepcopy(self.content[name])
        self.content = neo_content

    # build front using each sets of solutions
    # each project a true_front (and true_front_map)
    def build_all_true_front(self) -> None:
        for project_name, name_list in self.which_names.items():
            self.__true_front[project_name] = NonDominatedSolutionsArchive()
            self.__true_front_map[project_name] = dict()
            for name in name_list:
                for ite in range(self.ite_num):
                    solutions = self.result[name][str(ite)]['solutions']
                    self.__true_front[project_name], self.__true_front_map[project_name] = \
                        self.build_true_front(self.__true_front[project_name], self.__true_front_map[project_name], solutions)
    
    # sort non dominated solutions
    def sort_all_non_dominated_solutions(self) -> None:
        for project_name, name_list in self.which_names.items():
            for name in name_list:
                contained = set()
                self.__pareto[name] = []
                for ite in range(self.ite_num):
                    self.content[project_name][name][str(ite)]['nd'] = 0
                    solution_list = self.result[name][str(ite)]['solutions']
                    for slt in solution_list:
                        slt_key = str(slt.objectives)
                        if slt_key in self.__true_front_map[project_name]:
                            self.content[project_name][name][str(ite)]['nd'] += 1
                            if slt_key not in contained:
                                self.__pareto[name].append(slt)
                                contained.add(slt_key)
                            # indicate no else statement here
                        else:
                            assert not self.__true_front[project_name].add(slt)
                self.content[project_name][name]['all']['nd'] = len(self.__pareto[name])
            
    # calculate all scores
    def evaluate_all(self):
        for project_name, name_list in self.which_names.items():
            for name in name_list:
                # caculate indicators
                self.content[project_name][name]['all']['igd'] = \
                    self.igd(self.__true_front[project_name], self.__pareto[name])
                self.content[project_name][name]['all']['hv'] = \
                    self.hv(self.__true_front[project_name], self.__pareto[name])
                self.content[project_name][name]['all']['evenness'] = \
                    self.evenness(self.__true_front[project_name], self.__pareto[name])
                # dump
                self.dump('comparison.json')