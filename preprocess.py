"""

"""
import os

class Preprocess:
    def __init__(self, specific_location: str = None) -> None:
        if specific_location is None: self.__spec_loc = 'all'
        else: self.__spec_loc = specific_location


    def pre_process(self):
        """
            this will run in the start of the app and control all parts of the preprocess
        :return: None
        """
        if self.__spec_loc == 'all':
            starting_path = 'C:\\\\' if os.name == 'nt' else '/'  # start path of the PC depend on operation system
        else:
            starting_path = self.__spec_loc
        all_files = self._file_reader(starting_path)
        print(all_files)

    def _file_reader(self, start_director: str):
        """
            this function wil read all .txt files from the computer.
        :return: list of all .txt files.
        """
        all_files = list()  # all files list
        for root, dirs, files in os.walk(start_director):  # walk in each location of PC
            for file in files:  # for each file in eac location
                if file.endswith('.txt'):  # add it to the all files list if the file is txt file.
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
        return all_files

    def __verify_language(self):
        pass

    def __language_detect(self):
        pass

x = Preprocess('/Users/yasharzavary/Desktop/Projects/information reterival/Project')
x.pre_process()
