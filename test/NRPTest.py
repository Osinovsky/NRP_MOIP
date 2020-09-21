# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# NRPTest.py, created: 2020.09.21    #
# Last Modified: 2020.09.21          #
# ################################## #

import unittest
import sys
from functools import reduce, partial
from copy import deepcopy
sys.path.append("C:\\Users\\osino\\Desktop\\dev\\prototype\\NRP_MOIP\\src")
from NRP import NextReleaseProblem
from config import *

class NRPTest(unittest.TestCase):
    # test inventory
    def test_inventory(self):
        for project_name in ALL_FILES_DICT.keys():
            # assert is in NRP initialization
            nrp = NextReleaseProblem(project_name)

    # help test_flatten find requesters
    def requester(self, dependencies, req):
        # find all requirements need this req
        requesters = [x[0] for x in dependencies if x[1] == req]
        # recur
        requesters_ready = partial(self.requester, dependencies)
        if len(requesters) == 0:
            return set(requesters)
        else:
            return set(requesters).union(set(reduce(lambda x, y : list(x)+list(y), map(requesters_ready, requesters))))

    # help test_flatten find requestees
    def requestee(self, dependencies, req):
        # find all requirements required by this req
        requestees = [x[1] for x in dependencies if x[0] == req]
        # recur
        requestee_ready = partial(self.requestee, dependencies)
        if len(requestees) == 0:
            return set(requestees)
        else:
            return set(requestees).union(set(reduce(lambda x, y : list(x)+list(y), map(requestee_ready, requestees))))

    # test flatten
    def test_flatten(self):
        for project_name in ALL_FILES_DICT.keys():
            # get content
            nrp = NextReleaseProblem(project_name)
            cost, profit, dependencies, requests = deepcopy(nrp.content())
            # only test who has dependencies
            if not dependencies or len(dependencies) == 0:
                continue
            # flatten
            nrp.flatten()
            # get content again
            neo_cost, neo_profit, neo_dependencies, neo_requests = nrp.content()
            # cost and profit should not be changed
            assert neo_cost == cost
            assert neo_profit == profit
            # dependencies should be empty
            assert not neo_dependencies or len(neo_dependencies) == 0
            # now check requests
            # depdencies, request => neo_requests
            for cus, req in requests:
                # this cus, req should in new requests
                assert (cus, req) in neo_requests
                # find all requirement that require this req
                requesters = self.requester(dependencies, req)
                # find all customers
                for requester in list(requesters):
                    assert (cus, requester) in neo_requests
                
            # neo_requests, dependencies => requests
            for cus, req in neo_requests:
                if (cus, req) in requests:
                    pass # no problem
                else:
                    # find all requestees
                    requestees = self.requestee(dependencies, req)
                    # print(list(requestees))
                    flag = False
                    for requestee in list(requestees):
                        if (cus, requestee) in requests:
                            flag = True
                            break
                    assert flag

    # test xuan reencoding
    def test_xuan_encoding(self):
        for project_name in ALL_FILES_DICT.keys():
            if not project_name.startswith('classic') and not project_name.startswith('realistic'):
                continue
            # get content
            nrp = NextReleaseProblem(project_name)
            if project_name.startswith('classic'):
                nrp.flatten()
            cost, profit, dependencies, requests = deepcopy(nrp.content())
            # encoding
            req_encoder, cus_encoder = nrp.xuan_reencoding()
            # get content again
            neo_cost, neo_profit, neo_dependencies, neo_requests = nrp.content()
            # check if encoding is one-one mapping
            assert len(set(req_encoder.values())) == len(req_encoder)
            assert len(set(cus_encoder.values())) == len(cus_encoder)
            assert not dependencies and not neo_dependencies
            # construct decoder of encoder
            req_decoder = dict(zip(list(req_encoder.values()), list(req_encoder.keys())))
            cus_decoder = dict(zip(list(cus_encoder.values()), list(cus_encoder.keys())))
            # decode neo_cost
            de_cost = dict()
            for req, req_cost in neo_cost.items():
                de_cost[req_decoder[req]] = req_cost
            # decode neo_profit
            de_profit = dict()
            for cus, cus_profit in neo_profit.items():
                de_profit[cus_decoder[cus]] = cus_profit
            # decode requests
            de_requests = []
            for cus, req in neo_requests:
                de_requests.append((cus_decoder[cus], req_decoder[req]))
            # compare
            assert cost == de_cost
            assert profit == de_profit
            assert set(requests) == set(de_requests)

    # check find demands
    def test_find_demands(self):
        for project_name in ALL_FILES_DICT.keys():
            if not project_name.startswith('classic') and not project_name.startswith('realistic'):
                continue
            # get content
            nrp = NextReleaseProblem(project_name)
            if project_name.startswith('classic'):
                nrp.flatten()
            # construct demands
            requests = nrp.content()[3]
            demands = NextReleaseProblem.find_demands(requests)
            # demands => requests
            for key, values in demands.items():
                for value in values:
                    assert (value, key) in requests
            # requests => demands
            for key, value in requests:
                assert value in demands
                assert key in demands[value]

    # help test inequation
    @staticmethod
    def unzip_inequation(inequation):
        assert len(inequation) == 3
        assert 1 in inequation.values()
        assert -1 in inequation.values()
        left = None
        right = None
        for key, value in inequation.items():
            if value == 1:
                left = key
            elif value == -1:
                right = key
        assert left != None and right != None
        return (left, right)
    
    # get a positive coef key
    @staticmethod
    def positive_one(inequation):
        for key, value in inequation.items():
            if value > 0:
                return key
        return None
    
    # get all negative keys
    @staticmethod
    def negative_ones(inequation):
        l = []
        for key, value in inequation.items():
            if value < 0:
                l.append(key)
        return l

    # test for single objective general MOIP conversion
    def test_single_general(self):
        for project_name in ALL_FILES_DICT.keys():
            if not project_name.startswith('classic'):
                continue
            # get content and modelling
            nrp = NextReleaseProblem(project_name)
            moip = nrp.model('single', {'b':0.5})
            cost, profit, _, requests = nrp.content()
            # check for counts
            assert moip.objectiveCount == 1
            assert moip.featureCount == len(cost) + len(profit)
            constant_id = moip.featureCount
            # check for equations
            assert moip.sparseEquationsMapList == [dict()]
            # check for objective
            assert len(moip.objectiveSparseMapList) == 1
            neo_profit = {k:-v for k, v in moip.objectiveSparseMapList[0].items()}
            assert neo_profit == profit
            # check for inequations
            assert len(moip.sparseInequationsMapList) == len(moip.sparseInequationSensesList)
            assert moip.sparseInequationSensesList == ['L']*len(moip.sparseInequationSensesList)
            # construct new requests from inequations
            neo_requests = []
            cost_inequation = None
            for inequation in moip.sparseInequationsMapList:
                if len(inequation) == 3:
                    # constant == 0
                    assert inequation[constant_id] == 0
                    # request
                    neo_requests.append(self.unzip_inequation(inequation))
                else:
                    assert not cost_inequation
                    cost_inequation = inequation
            assert neo_requests == requests
            # check for cost_inequation
            assert not cost_inequation[constant_id] - sum(cost.values())*0.5 > 10e-6
            assert not cost_inequation[constant_id] - sum(cost.values())*0.5 < -10e-6
            del cost_inequation[constant_id]
            assert cost_inequation == cost

    # test for single objective basic stakeholder MOIP conversion
    def test_single_stakeholder(self):
        for project_name in ALL_FILES_DICT.keys():
            if not project_name.startswith('realistic'):
                continue
            # get content
            nrp = NextReleaseProblem(project_name)
            # modelling
            moip = nrp.model('single', {'b':0.5})
            cost, profit, _, requests = nrp.content()
            # check for counts
            assert moip.objectiveCount == 1
            assert moip.featureCount == len(cost) + len(profit)
            constant_id = moip.featureCount
            # check for equations
            assert moip.sparseEquationsMapList == [dict()]
            # check for objective
            assert len(moip.objectiveSparseMapList) == 1
            neo_profit = {k:-v for k, v in moip.objectiveSparseMapList[0].items()}
            assert neo_profit == profit
            # check for inequations
            assert len(moip.sparseInequationsMapList) == len(moip.sparseInequationSensesList)
            assert moip.sparseInequationSensesList == ['L']*len(moip.sparseInequationSensesList)
            # construct new requests from inequations
            neo_requests = []
            neo_demands = dict()
            cost_inequation = None
            # get demands
            demands = NextReleaseProblem.find_demands(requests)
            for inequation in moip.sparseInequationsMapList:
                if inequation[constant_id] != 0:
                    assert not cost_inequation
                    cost_inequation = inequation
                else:
                    # either request or xj - Sum yi <= 0
                    # get a positive key to have a look
                    key = self.positive_one(inequation)
                    assert key != None
                    if key in cost:
                        # xj - Sum yi <= 0
                        demands_list = self.negative_ones(inequation)
                        assert demands_list
                        neo_demands[key] = demands_list
                    elif key in profit:
                        # request
                        # length == 3
                        assert len(inequation) == 3
                        # constant == 0
                        assert inequation[constant_id] == 0
                        # request
                        neo_requests.append(self.unzip_inequation(inequation))
                    else:
                        assert False
            assert neo_demands == demands
            assert neo_requests == requests
            # check for cost_inequation
            assert not cost_inequation[constant_id] - sum(cost.values())*0.5 > 10e-6
            assert not cost_inequation[constant_id] - sum(cost.values())*0.5 < -10e-6
            del cost_inequation[constant_id]
            assert cost_inequation == cost

if __name__ == '__main__':
    unittest.main()