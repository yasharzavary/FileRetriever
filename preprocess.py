"""
created by: yashar zavary rezaie
"""
import os
from langdetect import detect, DetectorFactory, LangDetectException
from fileManager import FileManager

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
        # read all files and filter language
        verified_files_address = self.__verify_language(self._file_reader(starting_path))
        FileManager(verified_files_address).addFile()

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

    def __verify_language(self, raw_files_address:list):
        """
            responsible for find english files and save them in one list and return them back.
        :param raw_files_address: lisr of raw file address that there language don't known
        :return: filtered english files adress list
        """
        filtered_files = list()
        for file_address in raw_files_address:
            # if file is english, add it to the filtered list
            if self.__language_detect(file_address) == 'en': filtered_files.append(file_address)
        return filtered_files


    def __language_detect(self, file_address: str):
        """
            this function is responsible for detecting langauge of texts and return it to the father function
        :param file_address: file address for reading and detecting language
        :return: if detecting complete, language, if not empty string(False)
        """
        with open(file_address, 'r') as file:
            text = file.read().strip()
            if not text: return ''  # if file empty, return False
            # try to detect text of the file and return related result.
            try: return detect(text)
            except: return ''

x = Preprocess('/Users/yasharzavary/Desktop/Projects/tests/information_reterival_tesets')
x.pre_process()
