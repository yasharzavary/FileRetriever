import spacy
import json




class FileManager:
    nlp = spacy.load('en_core_web_sm')
    def __init__(self, files_address: list):
        if not files_address: raise('file address is empty')
        self.files_address = files_address
        self.__binaryDict = dict()
        self.__fileCounter = dict()
        self.__counter = 0

    def addFile(self, callback):
        """
            responsible to control file managing process.
        :param callback: send signals to ui for updating progress bar
        :return:
        """
        # data for sending signal to ui
        i = 0
        step = 100 / len(self.files_address)
        for file_address in self.files_address:
            i += step
            callback(i)
            try:
                file = open(file_address)
                txt = file.read().strip()
                file.close()
                tokens = FileManager.filter(txt)  # filter nouns from text
                if not tokens: continue  # if we don't have tokens, go next file
                # store file and tokens of file in binary dict
                self.__fileCounter[self.__counter] = file_address
                self.__addToBinaryDict(tokens)
                self.__counter+=1
            except: continue

        # create final dict
        final_dict = {
            'files': self.__fileCounter,
            'tokens': self.__binaryDict
        }
        # open a file and dump final dict
        with open('data/binary_dict.json', 'w') as outfile:
            json.dump(final_dict, outfile, indent=4)


    @staticmethod
    def filter(text: str) -> list:
        """
            responsible to detect tokens and ignore useless words like verbs, aux and adjectives.
        :param text: raw text
        :return: list of usefull tokens of text.
        """
        # read tokens and get lemma of  the words(normaliztion)
        words = FileManager.nlp(text)
        return [token.lemma_.lower() for token in words
                if token.is_alpha and not token.is_stop and token.pos not in ['VERB', 'AUX', 'ADJ']
                ]

    def __addToBinaryDict(self, token_list: list):
        """
            responsible to add tokens to binary dict and set releated file to that token.
        :param token_list: list of filtered, normalized tokens
        :return: None
        """
        # check each token and add them to the related dictionary
        for token in token_list:
            if token in self.__binaryDict and self.__counter not in self.__binaryDict[token]:
                self.__binaryDict[token].append(self.__counter)
            else:
                self.__binaryDict[token] = [self.__counter]
