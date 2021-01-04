class InvalidRequestObject(object):

    def __init__(self, chain_=None):
        self.errors = {'errors': []}
        self.chain = chain_

    def add_error(self, parameter, message):
        self.errors['errors'].append({'parameter': parameter, 'message': message})

    def has_errors(self):
        return len(self.errors['errors']) > 0

    def __nonzero__(self):
        return False

    __bool__ = __nonzero__

    def __to_dict__(self):
        return {
            'errors': self.errors
        }

    __dict__ = __to_dict__


class ValidRequestObject(object):
    def __init__(self, type_, data_, chain_=None):
        self.type = type_
        self.data = data_
        self.chain = chain_

    def __to_dict__(self):
        return {
            'type': self.type,
            'data': self.data
        }

    __dict__ = __to_dict__

    @classmethod
    def validate(cls):
        raise NotImplementedError

    def __nonzero__(self):
        return True

    __bool__ = __nonzero__
