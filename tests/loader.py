import json
import os

from sqlalchemy import Table


class Loader(object):
    """
    Reusable class for loading fixture data into test databases.
    """

    # TODO: Accept the app as a param to look up configs
    # TODO: Load JSON files here instead of in the test
    def __init__(self, db, filename):
        self.connection = db.engine.connect()
        self.filename = filename
        self.metadata = db.metadata

    def load(self):
        with open(self.filename) as file_in:
            self.data = json.load(file_in)
        return self.load_from_file()

    def load_from_file(self):
        table = Table(self.data[0]["table"], self.metadata)
        self.connection.execute(table.insert(), self.data[0]["records"])
        return
