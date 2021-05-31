import ast
import collections
import hashlib
import itertools
import re
import string
import pandas as pd
import numbers
from unidecode import unidecode

import database


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
            return (split_word[0] + '\u200c' + split_word[1]), considered

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
            return (split_word[0] + '\u200c' + split_word[1]), considered

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
            return (split_word[0] + '\u200c' + split_word[1]), considered

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
            return (split_word[0] + '\u200c' + split_word[1]), considered

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
            return (split_word[0] + '\u200c' + split_word[1]), considered

    """
    Sorts the dictionary
    """

    def sort_dict(self):
        self.dictionary = collections.OrderedDict(sorted(self.dictionary.items()))

    """
    Updates the dictionary
    """

    def update_dictionary(self, id, term, pos):
        self.dictionary[term][id].append(pos)
        self.dictionary[term]['freq'] += 1
        pass

    """
    """

    def find_in_query(self, query):
        query2 = []
        commons = self.db.get("Commons")
        commons = commons.decode(encoding="utf-8")
        commons = ast.literal_eval(commons)
        for word in query.split():
            for char in self.punc_chars:
                word = str.replace(word, char, "")
            if word not in commons and (not (str(word).isnumeric())):
                if '\u200c' in word:
                    reduced = False
                    print(f" original word : {word}")
                    word, reduced = self.remove_plural_signs(word, reduced)
                    # print(word, reduced)
                    word, reduced = self.remove_continuous_verb_signs(word, reduced)
                    word, reduced = self.remove_comparative_superlative_signs(word, reduced)
                    word, reduced = self.remove_prefixes(word, reduced)
                    word, reduced = self.remove_postfixes(word, reduced)
                    print(f" reduced word : {word}")
                    print("---------")
                query2.append(word)

        doc_id_list = []
        # print(clean_query)
        query_sub_list = []
        for i in range(len(query2), 0, -1):
            temp = self.findsubsets(query2, i)
            query_sub_list.append(temp)

        doc_ids_dict = {}
        assert isinstance(self.db, database)
        for sub_lists in query_sub_list:
            for sub_list in sub_lists:
                # print(sub_list)
                doc_id_list.clear()
                for c_word in sub_list:
                    # print(sub_list)
                    # print(c_word)
                    match = self.db.get(str(hashlib.sha1(c_word.encode()).hexdigest()))
                    if match is None:
                        # print(c_word)
                        # print("Word not found!")
                        lst = []
                        doc_id_list = lst
                        # print("break")
                        break
                    match = match.decode(encoding="utf-8")
                    res = ast.literal_eval(match)
                    # print(res)
                    lst = []
                    i = 0
                    for ids in res:
                        if i == 0:
                            i += 1
                            continue
                        else:
                            lst.append(ids[0])
                    doc_id_list.append(lst)
                doc_ids_dict[sub_list] = doc_id_list.copy()
        # print(doc_ids_dict)

        results = {}

        for key in doc_ids_dict.keys():
            result = []
            tmp = {}
            if not doc_ids_dict[key]:
                results[key] = []
            else:
                # print(key)
                # print(doc_ids_dict[key])
                if len(doc_ids_dict[key]) == 1:
                    # print(key)
                    for r in doc_ids_dict[key]:
                        # print(r)
                        result.append(r)
                else:
                    for r in doc_ids_dict[key]:
                        # print(key)
                        # print(r)
                        for t in r:
                            if t not in tmp.keys():
                                # print(t)
                                tmp[t] = 1
                            else:
                                tmp[t] += 1
                    # print(key)
                    # print(len(doc_ids_dict[key]))
                    for value in tmp.keys():
                        # print(value, tmp[value])
                        if tmp[value] == len(doc_ids_dict[key]):
                            result.append(value)
                    # print(result)
                    # print()
                    # print("---")
                results[key] = result.copy()
        # print(results)
        return results

    def findsubsets(self, s, n):
        return list(itertools.combinations(s, n))
