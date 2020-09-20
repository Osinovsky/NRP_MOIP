# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# config.py, created: 2020.09.18     #
# Last Modified: 2020.09.19          #
# ################################## #

import unittest
import os
import sys
sys.path.append("C:\\Users\\osino\\Desktop\\dev\\prototype\\NRP_MOIP\\src")
from loaders import Loader, XuanLoader, MotorolaLoader
from config import *

class loadersTest(unittest.TestCase):
    # # test if all files are correct
    # def test_load(self):
    #     for project_name in ALL_FILES_DICT.keys():
    #         loader = Loader(project_name)
    #         content = loader.load()
    #         if project_name.startswith('classic') or project_name.startswith('realistic'):
                
    #             # should not empty, excluding dependencies
    #             assert content[0] and content[1] and content[2]
    #         elif project_name.startswith('Motorola'):
    #             # content should be cost&revenue
    #             assert isinstance(content, list)
    #             # should not empty
    #             assert content
    #         elif project_name.startswith('RALIC'):
    #             # content should be levels
    #             assert content
    #         elif project_name.startswith('Baan'):
    #             # content should be (cost, profit)
    #             assert len(content) == 2
    #             # shoule not be empty
    #             assert content[0] and content[1]
    #         else:
    #             # shoule not be here
    #             assert False
    
    # test if XuanLoader content is equal after convertion
    def test_XuanLoader_convertion(self):
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

    # test Motorola dataset convertion
    def test_Motorola_convertion(self):
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

if __name__ == '__main__':
    unittest.main()