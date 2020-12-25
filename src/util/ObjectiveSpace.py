#
# DONG Shi, dongshi@mail.ustc.edu.cn
# ObjectiveSpace.py, created: 2020.12.24
# last modified: 2020.12.24
#

from typing import List, Any, Dict, Tuple
from random import uniform
from math import cos, sin, pi
from cplex import Cplex, SparsePair, infinity
import numpy as np
from numpy import array, matrix, linalg, cross
import matplotlib.pyplot as plt
from matplotlib import cm
from src.Config import Config
from src.NRP import NRPProblem


class ObjectiveSpace3D:
    max_offset = 1e-5

    def __init__(self, problem: NRPProblem) -> None:
        # only support 3D objective space
        assert len(problem.objectives) == 3
        self.dimension = len(problem.objectives)

        # sort the variables
        problem.variables = sorted(problem.variables)
        # store the problem members
        self.binary_index: Dict[int, int] = {}
        for index, var in enumerate(problem.variables):
            self.binary_index[var] = index
        self.binary_variables = \
            ['x' + str(v) for v in range(len(problem.variables))]
        self.object_variables = \
            ['o' + str(o) for o in range(len(problem.objectives))]
        # convert objectives into vectors
        self.objectives: List[array] = []
        for objective in problem.objectives:
            obj: List[Any] = []
            for var in problem.variables:
                if var in objective:
                    obj.append(objective[var])
                else:
                    obj.append(0.0)
            self.objectives.append(array(obj))
        # end for
        # prepare the solver
        self.solver = Cplex()
        # set solver with config
        config = Config()
        self.solver.set_results_stream(None)
        self.solver.set_warning_stream(None)
        self.solver.set_error_stream(None)
        self.solver.parameters.threads.set(config.threads)

        # add variables
        self.solver.variables.add(names=self.binary_variables,
                                  types='B' * len(self.binary_variables))
        self.solver.variables.add(names=self.object_variables + ['l'],
                                  types='C' * (self.dimension + 1),
                                  lb=[-infinity] * self.dimension + [0.0],
                                  ub=[infinity] * (self.dimension + 1))
        # add binary constraints
        pairs: List[SparsePair] = []
        for inequation in problem.inequations:
            c, r = ObjectiveSpace3D.parse_request(inequation)
            c = self.binary_index[c]
            r = self.binary_index[r]
            pair = SparsePair(ind=['x' + str(c), 'x' + str(r)],
                              val=[1, -1])
            pairs.append(pair)
        names = ['req' + str(i) for i in range(len(pairs))]
        self.solver.linear_constraints.add(lin_expr=pairs,
                                           senses='L'*len(pairs),
                                           rhs=[0.0]*len(pairs),
                                           names=names)
        # add objective as constraints
        pairs = []
        for ind, obj in enumerate(self.objectives):
            pair = SparsePair(ind=self.binary_variables + ['o' + str(ind)],
                              val=list(obj) + [-1.0])
            pairs.append(pair)
        names = ['obj' + str(i) for i in range(len(pairs))]
        self.solver.linear_constraints.add(lin_expr=pairs,
                                           senses='E'*len(pairs),
                                           rhs=[0.0]*len(pairs),
                                           names=names)
        # calculate anchors
        self.anchors: List[array] = []
        for obj_name in self.object_variables:
            self.solver.objective.set_linear([(obj_name, 1)])
            self.solver.solve()
            status = self.solver.solution.get_status_string()
            assert 'optimal' in status
            anchor = self.solver.solution.get_values(self.object_variables)
            # reset objective
            self.solver.objective.set_linear([(obj_name, 0)])
            self.anchors.append(array(anchor))

        # calculate utopia plane, assume plane: a1x1 + a2x2 + ... = 1
        # X = [anchor1; anchor2; ...], AX = [1;1;...]
        # A = X^-1. plane is the normal vector of utopia plane
        X = matrix(self.anchors)
        k = np.ones((self.dimension, 1))
        self.plane = \
            np.squeeze(np.asarray(np.transpose(linalg.inv(X).dot(k))))
        # DO NOT NORMALIZE PLANE VECTOR
        # initialize the sampling point, choose the centre point among anchors
        self.centre: array = sum(self.anchors)
        self.centre = self.centre / self.centre.dot(self.plane)
        self.base_vector = self.anchors[0] - self.centre
        self.base_vector = self.base_vector / linalg.norm(self.base_vector)
        self.point = self.centre

    @staticmethod
    def parse_request(inequation: Dict[int, int]) -> Tuple[int, int]:
        customer = -1
        requirement = -1
        for k, v in inequation.items():
            if v == 1:
                customer = k
            elif v == -1:
                requirement = k
        assert customer >= 0 and requirement >= 0
        return (customer, requirement)

    def distance_from_plane(self, point: array) -> float:
        return (point.dot(self.plane) + 1.0) / linalg.norm(self.plane)

    def HR_sample(self) -> Tuple[bool, array]:
        # generate a deflection angle theta
        theta = uniform(0.0, 2.0 * pi)
        # rotate from the base vector
        direction = (cos(theta) * self.base_vector) \
            + (sin(theta) * cross(self.plane, self.base_vector))
        # add l * direction + p = (o1, o2, ...)into constraint
        # di * l - oi = - pi
        pairs: List[SparsePair] = []
        for dim in range(self.dimension):
            pair = SparsePair(ind=['l', self.object_variables[dim]],
                              val=[direction[dim], -1])
            pairs.append(pair)
        names = ['sample' + str(i) for i in range(self.dimension)]
        self.solver.linear_constraints.add(lin_expr=pairs,
                                           senses='E'*self.dimension,
                                           rhs=list(-self.point),
                                           names=names)
        # max l
        self.solver.objective.set_linear([('l', 1.0)])
        self.solver.objective.set_sense(self.solver.objective.sense.maximize)
        # solve max l
        self.solver.solve()
        status = self.solver.solution.get_status_string()
        if 'optimal' in status:
            # have bounded solution
            l_max = self.solver.solution.get_values('l')
        elif 'unbounded' in status:
            # inf, TODO: just set 1.0 maybe not suitable
            print('unbounded set to 1.0 in H&R sampling')
            l_max = 1.0
        elif 'infeasible' in status:
            print(status)
            return (False, array([]))
        else:
            print(status)
            assert False
        # delete constraints
        self.solver.linear_constraints.delete(names)
        # random l in range(0, l_max)
        l_flake8_does_not_accept_too_short_name = uniform(0.0, l_max)
        # update the point = point + l * direction
        self.point = \
            self.point + l_flake8_does_not_accept_too_short_name * direction
        # check if point is far away from the plane
        dist = self.distance_from_plane(self.point)
        if abs(dist) > self.max_offset:
            print('fix point on the plane')
            self.point = self.point - (dist/linalg.norm(self.plane))
        return (True, self.point)

    def plot(self, points: List[array]) -> None:
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        # set plot range
        x_range = [a[0] for a in self.anchors]
        y_range = [a[1] for a in self.anchors]
        z_range = [a[2] for a in self.anchors]
        x_min, x_max = min(x_range), max(x_range)
        y_min, y_max = min(y_range), max(y_range)
        z_min, z_max = min(z_range), max(z_range)
        min_min = min([x_min, y_min, z_min])
        max_max = max([x_max, y_max, z_max])
        step = (max_max - min_min) / 1000.0
        X = np.arange(min_min, max_max, step)
        Y = np.arange(min_min, max_max, step)
        X, Y = np.meshgrid(X, Y)
        Z = (1.0 - self.plane[0] * X - self.plane[1] * Y) / self.plane[2]
        # plot
        ax.plot_surface(X, Y, Z, cmap=cm.binary, linewidth=0, antialiased=True)
        # plot points
        if len(points) == 0:
            # draw point
            plt.plot(self.centre[0], self.centre[1], self.centre[2], 'ro')
        else:
            # draw routes
            x = [p[0] for p in points]
            y = [p[1] for p in points]
            z = [p[2] for p in points]
            for i in range(len(points) - 1):
                plt.plot(x[i:i+2], y[i:i+2], z[i:i+2], 'ro-')
        plt.show()
