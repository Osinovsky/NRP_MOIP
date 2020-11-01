#
# DONG Shi, dongshi@mail.ustc.edu.cn
# LoaderTest.py, created: 2020.10.31
# last modified: 2020.10.31
#

import unittest
from src.Config import Config
from src.Loader import Loader


class LoaderTest(unittest.TestCase):
    def test_load_xuan(self):
        config = Config()
        loader = Loader()
        for name in config.get_index_dict(['classic', 'realistic']):
            problem = loader.load(name)
            # check problem
            # for each dependency
            for dependency in problem.dependencies:
                flag = [False, False]
                for level in problem.cost:
                    for require in level:
                        if require[0] == dependency[0]:
                            flag[0] = True
                        if require[0] == dependency[1]:
                            flag[1] = True
                    if all(flag):
                        break
                assert all(flag)
            # for each requests
            for customer in problem.customers:
                for requirement in customer[2]:
                    flag = False
                    for level in problem.cost:
                        for require in level:
                            if require[0] == requirement:
                                flag = True
                                break
                        if flag:
                            break
                    assert flag


if __name__ == '__main__':
    unittest.main()
