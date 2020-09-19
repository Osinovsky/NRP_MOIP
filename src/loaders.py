# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# loaders.py, created: 2020.08.25    #
# Last Modified: 2020.09.18          #
# ################################## #

import os
from typing import *
from config import *
import xlrd

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
    def load_triple(self, obj_file : str, req_file : str, sreq_file : str) -> List[List[Tuple[str, str, str]]]:
        # load datas
        self.__levels.append(self.table_separated_file_loader(obj_file))
        self.__levels.append(self.table_separated_file_loader(req_file))
        self.__levels.append(self.table_separated_file_loader(sreq_file))
        # return the content
        return self.content()
    
    # content 
    def content(self) -> List[List[Tuple[str, str, str]]]:
        return self.__levels

# read from Baan dataset
class BaanLoader:
    # initialize
    def __init__(self) -> None:
        # store (requirement, team) -> int 
        # which means manday need for team to develop on requirement
        self.__cost : Dict[Tuple[int, int], int] = {}
        # profit
        self.__profit : Dict[int, int] = {}

    # return content
    def content(self) -> Tuple[Dict[Tuple[int, int], int], Dict[int, int]]:
        return (self.__cost, self.__profit)

    # load
    def load(self) -> Tuple[Dict[Tuple[int, int], int], Dict[int, int]]:
        # load from Baarn file, 1, 4  ... 1, 21
        #                       100,4 ... 100, 21
        table = self.__load_xls((1, 4), (101, 22))
        # tranverse all cell
        for requirements_id in range(1, 101):
            requirements_id -= 1
            # cost
            for team_id in range(4, 21):
                team_id -= 4
                num_str = table[requirements_id][team_id]
                # filter cell not empty and not zero
                if num_str != '' and int(num_str) != 0:
                    self.__cost[(requirements_id, team_id)] = int(table[requirements_id][team_id])
            # profit
            self.__profit[requirements_id] = int(table[requirements_id][-1])
        # return content
        return self.content()      
        
    # load xls file into list[list](2d string table)
    def __load_xls(self, \
        left_up : Tuple[int, int], \
        right_down : Tuple[int, int], \
        file_name : str = BAAN_FILE_NAME, \
        sheet_name : str = 'all requirements' \
        ) -> List[List[str]]:
        # read xls file
        data = xlrd.open_workbook(BAAN_FILE_NAME)
        table = data.sheet_by_name(sheet_name)
        # check for left_up and right_down
        assert left_up[0] < right_down[0] and left_up[1] < right_down[1] \
           and left_up[0] >= 0 and left_up[1] >= 0
        # prepare the cell translator, it will give out a solution on 
        # which type the cell is and transfer it into str 
        translator = {
            0 : lambda x : '', # empty -> '' 
            1 : lambda x : x.value,  # str -> str
            2 : lambda x : str(int(x.value)), # int -> str, actually it's float but what we need is only int
            # others should not appear
        }
        # load each cell in sheet
        lines : List[List[str]] = []
        for i in range(left_up[0], right_down[0]):
            line : List[str] = []
            for j in range(left_up[1], right_down[1]):
                cell = table.cell(i, j)
                # we assert there only empty, str and number in sheet
                assert cell.ctype <= 2 and cell.ctype >= 0
                line.append(translator[cell.ctype](cell))
            lines.append(line)
        # return result
        return lines
        
# Interface for loading files
class Loader:
    # initialization
    @classmethod
    def __init__(self, project_name : str):
        # check project name is in ALL_FILES_DICT
        assert project_name in ALL_FILES_DICT
        self.__project = project_name
        # construct a dict to choose loader
        self.__loaders = { \
            'classic' : Loader.__XuanLoader,\
            'realistic' : Loader.__XuanLoader, \
            'Motorola' : Loader.__MotorolaLoader, \
            'RALIC' : Loader.__RALICLoader, \
            'Baan' : Loader.__BaanLoader, \
        }
    
    # load
    @classmethod
    def load(self):
        for key, loader in self.__loaders.items():
            if self.__project.startswith(key):
                return loader(self.__project)

    # load from XuanLoader
    @staticmethod
    def __XuanLoader(project : str):
        # get content from XuanLoader
        loader = XuanLoader()
        cost, dependencies, customers = loader.load(ALL_FILES_DICT[project])
        # prepare results
        neo_cost = dict()
        neo_profit = dict()
        neo_dependencies = []
        neo_requests = []
        # there are many level in cost, we should collect them up
        for cost_line in cost:
            # iterate each element in this line
            for cost_pair in cost_line:
                # the key should be unique
                assert cost_pair[0] not in neo_cost
                # we convert cost as a int for generalizing
                neo_cost[cost_pair[0]] = int(cost_pair[1])
        # then, the customers' profit and the requirement pair list
        for customer in customers:
            # parse the tuple
            customer_id = customer[0]
            customer_requirement = customer[2]
            # add profit into self profit
            assert customer_id not in neo_profit
            neo_profit[customer_id] = int(customer[1])
            # construct (requirer, requiree) pairs and store
            assert customer_requirement # non-empty check
            for req in customer_requirement:
                neo_requests.append(tuple((customer_id, req)))
        # now we copy the dependencies
        neo_dependencies = list(set(dependencies))
        # return content
        return neo_cost, neo_profit, neo_dependencies, neo_requests

    # load from MotorolaLoader
    @staticmethod
    def __MotorolaLoader(project : str):
        loader = MotorolaLoader()
        return loader.load(ALL_FILES_DICT[project])
    
    # load from RALICLoader
    @staticmethod
    def __RALICLoader(project : str):
        loader = RALICLoader()
        # note that RALIC need 3 files
        files = ALL_FILES_DICT[project]
        return loader.load_triple(files['obj'], files['req'], files['sreq'])
    
    # load from BaanLoader
    @staticmethod
    def __BaanLoader(project : str):
        loader = BaanLoader()
        return loader.load()
