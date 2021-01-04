from pamm.rest.handlers import *

routes = [
    ('GET', '/', index, 'index'),

    ('POST', '/accounts/create', create_account),
    ('POST', '/accounts/get', get_accounts),
    ('POST', '/accounts/status/get', get_accounts_status),
    ('POST', '/accounts-status/get', get_statuses),

    ('POST', '/early-rollover/set', set_early_rollover),

    ('POST', '/orders/create', create_order),
    ('POST', '/orders/get', get_orders),

    ('POST', '/investors/create', create_investor),
    ('POST', '/investors/get', get_investors),

    ('POST', '/tickets/get', get_tickets),
]
