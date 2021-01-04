from pamm.constants import TRANSACTIONS_TYPES_VALUE_KEYS, USER_IDS_VALUE_KEYS
from pamm.core.shared import request_object as req
from pamm.core.math import is_number


class GetAccountsRequestObject(req.ValidRequestObject):
    TYPE = 'GetAccounts'

    def __init__(self, data_):
        super(GetAccountsRequestObject, self).__init__(self.TYPE, data_)

    @classmethod
    def validate(cls, data=None):
        return GetAccountsRequestObject(data)


class GetAccountsStatusRequestObject(req.ValidRequestObject):
    TYPE = 'GetAccountsStatus'

    def __init__(self, data_):
        super(GetAccountsStatusRequestObject, self).__init__(self.TYPE, data_)

    @classmethod
    def validate(cls, data=None):
        return GetAccountsStatusRequestObject(data)


class GetStatusesRequestObject(req.ValidRequestObject):
    TYPE = 'GetStatuses'

    def __init__(self, data_):
        super(GetStatusesRequestObject, self).__init__(self.TYPE, data_)

    @classmethod
    def validate(cls, data=None):
        return GetStatusesRequestObject(data)


class CreateAccountRequestObject(req.ValidRequestObject):
    TYPE = 'CreateAccount'

    def __init__(self, data_, chain_=None):
        super(CreateAccountRequestObject, self).__init__(self.TYPE, data_, chain_)

    @classmethod
    def validate(cls, data: dict = None):
        invalid_req = req.InvalidRequestObject()
        chain = None

        if data is None:
            invalid_req.add_error('request', 'No data in request')
        if 'user_id' not in data:
            invalid_req.add_error('request', 'user_id - field is required')
        else:
            if type(data['user_id']) != int or data['user_id'] <= 0:
                invalid_req.add_error('request', 'user_id - must be an integer > 0')
        if 'id' not in data:
            invalid_req.add_error('request', 'id - field is required')
        else:
            chain = f'wallet_{data["id"]}'
        if 'currency_digits' not in data:
            invalid_req.add_error('request', 'currency_digits - field is required')
        if 'currency_code' not in data:
            invalid_req.add_error('request', 'currency_code - field is required')
        if 'currency_id' not in data:
            invalid_req.add_error('request', 'currency_id - field is required')
        if invalid_req.has_errors():
            invalid_req.chain = chain
            return invalid_req

        return CreateAccountRequestObject(data, chain)


class CreateOrderRequestObject(req.ValidRequestObject):
    TYPE = 'CreateOrder'

    def __init__(self, data_, chain_=None):
        super(CreateOrderRequestObject, self).__init__(self.TYPE, data_, chain_)

    @classmethod
    def validate(cls, data: dict = None):
        invalid_req = req.InvalidRequestObject()
        chain = None

        if 'id' not in data or type(data['id']) != int:
            invalid_req.add_error('request', 'id - field is required and must be an integer value')
        if 'currency_id' not in data or type(data['currency_id']) != int:
            invalid_req.add_error('request', 'currency_id - field is required and must be an integer value')
        if 'currency_digit' not in data or type(data['currency_digit']) != int:
            invalid_req.add_error('request', 'currency_digit - field is required and must be an integer value')
        if 'amount' not in data or type(data['amount']) != str or not is_number(data['amount']):
            invalid_req.add_error('request', 'amount - field is required and must be an numeric value')
        if 'type' not in data or data['type'] not in TRANSACTIONS_TYPES_VALUE_KEYS.keys():
            invalid_req.add_error('request',
                                  f'type - field is required and must be in list: {TRANSACTIONS_TYPES_VALUE_KEYS.keys()}')
        else:
            if 'account_id' not in data:
                value_key = f'{TRANSACTIONS_TYPES_VALUE_KEYS[data["type"]]}_id'
                if value_key in data and type(data[value_key]) == int:
                    data['account_id'] = data.get(value_key)
                    if 'recipient_id' in data:
                        del data['recipient_id']
                    if 'sender_id' in data:
                        del data['sender_id']
                    chain = f'wallet_{data["account_id"]}'
                else:
                    invalid_req.add_error('request',
                                          f'{value_key} or account_id - field is required and must be an integer value')
            if 'user_id' not in data:
                value_key = f'{USER_IDS_VALUE_KEYS[data["type"]]}_user_id'
                if value_key in data and type(data[value_key]) == int:
                    data['user_id'] = data.get(value_key)
                    if 'recipient_user_id' in data:
                        del data['recipient_user_id']
                    if 'sender_user_id' in data:
                        del data['sender_user_id']
                else:
                    invalid_req.add_error('request',
                                          f'{value_key} or user_id - field is required and must be an integer value')
        if invalid_req.has_errors():
            invalid_req.chain = chain
            return invalid_req

        return CreateOrderRequestObject(data, chain)


