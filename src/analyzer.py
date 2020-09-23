# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# analyzer.py, created: 2020.09.22   #
# Last Modified: 2020.09.23          #
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

# analyzer, used to compare multipule solutions sets
# calculate non-dominated solutions, and some indicators scores
# such as IGD, HV, Evenness
class Analyzer:
    # initialize
    # Analyzer will read out_path/checklist.json automaticly
    # and find the results you want to compare inside this folder
    def __init__(self, out_path : str, names : List[str], ite_num : int = 1):
        # load the checklist
        self.__results = self.load_checklist(out_path, names, ite_num)
        # load results files
        for name in names:
            exact_path = os.path.join(out_path, name)
            for ite in range(ite_num):
                file_name = os.path.join(exact_path, str(ite)+'.txt')
                self.__results[name][str(ite)]['solutions'] = self.load_solutions(file_name)
        
        # prepare the member variables
        self.pareto : Dict[str, List[Solution]] = dict()
        self.pareto_map : Dict[str, Dict[int, List[Solution]]] = dict()
        self.true_front: Archive = NonDominatedSolutionsArchive()
        self.true_front_map: Dict[str, Solution] = {}
        # initialize
        for name in names:
            self.pareto[name] = []
            self.pareto_map[name] = dict()
            for ite in range(ite_num):
                self.pareto_map[name][ite] = None
        # scores, comparison is strored as
        # comparison[project_name][str(certain_iteration)/'all'][<score entry>]
        # <score entry> \in \{'nd', 'igd', 'hv', 'evenness' \}
        self.comparison = dict()
        # initialize the comparison
        self.initialize_comparison(names, ite_num)

        # load runtimes
        self.load_runtime(names, ite_num)
        # load result to true front and pareto map
        self.load_true_front(names, ite_num)
        # build true front map
        self.build_map_for_front()
        # sort solutions for getting non-dominated solutions
        self.sort_nondominated_solutions(names, ite_num)

        # evaluation
        self.evaluation(names, ite_num)

        # dump to file
        self.dump_comparison(out_path)

    # get results
    def content(self):
        return self.__results, self.comparison

    # initialize members
    def initialize_comparison(self, names : List[str], ite_num : int) -> None:
        for name in names:
            self.comparison[name] = dict()
            self.comparison[name]['all'] = dict()
            self.comparison[name]['all']['runtime'] = .0
            self.comparison[name]['all']['nd'] = .0
            self.comparison[name]['all']['igd'] = .0
            self.comparison[name]['all']['hv'] = .0
            self.comparison[name]['all']['evenness'] = .0
            for ite in range(ite_num):
                self.comparison[name][str(ite)] = dict()
                self.comparison[name][str(ite)]['runtime'] = .0
                self.comparison[name][str(ite)]['nd'] = .0
                self.comparison[name][str(ite)]['igd'] = .0
                self.comparison[name][str(ite)]['hv'] = .0
                self.comparison[name][str(ite)]['evenness'] = .0

    # check if files are available and return checklist
    @staticmethod
    def load_checklist(out_path : str, names : List[str], ite_num : int) -> Dict[str, Any]:
        # check if files are available
        assert os.path.exists(out_path)
        assert os.path.exists(os.path.join(out_path, 'checklist.json'))
        # load checklist file
        checklist_file = open(os.path.join(out_path, 'checklist.json'), 'r')
        checklist = json.load(checklist_file)
        checklist_file.close()
        # check files
        for name in names:
            assert name in checklist
            exact_path = os.path.join(out_path, name)
            assert os.path.exists(exact_path)
            for ind in range(ite_num):
                assert os.path.exists(os.path.join(exact_path, str(ind)+'.txt'))
        # return the checklist
        return checklist

    # load the soultions file
    @staticmethod
    def load_solutions(file_name : str) -> Set[Any]:
        results = set()
        with open(file_name, 'r') as fin:
            for line in fin.readlines():
                line = line.strip('\n\r')
                results.add(to_tuple(line))
            fin.close()
        return results

    # load runtime from result to comparison
    def load_runtime(self, names : List[str], ite_num : int) -> None:
        for name in names:
            all_time = .0
            for ite in range(ite_num):
                each_time = self.__results[name][str(ite)]['runtime']
                all_time += each_time
                self.comparison[name][str(ite)]['runtime'] = each_time
            self.comparison[name]['all']['runtime'] = all_time

    # load result to true front and pareto map
    # this function is copied from my adviser's project
    def load_true_front(self, names : List[str], ite_num : int) -> None:
        for name in names:
            for ite in range(ite_num):
                self.pareto_map[name][ite] = []
                for slt in list(self.__results[name][str(ite)]['solutions']):
                    vector = [round(float(x), 2) for x in slt]
                    solution = FloatSolution([], [], len(vector))
                    solution.objectives = vector
                    # append to this pareto map and add to true front
                    self.pareto_map[name][ite].append(solution)
                    self.true_front.add(solution)

    # build map for front
    # this function is copied from my adviser's project
    def build_map_for_front(self) -> None:
        front_size = self.true_front.size()
        for ite in range(front_size):
            current : Solution =  self.true_front.get(ite)
            current_key : str = str(current.objectives)
            self.true_front_map[current_key]= current

    # self.trueFront, self.trueFrontMap, self.paretoMap[name]
    # trueFront : NonDominatedSolutionsArchive, trueFrontMap: Dict[str, Solution], paretoMap: Dict[int,List[Solution]]
    # sort non-dominated solutions
    # this function is copied from my adviser's project
    def sort_nondominated_solutions(self, names : List[str], ite_num : int) -> None:
        for name in names:
            self.pareto[name] : List[Solution] = []
            contained : Set[str] = set()
            for ite in range(ite_num):
                current_set = self.pareto_map[name][ite]
                for slt in current_set:
                    slt_key = str(slt.objectives)
                    if slt_key in self.true_front_map:
                        if slt_key not in contained:
                            self.pareto[name].append(slt)
                            contained.add(slt_key)
                        self.comparison[name][str(ite)]['nd'] += 1
                    else:
                        is_nd = self.true_front.add(slt)
                        assert not is_nd
            # calculate nd for 'name' not for 'name''ite'
            self.comparison[name]['all']['nd'] = len(self.pareto[name])

    # find reference point for hv
    # this function is copied from my adviser's project
    def findReferencePoint(self, solutions: List[Solution])-> List[float]:
        objSize = len(solutions[0].objectives)
        minValue= -sys.float_info.max
        referencePoint: List[float] =  [minValue for i in range(objSize)]
        for solution in solutions:
            currentObjectives=solution.objectives
            for index in range(objSize): 
                currentValue = currentObjectives[index]
                if currentValue > referencePoint[index]:
                    referencePoint[index] = currentValue
        for value in referencePoint:
            value = value+1.0
        return referencePoint

    @staticmethod
    def to_numpy_array(solutions : List[Solution]):
        return np.array([solutions[i].objectives for i in range(len(solutions))])

    # caculate indicator scores
    def evaluation(self, names : List[str], ite_num : int) -> None:
        # convert solutions(front, pareto...) numpy array
        # true front
        true_front = self.to_numpy_array(self.true_front.solution_list)
        # prepare indicators
        IGD_indicator = InvertedGenerationalDistance(true_front)
        refer_point : List[float] = self.findReferencePoint(self.true_front.solution_list)
        mod = np.prod(refer_point)
        HV_indicator = HyperVolume(refer_point)
        E_indicator = EvennessIndicator(refer_point)
        # paretos
        for name in names:
            # pareto[name]
            tmp = self.to_numpy_array(self.pareto[name])
            self.comparison[name]['all']['igd'] = IGD_indicator.compute(tmp)
            self.comparison[name]['all']['hv'] = HV_indicator.compute(tmp)/mod
            self.comparison[name]['all']['evenness'] = E_indicator.compute(self.pareto[name])
            
        # pareto maps (each iteration)
        for name in names:
            for ite in range(ite_num):
                # pareto_map[name][ite]
                tmp = self.to_numpy_array(self.pareto_map[name][ite])
                self.comparison[name][str(ite)]['igd'] = IGD_indicator.compute(tmp)
                self.comparison[name][str(ite)]['hv'] = HV_indicator.compute(tmp)/mod
                self.comparison[name][str(ite)]['evenness'] = E_indicator.compute(self.pareto_map[name][ite])

    # dump comparison
    def dump_comparison(self, out_path : str) -> None:
        # result folder should already there
        assert os.path.exists(os.path.dirname(out_path))
        # write comparison
        comparison_file = open(os.path.join(out_path, 'comparison.json'), 'w+')
        json_object = json.dumps(self.comparison, indent = 4)
        comparison_file.write(json_object)
        comparison_file.close()

# Just for DEBUG
# analyzer = Analyzer(RESULT_PATH, ['classic_1_binary_epsilon', 'realistic_g4_binary_epsilon'], 10)
# result, comparison = analyzer.content()
# print(result)
# print(comparison)