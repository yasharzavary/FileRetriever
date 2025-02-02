"""

"""


class Preprocess:
    def __init__(self, specific_location: str = None) -> None:
        if specific_location is None: self.__spec_loc = 'all'
        else: self.__spec_loc = specific_location


    def pre_process(self):
        pass

    def _file_reader(self):
        pass

    def __verify_language(self):
        pass

    def __language_detect(self):
        pass
