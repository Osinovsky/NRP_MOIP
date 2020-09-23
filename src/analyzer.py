# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# analyzer.py, created: 2020.09.22   #
# Last Modified: 2020.09.23          #
# ################################## #

from typing import *
import json
import os
from ast import literal_eval as to_tuple
from config import *

# analyzer, used to compare multipule solutions sets
# calculate non-dominated solutions, and some indicators scores
# such as IGD, HV, Evenness
class Analyzer:
    # initialize
    # Analyzer will read out_path/checklist.json automaticly
    # and find the results you want to compare inside this folder
    def __init__(self, out_path : str, names : List[str], ite_num : int = 1):
        # load the checklist
        self.__results = self.load_checklist(out_path, names)
        # load results files
        for name in names:
            file_name = os.path.join(out_path, name+'.txt')
            self.__results[name]['solutions'] = self.load_solutions(file_name)

    # get results
    def content(self):
        return self.__results

    # check if files are available and return checklist
    @staticmethod
    def load_checklist(out_path : str, names : List[str]) -> Dict[str, Any]:
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
            assert os.path.exists(os.path.join(out_path, name+'.txt'))
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

# Just for DEBUG
analyzer = Analyzer(RESULT_PATH, ['classic_1_binary_epsilon', 'realistic_g4_single_single_b0.3'])
print(analyzer.content())