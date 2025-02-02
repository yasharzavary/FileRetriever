import spacy



class FileManager:
    def __init__(self, files_address: list):
        if not files_address: raise('file address is empty')
        self.files_address = files_address
        self.nlp = spacy.load('en_core_web_sm')

    def addFile(self):
        for file_address in self.files_address:
            file = open(file_address)
            txt = file.read().strip()
            file.close()
            tokens = self.__filter(txt)
            print(tokens)

    def __filter(self, text):
        words = self.nlp(text)
        return [token.text for token in words
                if token.is_alpha and not token.is_stop and token.pos not in ['VERB', 'AUX', 'ADJ']
                ]

    def __normalize(self, text):
        pass

    def __addToBinaryDict(self):
        pass
