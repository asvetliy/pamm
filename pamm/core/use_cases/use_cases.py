import importlib
import logging

from pamm.core.shared.response_object import ResponseFailure

log = logging.getLogger(__name__)


class UseCases(object):
    def __init__(self, repo):
        self.repo = repo

    @classmethod
    def make(cls, repo):
        return cls(repo)

    def _usecase(self, request_object):
        class_name = request_object.type + 'UseCase'
        module = importlib.import_module('pamm.core.use_cases.pamm_use_cases')
        uc = getattr(module, class_name, None)
        if uc is None:
            return None

        return uc.make(self.repo)

    async def execute(self, request_object):
        try:
            uc = self._usecase(request_object)
            if uc is None:
                return ResponseFailure.build_system_error(
                    f'{self.__class__.__name__}: No UseCase found for this request object'
                )
            return await uc.process(request_object)
        except Exception as exc:
            response_object = ResponseFailure.build_system_error(f'{exc.__class__.__name__}: {exc}')
            log.exception(response_object.value, exc_info=False)
            return response_object
