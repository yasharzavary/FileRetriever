
import json
from algorithms.fileManager import FileManager
import re
from pathlib import Path

class Search:
    def __init__(self):
        pass


    def readBinaryDict(self):
        if not Path('data/binary_dict.json').is_file():
            self.__binaryDict = {
                'files': dict(),
                'tokens':dict()
            }
        else:
            with open('data/binary_dict.json') as file:
                self.__binaryDict = json.load(file)

        self.__raw_files = self.__binaryDict['files']
        self.__tokens = self.__binaryDict['tokens']
        self.__files = set(self.__binaryDict['files'].keys())



    def __add(self, word, add:bool = False, notToken:bool = False):
        temp = {int(x) for x in self.__files}
        if add:
            self.squence.append(word)
            self.file_list.append('')
        else:
            self.squence.append('H')
            filtered_word = FileManager.filter(word)[0]
            if notToken and filtered_word not in self.__tokens:
                self.file_list.append(temp)
            elif filtered_word in self.__tokens:
                if notToken:
                    self.file_list.append(temp - set(self.__tokens[filtered_word]))
                else:
                    self.file_list.append(set(self.__tokens[filtered_word]))
            else:
                self.file_list.append(set())


    def search(self, query):
        """
            binary query search.
        :param query: user query for search
        :return:
        """
        # operators and usages

        self.squence = list()
        self.file_list = list()
        word_list = query.lower().split(' ')
        i = 0
        while i < len(word_list):
            try:
                if word_list[i] == '' or word_list[i] == ' ':  # ignore if it is empty
                    i+=1
                # add each one to releated part.
                elif word_list[i] == 'not':
                    self.__add(word_list[i+1], notToken=True)
                    i+=1

                elif len(word_list) == 1:
                    self.__add(word_list[i])
                    i+=1
                elif len(word_list)-1 == i:
                    if word_list[i-1] != 'not':
                        self.__add(word_list[i])
                    i+=1
                else:
                    if word_list[i-1] == 'not':
                        if word_list[i + 1] == 'and':
                            self.__add('I', True)
                        elif word_list[i + 1] == 'or':
                            self.__add('U', True)
                    elif word_list[i+1] == 'and':
                        self.__add(word_list[i])
                        self.__add('I', True)
                    elif word_list[i+1] == 'or':
                        self.__add(word_list[i])
                        self.__add('U', True)
                    i+=2
            except: break

        if len(self.squence) == 0: return False  # if squence empty, return file not found.
        while len(self.squence) != 1:

            # updatr sequence and file list depend on words.
            if self.squence[1] == 'I':
                self.squence = self.squence[3:]
                temp = self.file_list[0].intersection(self.file_list[2])
                self.file_list = self.file_list[3:]
                self.file_list.insert(0,temp)
                self.squence.insert(0,'H')
            elif self.squence[1] == 'U':
                self.squence = self.squence[3:]
                temp = self.file_list[0].union(self.file_list[2])
                self.file_list = self.file_list[3:]
                self.file_list.insert(0,temp)
                self.squence.insert(0,'H')

        results = dict()
        for doc_num in self.file_list[0]:
            doc_add = self.__raw_files[f"{doc_num}"]
            results[re.search(r'.*/(.*)', doc_add).group(1)] = doc_add
        return results




