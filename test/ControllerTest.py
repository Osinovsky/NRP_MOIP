#
# DONG Shi, dongshi@mail.ustc.edu.cn
# ControllerTest.py, created: 2020.11.04
# last modified: 2020.11.04
#

import unittest
from string import ascii_letters, digits
from random import choice, randint
from src.Controller import Controller


class ControllerTest(unittest.TestCase):
    def random_string(self):
        return ''.join(choice(ascii_letters+'_'+digits) for _ in range(12))

    def random_dict(self):
        if randint(0, 3):
            result = dict()
            for _ in range(12):
                key = self.random_string()
                while key in result:
                    key = self.random_string()
                value = self.random_string()
                result[key] = value
            return result
        else:
            return {}

    def test_project_name(self):
        for _ in range(100):
            raw = (
                self.random_string(),
                self.random_string(),
                self.random_dict()
            )
            project = Controller.project_name(*raw)
            after = Controller.parse_project(project)
            assert after == raw

    def test_method_name(self):
        for _ in range(100):
            raw = (
                self.random_string(),
                self.random_dict()
            )
            method = Controller.method_name(*raw)
            after = Controller.parse_method(method)
            assert raw == after


if __name__ == "__main__":
    unittest.main()
