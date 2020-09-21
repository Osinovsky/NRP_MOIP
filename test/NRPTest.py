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
                    

if __name__ == '__main__':
    unittest.main()