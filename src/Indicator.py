#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Indicator.py, created: 2020.11.10
# last modified: 2021.01.17
#

from typing import Dict, List, Any
import numpy
from jmetal.core.solution import BinarySolution
from jmetal.util.archive import NonDominatedSolutionsArchive
from jmetal.core.quality_indicator import InvertedGenerationalDistance, \
                                          HyperVolume
from src.util.evenness_indicator import EvennessIndicator
from src.util.ComprehensivenessIndicator import MeanIndicator, MedianIndicator


class Indicator:
    def __init__(self):
        print('Indicator should not be instanced.')

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

    @staticmethod
    def compute(indicators: List[str],
                solution_archive: NonDominatedSolutionsArchive,
                true_front: NonDominatedSolutionsArchive = None
                ) -> Dict[str, Any]:
        """compute [summary] compute a indicator score for all in
        result dict

        Args:
            indicator (str): [description] indicator name
            solution_archive (NonDominatedSolutionsArchive): [description]
            true_front (NonDominatedSolutionsArchive): [description]
            the whole pareto front
        """
        scores: Dict[str, Any] = {}
        for indicator in indicators:
            solutions = Indicator.numpy_array(solution_archive.solution_list)
            scores[indicator] = \
                getattr(Indicator, 'compute_{}'.format(indicator))(
                    solutions, true_front
                )
        return scores

    def compute_igd(solutions: numpy.array,
                    true_front: NonDominatedSolutionsArchive) -> float:
        pareto_array = Indicator.numpy_array(true_front.solution_list)
        return InvertedGenerationalDistance(pareto_array).compute(solutions)

    def compute_hv(solutions: numpy.array,
                   true_front: NonDominatedSolutionsArchive) -> float:
        reference_point = \
            Indicator.find_reference_point(true_front.solution_list)
        # mod = numpy.prod(reference_point)
        return HyperVolume(reference_point).compute(solutions)

    def compute_evenness(solutions: numpy.array,
                         true_front: NonDominatedSolutionsArchive) -> float:
        reference_point = \
            Indicator.find_reference_point(true_front.solution_list)
        return EvennessIndicator(reference_point).compute(solutions)

    def compute_mean(solutions: numpy.array,
                     true_front: NonDominatedSolutionsArchive) -> float:
        return MeanIndicator().compute(solutions)

    def compute_median(solutions: numpy.array,
                       true_front: NonDominatedSolutionsArchive) -> float:
        return MedianIndicator().compute(solutions)
