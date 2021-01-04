create_account_scheme = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer', 'minimum': 0},
        'user_id': {'type': 'number', 'minimum': 0},
        'currency_id': {'type': 'number', 'minimum': 0},
        'currency_digits': {'type': 'number', 'minimum': 0},
        'min_invest': {'type': 'number', 'minimum': 0},
        'reward_percent': {'type': 'number', 'minimum': 0, 'maximum': 100},
        'rollover_period': {'type': 'number', 'minimum': 0},
        'pub_stat_lag': {'type': 'number', 'minimum': 0},
        'started_at': {'type': 'number', 'minimum': 0},
    },
    'required': ['id', 'user_id', 'currency_id', 'currency_digits', 'reward_percent', 'rollover_period', 'started_at'],
    'additionalProperties': False
}

default_get_scheme = {
    'type': 'object',
    'properties': {
        'filters': {
            'type': 'object',
            'properties': {
                'from': {'type': 'integer', 'minimum': 0},
                'to': {'type': 'integer', 'minimum': 0},
                'limit': {'type': 'integer', 'minimum': 0},
                'offset': {'type': 'integer', 'minimum': 0},
                'id': {'type': 'integer', 'minimum': 0},
                'ids': {'type': 'array'}
            },
            'additionalProperties': False
        }
    },
    'additionalProperties': False
}

get_investors_scheme = {
    'type': 'object',
    'properties': {
        'filters': {
            'type': 'object',
            'properties': {
                'from': {'type': 'integer', 'minimum': 0},
                'to': {'type': 'integer', 'minimum': 0},
                'limit': {'type': 'integer', 'minimum': 0},
                'offset': {'type': 'integer', 'minimum': 0},
                'id': {'type': 'integer', 'minimum': 0},
                'ids': {'type': 'array'},
                'account_id': {'type': 'integer', 'minimum': 0}
            },
            'additionalProperties': False
        }
    },
    'additionalProperties': False
}

get_orders_scheme = {
    'type': 'object',
    'properties': {
        'filters': {
            'type': 'object',
            'properties': {
                'from': {'type': 'integer', 'minimum': 0},
                'to': {'type': 'integer', 'minimum': 0},
                'limit': {'type': 'integer', 'minimum': 0},
                'offset': {'type': 'integer', 'minimum': 0},
                'id': {'type': 'integer', 'minimum': 0},
                'ids': {'type': 'array'},
                'account_id': {'type': 'integer', 'minimum': 0},
                'order_status_id': {'type': 'integer', 'minimum': 0}
            },
            'additionalProperties': False
        }
    },
    'additionalProperties': False
}

set_early_rollover_scheme = {
    'type': 'object',
    'properties': {
        'account_id': {'type': 'integer', 'minimum': 0},
        'timestamp': {'type': 'integer', 'minimum': 0},
    },
    'required': ['account_id'],
    'additionalProperties': False
}
