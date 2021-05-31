from pymemcache.client import base
import ast


class Database:

    def __init__(self):
        self.client = base.Client(('localhost', 8080), encoding="utf8", allow_unicode_keys=True)
        # self.client.add('exists', False)
        # print(self.get('exists'))
        # key = "the"
        # obj = [["1,1,1"], ["2,12,3"], ["3,2,300"]]
        # self.client.set(key, obj)
        # list = self.client.get(key).decode(encoding="utf-8")
        # res = ast.literal_eval(list)
        # print(res)

    def get(self, key):
        return self.client.get(key)

    def add(self, key, document):
        """
        Adds a document to the DB.
        """
        self.client.set(key, document)

    def remove(self, key):
        """
        Removes document from DB.
        """
        self.client.delete(key)
