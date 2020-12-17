#
# DONG Shi, dongshi@mail.ustc.edu.cn
# QuantumAnnealing.py, created: 2020.12.15
# last modified: 2020.12.17
#

from typing import List, Dict, Tuple, Any
import pickle as pkl
from math import floor, log2
from dwave.system import DWaveSampler, EmbeddingComposite
from jmetal.core.solution import BinarySolution
from jmetal.util.archive import NonDominatedSolutionsArchive
from src.Solvers.ABCSolver import ABCSolver
from src.NRP import NRPProblem

from time import time

QItem = Dict[Tuple[str, str], Any]


class Quadratic:
    def __init__(self) -> None:
        """__init__ [summary] to store quadratic coefficients\
        """
        # members
        self.fixed_variables: List[str] = []
        self.variables: List[str] = []
        self.linear: QItem = {}
        self.quadratic: QItem = {}
        # other members
        self.A: int = 0
        self.n: List[int] = []
        self.problem: NRPProblem
        self.requests: List[Tuple[int, int]] = []

    def qubo(self) -> QItem:
        return {**self.linear, **self.quadratic}

    @staticmethod
    def times_dict_list(dx: Dict[int, int], lx: List[int],
                        pd: str, pl: str, coef: int
                        ) -> QItem:
        quadratic = {}
        dk = list(dx.keys())
        dk_size = len(dk)
        lx_size = len(lx)
        for i in range(dk_size):
            k = dk[i]
            tmp_coef = coef * dx[k]
            for x in range(lx_size):
                key = (pd + str(k), pl + str(x))
                quadratic[key] = tmp_coef * lx[x]
        return quadratic

    @staticmethod
    def quadratic_dict(dx: Dict[int, int], prefix: str, coef: int
                       ) -> Tuple[QItem, QItem]:
        lx = list(dx.keys())
        l_size = len(lx)
        linear = {}
        for k in range(l_size):
            x = lx[k]
            key = (prefix + str(x), prefix + str(x))
            linear[key] = coef * (dx[x] ** 2)
        quadratic = {}
        for k1 in range(l_size):
            x1 = lx[k1]
            tmp_coef = 2 * coef * dx[x1]
            for k2 in range(k1 + 1, l_size):
                x2 = lx[k2]
                key = (prefix + str(x1), prefix + str(x2))
                quadratic[key] = tmp_coef * dx[x2]
        return linear, quadratic

    @staticmethod
    def quadratic_list(lx: List[int], prefix: str, coef: int
                       ) -> Tuple[QItem, QItem]:
        l_size = len(lx)
        linear = {}
        for k in range(l_size):
            key = (prefix + str(k), prefix + str(k))
            linear[key] = coef * (lx[k] ** 2)
        quadratic = {}
        for k1 in range(l_size):
            tmp_coef = 2 * coef * lx[k1]
            for k2 in range(k1 + 1, l_size):
                key = (prefix + str(k1), prefix + str(k2))
                quadratic[key] = tmp_coef * lx[k2]
        return linear, quadratic

    def from_bireq_NRP(self, problem: NRPProblem, W: int = None) -> None:
        """from_bireq_NRP [summary] construct from bireq
        form NRP problem.

        Args:
            problem (NRPProblem): [description]
            W (int): [description] Default to None.
        """
        # should be not constraints
        assert not problem.inequations
        self.problem = problem
        # prepare variables
        self.fixed_variables = ['x' + str(i) for i in problem.variables]
        # prepare the objective
        profit = problem.objectives[0]
        cost = problem.objectives[1]
        # A = max(profit)
        self.A = - min(profit.values())
        # set x and xx
        self.linear, self.quadratic = \
            Quadratic.quadratic_dict(cost, 'x', self.A)
        for key in self.linear:
            x = int(key[0][1:])
            # NOTE that profit is negative
            self.linear[key] = self.linear[key] + profit[x]
        # add z for W bound
        if W:
            self.set_bireq_W(W)

    def set_bireq_W(self, W: int) -> None:
        """set W for bireq
        """
        # set n, n = [1, 2, 4, ..., 2^M-1, W + 1 - 2^M]
        self.n = []
        M = floor(log2(W))
        one = 1
        for _ in range(M):
            self.n.append(one)
            one = one << 1
        self.n.append(W + 1 - one)
        # update vairables
        self.variables = \
            self.fixed_variables + ['z' + str(i) for i in range(len(self.n))]
        # set z linear
        zl, zz = Quadratic.quadratic_list(self.n, 'z', self.A)
        self.linear.update(zl)
        self.quadratic.update(zz)
        # set x-z
        cost = self.problem.objectives[1]
        xz = Quadratic.times_dict_list(cost, self.n, 'x', 'z', -2 * self.A)
        self.quadratic.update(xz)

    @staticmethod
    def parse_request(inequation: Dict[int, int]) -> Tuple[int, int]:
        assert len(inequation) == 3
        customer: int = -1
        requirement: int = -1
        for k, v in inequation.items():
            if v == 0:
                continue
            elif v == 1:
                customer = k
            elif v == -1:
                requirement = k
        assert customer >= 0
        assert requirement >= 0
        return customer, requirement

    def from_binary_NRP(self, problem: NRPProblem, W: int = None) -> None:
        """from_binary_NRP [summary] construct from binary
        form NRP problem.

        Args:
            problem (NRPProblem): [description]
            W (int): [description] Default to None.
        """
        self.problem = problem
        # prepare requests
        for inequ in problem.inequations:
            self.requests.append(Quadratic.parse_request(inequ))
        # prepare the objective
        profit = problem.objectives[0]
        cost = problem.objectives[1]
        # prepare variables
        self.fixed_variables = \
            ['x' + str(i) for i in cost] + ['y' + str(i) for i in profit]
        # A = max(profit)
        self.A = - min(profit.values())
        # set x and xx
        self.linear, self.quadratic = \
            Quadratic.quadratic_dict(cost, 'x', self.A)
        # count each y in requests
        y_count = {}
        for y, _ in self.requests:
            if y not in y_count:
                y_count[y] = 1
            else:
                y_count[y] += 1
        # set y
        yl = {}
        for y, p in profit.items():
            key = ('y' + str(y), 'y' + str(y))
            yl[key] = self.A * y_count[y] - p
        self.linear.update(yl)
        # set xy
        xy = {}
        neg_A = -self.A
        for y, x in self.requests:
            key = ('x' + str(x), 'y' + str(y))
            xy[key] = neg_A
        self.quadratic.update(xy)
        # add z for W bound
        if W:
            self.set_binary_W(W)

    def set_binary_W(self, W: int) -> None:
        """set W for binary, same as bireq
        """
        # set n, n = [1, 2, 4, ..., 2^M-1, W + 1 - 2^M]
        self.n = []
        M = floor(log2(W))
        one = 1
        for _ in range(M):
            self.n.append(one)
            one = one << 1
        self.n.append(W + 1 - one)
        # update vairables
        self.variables = \
            self.fixed_variables + ['z' + str(i) for i in range(len(self.n))]
        # set z linear
        zl, zz = Quadratic.quadratic_list(self.n, 'z', self.A)
        self.linear.update(zl)
        self.quadratic.update(zz)
        # set x-z
        cost = self.problem.objectives[1]
        xz = Quadratic.times_dict_list(cost, self.n, 'x', 'z', -2 * self.A)
        self.quadratic.update(xz)


