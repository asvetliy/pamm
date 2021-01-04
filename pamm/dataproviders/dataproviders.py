from pamm.dataproviders.postgresql.dataprovider import PostgreSQL


class Dataproviders:
    def __init__(self, type_, options_):
        self.type = type_
        self.options = options_

    def make(self):
        if self.type == 'postgresql':
            return PostgreSQL.make(self.options)
        else:
            return None
