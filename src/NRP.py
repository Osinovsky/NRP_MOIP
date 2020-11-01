#
# DONG Shi, dongshi@mail.ustc.edu.cn
# NRP.py, created: 2020.10.31
# last modified: 2020.10.31
#

import os
import json
from copy import deepcopy
from functools import reduce
from math import ceil, floor
from typing import Dict, Tuple, List, Union, Set, Any
from Loader import Loader, XuanProblem
from src.Config import Config
from util.moipProb import MOIPProblem


class XuanNRP:
    def __init__(self) -> None:
        """__init__ [summary] record members
        """
        # customer -> profit
        self.profit: Dict[int, int] = dict()
        # requirement -> cost
        self.cost: Dict[int, int] = dict()
        # dependency, (x_i, x_j) denotes x_i -> x_j, x_i is precursor of x_j
        self.dependencies: List[Tuple[int, int]] = []
        # requests, customer -> requirement
        self.requests: List[Tuple[int, int]] = []


class NRPProblem:
    def __init__(self) -> None:
        """__init__ [summary] record members
        """
        # variables
        self.variables: List[int] = []
        # objectives
        self.objectives: List[Dict[int, float]] = []
        # inequations, lhs <= rhs
        self.inequations: List[Dict[int, float]] = []


# Type
NRPType = Union[XuanNRP]


