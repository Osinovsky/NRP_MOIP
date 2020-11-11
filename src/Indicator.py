#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Indicator.py, created: 2020.11.10
# last modified: 2020.11.11
#

from typing import Dict, List
import numpy
from jmetal.core.solution import BinarySolution
from jmetal.util.archive import NonDominatedSolutionsArchive
from jmetal.core.quality_indicator import InvertedGenerationalDistance, \
                                          HyperVolume
from src.Result import ResultEntry
from src.util.evenness_indicator import EvennessIndicator
from src.util.ComprehensivenessIndicator import MeanIndicator, MedianIndicator


class Indicator:
    def __init__(self, results: Dict[str, List[ResultEntry]],
                 pareto: NonDominatedSolutionsArchive,
                 methods: List[str], iteration: int) -> None:
        """__init__ [summary] Indicator helps solutions find their
        indicator scores, such as ign, hv and evenness

        Args:
            results (Dict[str, List[ResultEntry]]): [description] results dict
            pareto (NonDominatedSolutionsArchive): [description] pareto front
            methods (List[str]): [description] method names
            iteration (int): [description] iteration times
        """
        # store the pareto results, all pareto front
        # method names, iteration num
        self.results = results
        self.pareto = pareto
        self.methods = methods
        self.iteration = iteration

    @staticmethod
    def numpy_array(solutions: List[BinarySolution]) -> numpy.array:
        """numpy_array [summary] convert BinarySolutions into numpy.array

        Args:
            solutions (List[BinarySolution]): [description]

        Returns:
            numpy.array: [description]
        """
        return numpy.array([solutions[i].objectives
                            for i in range(len(solutions))])

    @staticmethod
    def find_reference_point(solutions: List[BinarySolution]) -> List[float]:
        """find_reference_point [summary] find the reference point

        Args:
            solutions (List[BinarySolution]): [description]

        Returns:
            List[float]: [description] reference point
        """
        # get solution widths
        width = len(solutions[0].objectives)
        # prepare result list
        reference_point = []
        for ite in range(width):
            reference_point.append(max([solutions[i].objectives[ite]
                                   for i in range(len(solutions))]) + 1.0)
        # return it
        return reference_point

    def compute(self, indicator: str, on_front: bool
                ) -> Dict[str, List[ResultEntry]]:
        """compute [summary] compute a indicator score for all in
        result dict

        Args:
            indicator (str): [description] indicator name
            on_front (bool): [description] if compute front or
            all solutions found

        Returns:
            Dict[str, List[ResultEntry]]: [description] results
        """
        for method in self.methods:
            for index in range(self.iteration + 1):
                if on_front:
                    solutions = self.results[method][index].front.solution_list
                else:
                    solutions = self.results[method][index].found.solution_list
                # convert to numpy array
                solution_list = Indicator.numpy_array(solutions)
                self.results[method][index].score[indicator] = \
                    getattr(self, 'compute_{}'.format(indicator)
                            )(solution_list)
        # end nest for
        return self.results

    def compute_igd(self, solutions: numpy.array) -> float:
        pareto_array = Indicator.numpy_array(self.pareto.solution_list)
        return InvertedGenerationalDistance(pareto_array).compute(solutions)

    def compute_hv(self, solutions: numpy.array) -> float:
        reference_point = \
            Indicator.find_reference_point(self.pareto.solution_list)
        mod = numpy.prod(reference_point)
        return HyperVolume(reference_point).compute(solutions) / mod

    def compute_evenness(self, solutions: numpy.array) -> float:
        reference_point = \
            Indicator.find_reference_point(self.pareto.solution_list)
        return EvennessIndicator(reference_point).compute(solutions)

    def compute_mean(self, solutions: numpy.array) -> float:
        return MeanIndicator().compute(solutions)

    def compute_median(self, solutions: numpy.array) -> float:
        return MedianIndicator().compute(solutions)
