#
# DONG Shi, dongshi@mail.ustc.edu.cn
# NRP.py, created: 2020.10.31
# last modified: 2021.01.14
#

import os
import json
from copy import deepcopy
from functools import reduce
from os.path import join
# from statistics import median
# from math import ceil, floor
from typing import Dict, Tuple, List, Union, Set, Any
from src.Loader import Loader, XuanProblem, ReleasePlannerProblem
from src.Config import Config
from src.util.moipProb import MOIPProblem


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


class RPNRP:
    def __init__(self) -> None:
        """__init__ [summary] record members for ReleasePlanner NRP
        """
        # weight of stakeholders
        self.weight: List[Any] = []
        # cost of requirements
        self.cost: List[Any] = []
        # value, (requirement, stakeholder) -> value
        self.value: Dict[Tuple[int, int], Any] = dict()
        # importance, (requirement, stakeholder) -> value
        self.importance: Dict[Tuple[int, int], Any] = dict()
        # dependencies, (x_i, x_j) denotes x_i -> x_j, x_i is precursor of x_j
        self.dependencies: List[Tuple[int, int]] = []
        # couplings, (x_i, x_j) denotes x_i = x_j
        self.couplings: List[Tuple[int, int]] = []

        # profit with requirements
        self.profit: List[Any] = []
        # urgency with requirements
        self.urgency: List[Any] = []
        # risk with requirements
        self.risk: List[Any] = []


class NRPProblem:
    def __init__(self) -> None:
        """__init__ [summary] record members
        """
        # variables
        self.variables: List[int] = []
        # objectives
        self.objectives: List[Dict[int, Any]] = []
        # inequations, lhs <= rhs
        self.inequations: List[Dict[int, int]] = []

    def attributes(self) -> List[List[int]]:
        """attributes [summary] convert objectives into attributes matrix

        Returns:
            List[int]: [description] the attributes
        """
        zeros = [0] * len(self.variables)
        attributes = []
        for i in range(len(self.objectives)):
            line = zeros[:]
            for key, val in self.objectives[i].items():
                line[key] = val
            attributes.append(line)
        return attributes


