#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Loader.py, created: 2020.10.31
# last modified: 2020.10.31
#

from typing import List, Tuple, Union
from src.Config import Config


# types
# costs of requirements, level x [(requirement id, cost)]
XuanCost = List[List[Tuple[int, int]]]
# dependencies of requirements per level, [(from, to)]
XuanDependency = List[Tuple[int, int]]
# number of customers, [(custrom id, profit, [requirements])]
XuanCustomer = List[Tuple[int, int, List[int]]]


class XuanProblem:
    """ [summary] record classic and realistic nrp
    """
    def __init__(self) -> None:
        """__init__ [summary] define members
        """
        # costs of requirements, level x [(requirement id, cost)]
        self.cost: XuanCost = []
        # dependencies of requirements per level, [(from, to)]
        self.dependencies: XuanDependency = []
        # number of customers, [(custrom id, profit, [requests])]
        self.customers: XuanCustomer = []


# dataset types
ProblemType = Union[XuanProblem]


class Loader:
    """
    [summary]
    Loader is used to handle raw datasets
    """
    def __init__(self):
        """__init__ [summary] define some members
        """
        pass

    def load(self, name: str) -> ProblemType:
        """load [summary] load a certain dataset
        Args:
            name (str): [description] dataset name (stored in index.json)

        Returns:
            XuanProblem: [description] loaded raw problem
        """
        # load the config
        config = Config()
        # parse the keyword
        keyword = config.parse_keyword(name)
        # get the file name
        file_name = config.dataset[name]
        #  load from the dataset
        return getattr(Loader, 'load_{}'.format(keyword))(file_name)

    @staticmethod
    def load_classic(name: str) -> XuanProblem:
        """load_classic [summary] load classic

        Args:
            name (str): [description] project name

        Returns:
            XuanProblem: [description] loaded raw problem
        """
        return Loader.load_xuan(name)

    @staticmethod
    def load_realistic(name: str) -> XuanProblem:
        """load_realistic [summary] load realistic nrps

        Args:
            name (str): [description] project name

        Returns:
            XuanProblem: [description] loaded raw problem
        """
        return Loader.load_xuan(name)

    @staticmethod
    def load_xuan(name: str) -> XuanProblem:
        """load_xuan [summary] load classic and realistic nrps

        Args:
            name (str): [description] project name

        Returns:
            XuanProblem: [description] loaded raw problem
        """
        # prepare xuan problem
        problem = XuanProblem()
        # open the file
        with open(name, 'r') as fin:
            # level of requirements
            level = int(fin.readline())
            # employ an encoder for encoding requirements
            encoder = 1
            for _ in range(level):
                # requirements in current level
                requirements_num = int(fin.readline())
                # read requirements costs in current level
                line_cost = [int(x) for x in fin.readline().split(' ')
                             if x != '' and x != '\n']
                cost_line: List[Tuple[int, int]] = []
                # make (id, cost) for each requirement
                for cost in line_cost:
                    cost_line.append((encoder, cost))
                    encoder += 1
                # ... and append this line into cost
                problem.cost.append(cost_line)
                # requirements_num should equal to costs read from file
                assert requirements_num == len(problem.cost[-1])
            # number of dependencies
            dependencies_num = int(fin.readline())
            for _ in range(dependencies_num):
                # read dependence x -> y
                dep_line = [int(x) for x in
                            fin.readline().split(' ') if x != '' and x != '\n']
                # should be exactly 2
                assert len(dep_line) == 2
                # append to dependencies
                problem.dependencies.append((dep_line[0], dep_line[1]))
            # dependencies_num should match exact the dependencies we read
            assert dependencies_num == len(problem.dependencies)
            # read customers num
            customers_num = int(fin.readline())
            # we employ a encoder for helping marking customers
            encoder = 1
            for _ in range(customers_num):
                line = [x for x in fin.readline().split(' ')
                        if x != '' and x != '\n']
                # parse the line, it's formatted as profit
                # number of requirements and the requirements
                profit = int(line[0])
                require_num = int(line[1])
                require_list = [int(x) for x in line[2:]]
                # require_num should equal to require_list length
                assert require_num == len(require_list)
                # load into problem.customers
                problem.customers.append((encoder, profit, require_list))
                # ... and then, increase encoder
                encoder += 1
            # close file in the end of courses
            fin.close()
        # end with open
        return problem
