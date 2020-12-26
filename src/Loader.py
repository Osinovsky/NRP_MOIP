#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Loader.py, created: 2020.10.31
# last modified: 2020.12.26
#

from typing import List, Tuple, Union, Dict
from os.path import join
from csv import reader
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


class ReleasePlannerProblem:
    """ [summary] record MS Word and ReleasePlanner Problem
    """
    def __init__(self) -> None:
        """__init__ [summary] define members
        """
        # costs of requirements
        self.cost: List[int] = []
        # weight of stakeholders
        self.weight: List[int] = []
        # coupling
        self.couplings: List[Tuple[int, int]] = []
        # requirements precedes, xi -> xj pair
        self.precedes: List[Tuple[int, int]] = []
        # profit, (requirement, stakeholder) -> value
        self.profit: List[Tuple[int, int, int]] = []
        # urgency, (requirement, stakeholder) -> value
        self.urgency: List[Tuple[int, int, int]] = []


# dataset types
ProblemType = Union[XuanProblem, ReleasePlannerProblem]


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

    @staticmethod
    def load_MSWord(name: str) -> ReleasePlannerProblem:
        """load_MSWord [summary] load MSWord NRP instance

        Args:
            name (str): [description] file path

        Returns:
            RealsePlannerProblem: [description]
        """
        return Loader.load_rp(name)

    @staticmethod
    def load_ReleasePlanner(name: str) -> ReleasePlannerProblem:
        """load_ReleasePlanner [summary] load ReleasePlanner NRP instance

        Args:
            name (str): [description] file path

        Returns:
            RealsePlannerProblem: [description]
        """
        return Loader.load_rp(name)

    @staticmethod
    def parse_comma_list(line: str) -> List[str]:
        return [e for e in line.strip(' ').split(',') if e]

    @staticmethod
    def load_rp(name: str) -> ReleasePlannerProblem:
        """load_rp [summary] load MSWord and ReleasePlanner datasets

        Args:
            name (str): [description] dataset file path

        Returns:
            RealsePlannerProblem: [description] the raw problem
        """
        # prepare the problem
        problem = ReleasePlannerProblem()
        # find the data set path
        data_path = name
        # prepare three files
        requirement_file = join(data_path, 'requirements.csv')
        stakeholder_file = join(data_path, 'stakeholders.csv')
        value_file = join(data_path, 'value.csv')
        urgency_file = join(data_path, 'urgency.csv')
        # read requirement file and make cost, couplings and precedes
        tmp_cost: Dict[str, int] = {}
        tmp_couplings: Dict[str, List[str]] = {}
        tmp_precedes: Dict[str, List[str]] = {}
        with open(requirement_file, 'r') as req_file:
            csv = reader(req_file, delimiter='|', skipinitialspace=True)
            for row in csv:
                if not row:
                    break
                row = [e.strip(' ') for e in row]
                name, cost, couplings, precedes = row
                # check name
                assert name not in tmp_cost
                assert name not in tmp_couplings
                assert name not in tmp_precedes
                # add into tmp dicts
                tmp_cost[name] = int(cost)
                tmp_couplings[name] = Loader.parse_comma_list(couplings)
                tmp_precedes[name] = Loader.parse_comma_list(precedes)
            req_file.close()
        # encode requirments with code and make cost
        remap: Dict[str, int] = {}
        for index, req in enumerate(tmp_cost):
            remap[req] = index
            problem.cost.append(tmp_cost[req])
        for req in tmp_cost:
            assert problem.cost[remap[req]] == tmp_cost[req]
        # make coupling
        for req in tmp_couplings:
            if not tmp_couplings[req]:
                continue
            for coupling in tmp_couplings[req]:
                if coupling not in remap:
                    print()
                    print(coupling)
                    print(remap)
                problem.couplings.append((remap[req], remap[coupling]))
        # make precedes
        for req in tmp_precedes:
            if not tmp_precedes[req]:
                continue
            for precede in tmp_precedes[req]:
                problem.precedes.append((remap[req], remap[precede]))
        # read stakeholder file and make weight
        with open(stakeholder_file, 'r') as sh_file:
            csv = reader(sh_file, delimiter='|', skipinitialspace=True)
            for index, row in enumerate(csv):
                if not row:
                    break
                row = [e.strip(' ') for e in row]
                problem.weight.append(int(row[0]))
        # read value file and make profit
        with open(value_file, 'r') as val_file:
            csv = reader(val_file, delimiter='|', skipinitialspace=True)
            for row in csv:
                if not row:
                    break
                row = [e.strip(' ') for e in row]
                for stakeholder in range(len(problem.weight)):
                    profit_triple = \
                        (remap[row[0]], stakeholder, int(row[stakeholder + 1]))
                    problem.profit.append(profit_triple)
        # read urgency file and make profit
        with open(urgency_file, 'r') as urg_file:
            csv = reader(urg_file, delimiter='|', skipinitialspace=True)
            for row in csv:
                if not row:
                    break
                row = [e.strip(' ') for e in row]
                for stakeholder in range(len(problem.weight)):
                    urgency_triple = \
                        (remap[row[0]], stakeholder, int(row[stakeholder + 1]))
                    problem.urgency.append(urgency_triple)
        # return
        return problem