class ApplyOrderRequestObject(req.ValidRequestObject):
    TYPE = 'ApplyOrder'

    def __init__(self, data_, chain_=None):
        super(ApplyOrderRequestObject, self).__init__(self.TYPE, data_, chain_)

    @classmethod
    def validate(cls, data=None):
        invalid_req = req.InvalidRequestObject()
        chain = None

        if 'id' not in data or type(data['id']) != int:
            invalid_req.add_error('request', 'id - field is required and must be an integer value')
        if 'type' not in data or data['type'] not in TRANSACTIONS_TYPES_VALUE_KEYS.keys():
            invalid_req.add_error('request',
                                  f'type - field is required and must be in list: {TRANSACTIONS_TYPES_VALUE_KEYS.keys()}')
        else:
            if 'account_id' not in data:
                value_key = f'{TRANSACTIONS_TYPES_VALUE_KEYS[data["type"]]}_id'
                if value_key in data and type(data[value_key]) == int:
                    data['account_id'] = data.get(value_key)
                    if 'recipient_id' in data:
                        del data['recipient_id']
                    if 'sender_id' in data:
                        del data['sender_id']
                    chain = f'wallet_{data["account_id"]}'
                else:
                    invalid_req.add_error('request',
                                          f'{value_key} or account_id - field is required and must be an integer value')
        if invalid_req.has_errors():
            invalid_req.chain = chain
            return invalid_req

        return ApplyOrderRequestObject(data, chain)


class GetOrdersRequestObject(req.ValidRequestObject):
    TYPE = 'GetOrders'

    def __init__(self, data_):
        super(GetOrdersRequestObject, self).__init__(self.TYPE, data_)

    @classmethod
    def validate(cls, data=None):
        invalid_req = req.InvalidRequestObject()

        if data is not None:
            if 'filters' not in data or type(data['filters']) != dict:
                invalid_req.add_error('filters', 'Is not iterable')

        if invalid_req.has_errors():
            return invalid_req

        return GetOrdersRequestObject(data)


class GetInvestorsRequestObject(req.ValidRequestObject):
    TYPE = 'GetInvestors'

    def __init__(self, data_):
        super(GetInvestorsRequestObject, self).__init__(self.TYPE, data_)

    @classmethod
    def validate(cls, data=None):
        invalid_req = req.InvalidRequestObject()

        if data is not None:
            if 'filters' not in data or type(data['filters']) != dict:
                invalid_req.add_error('filters', 'Is not iterable')

        if invalid_req.has_errors():
            return invalid_req

        return GetInvestorsRequestObject(data)


class CreateInvestorRequestObject(req.ValidRequestObject):
    TYPE = 'CreateInvestor'

    def __init__(self, data_):
        super(CreateInvestorRequestObject, self).__init__(self.TYPE, data_)

    @classmethod
    def validate(cls, data=None):
        invalid_req = req.InvalidRequestObject()

        if invalid_req.has_errors():
            return invalid_req

        return CreateInvestorRequestObject(data)


class AccountStoppedRequestObject(req.ValidRequestObject):
    TYPE = 'AccountStopped'

    def __init__(self, data_, chain_=None):
        super(AccountStoppedRequestObject, self).__init__(self.TYPE, data_, chain_)

    @classmethod
    def validate(cls, data=None):
        invalid_req = req.InvalidRequestObject()
        chain = None

        if 'account_id' not in data or type(data['account_id']) != int:
            invalid_req.add_error('request', 'account_id - field is required and must be an integer value')
        else:
            chain = f'wallet_{data["account_id"]}'
        if 'last_balance' not in data or type(data['last_balance']) != str:
            invalid_req.add_error('request', 'last_balance - field is required and must be an not empty string')
        else:
            data['last_balance'] = float(data['last_balance'])

        if invalid_req.has_errors():
            invalid_req.chain = chain
            return invalid_req

        data['status_code_id'] = 3
        return AccountStoppedRequestObject(data, chain)


class GetTicketsRequestObject(req.ValidRequestObject):
    TYPE = 'GetTickets'

    def __init__(self, data_):
        super(GetTicketsRequestObject, self).__init__(self.TYPE, data_)

    @classmethod
    def validate(cls, data=None):
        invalid_req = req.InvalidRequestObject()

        if data is not None:
            if 'filters' not in data or type(data['filters']) != dict:
                invalid_req.add_error('filters', 'Is not iterable')

        if invalid_req.has_errors():
            return invalid_req

        return GetTicketsRequestObject(data)


class SetEarlyRolloverRequestObject(req.ValidRequestObject):
    TYPE = 'SetEarlyRollover'

    def __init__(self, data_):
        super(SetEarlyRolloverRequestObject, self).__init__(self.TYPE, data_)

    @classmethod
    def validate(cls, data=None):
        invalid_req = req.InvalidRequestObject()

        if data is not None:
            if 'account_id' not in data or type(data['account_id']) != int:
                invalid_req.add_error('request', 'account_id - field is required and must be an integer value')
            if 'timestamp' in data and type(data['timestamp']) != int:
                invalid_req.add_error('request', 'timestamp - field is must be an integer value')

        if invalid_req.has_errors():
            return invalid_req

        return SetEarlyRolloverRequestObject(data)
