from pamm.core.shared import response_object as res


class LogTypes:
    TYPE_MESSAGE = 'MESSAGE'
    TYPE_EVENT = 'EVENT'


TRANSACTIONS_TYPES_VALUE_KEYS = {
    'MANAGED_IN': 'recipient',
    'INVEST_IN': 'recipient',
    'MANAGED_OUT': 'sender',
    'INVEST_OUT': 'sender'
}

USER_IDS_VALUE_KEYS = {
    'MANAGED_IN': 'sender',
    'INVEST_IN': 'sender',
    'MANAGED_OUT': 'recipient',
    'INVEST_OUT': 'recipient'
}

HTTP_STATUS_CODES = {
    res.ResponseSuccess.SUCCESS: 200,
    res.ResponseFailure.RESOURCE_ERROR: 404,
    res.ResponseFailure.PARAMETERS_ERROR: 400,
    res.ResponseFailure.SYSTEM_ERROR: 500
}