class NextReleaseProblem:
    def __init__(self, project: str) -> None:
        """__init__ [summary] constuct basic nrp form from Loader

        Args:
            project (str): [description] project name
        """
        # project name
        self.__project = project

        # load config
        config = Config()
        keyword = config.parse_keyword(project)
        # construct NRP from dataset
        self.nrp = getattr(self, 'constuct_from_{}'.format(keyword))(project)
        # for MOIPProblem
        self.problem: MOIPProblem = None

    @staticmethod
    def construct_from_classic(project: str) -> XuanNRP:
        """construct_from_classic [summary] construct XuanNRP from classic dataset

        Args:
            project (str): [description] project name

        Returns:
            XuanNRP: [description] raw NRP (Xuan form)
        """
        return NextReleaseProblem.construct_from_xuan(project)

    @staticmethod
    def construct_from_realistic(project: str) -> XuanNRP:
        """construct_from_realistic [summary] construct XuanNRP from realistic dataset

        Args:
            project (str): [description] project name

        Returns:
            XuanNRP: [description] raw NRP (Xuan form)
        """
        return NextReleaseProblem.construct_from_xuan(project)

    @staticmethod
    def construct_from_xuan(project: str) -> XuanNRP:
        """construct_from_xuan [summary] construct XuanNRP from xuan dataset

        Args:
            project (str): [description] project name

        Returns:
            XuanNRP: [description] raw NRP (Xuan form)
        """
        # load from dataset
        loader = Loader()
        raw_problem: XuanProblem = loader.load(project)
        # prepare cost, profit, dependencies, requests
        nrp = XuanNRP()
        # constrcut from loader to nrp
        # there are many level in cost, we should collect them up
        for cost_line in raw_problem.cost:
            # iterate each element in this line
            for cost_pair in cost_line:
                # the key should be unique
                assert cost_pair[0] not in nrp.cost
                # we convert cost as a int for generalizing
                nrp.cost[cost_pair[0]] = int(cost_pair[1])
        # then, the customers' profit and the requirement pair list
        for customer in raw_problem.customers:
            # parse the tuple
            customer_id = customer[0]
            customer_requirement = customer[2]
            # add profit into self profit
            assert customer_id not in nrp.profit
            nrp.profit[customer_id] = int(customer[1])
            # construct (requirer, requiree) pairs and store
            assert customer_requirement  # non-empty check
            for req in customer_requirement:
                nrp.requests.append((customer_id, req))
        # now we copy the dependencies
        nrp.dependencies = list(set(raw_problem.dependencies))
        # return
        return nrp

    def __precursors(self, req_id: int) -> Set[int]:
        """__precursors [summary] find one requirement all precursors

        Args:
            req_id (int): [description] required requirement id

        Returns:
            Set[int]: [description] precurosrs
        """
        # find all depdency with right value as requst id input
        last_level = set([x[0] for x in self.nrp.dependencies
                          if x[1] == req_id])
        # check result
        if len(last_level) == 0:
            return last_level
        else:
            # find their dependecies each and merge their result
            # then convert then into set for dupicate elimination
            return last_level.union(
                set(reduce(lambda x, y: list(x) + list(y),
                           map(self.__precursors, last_level)))
            )

    def flatten_xuan(self) -> None:
        """flatten_xuan [summary] flatten dependencies,
        eliminate all dependencies between requirements
        """
        # of course depdencies should not be empty
        assert self.nrp.dependencies
        # copy a new requests from self.requests
        neo_requests = deepcopy(self.nrp.requests)
        # traverse requests
        for req in self.nrp.requests:
            # find all real requests
            dependencies = list(self.__precursors(req[1]))
            # add into new requests
            for dep in dependencies:
                if (req[0], dep) not in neo_requests:
                    neo_requests.append((req[0], dep))
        # change requests and clear dependencies
        self.nrp.requests = neo_requests
        self.nrp.dependencies.clear()

    def reencode_xuan(self) -> Tuple[Dict[int, int], Dict[int, int]]:
        """reencode_xuan [summary] classic and realistic reencode, single objective
            encoding will be compact and from 0

        Returns:
            Tuple[Dict[int, int], Dict[int, int]]: [description]
        """
        # assume that dependencies is empty
        assert not self.nrp.dependencies
        # employ an encoder
        encoder = 0
        # prepare a requirement encoder
        req_encoder = dict()
        neo_cost = dict()
        for req, cost in self.nrp.cost.items():
            assert req not in req_encoder
            req_encoder[req] = encoder
            neo_cost[encoder] = cost
            encoder += 1
        # prepare a customer encoder
        cus_encoder = dict()
        neo_profit = dict()
        for cus, profit in self.nrp.profit.items():
            assert cus not in cus_encoder
            cus_encoder[cus] = encoder
            neo_profit[encoder] = profit
            encoder += 1
        # apply them on requests
        neo_requests = []
        for cus, req in self.nrp.requests:
            neo_requests.append((cus_encoder[cus], req_encoder[req]))
        # change them all
        self.nrp.cost = neo_cost
        self.nrp.profit = neo_profit
        self.nrp.requests = neo_requests
        # return dicts
        return req_encoder, cus_encoder

    @staticmethod
    def dump(
        file_name: str,
        variables: List[int],
        objectives: List[Dict[int, int]],
        inequations: List[Dict[int, int]],
    ) -> None:
        """dump [summary] dump problem

        Args:
            file_name (str): [description] where to store
            variables (List[int]): [description] variables
            objectives (List[Dict[int, int]]): [description] objectives
            inequations (List[Dict[int, int]]): [description] inequations
        """
        # load config
        config = Config()
        # prepare a dict for storing all
        result: Dict[str, Any] = dict()
        # turn variables into dict
        result['variables'] = dict()
        for index, variable in enumerate(variables):
            result['variables'][str(index)] = variable
        # turn objectives into dict
        result['objectives'] = dict()
        for index, objective in enumerate(objectives):
            result['objectives'][str(index)] = objective
        # turn inequations into dict
        result['inequations'] = dict()
        for index, inequation in enumerate(inequations):
            result['inequations'][str(index)] = inequation
        # see if folder exists
        if not os.path.exists(config.dump_path):
            os.makedirs(config.dump_path)
        # add file_name on path
        file_name = os.path.join(config.dump_path, file_name)
        # open output file
        with open(file_name, 'w+') as out_file:
            # dump
            json_object = json.dumps(result, indent=4)
            out_file.write(json_object)
            # close the file
            out_file.close()

    @staticmethod
    def MOIP(
        variables: List[int],
        objectives: List[Dict[int, int]],
        inequations: List[Dict[int, int]]
    ) -> MOIPProblem:
        """MOIP [summary] construct MOIPProblem

        Args:
            variables (List[int]): [description]
            objectives (List[Dict[int, int]]): [description]
            inequations (List[Dict[int, int]]): [description]
        Returns:
            MOIPProblem: [description]
        """
        # use objectives make attribute matrix
        attribute_matrix = []
        for objective in objectives:
            line = [0] * (len(variables))
            for key, value in objective.items():
                line[key] = value
            # there was a constant_id = max_id + 1, then api do not work
            # so I assume there's no constant in objective
            attribute_matrix.append(line)
        # load into the MOIP
        # construct MOIP
        MOIP = MOIPProblem(len(objectives), len(variables), 0)
        # call load
        MOIP.load(objectives, inequations, dict(), False, None)
        # ...load manually
        MOIP.sparseInequationSensesList = ['L'] * len(inequations)
        MOIP.attributeMatrix = attribute_matrix
        # return
        return MOIP

    def model(self, form: str, option: Dict[str, Any]) -> MOIPProblem:
        """model [summary] modelling to MOIPProblem

        Args:
            form (str): [description] problem form
            option (Dict[str, Any]): [description]
        """
        # modelling with certain form
        return getattr(self, 'to_{}_form'.format(form))(option)

    def to_single_form(self, option: Dict[str, Any]) -> NRPProblem:
        """to_single_form [summary] only for classic nrps,
        form as basic single form as metioned in

        An Integer Linear Programming approach to the single
        and bi-objective Next Release Problem, NadarajenVeerapen
        https://doi.org/10.1016/j.infsof.2015.03.008

        Args:
            option (Dict[str, Any]): [description]

        Returns:
            NRPProblem (NRPProblem): [description]
        """
        # check dependencies
        assert not self.nrp.dependencies
        # check option
        assert 'b' in option and isinstance(option['b'], float)
        # prepare the NRPProblem, modelled nrp, mnrp
        mnrp = NRPProblem()
        # variables
        mnrp.variables = \
            list(self.nrp.cost.keys()) + list(self.nrp.profit.keys())
        # prepare objective coefs
        mnrp.objectives = [{k: -v for k, v in self.nrp.profit.items()}]
        # don't forget encode the constant, it always be MAX_CODE + 1
        constant_id = len(mnrp.variables)
        assert constant_id not in self.nrp.cost.keys()
        assert constant_id not in self.nrp.profit.keys()
        # convert requirements
        # use requirements, y <= x
        for req in self.nrp.requests:
            # custom req[0] need requirement req[1]
            # req[0] <= req[1] <=> req[0] - req[1] <= 0
            mnrp.inequations.append({req[0]: 1, req[1]: -1, constant_id: 0})
        # use sum cost_i x_i < b sum(cost)
        cost_sum = sum(self.nrp.cost.values())
        tmp_inequation = deepcopy(self.nrp.cost)
        tmp_inequation[constant_id] = float(cost_sum * option['b'])
        mnrp.inequations.append(tmp_inequation)
        # return
        return mnrp

    @staticmethod
    def find_demands(requests: List[Tuple[int, int]]) -> Dict[int, List[int]]:
        """find_demands [summary] make demand mapping from requests

        Args:
            requests (List[Tuple[int, int]]): [description]

        Returns:
            Dict[int, List[int]]: [description]
        """
        # prepare a dict
        tmp_demands: Dict[int, Set[int]] = dict()
        # iterate the requirements
        for customer_id, requirement_id in requests:
            if requirement_id not in tmp_demands:
                tmp_demands[requirement_id] = set()
            # add into the set
            tmp_demands[requirement_id].add(customer_id)
        # turn sets into list
        demands: Dict[int, List[int]] = dict()
        for key, value in tmp_demands.items():
            demands[key] = list(value)
        # return the demands
        return demands

    def to_sincus_form(self, option: Dict[str, Any]) -> NRPProblem:
        """to_sincus_form [summary] only for realistic nrps,
        form as basic stakeholders form as metioned in

        An Integer Linear Programming approach to the single
        and bi-objective Next Release Problem, NadarajenVeerapen
        https://doi.org/10.1016/j.infsof.2015.03.008

        Args:
            option (Dict[str, Any]): [description]

        Returns:
            NRPProblem: [description]
        """
        # check dependencies
        assert not self.nrp.dependencies
        # check option
        assert 'b' in option and isinstance(option['b'], float)
        # prepare the NRPProblem, modelled nrp, mnrp
        mnrp = NRPProblem()
        # prepare the "variables"
        mnrp.variables = \
            list(self.nrp.cost.keys()) + list(self.nrp.profit.keys())
        # prepare objective coefs
        mnrp.objectives = [{k: -v for k, v in self.nrp.profit.items()}]
        # don't forget encode the constant, it always be MAX_CODE + 1
        constant_id = len(mnrp.variables)
        assert constant_id not in self.nrp.cost.keys()
        assert constant_id not in self.nrp.profit.keys()
        # find set Si which consists of customers who need requirement xi
        # ...or we can name it demand 'list',
        # dict[requirement_id:list[customer_id]]
        demands = self.find_demands(self.nrp.requests)
        # use OR method to convert or-logic into linear planning
        # we assume requirement are (y, x), note that y is customer
        # and x a requirement
        # there should be constraints: OR_j(yi) where yi requires xj
        # they could be converted into: each yi - xj <= 0
        # ... and Sum yi - xj >= 0  <=> xj - Sum yi <= 0
        # first, each yi <= xj in requirements
        for req in self.nrp.requests:
            # custom req[0] need requirement req[1]
            # req[0] <= req[1] <=> req[0] - req[1] <= 0
            mnrp.inequations.append({req[0]: 1, req[1]: -1, constant_id: 0})
        # second, xj - Sum yi <= 0
        for req, demand_list in demands.items():
            tmp_inequation = {req: 1.0}
            for customer_id in demand_list:
                tmp_inequation[customer_id] = -1.0
            tmp_inequation[constant_id] = 0.0
            mnrp.inequations.append(tmp_inequation)
        # finialy, use sum cost_i x_i < b sum(cost) of course
        cost_sum = sum(self.nrp.cost.values())
        tmp_inequation = deepcopy(self.nrp.cost)
        tmp_inequation[constant_id] = float(cost_sum * option['b'])
        mnrp.inequations.append(tmp_inequation)
        # return
        return mnrp

    def to_basic_binary_form(self) -> NRPProblem:
        """to_basic_binary_form [summary] constuct the
        very basic binary form nrp

        Returns:
            NRPProblem: [description]
        """
        # check dependencies
        assert not self.nrp.dependencies
        # prepare the NRPProblem, modelled nrp, mnrp
        mnrp = NRPProblem()
        # prepare the "variables"
        mnrp.variables = \
            list(self.nrp.profit.keys()) + list(self.nrp.cost.keys())
        # prepare objective coefs
        max_profit = {k: -v for k, v in self.nrp.profit.items()}
        min_cost = {k: v for k, v in self.nrp.cost.items()}
        mnrp.objectives = [max_profit, min_cost]
        # don't forget encode the constant, it always be MAX_CODE + 1
        constant_id = len(mnrp.variables)
        assert constant_id not in self.nrp.cost.keys()
        assert constant_id not in self.nrp.profit.keys()
        # convert requirements
        # use requirements, y <= x
        for req in self.nrp.requests:
            # custom req[0] need requirement req[1]
            # req[0] <= req[1] <=> req[0] - req[1] <= 0
            mnrp.inequations.append({req[0]: 1, req[1]: -1, constant_id: 0})
        # return
        return mnrp

    def to_binary_form(self, option: Dict[str, Any]) -> NRPProblem:
        """to_binary_form [summary]
        form as binary-objective form as metioned in

        An Integer Linear Programming approach to the single
        and bi-objective Next Release Problem, NadarajenVeerapen
        https://doi.org/10.1016/j.infsof.2015.03.008


        Args:
            option (Dict[str, Any]): [description]

        Returns:
            NRPProblem: [description]
        """
        # basic form
        return self.to_basic_binary_form()

    def to_bincst_form(self, option: Dict[str, Any]) -> NRPProblem:
        """to_bincst_form [summary] binary form with
        addtional constraints, there are four constraints could be chosen:
        max_cost, min_profit, min_requirements, min_customers

        Args:
            option (Dict[str, Any]): [description]

        Returns:
            NRPProblem: [description]
        """
        # basic form
        mnrp = self.to_basic_binary_form()
        # constant
        constant_id = len(self.nrp.variables)
        # put more inequations
        if 'max_cost' in option:
            # sum cost <= max_cost
            max_cost = option['max_cost']
            inequation = {k: v for k, v in self.nrp.cost.items()}
            if isinstance(max_cost, int):
                inequation[constant_id] = max_cost
            else:
                inequation[constant_id] = \
                    ceil(max_cost * sum(list(self.nrp.cost.values())))
            mnrp.inequations.append(inequation)
        # end if
        if 'min_profit' in option:
            # sum profit >= min_profit
            min_profit = option['min_profit']
            inequation = {k: v for k, v in self.nrp.cost.items()}
            if isinstance(min_profit, int):
                inequation[constant_id] = min_profit
            else:
                inequation[constant_id] = \
                    - floor(min_profit * sum(list(self.nrp.profit.values())))
            mnrp.inequations.append(inequation)
        # end if
        if 'min_requirements' in option:
            # |requirements| >= min_requirements
            min_requirements = option['min_requirements']
            inequation = {k: -1 for k in self.nrp.cost}
            if isinstance(min_requirements, int):
                inequation[constant_id] = - min_requirements
            else:
                inequation[constant_id] = \
                    - floor(min_requirements * len(self.nrp.cost))
            mnrp.inequations.append(inequation)
        # end if
        if 'min_customers' in option:
            # |requirements| >= min_requirements
            min_requirements = option['min_customers']
            inequation = {k: -1 for k in self.nrp.cost}
            if isinstance(min_requirements, int):
                inequation[constant_id] = - min_requirements
            else:
                inequation[constant_id] = \
                    - floor(min_requirements * len(self.nrp.profit))
            mnrp.inequations.append(inequation)
        # end if
        # return
        return mnrp
