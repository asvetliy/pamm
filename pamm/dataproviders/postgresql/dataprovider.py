import logging

from asyncpgsa import create_pool
from json import dumps
from time import time
from sqlalchemy import select, and_
from pamm.core.repository import Repository
from pamm.core.serializers import AccountsRecordsEncoder, RecordsEncoder
from pamm.core.math import ftoi
from pamm.dataproviders.postgresql.models import *
from pamm.dataproviders.postgresql.scheduler import Scheduler

log = logging.getLogger(__name__)


class PostgreSQL(Repository):
    def __init__(self, pool, options_):
        self.options = options_
        self.pool = pool
        self.scheduler = Scheduler(pool)

    @classmethod
    async def make(cls, options_):
        repository = cls(await create_pool(options_['dsn']), options_)
        await repository.scheduler.load_jobs()
        return repository

    def _add_default_filters(self, request_object, query, table_cls):
        if 'ids' in request_object.data['filters']:
            query = query.where(table_cls.id.in_(request_object.data['filters']['ids']))

        if 'from' in request_object.data['filters'] and 'to' in request_object.data['filters']:
            query = query.where(and_(table_cls.id >= request_object.data['filters']['from'],
                                     table_cls.id <= request_object.data['filters']['to']))
        elif 'from' in request_object.data['filters']:
            query = query.where(table_cls.id >= request_object.data['filters']['from'])
        elif 'to' in request_object.data['filters']:
            query = query.where(table_cls.id <= request_object.data['filters']['to'])

        if 'id' in request_object.data['filters']:
            query = query.where(table_cls.id == request_object.data['filters']['id'])

        if 'offset' in request_object.data['filters']:
            query = query.offset(request_object.data['filters']['offset'])

        if 'limit' in request_object.data['filters']:
            query = query.limit(request_object.data['filters'].get('limit', self.options['get_limit']))

        return query

    def _add_account_id_filter(self, request_object, query, table_cls):
        if 'account_id' in request_object.data['filters']:
            query = query.where(table_cls.account_id == request_object.data['filters']['account_id'])
        return query

    async def get_accounts(self, request_object):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                query = accounts_tbl.select()
                if 'filters' in request_object.data:
                    query = self._add_default_filters(request_object, query, PammAccounts)
                return dumps(await connection.fetch(query), cls=AccountsRecordsEncoder, indent=2)

    async def get_accounts_status(self, request_object):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                query = select(columns=[
                    PammAccounts.id,
                    PammAccounts.user_id,
                    PammAccounts.params,
                    PammAccounts.currency,
                    PammAccounts.created_at,
                    PammAccounts.activated_at,
                    PammAccountsStatus.start_at,
                    PammAccountsStatus.stop_at,
                    PammAccountsStatus.status_code_id
                ]).where(PammAccounts.id == PammAccountsStatus.account_id)
                if 'filters' in request_object.data:
                    query = self._add_default_filters(request_object, query, PammAccounts)
                return dumps(await connection.fetch(query), cls=AccountsRecordsEncoder, indent=2)

    async def get_statuses(self, request_object):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                query = accounts_status_tbl.select()
                if 'filters' in request_object.data:
                    query = self._add_default_filters(request_object, query, PammAccountsStatus)
                return dumps(await connection.fetch(query), cls=RecordsEncoder, indent=2)

    async def update_account_status(self, request_object):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                data = request_object.data.copy()
                account_id = int(data.pop('account_id'))
                return await connection.fetchrow(accounts_status_tbl.update().where(
                    PammAccountsStatus.account_id == account_id
                ).values(data))

    async def account_rollover(self, request_object):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                data = request_object.data.copy()
                digits = await connection.fetchval(
                    f"select currency -> 'digits' as digits from pamm_accounts where id = {data['account_id']}"
                )
                if digits is not None:
                    data['last_balance'] = ftoi(float(request_object.data.get('last_balance')), int(digits))
                    return await connection.fetchrow(accounts_status_tbl.update().where(
                        PammAccountsStatus.account_id == data['account_id']
                    ).values(data))
                return None

    async def create_account(self, request_object):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                data = request_object.data.copy()
                query_data = {
                    'id': data.pop('id'),
                    'user_id': data.pop('user_id'),
                    'params': {},
                    'currency': {
                        'digits': data.pop('currency_digits'),
                        'code': data.pop('currency_code'),
                        'id': data.pop('currency_id')
                    },
                    'created_at': int(time())
                }

                for key, value in data.items():
                    query_data['params'][key] = data[key]

                account_create_result = await connection.fetchrow(
                    accounts_tbl.insert().values(query_data)
                )
                start_at = int(query_data['params']['started_at'])
                stop_at = start_at + int(query_data['params']['rollover_period'])
                query = accounts_status_tbl.insert().values({
                    'account_id': query_data['id'],
                    'start_balance': 0,
                    'last_balance': 0,
                    'status_code_id': 1,
                    'start_at': start_at,
                    'stop_at': stop_at
                })
                await connection.fetchrow(query)

                self.scheduler.add_job(int(query_data['params']['started_at']), query_data['id'],
                                       Scheduler.JOB_TYPE_START)
                self.scheduler.add_job(stop_at, query_data['id'], Scheduler.JOB_TYPE_STOP)

                return account_create_result

    async def get_orders(self, request_object):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                query = orders_tbl.select()
                if 'filters' in request_object.data:
                    query = self._add_default_filters(request_object, query, PammOrders)
                    query = self._add_account_id_filter(request_object, query, PammOrders)
                    if 'order_status_id' in request_object.data['filters']:
                        query = query.where(
                            PammOrders.order_status_id == request_object.data['filters']['order_status_id']
                        )
                return dumps(await connection.fetch(query), cls=RecordsEncoder, indent=2)

    async def create_order(self, request_object):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                query_data = request_object.data.copy()
                query_data['amount'] = ftoi(float(query_data['amount']), int(query_data.pop('currency_digit')))
                query_data['order_type_id'] = select(columns=[PammOrdersType.id]).where(
                    PammOrdersType.code == query_data.pop('type'))
                query_data['order_status_id'] = 1
                query_data['created_at'] = query_data['updated_at'] = int(time())
                return await connection.fetchrow(orders_tbl.insert().values(query_data))

    async def apply_order(self, request_object):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                query = orders_tbl.update().where(PammOrders.id == request_object.data['id']).values({
                    'order_status_id': 3
                })
                return await connection.fetchrow(query)

    async def get_investors(self, request_object):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                query = investors_tbl.select()
                if 'filters' in request_object.data:
                    query = self._add_default_filters(request_object, query, PammInvestors)
                    query = self._add_account_id_filter(request_object, query, PammInvestors)
                return dumps(await connection.fetch(query), cls=RecordsEncoder, indent=2)

    async def create_investor(self, request_object):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                pass

    async def get_tickets(self, request_object):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                query = tickets_tbl.select()
                if 'filters' in request_object.data:
                    query = self._add_default_filters(request_object, query, PammTickets)
                return dumps(await connection.fetch(query), cls=RecordsEncoder, indent=2)

    async def set_early_rollover(self, request_object):
        timestamp = request_object.data.get('timestamp', 1)
        self.scheduler.add_job(timestamp, request_object.data['account_id'], Scheduler.JOB_TYPE_EARLY_STOP)
        return dumps({})