class QuantumAnnealing(ABCSolver):
    def __init__(self, problem: NRPProblem):
        """__init__ [summary] using Quantum Annealing
        Sampler to solve NRP

        Args:
            problem (NRPProblem): [description] nrp (p)roblem
        """
        # store the problem
        self.problem = problem

        # sampler
        self.sampler = \
            EmbeddingComposite(DWaveSampler(solver='Advantage_system1.1'))

        # solution list
        self.solution_list: List[BinarySolution] = []
        self.archive: NonDominatedSolutionsArchive = \
            NonDominatedSolutionsArchive

        # prepare modelling as Hamiltonian
        self.quadratic = Quadratic()

    def prepare(self):
        # NOTE: only support binary and bireq form NRP
        if self.problem.inequations:
            self.quadratic.from_binary_NRP(self.problem)
        else:
            self.quadratic.from_bireq_NRP(self.problem)

    def execute(self):
        start = time()
        sampleset = \
            self.sampler.sample_qubo(self.quadratic.qubo(), num_reads=1000)
        end = time()
        print('Advantage_system1.1 time:', end - start)
        print(sampleset)
        with open('tmp.sampleset', 'wb') as fout:
            pkl.dump(sampleset, fout)
            fout.close()

    def solutions(self):
        pass

    def variables(self):
        pass
