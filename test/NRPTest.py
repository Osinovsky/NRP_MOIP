#
# DONG Shi, dongshi@mail.ustc.edu.cn
# LoaderTest.py, created: 2020.11.02
# last modified: 2020.12.25
#

import unittest
from copy import deepcopy
from random import randint
from functools import partial, reduce
from src.Config import Config
from src.NRP import NRPProblem, NextReleaseProblem, RPNRP


class NRPTest(unittest.TestCase):
    @staticmethod
    def reverse_map(d):
        return {v: k for k, v in d.items()}

    def test_reencode_xuan(self):
        config = Config()
        for name in config.dataset:
            if config.parse_dataset_keyword(name) != 'xuan':
                continue
            nrp = NextReleaseProblem(name)
            # old nrp
            onrp = deepcopy(nrp.nrp)
            # reencode
            req, cus = nrp.reencode_xuan()
            assert len(set(req.keys())) == len(set(req.values()))
            assert len(set(cus.keys())) == len(set(cus.values()))
            # new nrp
            nnrp = deepcopy(nrp.nrp)
            rreq = NRPTest.reverse_map(req)
            rcus = NRPTest.reverse_map(cus)
            # rename back nnrp
            cost = dict()
            for req in nnrp.cost:
                cost[rreq[req]] = nnrp.cost[req]
            profit = dict()
            for cus in nnrp.profit:
                profit[rcus[cus]] = nnrp.profit[cus]
            dependencies = \
                [(rreq[x[0]], rreq[x[1]])
                 for x in nnrp.dependencies]
            requests = \
                [(rcus[x[0]], rreq[x[1]])
                 for x in nnrp.requests]
            # check
            assert profit == onrp.profit
            assert cost == onrp.cost
            assert set(requests) == set(onrp.requests)
            assert set(dependencies) == set(onrp.dependencies)

    # help test_flatten find requesters
    def requester(self, dependencies, req):
        # find all requirements need this req
        requesters = [x[0] for x in dependencies if x[1] == req]
        # recur
        requesters_ready = partial(self.requester, dependencies)
        if len(requesters) == 0:
            return set(requesters)
        else:
            tmp = set(reduce(lambda x, y: list(x) + list(y),
                             map(requesters_ready, requesters)))
            return set(requesters).union(tmp)

    # help test_flatten find requestees
    def requestee(self, dependencies, req):
        # find all requirements required by this req
        requestees = [x[1] for x in dependencies if x[0] == req]
        # recur
        requestee_ready = partial(self.requestee, dependencies)
        if len(requestees) == 0:
            return set(requestees)
        else:
            tmp = set(reduce(lambda x, y: list(x) + list(y),
                             map(requestee_ready, requestees)))
            return set(requestees).union(tmp)

    def test_flatten(self):
        config = Config()
        for name in config.dataset:
            key = config.parse_keyword(name)
            if config.parse_dataset_keyword(name) != 'xuan':
                continue
            nrp = NextReleaseProblem(name)
            if key == 'classic':
                if not nrp.nrp.dependencies:
                    continue
                # old nrp
                onrp = deepcopy(nrp.nrp)
                # flatten
                nrp.flatten_xuan()
                # new nrp
                nnrp = deepcopy(nrp.nrp)
                # check
                assert not nnrp.dependencies
                assert onrp.cost == nnrp.cost
                assert onrp.profit == nnrp.profit
                # depdencies, request => neo_requests
                for cus, req in onrp.requests:
                    # this cus, req should in new requests
                    assert (cus, req) in nnrp.requests
                    # find all requirement that require this req
                    requesters = self.requester(onrp.dependencies, req)
                    # find all customers
                    for requester in list(requesters):
                        assert (cus, requester) in nnrp.requests
                # neo_requests, dependencies => requests
                for cus, req in nnrp.requests:
                    if (cus, req) in onrp.requests:
                        pass  # no problem
                    else:
                        # find all requestees
                        requestees = self.requestee(onrp.dependencies, req)
                        # print(list(requestees))
                        flag = False
                        for requestee in list(requestees):
                            if (cus, requestee) in onrp.requests:
                                flag = True
                                break
                        assert flag
            else:
                assert key == 'realistic'
                assert not nrp.nrp.dependencies

    @staticmethod
    def random_objectives(num, dim):
        objectives_list = []
        for _ in range(num):
            objs = {}
            for _ in range(dim):
                objs[randint(0, 499)] = randint(1, 1000)
            objectives_list.append(objs)
        return objectives_list

    def test_attributes(self):
        for _ in range(100):
            nrp_problem = NRPProblem()
            objs = NRPTest.random_objectives(randint(1, 4), 500)
            nrp_problem.variables = list(range(500))
            nrp_problem.objectives = objs
            attrs = nrp_problem.attributes()
            assert len(attrs) == len(objs)
            # check objectives => attrs
            for i in range(len(objs)):
                for key in objs[i]:
                    assert attrs[i][key] == objs[i][key]
            # check attrs => objectives
            for i in range(len(objs)):
                for key in range(len(nrp_problem.variables)):
                    if attrs[i][key] == 0:
                        assert key not in objs[i]
                    else:
                        assert attrs[i][key] == objs[i][key]

    @staticmethod
    def equal_float(f1, f2):
        return abs(f2 - f1) <= 1e-6

    @staticmethod
    def equal_flist(l1, l2):
        assert len(l1) == len(l2)
        return all([NRPTest.equal_float(l1[i], l2[i]) for i in range(len(l1))])

    def test_rp_premodel(self):
        config = Config()
        for name in config.get_index_dict(['MSWord', 'ReleasePlanner']):
            problem = NextReleaseProblem(name)
            assert isinstance(problem.nrp, RPNRP)
            ori = deepcopy(problem.nrp)
            problem.premodel({})
            # calculate profit and risk
            ori.weight = [w/sum(ori.weight) for w in ori.weight]
            for req in range(len(ori.cost)):
                req_profit = 0
                req_risk = 0
                for sh in range(len(ori.weight)):
                    req_profit += ori.weight[sh] * ori.value[(req, sh)]
                ori.profit.append(req_profit)
                for sh in range(len(ori.weight)):
                    req_risk += \
                        ori.weight[sh] * ((ori.value[(req, sh)]-req_profit)**2)
                ori.risk.append(req_risk/len(ori.weight))
            # eliminate couplings
            reduced = dict()
            eq_sl = []
            for r1, r2 in ori.couplings:
                flag = True
                for index, s in enumerate(eq_sl):
                    if r1 in s or r2 in s:
                        eq_sl[index].add(r1)
                        eq_sl[index].add(r2)
                        flag = False
                        break
                if flag:
                    eq_sl.append(set([r1, r2]))
            for s in eq_sl:
                rd = min(s)
                for e in s:
                    if e != rd:
                        reduced[e] = rd
            for rfrom, rto in reduced.items():
                # profit, cost, risk
                ori.profit[rto] += ori.profit[rfrom]
                ori.cost[rto] += ori.cost[rfrom]
                ori.risk[rto] += ori.risk[rfrom]
                tmp_dep = []
                for d1, d2 in ori.dependencies:
                    if d1 == rfrom:
                        d1 = rto
                    if d2 == rfrom:
                        d2 = rto
                    tmp_dep.append((d1, d2))
                ori.dependencies = tmp_dep
            # reduce requirements
            size = len(ori.cost)
            reqs = list(range(size))
            reqs = [e for e in reqs if e not in reduced]
            # update profit, cost, risk
            ori.profit = \
                [e for i, e in enumerate(ori.profit) if i not in reduced]
            ori.cost = \
                [e for i, e in enumerate(ori.cost) if i not in reduced]
            ori.risk = \
                [e for i, e in enumerate(ori.risk) if i not in reduced]
            # update dependencies
            rn = {}
            for ind, var in enumerate(reqs):
                rn[var] = ind
            tmp_dep = []
            for r1, r2 in ori.dependencies:
                tmp_dep.append((rn[r1], rn[r2]))
            ori.dependencies = list(set(list(tmp_dep)))
            # check
            assert not problem.nrp.couplings
            assert NRPTest.equal_flist(problem.nrp.cost, ori.cost)
            assert set(problem.nrp.dependencies) == set(ori.dependencies)
            assert NRPTest.equal_flist(problem.nrp.weight, ori.weight)
            assert NRPTest.equal_flist(problem.nrp.profit, ori.profit)
            assert NRPTest.equal_flist(problem.nrp.risk, ori.risk)


if __name__ == '__main__':
    unittest.main()
