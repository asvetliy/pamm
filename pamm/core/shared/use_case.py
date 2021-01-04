class UseCase(object):
    def __init__(self, repo):
        self.repo = repo

    @classmethod
    def make(cls, repo):
        return cls(repo)

    def process(self, request_object):
        raise NotImplementedError('process_request() not implemented by UseCase class')
