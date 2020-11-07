#
# DONG Shi, dongshi@mail.ustc.edu.cn
# Config.py, created: 2020.10.31
# last modified: 2020.11.07
#

from typing import Dict, List
from os import path


class Config:
    """ [summary] Config class is used to store global configs

    Please update Config if you:
        update datasets
        update Loader
    """

    def __init__(self) -> None:
        # datasets
        self.dataset: Dict[str, str] = {}
        # datasets path
        self.dataset_path = './datasets/'
        # keywords, sub-dataset name: dataset name
        self.keywords = {
            'classic': 'xuan',
            'realistic': 'xuan'
        }

        # prepare datasets
        make_index_string = 'make_{}_index'
        for name in self.keywords:
            getattr(self, make_index_string.format(name))()

        # model form
        self.modelling = \
            ['single', 'sincus', 'binary', 'bincst', 'trireq', 'tricus']
        # solving methods
        self.method = \
            ['single', 'epsilon', 'cwmoip', 'ncgop', 'NSGAII']
        # moip methods
        self.moip_method = \
            ['single', 'epsilon', 'cwmoip', 'ncgop']
        # dump methods(for jar algorithm)
        self.dump_method = \
            ['NSGAII']

        # result root path
        self.result_root_path = './results/'
        # dump path
        self.dump_path = './dump/'
        # default task path
        self.task_path = './tasks/'

        # java path
        self.java_exe = 'C:\\Program Files\\Java\\jdk-11.0.8\\bin\\java.exe'
        # self.java_exe = 'java'

    def make_classic_index(self) -> None:
        """make_classic_index [summary] make classic datasets
        index in self.dataset
        """
        # classic nrp index
        classic_name = 'classic_{}'
        classic_format = 'xuan/classic-nrp/nrp{}.txt'
        for name in ['1', '2', '3', '4', '5']:
            self.dataset[classic_name.format(name)] = \
                path.join(self.dataset_path, classic_format.format(name))

    def make_realistic_index(self) -> None:
        """make_realistic_index [summary] make realistic datasets
        index in self.dataset
        """
        # realistic nrp index
        realistic_name = 'realistic_{}'
        realistic_format = 'xuan/realistic-nrp/nrp-{}.txt'
        for name_left in ['e', 'm', 'g']:
            for name_right in ['1', '2', '3', '4']:
                name = name_left + name_right
                self.dataset[realistic_name.format(name)] = \
                    path.join(self.dataset_path, realistic_format.format(name))

    def get_index_dict(self, keywords: List[str]) -> Dict[str, str]:
        """get_index_dict [summary] get given keywords dataset subset

        Args:
            keywords (List[str]):
            [description] project name startswith keywords

        Returns:
            Dict[str, str]: [description] a map from name to file path
        """
        # check if keyword in keywords
        for keyword in keywords:
            assert keyword in self.keywords
        # prepare a tmp dict
        dataset_subset: Dict[str, str] = {}
        # traverse all entry in dataset
        for key in self.dataset:
            # try each keywords
            for keyword in keywords:
                if key.startswith(keyword):
                    dataset_subset[key] = self.dataset[key]
        # return
        return dataset_subset

    def parse_keyword(self, name: str) -> str:
        """parse_keyword [summary] parse the keyword in project name

        Args:
            name (str): [description] project name

        Returns:
            str: [description] the keyword
        """
        # should be in dataset
        assert name in self.dataset
        # find keyword by check startswith
        for keyword in self.keywords:
            if name.startswith(keyword):
                return keyword
        # if not found
        print('keyword lost as project: ', name)
        return ''

    def parse_dataset_keyword(self, name: str) -> str:
        """parse_dataset_keyword [summary] parse the keyword in project name
        but return the dataset name

        Args:
            name (str): [description] project name

        Returns:
            str: [description] dataset keyword
        """
        # should be in dataset
        assert name in self.dataset
        # find keyword by check startswith
        for keyword in self.keywords:
            if name.startswith(keyword):
                return self.keywords[keyword]
        # if not found
        print('keyword lost as project: ', name)
        return ''

    def dataset_names(self) -> List[str]:
        """dataset_names [summary] get all names of datasets

        Returns:
            List[str]: [description] datasets names
        """
        name_set = set()
        for keyword in self.keywords:
            name_set.add(self.keywords[keyword])
        return list(name_set)

    def keyword_cluster(self, keyword: str) -> List[str]:
        """keyword_cluster [summary] cluster problems with same keyword

        Args:
            keyword (str): [description] keyword

        Returns:
            List[str]: [description] all problems with same keyword
        """
        cluster = []
        for name in self.dataset:
            if self.parse_keyword(name) == keyword:
                cluster.append(name)
        return cluster

    def dataset_cluster(self, dataset_name: str) -> List[str]:
        """dataset_cluster [summary] cluster problems inside a dataset

        Args:
            dataset_name (str): [description] dataset name

        Returns:
            List[str]: [description] all problems within same dataset
        """
        cluster = []
        for name in self.dataset:
            if self.parse_dataset_keyword(name) == dataset_name:
                cluster.append(name)
        return cluster

    def name_type(self, name: str) -> str:
        """name_type [summary] testify if name is
        dataset name, keyword or a specific problem name.

        Note that check from dataset name to problem name,
        if there are duplicated names among three levels,
        it will return the toppest level it has met.

        Args:
            name (str): [description] name

        Returns:
            str: [description] 'dataset'/'keyword'/'problem'/'not found'
        """
        for keyword, dataset_name in self.keywords.items():
            if name == dataset_name:
                return 'dataset'
            if name == keyword:
                return 'keyword'
        for problem in self.dataset:
            if name == problem:
                return 'problem'
        return 'not found'

    def if_dump(self, method: str) -> bool:
        """if_dump [summary] if problem should be dumpped,
        or just use MOIPProblem form

        Args:
            method (str): [description] method name

        Returns:
            bool: [description] True -> dump, False -> MOIPProblem
        """
        return method in self.dump_method
