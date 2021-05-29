import collections
import re
import string
import pandas as pd
import numbers
from unidecode import unidecode


class Index:
    def __init__(self):
        self.index = dict()
        self.dictionary = dict()
        self.most_repeated_words = []
        self.prefixes = ["پیش", "ریز", "خوش", "نا"]
        self.postfixes = ["نژاد", "اش", "گذاری", "کننده", "گر", "گری", "زار", "آگین", "مند", "ای"]
        self.punctuations = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<',
                             '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', '،', '؟', '!?', '»',
                             '«', '؛']
        self.persian_nums = ['۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۰', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨',
                             '٩', '٠']

    """
    Reads the document by Pandas and updates the index
    """

    def handle_document(self):
        data = pd.read_excel(r'.\data.xlsx', sheet_name='Sheet1')
        data2 = data.to_dict(orient="index")
        for i in range(len(data2)):
            new_data = self.make_document_ready(data2[i]['content'])
            for pos, term in enumerate(new_data):
                if term not in self.dictionary.keys():
                    self.dictionary[term] = dict()
                    self.dictionary[term]['freq'] = 0
                if data2[i]['id'] not in self.dictionary[term].keys():
                    self.dictionary[term][data2[i]['id']] = []
                self.update_dictionary(data2[i]['id'], term, pos)

        self.remove_most_repeated_words(self.dictionary)
        self.numbers(self.dictionary)
        self.sort_dict()
        print(self.dictionary)

    """
    Removes punctuations, numbers, prefixes and postfixes from document
    """

    def make_document_ready(self, doc):
        document = []
        for term in doc.split():
            for punc in self.punctuations:
                term = str.replace(term, punc, '')
            for num in self.persian_nums:
                if num in term:
                    term = str.replace(term, num, unidecode(num))
            if '\u200c' in term:
                considered = False
                term, considered = self.remove_plural_signs(term, considered)
                term, considered = self.remove_continuous_verb_signs(term, considered)
                term, considered = self.remove_comparative_superlative_signs(term, considered)
                term, considered = self.remove_prefixes(term, considered)
                term, considered = self.remove_postfixes(term, considered)
            document.append(term)
        return document

    """
    1. Numbers
    """

    def numbers(self, dictionary: dict):
        for item in dictionary.keys():
            for num in self.persian_nums:
                if num in item:
                    item = str.replace(item, num, unidecode(num))

    """
    2. Removes most repeated words
    """

    def remove_most_repeated_words(self, dictionary: dict):
        result = sorted(dictionary.copy().items(), key=lambda item: item[1]['freq'])
        for i in range(10):
            word = result.pop()[0]
            self.most_repeated_words.append(word)
            del dictionary[word]

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

    def sort_dict(self):
        self.dictionary = collections.OrderedDict(sorted(self.dictionary.items()))

    def update_dictionary(self, id, term, pos):
        self.dictionary[term][id].append(pos)
        self.dictionary[term]['freq'] += 1
        pass
