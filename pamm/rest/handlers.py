from json import dumps
from aiohttp.web import Response
from aiohttp_validate import validate
from pamm.core.use_cases.request_objects import *
from pamm.core.serializers import AccountsRecordsEncoder
from pamm.constants import HTTP_STATUS_CODES
from .request_schemes import *


async def index(request):
    return Response(text='{"name":"PAMM REST API service"}')


@validate(request_schema=default_get_scheme)
async def get_accounts(params, request):
    request_object = GetAccountsRequestObject.validate(params)
    if request_object:
        response_object = await request.app.use_cases.execute(request_object)
        return Response(
            body=response_object.value,
            status=HTTP_STATUS_CODES[response_object.type],
            content_type='application/json'
        )

    return Response(
        body=dumps(request_object.errors),
        status=HTTP_STATUS_CODES['PARAMETERS_ERROR'],
        content_type='application/json'
    )


@validate(request_schema=default_get_scheme)
async def get_accounts_status(params, request):
    request_object = GetAccountsStatusRequestObject.validate(params)
    if request_object:
        response_object = await request.app.use_cases.execute(request_object)
        return Response(
            body=response_object.value,
            status=HTTP_STATUS_CODES[response_object.type],
            content_type='application/json'
        )

    return Response(
        body=dumps(request_object.errors),
        status=HTTP_STATUS_CODES['PARAMETERS_ERROR'],
        content_type='application/json'
    )


@validate(request_schema=default_get_scheme)
async def get_statuses(params, request):
    request_object = GetStatusesRequestObject.validate(params)
    if request_object:
        response_object = await request.app.use_cases.execute(request_object)
        return Response(
            body=response_object.value,
            status=HTTP_STATUS_CODES[response_object.type],
            content_type='application/json'
        )

    return Response(
        body=dumps(request_object.errors),
        status=HTTP_STATUS_CODES['PARAMETERS_ERROR'],
        content_type='application/json'
    )


@validate(request_schema=create_account_scheme)
async def create_account(params, request):
    request_object = CreateAccountRequestObject.validate(params)
    if request_object:
        response_object = await request.app.use_cases.execute(request_object)
        return Response(
            body=dumps(response_object.value, cls=AccountsRecordsEncoder, indent=2),
            status=HTTP_STATUS_CODES[response_object.type],
            content_type='application/json'
        )

    return Response(
        body=dumps(request_object.errors),
        status=HTTP_STATUS_CODES['PARAMETERS_ERROR'],
        content_type='application/json'
    )


@validate(request_schema=get_orders_scheme)
async def get_orders(params, request):
    request_object = GetOrdersRequestObject.validate(params)
    if request_object:
        response_object = await request.app.use_cases.execute(request_object)
        return Response(
            body=response_object.value,
            status=HTTP_STATUS_CODES[response_object.type],
            content_type='application/json'
        )

    return Response(
        body=dumps(request_object.errors),
        status=HTTP_STATUS_CODES['PARAMETERS_ERROR'],
        content_type='application/json'
    )


async def create_order(request):
    filters = None
    request_object = CreateOrderRequestObject.validate(filters)
    if request_object:
        response_object = await request.app.use_cases.execute(request_object)
        return Response(
            body=response_object.value,
            status=HTTP_STATUS_CODES[response_object.type],
            content_type='application/json'
        )

    return Response(
        body=dumps(request_object.errors),
        status=HTTP_STATUS_CODES['PARAMETERS_ERROR'],
        content_type='application/json'
    )


@validate(request_schema=get_investors_scheme)
async def get_investors(params, request):
    request_object = GetInvestorsRequestObject.validate(params)
    if request_object:
        response_object = await request.app.use_cases.execute(request_object)
        return Response(
            body=response_object.value,
            status=HTTP_STATUS_CODES[response_object.type],
            content_type='application/json'
        )

    return Response(
        body=dumps(request_object.errors),
        status=HTTP_STATUS_CODES['PARAMETERS_ERROR'],
        content_type='application/json'
    )


async def create_investor(request):
    filters = None
    request_object = CreateInvestorRequestObject.validate(filters)
    if request_object:
        response_object = await request.app.use_cases.execute(request_object)
        return Response(
            body=response_object.value,
            status=HTTP_STATUS_CODES[response_object.type],
            content_type='application/json'
        )

    return Response(
        body=dumps(request_object.errors),
        status=HTTP_STATUS_CODES['PARAMETERS_ERROR'],
        content_type='application/json'
    )


@validate(request_schema=default_get_scheme)
async def get_tickets(params, request):
    request_object = GetTicketsRequestObject.validate(params)
    if request_object:
        response_object = await request.app.use_cases.execute(request_object)
        return Response(
            body=response_object.value,
            status=HTTP_STATUS_CODES[response_object.type],
            content_type='application/json'
        )

    return Response(
        body=dumps(request_object.errors),
        status=HTTP_STATUS_CODES['PARAMETERS_ERROR'],
        content_type='application/json'
    )


@validate(request_schema=set_early_rollover_scheme)
async def set_early_rollover(params, request):
    request_object = SetEarlyRolloverRequestObject.validate(params)
    if request_object:
        response_object = await request.app.use_cases.execute(request_object)
        return Response(
            body=response_object.value,
            status=HTTP_STATUS_CODES[response_object.type],
            content_type='application/json'
        )

    return Response(
        body=dumps(request_object.errors),
        status=HTTP_STATUS_CODES['PARAMETERS_ERROR'],
        content_type='application/json'
    )
