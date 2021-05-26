import collections
import re
import string
import pandas as pd
import numbers


class Index:
    def __init__(self):
        self.index = dict()
        self.dictionary = dict()
        self.most_repeated_words = []
        self.prefixes = ["پیش", "ریز", "خوش", "نا"]
        self.postfixes = ["نژاد", "اش", "گذاری", "کننده", "گر", "گری", "زار", "آگین", "مند", "ای"]
        self.punctuations = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<',
                             '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', '،', '؟', "!?", "»",
                             "«", "؛"]

    """
    Reads the document by Pandas and updates the index
    """

    def handle_document(self):
        data = pd.read_excel(r'.\data.xlsx', sheet_name='Sheet1')
        # for doc in data['content']:
        #     self.make_document_ready(doc)
        self.make_document_ready(data['content'][0])

    """
    Removes punctuations, numbers, prefixes and postfixes from document
    """

    def make_document_ready(self, doc):
        document = []
        for term in doc.split():
            for punc in self.punctuations:
                term = str.replace(term, punc, "")
            if '\u200c' in term:
                considered = False
                term, considered = self.remove_plural_signs(term, considered)
                term, considered = self.remove_comparative_superlative_signs(term, considered)
                term, considered = self.remove_continuous_verb_signs(term, considered)
                term, considered = self.remove_prefixes(term, considered)
                term, considered = self.remove_postfixes(term, considered)
            document.append(term)
        print(document)
    """
    1. Removes numbers
    """

    @staticmethod
    def remove_numbers(dictionary):
        for item in dictionary.copy().keys():
            if isinstance(item, numbers.Number):
                del dictionary[item]

    """
    2. Removes most repeated words
    """

    def remove_most_repeated_words(self, dictionary):
        result = sorted(dictionary.copy().items(), key=lambda item: item[1]['freq'])
        for i in range(10):
            word = result.pop()[0]
            self.most_repeated_words.append(word)
            del result[word]

    """
    3. Removes plural signs "ها" and "های"
    """

    def remove_plural_signs(self, word, considered):
        if considered:
            return word, considered
        split_word = word.split('\u200c')
        if split_word[1] == 'ها' or split_word[1] == 'های':
            considered = True
            return split_word[0], considered
        else:
            return split_word[0] + '\u200c' + split_word[1], considered

    """
    4. Removes comparative and superlative signs
    """

    def remove_comparative_superlative_signs(self, word, considered):
        if considered:
            return word, considered
        split_word = word.split('\u200c')
        if split_word[1] == 'تر' or split_word[1] == 'ترین':
            considered = True
            return split_word[0], considered
        else:
            return split_word[0] + '\u200c' + split_word[1], considered

    """
    5. Removes prefixes
    """

    def remove_prefixes(self, word, considered):
        if considered:
            return word, considered
        split_word = word.split('\u200c')
        if split_word[0] in self.prefixes:
            considered = True
            return split_word[1], considered
        else:
            return split_word[0] + '\u200c' + split_word[1], considered

    """
    6. Removes postfixes
    """

    def remove_postfixes(self, word, considered):
        if considered:
            return word, considered
        split_word = word.split('\u200c')
        if split_word[1] in self.postfixes:
            considered = True
            return split_word[0], considered
        else:
            return split_word[0] + '\u200c' + split_word[1], considered

    """
    7. Removes continuous verb signs
    """

    def remove_continuous_verb_signs(self, word, considered):
        if considered:
            return word, considered
        split_word = word.split('\u200c')
        if split_word[0] == 'می' or split_word[0] == 'نمی':
            result = re.sub('((ند)|(ید)|(یم)|(د)|(ی)|(م))$', '', split_word[1])
            considered = True
            return result, considered
        else:
            return split_word[0] + '\u200c' + split_word[1], considered

    """
    Sorts the dictionary
    """

    def sort_dict(self, dictionary):
        self.dictionary = collections.OrderedDict(sorted(self.dictionary.items()))
