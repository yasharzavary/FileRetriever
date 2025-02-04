
import json

class Search:
    def __init__(self):
        pass


    def readBinaryDict(self):
        with open('data/binary_dict.json') as file:
            self.__binaryDict = json.load(file)



    def search(self, query):
        """
            binary query search.
        :param query: user query for search
        :return:
        """
        # operators and usages
        ops = {'and', 'not', 'or'}
        nots = list()
        ands = list()
        ors = list()

        word_list = query.lower().split(' ')
        i = 0
        while i < len(word_list):
            try:
                if word_list[i] == '' or word_list[i] == ' ':  # ignore if it is empty
                    i+=1
                # add each one to releated part.
                elif word_list[i] == 'not':
                    nots.append(word_list[i+1])
                    i+=1
                elif word_list[i+1] not in ops:
                    ors.append(word_list[i])
                    i+=1
                else:
                    if word_list[i+1] == 'and':
                        ands.append(word_list[i])
                        if word_list[i+2] == 'not':
                            ands.append(word_list[i+3])
                        else:
                            ands.append(word_list[i+2])
                    elif word_list[i+1] == 'or':
                        ors.append(word_list[i])
                        if word_list[i+2] == 'not':
                            ors.append(word_list[i+3])
                        else:
                            ors.append(word_list[i+2])
                    i+=2
            except: break








