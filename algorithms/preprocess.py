"""
created by: yashar zavary rezaie
"""
import os
from langdetect import detect
from algorithms.fileManager import FileManager
from pypdf import PdfReader
import docx2txt

class Preprocess:
    def __init__(self, specific_location: str = None) -> None:
        if specific_location is None: self.__spec_loc = 'all'
        else: self.__spec_loc = specific_location

    @property
    def loc(self):
        return self.__spec_loc
    @loc.setter
    def loc(self, new):
        self.__spec_loc = new

    def fileCount(self, dir, callback):
        """
            count number of file in the system or location
        :param dir: directory that user want to read files
        :param callback: callback function for talking with ui
        :return:
        """
        i = 0
        tot = 0
        for _, _, files in os.walk(dir):
            i+=0.0001
            callback(i)
            tot += len(files)

        self.__fileNumber = tot

    def pre_process(self, callback, phase):
        """
            this will run in the start of the app and control all parts of the preprocess
        :param callback: callback function for talking with ui
        :param phase: phase that this function will do depend on specific state ui say
        :return: None
        """
        if self.__spec_loc == 'all':
            starting_path = 'C:\\\\' if os.name == 'nt' else '/'  # start path of the PC depend on operation system
        else:
            starting_path = self.__spec_loc
        # read all files and filter language(depend on what state we are on ui)
        if phase == 'count':
            self.fileCount(starting_path, callback)
        elif phase == 'read':
            self.__verified_files_address = self._file_reader(starting_path, callback)
        elif phase == 'lanVerify':
            self.__verified_files_address, self.__fileNumber = self.__verify_language(self.__verified_files_address, callback)
        elif phase == 'analyze':
            FileManager(self.__verified_files_address).addFile(callback)

    def _file_reader(self, start_director: str, callback):
        """
            this function wil read all .txt files from the computer.
        :return: list of all .txt files.
        """
        all_files = list()  # all files list
        i = 0  # process bar show
        step = 100 / self.__fileNumber  # process bar steps
        for root, dirs, files in os.walk(start_director):  # walk in each location of PC
            for file in files:  # for each file in eac location
                i += step
                callback(i)  # update process bar in ui
                if (file.endswith('.txt') or
                        file.endswith('.pdf') or
                        file.endswith('.docx')):  # add it to the all files list if the file is valid format.
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
        return all_files

    def __verify_language(self, raw_files_address:list, callback):
        """
            responsible for find english files and save them in one list and return them back.
        :param raw_files_address: lisr of raw file address that there language don't known
        :return: filtered english files adress list
        """
        verifyFileNumber = 0
        i = 0
        step = 100 / len(raw_files_address)
        filtered_files = list()
        for file_address in raw_files_address:
            i+=step
            callback(i)
            # if file is english, add it to the filtered list
            if self.__language_detect(file_address) == 'en':
                filtered_files.append(file_address)
                verifyFileNumber+=1
        return filtered_files, verifyFileNumber


    def __language_detect(self, file_address: str):
        """
            this function is responsible for detecting langauge of texts and return it to the father function
        :param file_address: file address for reading and detecting language
        :return: if detecting complete, language, if not empty string(False)
        """
        try:
            if file_address[-5:] == '.docx':
                text = docx2txt.process("demo.docx")
            if file_address[-4:] == '.pdf':
                reader = PdfReader(file_address) # read pdf file with pdf reader library
                text = ''
                for i in range(len(reader.pages)):
                    text += reader.pages[i].extract_text()
                    text += '\n'
            elif file_address[-4:] == '.txt':
                # read txt files
                with open(file_address, 'r') as file:
                    text = file.read().strip()

            if not text: return ''  # if file empty, return False
            # try to detect text of the file and return related result.
            return detect(text)
        except:
            print('problem occure in file read and lang detect of preprocess.')
            return ''


