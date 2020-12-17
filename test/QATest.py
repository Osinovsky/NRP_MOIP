#
# DONG Shi, dongshi@mail.ustc.edu.cn
# QATest.py, created: 2020.12.16
# last modified: 2020.12.16
#

import unittest
from random import randint
from math import floor, log2
from src.Solvers.QuantumAnnealing import Quadratic
from src.NRP import NextReleaseProblem
from src.Config import Config


class QuadraticTest(unittest.TestCase):
    @staticmethod
    def random_dict(start, size):
        d = {}
        for k in range(start, start + size):
            d[k] = randint(1, 100)
        return d

    @staticmethod
    def random_list(length):
        return [randint(1, 100) for _ in range(length)]

    def test_times_dict_list(self):
        for _ in range(50):
            dd = QuadraticTest.random_dict(100, 100)
            ll = QuadraticTest.random_list(70)
            dtl = Quadratic.times_dict_list(dd, ll, 'x', 'z', max(dd.values()))
            # check
            coef = max(dd.values())
            assert len(dtl) == len(dd) * len(ll)
            for key, v in dtl.items():
                x = int(key[0][1:])
                z = int(key[1][1:])
                assert x in dd
                assert z >= 0 and z < len(ll)
                assert v == coef * dd[x] * ll[z]

    def test_dict_q(self):
        for _ in range(50):
            dd = QuadraticTest.random_dict(100, 100)
            lin, quad = Quadratic.quadratic_dict(dd, 'x', max(dd.values()))
            coef = max(dd.values())
            for key, v in lin.items():
                assert key[0] == key[1]
                x = int(key[0][1:])
                assert v == coef * dd[x] * dd[x]
            for key, v in quad.items():
                x1 = int(key[0][1:])
                x2 = int(key[1][1:])
                assert x1 < x2
                assert v == 2 * coef * dd[x1] * dd[x2]

    def test_list_q(self):
        for _ in range(50):
            ll = QuadraticTest.random_list(100)
            lin, quad = Quadratic.quadratic_list(ll, 'x', max(ll))
            coef = max(ll)
            for key, v in lin.items():
                assert key[0] == key[1]
                x = int(key[0][1:])
                assert v == coef * ll[x] * ll[x]
            for key, v in quad.items():
                x1 = int(key[0][1:])
                x2 = int(key[1][1:])
                assert x1 < x2
                assert v == 2 * coef * ll[x1] * ll[x2]

    @staticmethod
    def multiply(d1, d2, p1, p2, A, order):
        dd = {}
        for k1 in d1:
            for k2 in d2:
                if order:
                    if k1 <= k2:
                        key = (p1 + str(k1), p2 + str(k2))
                    else:
                        key = (p2 + str(k2), p1 + str(k1))
                else:
                    key = (p1 + str(k1), p2 + str(k2))
                if key in dd:
                    dd[key] += A * d1[k1] * d2[k2]
                else:
                    dd[key] = A * d1[k1] * d2[k2]
        return dd

    def test_from_bireq(self):
        config = Config()
        for project in config.dataset:
            nrp = NextReleaseProblem(project)
            nrp.premodel({})
            problem = nrp.model('bireq', {})
            q = Quadratic()
            W = int(sum(problem.objectives[1].values())/2)
            q.from_bireq_NRP(problem, W)

            # convert nrp.nrp to this kind of form and compare
            profit = problem.objectives[0]
            cost = problem.objectives[1]
            assert set(profit.keys()) == set(cost.keys())
            for v in profit.values():
                assert v <= 0
            A = -min(profit.values())
            M = floor(log2(W))
            n = [2 ** i for i in range(M+1)]
            n[M] = W + 1 - n[M]
            nd = {i: v for i, v in enumerate(n)}
            zz = QuadraticTest.multiply(nd, nd, 'z', 'z', A, True)
            assert len(zz) == int(((M+1)**2 + M+1)/2)
            xz = QuadraticTest.multiply(cost, nd, 'x', 'z', -2*A, False)
            xx = QuadraticTest.multiply(cost, cost, 'x', 'x', A, True)
            for x, p in profit.items():
                key = ('x' + str(x), 'x' + str(x))
                xx[key] += p
            qbm = {}
            qbm.update(zz)
            qbm.update(xz)
            qbm.update(xx)

            quadear = q.linear
            quadear.update(q.quadratic)
            for key in quadear:
                if key not in qbm:
                    print(key)
            assert set(qbm.keys()) == set(quadear.keys())
            for key in qbm:
                if qbm[key] != quadear[key]:
                    print(key, qbm[key], quadear[key])
            assert qbm == quadear

    @staticmethod
    def parse_requests(inequ):
        reqs = []
        for ineq in inequ:
            c = -1
            p = -1
            for k, v in ineq.items():
                if v == 1:
                    c = k
                elif v == -1:
                    p = k
            assert c != -1 and p != -1
            reqs.append((c, p))
        return reqs

    def test_from_binary(self):
        config = Config()
        for project in config.dataset:
            nrp = NextReleaseProblem(project)
            nrp.premodel({})
            problem = nrp.model('binary', {})
            q = Quadratic()
            W = int(sum(problem.objectives[1].values())/2)
            q.from_binary_NRP(problem, W)

            # convert nrp.nrp to this kind of form and compare
            profit = problem.objectives[0]
            cost = problem.objectives[1]
            for v in profit.values():
                assert v <= 0
            # get requests
            requests = QuadraticTest.parse_requests(problem.inequations)
            assert len(set(requests)) == len(requests)
            req_count = {}
            for cus, _ in requests:
                if cus in req_count:
                    req_count[cus] += 1
                else:
                    req_count[cus] = 1
            assert len(set(req_count.keys())) == len(profit)
            A = -min(profit.values())
            M = floor(log2(W))
            n = [2 ** i for i in range(M+1)]
            n[M] = W + 1 - n[M]
            nd = {i: v for i, v in enumerate(n)}
            zz = QuadraticTest.multiply(nd, nd, 'z', 'z', A, True)
            xz = QuadraticTest.multiply(cost, nd, 'x', 'z', -2*A, False)
            xx = QuadraticTest.multiply(cost, cost, 'x', 'x', A, True)
            yy = {}
            for cus, c in req_count.items():
                key = ('y' + str(cus), 'y' + str(cus))
                yy[key] = A * c - profit[cus]
            xy = {}
            for cus, req in requests:
                key = ('x' + str(req), 'y' + str(cus))
                xy[key] = -A
            qbm = {**zz, **xz, **xx, **yy, **xy}

            quadear = {**q.linear, **q.quadratic}
            # for key in quadear:
            #     if key not in qbm:
            #         print(key)
            assert set(qbm.keys()) == set(quadear.keys())
            # for key in qbm:
            #     if qbm[key] != quadear[key]:
            #         print(key, qbm[key], quadear[key])
            assert qbm == quadear


if __name__ == "__main__":
    unittest.main()
