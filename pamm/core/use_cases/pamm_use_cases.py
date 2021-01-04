from pamm.core.shared.response_object import ResponseSuccess
from pamm.core.shared.use_case import UseCase


class CreateAccountUseCase(UseCase):
    async def process(self, request_object):
        result = await self.repo.create_account(request_object)
        return ResponseSuccess(result)


class GetAccountsUseCase(UseCase):
    async def process(self, request_object):
        result = await self.repo.get_accounts(request_object)
        return ResponseSuccess(result)


class GetAccountsStatusUseCase(UseCase):
    async def process(self, request_object):
        result = await self.repo.get_accounts_status(request_object)
        return ResponseSuccess(result)


class GetStatusesUseCase(UseCase):
    async def process(self, request_object):
        result = await self.repo.get_statuses(request_object)
        return ResponseSuccess(result)


class CreateOrderUseCase(UseCase):
    async def process(self, request_object):
        result = await self.repo.create_order(request_object)
        self.repo.scheduler.add_event(request_object)
        return ResponseSuccess(result)


class ApplyOrderUseCase(UseCase):
    async def process(self, request_object):
        result = await self.repo.apply_order(request_object)
        self.repo.scheduler.add_event(request_object)
        return ResponseSuccess(result)


class AccountStoppedUseCase(UseCase):
    async def process(self, request_object):
        result = await self.repo.account_rollover(request_object)
        self.repo.scheduler.add_event(request_object)
        return ResponseSuccess(result)


class GetOrdersUseCase(UseCase):
    async def process(self, request_object):
        result = await self.repo.get_orders(request_object)
        return ResponseSuccess(result)


class CreateInvestorUseCase(UseCase):
    async def process(self, request_object):
        result = await self.repo.create_investor(request_object)
        return ResponseSuccess(result)


class GetInvestorsUseCase(UseCase):
    async def process(self, request_object):
        result = await self.repo.get_investors(request_object)
        return ResponseSuccess(result)


class GetTicketsUseCase(UseCase):
    async def process(self, request_object):
        result = await self.repo.get_tickets(request_object)
        return ResponseSuccess(result)


class SetEarlyRolloverUseCase(UseCase):
    async def process(self, request_object):
        result = await self.repo.set_early_rollover(request_object)
        return ResponseSuccess(result)
