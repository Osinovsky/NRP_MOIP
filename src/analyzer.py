# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# analyzer.py, created: 2020.09.24   #
# Last Modified: 2020.09.24          #
# ################################## #

from typing import *
import json
import os
import sys
from ast import literal_eval as to_tuple
from jmetal.core.solution import FloatSolution, Solution
from jmetal.util.archive import NonDominatedSolutionsArchive, Archive
from jmetal.core.quality_indicator import InvertedGenerationalDistance, HyperVolume
import numpy as np
from config import *
from evenness_indicator import EvennessIndicator

# result handling class
class ResultHandler:
    # members
    def __init__(self, result_path : str, names : List[str], ite_num : int = 1):
        # recording
        self.out_path = result_path
        self.names = names
        self.ite_num = ite_num
    
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
        results = set()
        # read file
        file_in = open(file_name, 'r')
        for line in file_in.readlines():
            line = line.strip('\n\r')
            tmp_tuple = to_tuple(line)
            results.add(tmp_tuple)
        file_in.close()
        # return it
        return results
    
    # load solutions sets for iterations
    @staticmethod
    def load_solution_sets(file_path : str, ite_num : int) -> Dict[int, Set[Any]]:
        # check path exist
        assert os.path.exists(file_path)
        # prepare a dict
        sets = dict()
        for ite in range(ite_num):
            sets[ite] = ResultHandler.load_solution_set(os.path.join(file_path, str(ite)+'.txt'))
        # return it
        return sets

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
        solution_list : List[Any]) -> Tuple[NonDominatedSolutionsArchive, Dict[str, Solution]]:
        # make true front
        for solution in solution_list:
            jmetal_solution = ResultHandler.to_jmetal_solution(solution)
            true_front.add(jmetal_solution)
            true_front_map[str(solution)] = jmetal_solution
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


# analyzer, used to calculate non-dominated solutions, and some indicators scores
# such as IGD, HV, Evenness
class Analyzer(ResultHandler):
    # initialize
    def __init__(self, result_path : str, names : List[str], ite_num : int = 1):
        super().__init__(result_path, names, ite_num)
        # load checklist and solutions
        self.result = self.load_checklist(result_path)
        for name in names:
            set_path = os.path.join(result_path, name)
            assert os.path.exists(set_path)
            self.result[name]['all'] = dict()
            self.result[name]['all']['solutions'] = []
            for ite in range(ite_num):
                file_name = os.path.join(set_path, str(ite)+'.txt')
                solution_list = list(self.load_solution_set(file_name))
                self.result[name][str(ite)]['solutions'] = solution_list
                self.result[name]['all']['solutions'] += solution_list
        # prepare analysis
        self.analysis = dict()
        for name in names:
            self.analysis[name] = dict()
            self.analysis[name]['all'] = dict()
            self.analysis[name]['all']['nd'] = 0
            for ite in range(ite_num):
                self.analysis[name][str(ite)] = dict()
                self.analysis[name][str(ite)]['nd'] = 0
        # prepare pareto
        self.__pareto = dict()
        # prepare true_front and true_front_map
        self.__true_front = dict()
        self.__true_front_map = dict()
        self.build_true_front_all()
        # sort nd solutions
        self.sort_non_dominated_solutions()
        # record solutions, runtimes and true front size
        for name in names:
            solution_count = 0
            runtime_count = 0.0
            for ite in range(ite_num):
                self.analysis[name][str(ite)]['solution number'] = self.result[name][str(ite)]['solution number']
                solution_count += self.result[name][str(ite)]['solution number']
                self.analysis[name][str(ite)]['runtime'] = self.result[name][str(ite)]['runtime']
                runtime_count += self.result[name][str(ite)]['runtime']
            self.analysis[name]['all']['solution number'] = solution_count
            self.analysis[name]['all']['runtime'] = runtime_count
    
    # get content
    def content(self):
        return self.analysis

    # build true front and record each name
    def build_true_front_all(self):
        for name in self.names:
            self.__true_front[name] = NonDominatedSolutionsArchive()
            self.__true_front_map[name] = dict()
            for ite in range(self.ite_num):
                solutions = self.result[name][str(ite)]['solutions']
                self.__true_front[name], self.__true_front_map[name] = \
                    self.build_true_front(self.__true_front[name], self.__true_front_map[name], solutions)

    # sort non dominated solutions
    def sort_non_dominated_solutions(self):
        for name in self.names:
            contained : Set[str] = set()
            self.__pareto[name] = []
            for ite in range(self.ite_num):
                solution_list = self.to_jmetal_solution_list(self.result[name][str(ite)]['solutions'])
                for slt in solution_list:
                    slt_key = str(slt)
                    if slt_key in self.__true_front_map[name]:
                        if slt_key not in contained:
                            self.__pareto[name].append(slt)
                            contained.add(slt_key)
                        self.analysis[name][str(ite)]['nd'] += 1
                    else:
                        is_nd = self.__true_front[name].add(slt)
                        assert not is_nd
            self.analysis[name]['all']['nd'] = len(self.__pareto[name])

    # calculate hv
    def calculate_hv(self):
        for name in self.names:
            solution_list = self.to_jmetal_solution_list(self.result[name]['all']['solutions'])
            self.analysis[name]['all']['hv'] = self.hv(self.__true_front[name], solution_list)

    # calculate igd
    def calculate_igd(self):
        for name in self.names:
            solution_list = self.to_jmetal_solution_list(self.result[name]['all']['solutions'])
            self.analysis[name]['all']['igd'] = self.igd(self.__true_front[name], solution_list)

    # calculate evenness
    def calculate_evenness(self):
        for name in self.names:
            solution_list = self.to_jmetal_solution_list(self.result[name]['all']['solutions'])
            self.analysis[name]['all']['evenness'] = self.evenness(self.__true_front[name], solution_list)

# comparator, used to compare multipule solutions sets
# calculate non-dominated solutions, and some indicators scores
# such as IGD, HV, Evenness
class Comparator:
    # initialize
    # Analyzer will read out_path/checklist.json automaticly
    # and find the results you want to compare inside this folder
    def __init__(self, out_path : str, names : List[str], ite_num : int = 1):
        pass