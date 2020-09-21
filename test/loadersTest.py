# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# loadersTest.py, created: 2020.09.18#
# Last Modified: 2020.09.20          #
# ################################## #

import unittest
import sys
sys.path.append("C:\\Users\\osino\\Desktop\\dev\\prototype\\NRP_MOIP\\src")
from loaders import Loader, XuanLoader, MotorolaLoader, RALICLoader
from config import *

class loadersTest(unittest.TestCase): 
    # test if XuanLoader content is equal after conversion
    def test_XuanLoader_conversion(self):
        for project_name, file_name in ALL_FILES_DICT.items():
            if not project_name.startswith('classic') and not project_name.startswith('realistic'):
                continue # only test classic* and realistic* NRPs
            # get content
            loader = Loader(project_name)
            content = loader.load()
            # content should be (cost, profit, dependencies, requests)
            assert len(content) == 4
            cost, profit, dependencies, requests = content
            # we employe a XuanLoader to load pre-process data
            loader = XuanLoader()
            xuan_cost, xuan_dependencies, xuan_customers = loader.load(file_name)
            # compare
            # cost => xuan_cost
            for req, req_cost in cost.items():
                flag = False
                for cost_line in xuan_cost:
                    cost_dict = dict(cost_line)
                    if req in cost_dict and cost_dict[req] == req_cost:
                        flag = True
                        break
                assert flag
            # xuan_cost => cost
            for cost_line in xuan_cost:
                for req, req_cost in cost_line:
                    assert req in cost
                    assert cost[req] == req_cost
            # profit <=> xuan_customers
            xuan_profit = {x[0]:x[1] for x in xuan_customers}
            assert xuan_profit == profit
            # dependencies <=> xuan_dependencies
            assert set(xuan_dependencies) == set(dependencies)
            # requests => customers
            xuan_requests = {x[0]:x[2] for x in xuan_customers}
            for cus, req in requests:
                assert cus in xuan_requests
                assert req in xuan_requests[cus]
            # customers => requests
            for cus, req_list in xuan_requests.items():
                for req in req_list:
                    assert (cus, req) in requests

    # test Motorola dataset conversion
    def test_Motorola_conversion(self):
        for project_name, file_name in ALL_FILES_DICT.items():
            if not project_name.startswith('Motorola'):
                continue
            # get content
            loader = Loader(project_name)
            cost, profit, _, _ = loader.load()
            # get content directly from MotorolaLoader
            loader = MotorolaLoader()
            cost_revenue = loader.load(file_name)
            # should not be empty
            assert cost_revenue
            assert cost.keys() == profit.keys()
            # cost and profit <=> cost_revenue
            cost_profit = []
            for ite in cost.keys():
                cost_profit.append((cost[ite], profit[ite]))
            assert cost_profit == cost_revenue

    # test RALICLoader conversion
    def test_RALICLoader_conversion(self):
        for project_name, file_name in ALL_FILES_DICT.items():
            if not project_name.startswith('RALIC'):
                continue
            # get content
            loader = Loader(project_name)
            neo_cost, neo_profit, _, _ = loader.load()
            # employ a RALICLoader to load original dataset
            loader = RALICLoader()
            level, cost = loader.load(file_name['sreq'], file_name['cost'])
            cost = {x[0]:x[2] for x in cost if len(x) == 3}
            # neo_cost and cost compare length
            assert len(neo_cost) == len(cost)
            # preprocess level
            profit = [x for x in level if x[1] in cost]
            # length
            assert len(profit) == len(neo_profit)
    
    # test BaanLoader
    def test_BAANLoader(self):
        for project_name, file_name in ALL_FILES_DICT.items():
            if not project_name.startswith('Baan'):
                continue
            # load from Loader
            loader = Loader(project_name)
            cost, profit, _, _ = loader.load()
            # should not be empty
            assert cost and profit

if __name__ == '__main__':
    unittest.main()