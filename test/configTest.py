#
# DONG Shi, dongshi@mail.ustc.edu.cn
# ConfigTest.py, created: 2020.10.31
# last modified: 2020.11.02
#

import unittest
import os.path
from src.Config import Config


class ConfigTest(unittest.TestCase):
    def test_index(self):
        # test index
        config = Config()
        # check if each file path is accessable
        for name in config.dataset:
            file_name = config.dataset[name]
            assert os.path.isfile(file_name)

    def test_keyword(self):
        config = Config()
        # test all keywords
        for keyword in config.keywords:
            subset = config.get_index_dict([keyword])
            for key in subset:
                assert key.startswith(keyword)
            count = 0
            for key in config.dataset:
                if key.startswith(keyword):
                    count += 1
            assert count == len(subset)

    def test_dataset_keyword(self):
        config = Config()
        # test all keywords
        for name in config.dataset:
            key = config.parse_keyword(name)
            assert config.keywords[key] == config.parse_database_keyword(name)


if __name__ == '__main__':
    unittest.main()
