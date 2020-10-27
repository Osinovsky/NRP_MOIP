# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# NRP.py, created: 2020.09.19        #
# Last Modified: 2020.10.27          #
# ################################## #

from typing import *
from config import *
from loaders import Loader
from moipProb import MOIPProblem
from JNRP import JNRP
from copy import deepcopy
from functools import reduce
from math import ceil, floor
import json
import os

# Type 
CostType = Union[Dict[int, int], Dict[Tuple[int, int], int]]
ProfitType = Union[Dict[int, int], Dict[Tuple[int, int], int]]
DependenciesType = List[Tuple[int, int]]
RequestsType = List[Tuple[int, int]]
NRPType = Tuple[CostType, ProfitType, DependenciesType, RequestsType]
ProblemType = Union[MOIPProblem, JNRP]

# describe a class provide an "universal" class 
# for recording next release problem
class NextReleaseProblem:
    # initialize
    def __init__(self, project_name : str, problem_type : str = 'default'):
        # prepare member variables
        self.__project : str = project_name;
        # profit, note that could be  requirement -> cost, customer -> cost
        # and even (requirement, customer/team) -> cost
        self.__cost : CostType = dict()
        # profit, note that could be customer -> profit, requirement -> profit
        # and even (requirement, customer/team) -> profit
        self.__profit : ProfitType = dict()
        # depdencies, describe dependencies among requirements
        # (x_i, x_j) denotes x_i -> x_j, x_i is precursor of x_j
        self.__dependencies : DependenciesType = []
        # request, customer -> requirement or team -> requirement
        self.__requests : RequestsType = []
        # decide to model as a NRP or JNRP form
        self.__problem_type : str = problem_type
        # load from file
        self.__load(project_name)
        # inventory
        assert self.inventory() == self.pattern()

    # load from file
    def __load(self, project_name : str) -> None:
        # employ a loader
        loader = Loader(project_name)
        self.__cost, self.__profit, self.__dependencies, self.__requests = loader.load()

    # check member variables status
    def inventory(self) -> Dict[str, str]:
        stats = dict()
        # check cost type
        assert self.__cost
        assert isinstance(self.__cost, dict)
        if isinstance(list(self.__cost.keys())[0], int):
            stats['cost'] = 'int'
        elif isinstance(list(self.__cost.keys())[0], tuple):
            assert len(list(self.__cost.keys())[0]) == 2
            stats['cost'] = 'tuple'
        else:
            assert False
        # check profit type
        assert self.__profit
        assert isinstance(self.__profit, dict)
        if isinstance(list(self.__profit.keys())[0], int):
            stats['profit'] = 'int'
        elif isinstance(list(self.__profit.keys())[0], tuple):
            assert len(list(self.__profit.keys())[0]) == 2
            stats['profit'] = 'tuple'
        else:
            assert False
        # check denpendencies
        if self.__dependencies:
            assert isinstance(self.__dependencies, list)
            assert isinstance(self.__dependencies[0], tuple)
            assert len(self.__dependencies[0]) == 2
            stats['dependencies'] = 'tuple'
        else:
            stats['dependencies'] = 'empty'
        # check requests
        if self.__requests:
            assert isinstance(self.__requests, list)
            assert isinstance(self.__requests[0], tuple)
            assert len(self.__requests[0]) == 2
            stats['requests'] = 'tuple'
        else:
            stats['requests'] = 'empty'
        # return
        return stats
    
    # what kind of pattern should a project has
    # compare with inventory
    def pattern(self) -> Dict[str, str]:
        if self.__project.startswith('classic'):
            return  {'cost':'int', 'profit':'int', 'dependencies':'tuple', 'requests':'tuple'}
        elif self.__project.startswith('realistic'):
            return {'cost':'int', 'profit':'int', 'dependencies':'empty', 'requests':'tuple'}
        elif self.__project.startswith('Motorola'):
            return {'cost':'int', 'profit':'int', 'dependencies':'empty', 'requests':'empty'}
        elif self.__project.startswith('RALIC'):
            return {'cost':'int', 'profit':'tuple', 'dependencies':'empty', 'requests':'empty'}
        elif self.__project.startswith('Baan'):
            return {'cost': 'tuple', 'profit':'int', 'dependencies':'empty', 'requests':'empty'}
        else:
            return None

    # get the content of NRP
    def content(self) -> NRPType:
        return self.__cost, self.__profit, self.__dependencies, self.__requests

    # find one requirement all precursors
    def __precursors(self, req_id : int) -> Set[int]:
        # find all depdency with right value as requst id input
        last_level = set([x[0] for x in self.__dependencies if x[1] == req_id])
        # check result
        if len(last_level) == 0:
            return last_level
        else:
            # find their dependecies each and merge their result
            # then convert then into set for dupicate elimination
            return last_level.union(set(reduce(lambda x, y: list(x)+list(y), map(self.__precursors, last_level))))

    # flatten dependencies, eliminate all dependencies between requirements
    def flatten(self) -> None:
        # of course depdencies should not be empty
        assert self.__dependencies
        # copy a new requests from self.requests
        neo_requests = deepcopy(self.__requests)
        # traverse requests
        for req in self.__requests:
            # find all real requests
            dependencies = list(self.__precursors(req[1]))
            # add into new requests
            for dep in dependencies:
                if (req[0], dep) not in neo_requests:
                    neo_requests.append((req[0], dep))
        # change requests and clear dependencies
        self.__requests = neo_requests
        self.__dependencies.clear()

    # check if this NRP could be modelled as given form
    def modelable(self, form : str) -> bool:
        # TODO: not sure how to do that yet
        return True

    # reencode with requirements, customers/teams and maybe (requirement, customers/teams)
    # encoding will be compact and from 0
    def reencode(self, pairwise : bool) -> Tuple[Dict[int, int], Dict[int, int]]:
        pass

    # classic and realistic reencode, single objective
    # encoding will be compact and from 0
    def xuan_reencode(self) -> Tuple[Dict[int, int], Dict[int, int]]:
        # assume that dependencies is empty
        assert not self.__dependencies
        # employ an encoder
        encoder = 0
        # prepare a requirement encoder
        req_encoder = dict()
        neo_cost = dict()
        for req, cost in self.__cost.items():
            assert req not in req_encoder
            req_encoder[req] = encoder
            neo_cost[encoder] = cost
            encoder += 1
        # prepare a customer encoder
        cus_encoder = dict()
        neo_profit = dict()
        for cus, profit in self.__profit.items():
            assert cus not in cus_encoder
            cus_encoder[cus] = encoder
            neo_profit[encoder] = profit
            encoder += 1
        # apply them on requests
        neo_requests = []
        for cus, req in self.__requests:
            neo_requests.append((cus_encoder[cus], req_encoder[req]))
        # change them all
        self.__cost = neo_cost
        self.__profit = neo_profit
        self.__requests = neo_requests
        # return dicts
        return req_encoder, cus_encoder

    # make demand mapping from requests 
    @staticmethod
    def find_demands(requests : List[Tuple[int, int]]) -> Dict[int, List[int]]:
        # prepare a dict
        tmp_demands : Dict[int, Set[int]] = dict()
        # iterate the requirements
        for customer_id, requirement_id in requests:
            if requirement_id not in tmp_demands:
                tmp_demands[requirement_id] = set()
            # add into the set
            tmp_demands[requirement_id].add(customer_id)
        # turn sets into list
        demands : Dict[int, List[int]] = dict()
        for key, value in tmp_demands.items():
            demands[key] = list(value)
        # return the demands
        return demands

    # to general form for classic nrps to singel objective
    def __to_single_general_form(self, b : float) -> MOIPProblem:
        # check project name and flatten
        assert self.__project.startswith('classic')
        assert not self.__dependencies
        # prepare the "variables"
        variables = list(self.__cost.keys()) + list(self.__profit.keys())
        # prepare objective coefs
        objectives = [{k:-v for k, v in self.__profit.items()}]
        # prepare the atrribute matrix
        inequations : List[Dict[int, int]] = []
        inequations_operators : List[str] = []
        # don't forget encode the constant, it always be MAX_CODE + 1
        constant_id = len(variables)
        assert constant_id not in self.__cost.keys()
        assert constant_id not in self.__profit.keys()
        # convert requirements
        # use requirements, y <= x
        for req in self.__requests:
            # custom req[0] need requirement req[1]
            # req[0] <= req[1] <=> req[0] - req[1] <= 0
            inequations.append({req[0]:1, req[1]:-1, constant_id:0})
            # 'L' for <= and 'G' for >=, we can just convert every inequations into <= format
            inequations_operators.append('L')
        # use sum cost_i x_i < b sum(cost)
        cost_sum = sum(self.__cost.values())
        tmp_inequation = deepcopy(self.__cost)
        tmp_inequation[constant_id] = float(cost_sum * b)
        inequations.append(tmp_inequation)
        inequations_operators.append('L')
        # construct Problem without equations
        return NextReleaseProblem.MOIP(variables, objectives, inequations, inequations_operators, dict())

    # to single objective basic stakeholder form
    def __to_single_stakeholder_form(self, b : float) -> MOIPProblem:
        # check project name and flatten
        assert self.__project.startswith('realistic')
        assert not self.__dependencies
        # prepare the "variables"
        variables = list(self.__cost.keys()) + list(self.__profit.keys())
        # prepare objective coefs
        objectives = [{k:-v for k, v in self.__profit.items()}]
        # prepare the atrribute matrix
        inequations : List[Dict[int, int]] = []
        inequations_operators : List[str] = []
        # don't forget encode the constant, it always be MAX_CODE + 1
        constant_id = len(variables)
        assert constant_id not in self.__cost.keys()
        assert constant_id not in self.__profit.keys()
        # find set Si which consists of customers who need requirement xi
        # ...or we can name it demand 'list', dict[requirement_id:list[customer_id]]
        demands = self.find_demands(self.__requests)
        # use OR method to convert or-logic into linear planning
        # we assume requirement are (y, x), note that y is customer and x a requirement
        # there should be constraints: OR_j(yi) where yi requires xj
        # they could be converted into: each yi - xj <= 0
        # ... and Sum yi - xj >= 0  <=> xj - Sum yi <= 0
        # first, each yi <= xj in requirements
        for req in self.__requests:
            # custom req[0] need requirement req[1]
            # req[0] <= req[1] <=> req[0] - req[1] <= 0
            inequations.append({req[0]:1, req[1]:-1, constant_id:0})
            # 'L' for <= and 'G' for >=, we can just convert every inequations into <= format
            inequations_operators.append('L')
        # second, xj - Sum yi <= 0
        for req, demand_list in demands.items():
            tmp_inequation = {req : 1}
            for customer_id in demand_list:
                tmp_inequation[customer_id] = -1
            tmp_inequation[constant_id] = 0
            inequations.append(tmp_inequation)
            inequations_operators.append('L')
        # finialy, use sum cost_i x_i < b sum(cost) of course
        cost_sum = sum(self.__cost.values())
        tmp_inequation = deepcopy(self.__cost)
        tmp_inequation[constant_id] = float(cost_sum * b)
        inequations.append(tmp_inequation)
        inequations_operators.append('L')
        # construct Problem 
        return NextReleaseProblem.MOIP(variables, objectives, inequations, inequations_operators, dict())

    # model basic bi objective form
    # return variables, objectives, inequations, inequations_operators, equations
    def __basic_bi_form(self) -> Tuple[List[int], List[Dict[int, int]], List[str], List[Dict[int, int]]]:
        # prepare the "variables"
        variables = list(self.__profit.keys()) + list(self.__cost.keys())
        # prepare objective coefs
        max_profit = {k:-v for k, v in self.__profit.items()}
        min_cost = {k:v for k, v in self.__cost.items()}
        objectives = [max_profit, min_cost]
        # prepare the atrribute matrix
        inequations : List[Dict[int, int]] = []
        inequations_operators : List[str] = []
        # don't forget encode the constant, it always be MAX_CODE + 1
        constant_id = len(variables)
        assert constant_id not in self.__cost.keys()
        assert constant_id not in self.__profit.keys()
        # convert requirements
        # use requirements, y <= x
        for req in self.__requests:
            # custom req[0] need requirement req[1]
            # req[0] <= req[1] <=> req[0] - req[1] <= 0
            inequations.append({req[0]:1, req[1]:-1, constant_id:0})
            # 'L' for <= and 'G' for >=, we can just convert every inequations into <= format
            inequations_operators.append('L')
        # ignore equations
        equations = dict() # non-empty and not a list
        # return
        return variables, objectives, inequations, inequations_operators, equations

    # model to bi-objective for classic and realistic nrps
    def __to_bi_general_form(self) -> ProblemType:
        # only for classic and realistic
        assert self.__project.startswith('classic') or self.__project.startswith('realistic')
        # requirement dependencies should be eliminated
        assert not self.__dependencies
        # modelling
        variables, objectives, inequations, inequations_operators, equations = \
            self.__basic_bi_form()
        # construct Problem
        if self.__problem_type == 'default':
            return NextReleaseProblem.MOIP(variables, objectives, inequations, inequations_operators, equations)
        elif self.__problem_type == 'jmetal':
            file_name = self.__project + '_' + 'binary.json'
            NextReleaseProblem.dump(file_name, variables, objectives, inequations)
            return JNRP(variables, objectives, inequations)
        else:
            assert False

    # model to bi-objective with additional constraints form
    def __to_bicst_form(self, 
        max_cost : Union[int, float] = None, \
        min_profit : Union[int, float] = None, \
        min_requirements : int = None, \
        min_customers : int = None\
    ) -> ProblemType:
        # only for classic and realistic
        assert self.__project.startswith('classic') or self.__project.startswith('realistic')
        # requirement dependencies should be eliminated
        assert not self.__dependencies
        # modelling
        variables, objectives, inequations, inequations_operators, equations = \
            self.__basic_bi_form()
        # add additional constraints
        constant_id = len(variables)
        if max_cost: # sum cost <= max_cost
            inequation = {k:v for k, v in self.__cost.items()}
            if isinstance(max_cost, int):
                inequation[constant_id] = max_cost
            else:
                print('max cost: ', ceil(max_cost*sum(list(self.__cost.values()))))
                inequation[constant_id] = ceil(max_cost*sum(list(self.__cost.values())))
            inequations.append(inequation)
            inequations_operators.append('L')
        if min_profit: # sum profit >= min_profit
            # -p1 -p2 - ... <= - min_profit
            inequation = {k:-v for k, v in self.__profit.items()}
            if isinstance(min_profit, int):
                inequation[constant_id] = - min_profit
            else:
                print('min profit: ', floor(min_profit*sum(list(self.__profit.values()))))
                inequation[constant_id] = - floor(min_profit*sum(list(self.__profit.values())))
            inequations.append(inequation)
            inequations_operators.append('L')
        if min_requirements: # |requirements| >= min_requirements
            inequation = {k:-1 for k in self.__cost}
            if isinstance(min_requirements, int):
                inequation[constant_id] = - min_requirements
            else:
                print('min requirements: ', floor(min_requirements*len(self.__cost)))
                inequation[constant_id] = - floor(min_requirements*len(self.__cost))
            inequations.append(inequation)
            inequations_operators.append('L')
        if min_customers: # |customers| >= min_customers
            inequation = {k:-1 for k in self.__profit}
            if isinstance(min_customers, int):
                inequation[constant_id] = - min_customers
            else:
                print('min customers: ', floor(min_customers*len(self.__profit)))
                inequation[constant_id] = - floor(min_customers*len(self.__profit))
            inequations.append(inequation)
            inequations_operators.append('L')
        # construct Problem
        if self.__problem_type == 'default':
            return NextReleaseProblem.MOIP(variables, objectives, inequations, inequations_operators, equations)
        elif self.__problem_type == 'jmetal':
            file_name = self.__project + '_' + 'bicst.json'
            NextReleaseProblem.dump(file_name, variables, objectives, inequations)
            return JNRP(variables, objectives, inequations)
        else:
            assert False

    # tri-objective form with max requirements selected as the third objective
    def __to_tri_max_requirements_form(self) -> ProblemType:
        # only for classic and realistic
        assert self.__project.startswith('classic') or self.__project.startswith('realistic')
        # requirement dependencies should be eliminated
        assert not self.__dependencies
        # modelling with bi-objective
        variables, objectives, inequations, inequations_operators, equations = \
            self.__basic_bi_form()
        # add the third objective, max requirements <=> min -requirements
        max_requirements = {k:-1 for k in self.__cost}
        objectives.append(max_requirements)
        # construct Problem
        if self.__problem_type == 'default':
            return NextReleaseProblem.MOIP(variables, objectives, inequations, inequations_operators, equations)
        elif self.__problem_type == 'jmetal':
            file_name = self.__project + '_' + 'trireq.json'
            NextReleaseProblem.dump(file_name, variables, objectives, inequations)
            return JNRP(variables, objectives, inequations)
        else:
            assert False

    # tri-objective form with max customers selected as the third objective
    def __to_tri_max_customers_form(self) -> ProblemType:
        # only for classic and realistic
        assert self.__project.startswith('classic') or self.__project.startswith('realistic')
        # requirement dependencies should be eliminated
        assert not self.__dependencies
        # modelling with bi-objective
        variables, objectives, inequations, inequations_operators, equations = \
            self.__basic_bi_form()
        # add the third objective, max customers <=> min -customers
        max_customers = {k:-1 for k in self.__profit}
        objectives.append(max_customers)
        # construct Problem
        if self.__problem_type == 'default':
            return NextReleaseProblem.MOIP(variables, objectives, inequations, inequations_operators, equations)
        elif self.__problem_type == 'jmetal':
            file_name = self.__project + '_' + 'tricus.json'
            NextReleaseProblem.dump(file_name, variables, objectives, inequations)
            return JNRP(variables, objectives, inequations)
        else:
            assert False

    # model to single objective
    # different dataset using different form (according to the IST-2015)
    def single_form(self, b : float) -> MOIPProblem:
        # only Xuan Dataset used in single objective
        if not self.__project.startswith('classic') and not self.__project.startswith('realistic'):
            assert False
        if self.__project.startswith('classic'):
            # flatten, only classic dataset need this
            self.flatten()
        # reencode
        self.xuan_reencode()
        # convert to MOIPProblem
        if self.__project.startswith('classic'):
            # for classic nrps, to general form
            return self.__to_single_general_form(b)
        else:
            # for realistic nrps, to basic stakeholder form
            return self.__to_single_stakeholder_form(b)

    # model to bi-objective form
    def bi_form(self) -> ProblemType:
        if self.__project.startswith('classic') or self.__project.startswith('realistic'):
            # classic and realistic nrps
            if self.__project.startswith('classic'):
                # flatten, only classic dataset need this
                self.flatten()
            # reencode
            self.xuan_reencode()
            # to bi-objective form
            return self.__to_bi_general_form()
        elif self.__project.startswith('Motorola'):
            pass
        elif self.__project.startswith('RALIC'):
            pass
        elif self.__project.startswith('Baan'):
            pass
        else:
            # not found
            assert False

    # model to bi-objective with additional constraints form
    def bicst_form(self, option : Dict[str, int]) -> ProblemType:
        if self.__project.startswith('classic') or self.__project.startswith('realistic'):
            # classic and realistic nrps
            if self.__project.startswith('classic'):
                # flatten, only classic dataset need this
                self.flatten()
            # reencode
            self.xuan_reencode()
            # to bi-objective form
            return self.__to_bicst_form(**option)
        elif self.__project.startswith('Motorola'):
            pass
        elif self.__project.startswith('RALIC'):
            pass
        elif self.__project.startswith('Baan'):
            pass
        else:
            # not found
            assert False

    # the tri-objective forms
    def tri_form(self, form : str) -> ProblemType:
        if self.__project.startswith('classic') or self.__project.startswith('realistic'):
            # classic and realistic nrps
            if self.__project.startswith('classic'):
                # flatten, only classic dataset need this
                self.flatten()
            # reencode
            self.xuan_reencode()
            # to bi-objective form
            if form == 'trireq':
                return self.__to_tri_max_requirements_form()
            elif form == 'tricus':
                return self.__to_tri_max_customers_form()
            else:
                assert False
        elif self.__project.startswith('Motorola'):
            pass
        elif self.__project.startswith('RALIC'):
            pass
        elif self.__project.startswith('Baan'):
            pass
        else:
            # not found
            assert False

    # dump
    @staticmethod
    def dump(
        file_name : str, \
        variables : List[int], \
        objectives : List[Dict[int, int]], \
        inequations : List[Dict[int, int]],
    ) -> None:
        # prepare a dict for storing all
        result = dict()
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
        if not os.path.exists(DUMP_PATH):
            os.makedirs(DUMP_PATH)
        # add file_name on path
        file_name = os.path.join(DUMP_PATH, file_name)
        # open output file
        with open(file_name, 'w+') as out_file:
            # dump
            json_object = json.dumps(result, indent=4)
            out_file.write(json_object)
            # close the file
            out_file.close()

    # construct MOIPProblem
    @staticmethod
    def MOIP(
        variables : List[int], \
        objectives : List[Dict[int, int]], \
        inequations : List[Dict[int, int]], \
        inequations_operators : List[str], \
        equations : List[Dict[int, int]]
    ) -> MOIPProblem:
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
        MOIP.load(objectives, inequations, equations, False, None)
        # ...load manually
        MOIP.sparseInequationSensesList = inequations_operators
        MOIP.attributeMatrix = attribute_matrix
        # return
        return MOIP

    # moudling, convert NRP to certain MOIPProblem
    def model(self, form : str, option : Dict[str, Any] = None) -> MOIPProblem:
        # check if in NRP FORMS
        assert self.modelable(form)
        # single objective 
        if form == 'single':
            # only allow classic and realistic datasets
            assert self.__project.startswith('classic') or self.__project.startswith('realistic')
            # should be a argument 'b' in option
            assert 'b' in option
            return self.single_form(option['b'])
        elif form == 'binary':
            return self.bi_form()
        elif form == 'bicst':
            return self.bicst_form(option)
        elif form.startswith('tri'):
            return self.tri_form(form)