# Type
NRPType = Union[XuanNRP, RPNRP]


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
        keyword = config.parse_dataset_keyword(project)
        # construct NRP from dataset
        self.nrp = getattr(self, 'construct_from_{}'.format(keyword))(project)
        # for MOIPProblem
        self.problem: MOIPProblem

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
        tmp_problem = loader.load(project)
        assert isinstance(tmp_problem, XuanProblem)
        raw_problem: XuanProblem = tmp_problem
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

    @staticmethod
    def construct_from_rp(project: str) -> RPNRP:
        """construct_from_rp [summary] construct RPNRP from rp datasets,
        they are MSWord and ReleasePlanner

        Args:
            project (str): [description] project name

        Returns:
            RPNRP: [description]
        """
        # load from files
        loader = Loader()
        tmp_problem = loader.load(project)
        assert isinstance(tmp_problem, ReleasePlannerProblem)
        raw_problem: ReleasePlannerProblem = tmp_problem
        # prepare RPNRP
        nrp = RPNRP()
        # assign weight of stakeholders
        nrp.weight = raw_problem.weight
        # make profit dict
        for req, sh, value in raw_problem.profit:
            nrp.value[(req, sh)] = value
        # make urgency dict
        for req, sh, value in raw_problem.profit:
            nrp.importance[(req, sh)] = value
        # assign dependencies and couplings and cost
        nrp.dependencies = raw_problem.precedes
        nrp.couplings = raw_problem.couplings
        nrp.cost = raw_problem.cost
        # return
        return nrp

    def reencode_xuan(self) -> Tuple[Dict[int, int], Dict[int, int]]:
        """reencode_xuan [summary] classic and realistic reencode, single objective
            encoding will be compact and from 0

        Returns:
            Tuple[Dict[int, int], Dict[int, int]]:
            [description] requirement renamer, customer renamer
        """
        # employ an encoder
        encoder = 0
        # prepare a requirement encoder
        req_encoder = dict()
        neo_cost = dict()
        # prepare a customer encoder
        cus_encoder = dict()
        neo_profit = dict()
        # encode
        for cus, profit in self.nrp.profit.items():
            assert cus not in cus_encoder
            cus_encoder[cus] = encoder
            neo_profit[encoder] = profit
            encoder += 1
        for req, cost in self.nrp.cost.items():
            assert req not in req_encoder
            req_encoder[req] = encoder
            neo_cost[encoder] = cost
            encoder += 1
        # apply them on dependencies
        neo_dependencies = \
            [(req_encoder[x[0]], req_encoder[x[1]])
             for x in self.nrp.dependencies]
        # apply them on requests
        neo_requests = \
            [(cus_encoder[x[0]], req_encoder[x[1]])
             for x in self.nrp.requests]
        # change them all
        self.nrp.cost = neo_cost
        self.nrp.profit = neo_profit
        self.nrp.dependencies = neo_dependencies
        self.nrp.requests = neo_requests
        # return dicts
        return req_encoder, cus_encoder

    def premodel(self, option: Dict[str, Any]) -> None:
        """premodel [summary] pre model
        """
        # get config
        config = Config()
        keyword = config.parse_keyword(self.__project)
        getattr(self, '{}_premodel'.format(keyword))(option)

    def classic_premodel(self, option: Dict[str, Any]) -> None:
        """classic_premodel [summary]
            premodel the classic keyword dataset
        """
        self.flatten_xuan()
        self.reencode_xuan()

    def realistic_premodel(self, option: Dict[str, Any]) -> None:
        """realistic_premodel [summary]
            premodel the realistic keyword dataset
        """
        self.reencode_xuan()

    def rp_premodel(self, option: Dict[str, Any]) -> None:
        assert isinstance(self.nrp, RPNRP)
        # make sum weight == 1
        base = sum(self.nrp.weight)
        self.nrp.weight = [w / base for w in self.nrp.weight]
        # calculate the urgency for each requirement
        self.nrp.urgency = [0] * len(self.nrp.cost)
        for (req, sh), val in self.nrp.importance.items():
            self.nrp.urgency[req] += self.nrp.weight[sh] * val
        # calculate the profit according to the requirements
        self.nrp.profit = [0] * len(self.nrp.cost)
        for (req, sh), val in self.nrp.value.items():
            self.nrp.profit[req] += self.nrp.weight[sh] * val
        # calculate the risk of each requirement
        self.nrp.risk = [0] * len(self.nrp.cost)
        for (req, sh), val in self.nrp.value.items():
            self.nrp.risk[req] += \
                self.nrp.weight[sh] * ((val - self.nrp.profit[req]) ** 2)
        self.nrp.risk = [e / len(self.nrp.weight) for e in self.nrp.risk]
        # convert each value into integer
        self.nrp.profit = [round(x) for x in self.nrp.profit]
        self.nrp.cost = [round(x) for x in self.nrp.cost]
        self.nrp.risk = [round(x) for x in self.nrp.risk]
        self.nrp.urgency = [round(x) for x in self.nrp.urgency]
        # elimate couplings
        self.eliminate_couplings()

    def eliminate_couplings(self) -> None:
        assert isinstance(self.nrp, RPNRP)
        # find the equivalent set
        equivalent: List[Set[int]] = []
        for r1, r2 in self.nrp.couplings:
            flag = False
            for s in equivalent:
                if r1 in s or r2 in s:
                    s.add(r1)
                    s.add(r2)
                    flag = True
            if not flag:
                equivalent.append(set([r1, r2]))
        # choose min requirement represent the equivalent set
        reduce: Dict[int, int] = {}
        for s in equivalent:
            present = min(s)
            for e in s:
                if e == present:
                    continue
                else:
                    reduce[e] = present
                    self.nrp.cost[present] += self.nrp.cost[e]
                    self.nrp.urgency[present] += self.nrp.urgency[e]
                    self.nrp.profit[present] += self.nrp.profit[e]
                    self.nrp.risk[present] += self.nrp.risk[e]
        # re arrange the profit and the risk and the cost
        left = list(range(len(self.nrp.cost)))
        for reduced in reduce:
            left.remove(reduced)
        rename: Dict[int, int] = {}
        for ind, var in enumerate(left):
            rename[var] = ind
        # rename dependenciesW
        tmp_dep = []
        for r1, r2 in self.nrp.dependencies:
            if r1 in reduce:
                r1 = rename[reduce[r1]]
            else:
                r1 = rename[r1]
            if r2 in reduce:
                r2 = rename[reduce[r2]]
            else:
                r2 = rename[r2]
            tmp_dep.append((r1, r2))
        self.nrp.dependencies = tmp_dep
        # rearrange profit, cost, risk and urgency
        self.nrp.profit = \
            [e for i, e in enumerate(self.nrp.profit) if i not in reduce]
        self.nrp.risk = \
            [e for i, e in enumerate(self.nrp.risk) if i not in reduce]
        self.nrp.cost = \
            [e for i, e in enumerate(self.nrp.cost) if i not in reduce]
        self.nrp.urgency = \
            [e for i, e in enumerate(self.nrp.urgency) if i not in reduce]
        # delete couplings
        self.nrp.couplings = []

    def MSWord_premodel(self, option: Dict[str, Any]) -> None:
        """MSWord_premodel [summary]
            premodel the MSWord dataset
        """
        self.rp_premodel(option)

    def ReleasePlanner_premodel(self, option: Dict[str, Any]) -> None:
        """ReleasePlanner_premodel [summary]
            premodel the ReleasePlanner dataset
        """
        self.rp_premodel(option)

    @staticmethod
    def dump_nrp(file_name: str, nrp: NRPProblem) -> None:
        # sort variables
        vrs = sorted(nrp.variables)
        index = {k: i for i, k in enumerate(vrs)}
        # reorder objectives
        objs = []
        for obj in nrp.objectives:
            objs.append([float(obj[var]) for var in vrs])
        # remap inequations
        csts = []
        if nrp.inequations:
            constant = len(vrs)
            for var in nrp.inequations[0]:
                if var not in vrs:
                    index[var] = constant
                    break
            for ineq in nrp.inequations:
                csts.append({index[k]: float(v) for k, v in ineq.items()})
        # prepare a dict for dumpping
        dumpping = {
            'objectives': objs,
            'inequations': csts
        }
        with open(file_name, 'w') as fout:
            json.dump(dumpping, fout, indent=4)
            fout.close()

    @staticmethod
    def dump_xuan(file_name: str, project_name: str, nrp: XuanNRP) -> None:
        assert not nrp.dependencies
        # load config
        config = Config()
        # prepare a dict for storing all
        result: Dict[str, Any] = dict()
        # requirements cost
        result['cost'] = nrp.cost
        # customers profits
        result['profit'] = nrp.profit
        # TODO: temp load here
        result['urgency'] = \
            NextReleaseProblem.load_xuan_urgency(project_name, nrp.cost)
        # requests
        # result['request'] = nrp.requests
        neo_requests: Dict[str, List[int]] = {}
        for request in nrp.requests:
            customer = str(request[0])
            requirement = request[1]
            if customer in neo_requests:
                neo_requests[customer].append(requirement)
            else:
                neo_requests[customer] = [requirement]
        result['request'] = neo_requests
        # see if folder exists
        if not os.path.exists(config.dump_path):
            os.makedirs(config.dump_path)
        with open(file_name, 'w+') as out_file:
            # dump
            json_object = json.dumps(result, indent=4)
            out_file.write(json_object)
            # close the file
            out_file.close()

    def model(self, form: str, option: Dict[str, Any]) -> NRPProblem:
        """model [summary] modelling to NRPProblem

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
            tmp_inequation = {req: 1}
            for customer_id in demand_list:
                tmp_inequation[customer_id] = -1
            tmp_inequation[constant_id] = 0
            mnrp.inequations.append(tmp_inequation)
        # finialy, use sum cost_i x_i < b sum(cost) of course
        cost_sum = sum(self.nrp.cost.values())
        tmp_inequation = deepcopy(self.nrp.cost)
        tmp_inequation[constant_id] = int(cost_sum * option['b'])
        mnrp.inequations.append(tmp_inequation)
        # return
        return mnrp

    def to_basic_binary_form(self, option: Dict[str, Any]) -> NRPProblem:
        """to_basic_binary_form [summary] constuct the
        very basic binary form nrp

        Returns:
            NRPProblem: [description]
        """
        # check dependencies
        assert not self.nrp.dependencies
        # get config
        # if 'profit_cost' in option:
        #     profit_cost = option['profit_cost']
        # else:
        profit_cost = True
        # prepare the NRPProblem, modelled nrp, mnrp
        mnrp = NRPProblem()
        # prepare objective coefs and variables
        mnrp.variables = \
            list(self.nrp.profit.keys()) + list(self.nrp.cost.keys())
        max_profit = {k: -v for k, v in self.nrp.profit.items()}
        min_cost = {k: v for k, v in self.nrp.cost.items()}
        if profit_cost:
            mnrp.objectives = [max_profit, min_cost]
        else:
            mnrp.objectives = [min_cost, max_profit]
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

    def to_rp_binary_form(self, option: Dict[str, Any]) -> NRPProblem:
        assert isinstance(self.nrp, RPNRP)
        # prepare the NRPProblem, modelled nrp, mnrp
        mnrp = NRPProblem()
        # prepare objective coefs and variables
        mnrp.variables = list(range(len(self.nrp.cost)))
        max_profit = {k: -v for k, v in enumerate(self.nrp.profit)}
        min_cost = {k: v for k, v in enumerate(self.nrp.cost)}
        mnrp.objectives = [max_profit, min_cost]
        # don't forget encode the constant, it always be MAX_CODE + 1
        constant_id = len(mnrp.variables)
        assert constant_id not in range(len(self.nrp.cost))
        # convert requirements
        # use requirements, y <= x
        for req in self.nrp.dependencies:
            # (i, j): xi precedes xj, xj <= xi
            # req[1] - req[0] <= 0
            mnrp.inequations.append({req[1]: 1, req[0]: -1, constant_id: 0})
        # return
        return mnrp

    def to_binary_form(self, option: Dict[str, Any]) -> NRPProblem:
        """to_binary_form [summary]
        form as binary-objective form as metioned in

        An Integer Linear Programming approach to the single
        and bi-objective Next Release Problem, NadarajenVeerapen
        https://doi.org/10.1016/j.infsof.2015.03.008

        And Risk-Aware with profit and cost binary form

        Args:
            option (Dict[str, Any]): [description]

        Returns:
            NRPProblem: [description]
        """
        if isinstance(self.nrp, XuanNRP):
            return self.to_basic_binary_form(option)
        elif isinstance(self.nrp, RPNRP):
            return self.to_rp_binary_form(option)
        else:
            assert False

    def to_bireq_form(self, option: Dict[str, Any]) -> NRPProblem:
        """to_bireq_form [summary] bireq form is a binary form, too.
        But the profit is according to requirements but not customers.

        The profit of each requirement is defined as reversed ranking
        ordered by the sum of customers profit
        which request this requirement.
        profit(x_i) = RevRank(sum(profit(y_j)), forall (x_i, y_j) in Requests)

        It reduces variables and eliminates constraints.

        Args:
            option (Dict[str, Any]): [description]

        Returns:
            NRPProblem: [description]
        """
        # check dependencies
        assert not self.nrp.dependencies
        # prepare the NRPProblem, modelled nrp, mnrp
        mnrp = NRPProblem()
        # find sum profit of each requirement
        req_profit: Dict[int, Any] = {}
        for request in self.nrp.requests:
            cus, req = request
            if req not in req_profit:
                req_profit[req] = self.nrp.profit[cus]
            else:
                req_profit[req] += self.nrp.profit[cus]
        # prepare find ranking for each raw profit
        sorted_values = list(sorted(set(req_profit.values())))
        value_map: Dict[Any, int] = {}
        for rank, value in enumerate(sorted_values):
            value_map[value] = rank + 1
        # prepare objective coefs and variables
        mnrp.variables = list(self.nrp.cost.keys())
        max_profit = {k: -value_map[v] for k, v in req_profit.items()}
        min_cost = {k: v for k, v in self.nrp.cost.items() if k in req_profit}
        mnrp.objectives = [max_profit, min_cost]
        # don't forget encode the constant, it always be MAX_CODE + 1
        constant_id = max(mnrp.variables) + 1
        assert constant_id not in self.nrp.cost.keys()
        # there are no constraints anymore
        mnrp.inequations = []
        # return
        return mnrp

    def to_bincst_form(self, option: Dict[str, Any]) -> NRPProblem:
        """to_bincst_form [summary] ReleasePlanner binary form
        with risk as its thrid objective constraint

        Args:
            option (Dict[str, Any]): [description]

        Returns:
            NRPProblem: [description]
        """
        if isinstance(self.nrp, XuanNRP):
            mnrp = self.to_xuan_triple_form(option)
            urgency_cst = deepcopy(mnrp.objectives[2])
            del mnrp.objectives[2]
            # constant
            constant_id = len(mnrp.variables)
            assert 'bound' in option
            sum_urgency = sum(urgency_cst.values())
            urgency_cst[constant_id] = sum_urgency * option['bound']
            mnrp.inequations.append(urgency_cst)
            # return
            return mnrp
        elif isinstance(self.nrp, RPNRP):
            # basic form
            mnrp = self.to_rp_binary_form(option)
            # convert the urgency as the constraint
            urgency_cst = {k: -v for k, v in enumerate(self.nrp.urgency)}
            # constant
            constant_id = len(mnrp.variables)
            # find the bound
            assert 'bound' in option
            sum_urgency = sum(urgency_cst.values())
            urgency_cst[constant_id] = sum_urgency * option['bound']
            mnrp.inequations.append(urgency_cst)
            # return
            return mnrp
        else:
            assert False

    def to_basic_rp_form(self, option: Dict[str, Any]) -> NRPProblem:
        assert isinstance(self.nrp, RPNRP)
        # prepare the NRPProblem, modelled nrp, mnrp
        mnrp = NRPProblem()
        # prepare objective coefs and variables
        # TODO: maybe should convert float to int
        mnrp.variables = list(range(len(self.nrp.cost)))
        max_profit = {k: -v for k, v in enumerate(self.nrp.profit)}
        min_cost = {k: v for k, v in enumerate(self.nrp.cost)}
        min_risk = {k: v for k, v in enumerate(self.nrp.risk)}
        max_urgency = {k: -v for k, v in enumerate(self.nrp.urgency)}
        mnrp.objectives = [max_profit, min_cost, min_risk, max_urgency]
        # don't forget encode the constant, it always be MAX_CODE + 1
        constant_id = len(mnrp.variables)
        assert constant_id not in mnrp.variables
        # convert denpendencies, (x_i, x_j) => x_j <= x_i <=> - x_i + x_j <= 0
        for req in self.nrp.dependencies:
            mnrp.inequations.append({req[0]: -1, req[1]: 1, constant_id: 0})
        # return
        return mnrp

    def to_xuan_triple_form(self, option: Dict[str, Any]) -> NRPProblem:
        """to_xuan_triple_form [summary] xuan binary -> triple,
        with random generated urgency value related to requirements

        Args:
            option (Dict[str, Any]): [description]

        Returns:
            NRPProblem: [description]
        """
        mnrp = self.to_basic_binary_form(option)
        # load urgency
        # TODO: maybe config in Config
        path = './datasets/xuan/urgency/'
        urgency_file = join(path, self.__project + '.json')
        max_urgency: Dict[int, int] = {}
        with open(urgency_file, 'r') as fin:
            urgency_value = json.load(fin)
            assert isinstance(urgency_value, list)
            # check if second objective is cost
            assert list(mnrp.objectives[1].values())[0] >= 0
            # make urgency
            assert len(mnrp.objectives[1]) == len(urgency_value)
            for index, req in enumerate(mnrp.objectives[1]):
                max_urgency[req] = - urgency_value[index]
            mnrp.objectives.append(max_urgency)
            fin.close()
        return mnrp

    def to_trisk_form(self, option: Dict[str, Any]) -> NRPProblem:
        """to_trisk_form [summary] triple objective NRP,
        with objectives: profit, cost and the risk
        Args:
            option (Dict[str, Any]): [description]

        Returns:
            NRPProblem: [description]
        """
        # basic form
        mnrp = self.to_basic_rp_form(option)
        mnrp.objectives = mnrp.objectives[:3]
        return mnrp

    @staticmethod
    def load_xuan_urgency(project: str,
                          cost: Dict[int, int]) -> Dict[int, int]:
        # load urgency value for xuan dataset
        # TODO: move it into problem loading
        # load urgency
        # TODO: maybe config in Config
        path = './datasets/xuan/urgency/'
        urgency_file = join(path, project + '.json')
        max_urgency: Dict[int, int] = {}
        with open(urgency_file, 'r') as fin:
            urgency_value = json.load(fin)
            assert isinstance(urgency_value, list)
            # make urgency
            assert len(cost) == len(urgency_value)
            for index, req in enumerate(cost):
                max_urgency[req] = urgency_value[index]
            fin.close()
        return max_urgency

    def to_triurgency_form(self, option: Dict[str, Any]) -> NRPProblem:
        """to_trisk_form [summary] triple objective NRP,
        with objectives: profit, cost and the urgency
        Args:
            option (Dict[str, Any]): [description]

        Returns:
            NRPProblem: [description]
        """
        if isinstance(self.nrp, XuanNRP):
            return self.to_xuan_triple_form(option)
        # basic form
        mnrp = self.to_basic_rp_form(option)
        profit = deepcopy(mnrp.objectives[0])
        # cost translation
        cost = deepcopy(mnrp.objectives[1])
        # mid = median(cost.values())
        # cost = {k: v - mid for k, v in cost.items()}
        # urgency translation
        urgency = deepcopy(mnrp.objectives[3])
        # mid = median(urgency.values())
        # urgency = {k: v - mid for k, v in urgency.items()}
        # objectives
        mnrp.objectives = [profit, cost, urgency]
        return mnrp

    @staticmethod
    def MOIP(nrp: NRPProblem) -> MOIPProblem:
        # use objectives make attribute matrix
        attribute_matrix = []
        for objective in nrp.objectives:
            line = [0] * (len(nrp.variables))
            for key, value in objective.items():
                line[key] = value
            # there was a constant_id = max_id + 1, then api do not work
            # so I assume there's no constant in objective
            attribute_matrix.append(line)
        # load into the MOIP
        # construct MOIP
        MOIP = MOIPProblem(len(nrp.objectives), len(nrp.variables), 0)
        # call load
        MOIP.load(nrp.objectives, nrp.inequations, None, False, None)
        # ...load manually
        MOIP.sparseInequationSensesList = ['L'] * len(nrp.inequations)
        MOIP.attributeMatrix = attribute_matrix
        # return
        return MOIP
