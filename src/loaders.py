# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# loaders.py, created: 2020.08.25    #
# Last Modified: 2020.08.31          #
# ################################## #

import os
from typing import *
from config import *

# type defining
# costs of requirements, level x [(requirement id, cost)]
XuanCost = List[List[Tuple[int, int]]]
# dependencies of requirements per level, [(from, to)]
XuanDependency = List[Tuple[int, int]]
# number of customers, [(custrom id, profit, [requirements])]
XuanCustomer = List[Tuple[int, int, List[int]]]

# datasets from Jifeng Xuan
class XuanLoader:
    # initialize
    def __init__(self) -> None:
        # costs of requirements, level x [(requirement id, cost)]
        self.__cost : XuanCost = []
        # dependencies of requirements per level, [(from, to)]
        self.__dependencies : XuanDependency = []
        # number of customers, [(custrom id, profit, [requirements])]
        self.__customers : XuanCustomer = []

    # load from file, the file format is given by example.txt
    def load(self, file_name : str) -> Tuple[XuanCost, XuanDependency, XuanCustomer]:
        with open(file_name, 'r') as fin:
            # level of requirements
            level = int(fin.readline())
            # employ an encoder for encoding requirements
            encoder = 1
            for ite in range(level):
                # requirements in current level
                requirements_num = int(fin.readline())
                # read requirements costs in current level
                line_cost = [int(x) for x in fin.readline().split(' ') if x != '' and x != '\n']
                cost_line = []
                # make (id, cost) for each requirement
                for cost in line_cost:
                    cost_line.append(tuple((encoder, cost)))
                    encoder += 1
                # ... and append this line into self cost
                self.__cost.append(cost_line)
                # requirements_num should equal to costs read from file
                assert requirements_num == len(self.__cost[-1])
            # number of dependencies
            dependencies_num = int(fin.readline())
            for ite in range(dependencies_num):
                # read dependence x -> y
                line = [int(x) for x in fin.readline().split(' ') if x != '' and x != '\n']
                # should be exactly 2 
                assert len(line) == 2
                # append to dependencies
                self.__dependencies.append(tuple(line))
            # dependencies_num should match exact the dependencies we read
            assert dependencies_num == len(self.__dependencies)
            # read customers num
            customers_num = int(fin.readline())
            # we employ a encoder for helping marking customers
            encoder = 1
            for ite in range(customers_num):
                line = [x for x in fin.readline().split(' ') if x != '' and x != '\n']
                # parse the line, it's formatted as profit, number of requirements and the requirements
                profit = int(line[0])
                require_num = int(line[1])
                require_list = [int(x) for x in line[2:]]
                # require_num should equal to require_list length
                assert require_num == len(require_list)
                # load into self.__customers
                self.__customers.append(tuple((encoder, profit, require_list)))
                # ... and then, increase encoder 
                encoder += 1
            # close file in the end of courses
            fin.close()
            return self.content()
    
    # provide data
    def content(self) -> Tuple[XuanCost, XuanDependency, XuanCustomer]:
        return (self.__cost, self.__dependencies, self.__customers)

# motorola loader
class MotorolaLoader:
    # initialize
    def __init__(self):
        self.__cost_revenue : List[Tuple[float, float]] = []
    # load data
    def load(self, file_name : str) -> List[Tuple[float, float]]:
        with open(file_name, 'r') as fin:
            # read into lines
            lines = fin.readlines()
            # for each line
            for line in lines:
                # parse the format (cost, revenue)
                line = [int(x) for x in line.split('\t') if x != '' and x != '\n']
                # should be 2 elements each line
                assert len(line) == 2
                # append
                self.__cost_revenue.append(tuple(line))
            fin.close()
            # return content
            return self.content()

    # read data
    def content(self) -> List[Tuple[float, float]]:
        return self.__cost_revenue

# RALIC loader
class RALICLoader:
    # initialize
    def __init__(self):
        # preprocess data file
        # There are three data file per dataset, but named as obj/req/sreq
        # actually they are three level of requirements
        self.__levels = []
    
    # load file with format tab separted
    def table_separated_file_loader(self, file_name : str) -> List[Tuple[str, str, str]]:
        results = []
        with open(file_name, 'r') as fin:
            # let us read all lines in file, because we don't know how many lines
            raw_file = fin.readlines()
            for line in raw_file:
                # skip empty line
                line = line.rstrip('\n\r')
                if line == '':
                    continue
                # parse the line as tab separated, triple-tuple
                tmp = tuple([x for x in line.split('\t')])
                # it should contain three elements per line
                assert len(tmp) == 3
                # append to result
                results.append(tmp)
            fin.close()
        return results

    # load from there files
    def load_triple(self, file_path : str, obj_file : str, req_file : str, sreq_file : str) -> List[List[Tuple[str, str, str]]]:
        # first of all, prepare the exact file names
        obj_file = os.path.join(file_path, obj_file)
        req_file = os.path.join(file_path, req_file)
        sreq_file = os.path.join(file_path, sreq_file)
        # load datas
        self.__levels.append(self.table_separated_file_loader(obj_file))
        self.__levels.append(self.table_separated_file_loader(req_file))
        self.__levels.append(self.table_separated_file_loader(sreq_file))
        # return the content
        return self.content()
    
    # content 
    def content(self) -> List[List[Tuple[str, str, str]]]:
        return self.__levels
        
# just a main for testing
if __name__ == "__main__":
    pass
    # try to load motorola
    # m_l = MotorolaLoader()
    # print(m_l.load(MOTOROLA_FILE_NAME))
    # try to load classic nrps
    # for file_name in CLASSIC_NRPS:
    #     file_name = os.path.join(CLASSIC_NRP_PATH, file_name)
    #     print(file_name)
    #     print('--------------------------------\n')
    #     c_l = XuanLoader()
    #     print(c_l.load(file_name))
    #     print('================================\n')
    # try to load realistic nrps
    # for file_name in REALISTIC_NRPS:
    #     file_name = os.path.join(REALISTIC_NRP_PATH, file_name)
    #     print(file_name)
    #     print('--------------------------------\n')
    #     c_l = XuanLoader()
    #     print(c_l.load(file_name))
    #     print('================================\n')
    # try to load RALIC nrps
    # r_l = RALICLoader()
    # print(r_l.load_triple(RALIC_PATH, RATEP_OBJ_FILE, RATEP_REQ_FILE, RATEP_SREQ_FILE))