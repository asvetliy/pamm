import asyncio
import logging
import json

from time import time
from sqlalchemy import and_, or_, text, select
from pamm.dataproviders.postgresql.models import *
from pamm.constants import LogTypes
from pamm.core.math import *

log = logging.getLogger(__name__)


class Scheduler(object):
    JOB_TYPE_START = 'JOB_TYPE_START'
    JOB_TYPE_STOP = 'JOB_TYPE_STOP'
    JOB_TYPE_EARLY_STOP = 'JOB_TYPE_EARLY_STOP'

    def __init__(self, pool_):
        self.pool = pool_
        self._jobs = {
            'JOB_TYPE_START': {},
            'JOB_TYPE_STOP': {},
            'JOB_TYPE_EARLY_STOP': {},
        }
        self._stop = False
        self._tasks = {}
        self._events = []
        self._checkers = []
        self.loop = asyncio.get_event_loop()
        checker = self.loop.create_task(self.checker())
        self._checkers.append(checker)
        watcher = self.loop.create_task(self.watcher())
        self._checkers.append(watcher)
        events_checker = self.loop.create_task(self.events_checker())
        self._checkers.append(events_checker)

    def add_event(self, request_object):
        self._events.append(request_object)

    async def events_checker(self):
        await asyncio.sleep(5)
        while not self._stop:
            if len(self._events):
                event = self._events.pop(0)
                if event.type == 'CreateOrder':
                    await self.check_is_managed_in(event.data)
                if event.type == 'ApplyOrder':
                    account_id = event.data.get('account_id', None)
                    order_id = event.data.get('id')
                    await self.balance_changed(order_id)
                    self.decrease_job_counter(account_id, self.JOB_TYPE_START)
                    self.decrease_job_counter(account_id, self.JOB_TYPE_STOP)
                if event.type == 'AccountStopped':
                    account_id = event.data.get('account_id', None)
                    self.decrease_job_counter(account_id, self.JOB_TYPE_STOP)
            await asyncio.sleep(1)

    async def balance_changed(self, order_id):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                order = await connection.fetchrow(orders_tbl.select().where(PammOrders.id == order_id))
                if order:
                    order = dict(order)
                    if order['order_type_id'] in (3, 4, ):
                        order['amount'] *= -1
                    investor = await connection.fetchrow(investors_tbl.select().where(and_(
                        PammInvestors.account_id == order['account_id'],
                        PammInvestors.user_id == order['user_id']
                    )))
                    if investor:
                        await connection.fetchrow(text(
                            f'update pamm_investors set last_amount = last_amount + {order["amount"]} '
                            f'where account_id = {order["account_id"]} and user_id = {order["user_id"]}'
                        ))
                    else:
                        timestamp = int(time())
                        await connection.fetchrow(investors_tbl.insert().values({
                            'account_id': order['account_id'],
                            'user_id': order['user_id'],
                            'start_amount': order['amount'],
                            'last_amount': order['amount'],
                            'created_at': timestamp,
                            'updated_at': timestamp,
                            'status_id': 1,
                            'last_percent': 0
                        }))

    async def watcher(self):
        await asyncio.sleep(5)
        while not self._stop:
            for k in list(self._tasks):
                if self._tasks[k]['jobs_counter'] < 1 or int(time()) - self._tasks[k]['timestamp'] >= 30:
                    task = self._tasks.pop(k)
                    self.add_job(1, k, task['task_type'])
            await asyncio.sleep(5)

    async def check_is_managed_in(self, data):
        if data['type'] == 'MANAGED_IN':
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    account_status_query = accounts_status_tbl.select().where(
                        PammAccountsStatus.account_id == data['account_id']
                    )
                    account_status = await connection.fetchrow(account_status_query)
                    if account_status['status_code_id'] == 1:
                        log.info({
                            'type': LogTypes.TYPE_EVENT,
                            'transaction': {'id': data['id']}
                        }, {'event_name': 'pamm.confirm_order.process', 'chain': f'wallet_{data["account_id"]}'})

    def decrease_job_counter(self, account_id, task_type):
        if account_id is not None and account_id in self._tasks.keys():
            if self._tasks[account_id]['task_type'] == task_type:
                self._tasks[account_id]['jobs_counter'] -= 1

    async def load_jobs(self):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                jobs = await connection.fetch(accounts_status_tbl.select().where(PammAccountsStatus.status_code_id != 4))
                for j in jobs:
                    if j['status_code_id'] == 1:
                        if j['start_at'] not in self._jobs['JOB_TYPE_START'].keys():
                            self._jobs['JOB_TYPE_START'][j['start_at']] = []
                        self._jobs['JOB_TYPE_START'][j['start_at']].append(j['account_id'])
                    if j['status_code_id'] == 2 or j['status_code_id'] == 3:
                        if j['stop_at'] not in self._jobs['JOB_TYPE_STOP'].keys():
                            self._jobs['JOB_TYPE_STOP'][j['stop_at']] = []
                        self._jobs['JOB_TYPE_STOP'][j['stop_at']].append(j['account_id'])

    def add_job(self, timestamp: int, account_id: int, job_type: str):
        if timestamp not in self._jobs[job_type].keys():
            self._jobs[job_type][timestamp] = []
        self._jobs[job_type][timestamp].append(account_id)

    def add_task(self, account_id, task_type, jobs_counter, timestamp):
        self._tasks[account_id] = {
            'task_type': task_type,
            'jobs_counter': jobs_counter,
            'timestamp': timestamp
        }

    def remove_job(self, account_id, timestamp, task_type):
        return self._jobs[task_type][timestamp].remove(account_id)

    async def checker(self):
        await asyncio.sleep(5)
        while not self._stop:
            try:
                timestamp = int(time())
                to_start = list(self._jobs['JOB_TYPE_START'].keys())
                to_stop = list(self._jobs['JOB_TYPE_STOP'].keys())
                to_early_stop = list(self._jobs['JOB_TYPE_EARLY_STOP'].keys())
                start_jobs = [x for x in to_start if x <= timestamp]
                stop_jobs = [x for x in to_stop if x <= timestamp]
                early_stop_jobs = [x for x in to_early_stop if x <= timestamp]
                for j in start_jobs:
                    account_ids = self._jobs['JOB_TYPE_START'].pop(j)
                    for account_id in account_ids:
                        self.loop.create_task(self.task_start(account_id))
                for j in stop_jobs:
                    account_ids = self._jobs['JOB_TYPE_STOP'].pop(j)
                    for account_id in account_ids:
                        self.loop.create_task(self.task_rollover(account_id))
                for j in early_stop_jobs:
                    account_ids = self._jobs['JOB_TYPE_EARLY_STOP'].pop(j)
                    for account_id in account_ids:
                        self.loop.create_task(self.task_rollover(account_id, True))
            except Exception as e:
                log.exception(e, exc_info=False)
            await asyncio.sleep(1)

    async def logging_account_info(self, account_id):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                timestamp = int(time())
                account = await connection.fetchrow(text(
                    f'select pa.currency, pa.id, pas.start_balance, pas.last_balance, pas.start_at, pas.stop_at '
                    f'from pamm_accounts as pa, pamm_accounts_status as pas '
                    f'where pa.id = pas.account_id and pa.id = {account_id}'
                ))
                if account is not None:
                    account = dict(account)
                    account['currency'] = dict(json.loads(account['currency']))
                    account['last_balance'] = itof(account['last_balance'], account['currency']['digits'])
                    account['rollover_at'] = timestamp

                    investors = await connection.fetch(select([
                        investors_tbl.c.user_id,
                        investors_tbl.c.account_id,
                        investors_tbl.c.last_amount,
                        investors_tbl.c.last_percent,
                        investors_tbl.c.created_at
                    ]).where(and_(
                        investors_tbl.c.account_id == account_id,
                        investors_tbl.c.status_id == 2
                    )))

                    for i in investors:
                        i = dict(i)
                        i['last_amount'] = itof(i['last_amount'], account['currency']['digits'])
                        i['currency'] = account['currency']['code']
                        i['last_percent'] = itof(i['last_percent'])
                        i['rollover_at'] = timestamp
                        log.info({
                            'type': LogTypes.TYPE_EVENT,
                            'investor': i
                        }, {'event_name': 'pamm.investor.info', 'chain': f'wallet_{account_id}'})
                    log.info({
                        'type': LogTypes.TYPE_EVENT,
                        'account': account
                    }, {'event_name': 'pamm.account.info', 'chain': f'wallet_{account_id}'})

    async def task_start(self, account_id: int) -> bool:
        log.info({
            'type': LogTypes.TYPE_EVENT,
            'account': {'id': account_id}
        }, {'event_name': 'pamm.account_start.processed', 'chain': f'wallet_{account_id}'})
        jobs_counter = 0
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                has_managed_in = False
                # First step: applying "MANAGED_IN" and "INVEST_IN" transactions
                in_transactions = await connection.fetch(orders_tbl.select().where(
                    and_(
                        PammOrders.account_id == account_id,
                        or_(PammOrders.order_status_id == 1, PammOrders.order_status_id == 3),
                        or_(PammOrders.order_type_id == 1, PammOrders.order_type_id == 2)
                    )
                ))
                for tr in in_transactions:
                    if tr['order_status_id'] == 1:
                        jobs_counter += 1
                        log.info({
                            'type': LogTypes.TYPE_EVENT,
                            'transaction': {'id': tr['id']}
                        }, {'event_name': 'pamm.confirm_order.process', 'chain': f'wallet_{account_id}'})
                    if tr['order_status_id'] == 3 and tr['order_type_id'] == 1:
                        has_managed_in = True
                timestamp = int(time())
                if jobs_counter:
                    self.add_task(account_id, self.JOB_TYPE_START, jobs_counter, timestamp)
                    # Exit if need to apply some transactions first
                    return False
                if not has_managed_in:
                    log.info({
                        'type': LogTypes.TYPE_EVENT,
                        'account': {'id': account_id, 'status': 'STATUS_REJECTED'},
                        'message': 'No transactions with type MANAGED_IN is applied.'
                    }, {'event_name': 'pamm.account_start.denied', 'chain': f'wallet_{account_id}'})
                    await connection.fetchrow(accounts_status_tbl.update().where(
                        PammAccountsStatus.account_id == account_id
                    ).values({'status_code_id': 5}))
                    # Exit if no MANAGED_IN transactions founded
                    return False
                # Second step: Creating an investors list
                balance = 0
                investors = await connection.fetch(investors_tbl.select().where(and_(
                    PammInvestors.account_id == account_id,
                    PammInvestors.status_id == 1
                )))
                investors_range = range(len(investors))
                for i in investors_range:
                    investors[i] = dict(investors[i])
                    investors[i]['start_amount'] = investors[i]['last_amount']
                    investors[i]['status_id'] = 2
                    investors[i]['updated_at'] = timestamp
                    balance += investors[i]['start_amount']
                for i in investors_range:
                    investors[i]['last_percent'] = iper(investors[i]['start_amount'], balance)
                    await connection.fetchrow(investors_tbl.update().values(investors[i]).where(and_(
                        PammInvestors.account_id == account_id,
                        PammInvestors.user_id == investors[i]['user_id']
                    )))
                # Third step: Changing account status to started
                await connection.fetchrow(accounts_status_tbl.update().where(
                    PammAccountsStatus.account_id == account_id
                ).values({
                    'status_code_id': 2,
                    'start_balance': balance,
                    'last_balance': balance
                }))
                log.info({
                    'type': LogTypes.TYPE_EVENT,
                    'account': {'id': account_id, 'status': 'STATUS_TRADING'}
                }, {'event_name': 'pamm.account_start.succeeded', 'chain': f'wallet_{account_id}'})
                await connection.fetchrow(accounts_tbl.update().where(
                    PammAccounts.id == account_id
                ).values({'activated_at': timestamp}))
        await self.logging_account_info(account_id)

    async def task_rollover(self, account_id: int, is_early: bool = False) -> bool:
        timestamp = int(time())
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                # First step: Checking if account is in STATUS_ROLLOVER
                account_status = dict(await connection.fetchrow(
                    text(f'select * from pamm_accounts_status where account_id = {account_id}')
                ))
                if account_status['status_code_id'] == 1:
                    return False
                if account_status['status_code_id'] == 2:
                    # Account is in STATUS_TRADING
                    if is_early:
                        self.remove_job(account_id, account_status['stop_at'], self.JOB_TYPE_STOP)
                        self.add_task(account_id, self.JOB_TYPE_EARLY_STOP, 1, timestamp)
                    else:
                        self.add_task(account_id, self.JOB_TYPE_STOP, 1, timestamp)
                    log.info({
                        'type': LogTypes.TYPE_EVENT,
                        'account': {'id': account_id, 'status': 'STATUS_ROLLOVER'}
                    }, {'event_name': 'pamm.account_rollover.processed', 'chain': f'wallet_{account_id}'})
                    # Exit because need to go STATUS_ROLLOVER
                    return False
                if account_status['status_code_id'] == 3:
                    # Account is in STATUS_ROLLOVER
                    log.info(f'Account {account_id} is in rollover')
                    account = await connection.fetchrow(text(
                        f'select pa.*, pas.start_balance, pas.last_balance, pas.start_at, pas.stop_at '
                        f'from pamm_accounts as pa, pamm_accounts_status as pas '
                        f'where pa.id = pas.account_id and pa.id = {account_id}'
                    ))
                    if account is not None:
                        account = dict(account)
                        account['currency'] = dict(json.loads(account['currency']))
                        account['params'] = dict(json.loads(account['params']))
                        investors = await connection.fetch(investors_tbl.select().where(and_(
                            PammInvestors.account_id == account_id,
                            or_(PammInvestors.status_id == 2, PammInvestors.status_id == 1)
                        )))
                        investors_range = range(len(investors))
                        for i in investors_range:
                            investors[i] = dict(investors[i])
                        balance = account['last_balance']
                        if account['start_balance'] < account['last_balance']:
                            # Profit
                            investors_profit = profit = account['last_balance'] - account['start_balance']
                            # calculating manager and investors share
                            manager_reward_percent = ftoi(float(account['params']['reward_percent']))
                            manager_index = amounts_sum = 0
                            for i in investors_range:
                                if investors[i]['user_id'] == account['user_id']:
                                    manager_index = i
                                    investors[i]['profit'] = ishare(profit, investors[i]['last_percent'])
                                    investors_profit -= investors[i]['profit']
                                    investors[i]['profit'] += ishare(investors_profit, manager_reward_percent)
                                else:
                                    investors[i]['profit'] = ishare(balance, investors[i]['last_percent'])
                                    investors[i]['profit'] -= investors[i]['last_amount']
                                    investors[i]['profit'] = ishare_c(investors[i]['profit'], manager_reward_percent)
                                investors[i]['last_amount'] += investors[i].pop('profit')
                                investors[i]['last_percent'] = iper(investors[i]['last_amount'], balance)
                                amounts_sum += investors[i]['last_amount']
                            if amounts_sum > balance:
                                investors[manager_index]['last_amount'] -= amounts_sum - balance
                            elif amounts_sum < balance:
                                investors[manager_index]['last_amount'] += balance - amounts_sum
                            # Saving investors and account data
                            for i in investors_range:
                                await connection.fetchrow(investors_tbl.update().where(and_(
                                    PammInvestors.account_id == account_id,
                                    PammInvestors.user_id == investors[i]['user_id']
                                )).values(investors[i]))
                            await connection.fetchrow(accounts_status_tbl.update().values({
                                'start_balance': account['last_balance'],
                                'last_balance': account['last_balance']
                            }).where(PammAccountsStatus.account_id == account_id))
                            account['start_balance'] = account['last_balance']
                            # End of Profit block
                        if account['start_balance'] > account['last_balance']:
                            # Loss
                            for i in investors_range:
                                investors[i]['last_amount'] = ishare(investors[i]['last_percent'], balance)
                                await connection.fetchrow(investors_tbl.update().where(and_(
                                    PammInvestors.account_id == account_id,
                                    PammInvestors.user_id == investors[i]['user_id']
                                )).values({'last_amount': investors[i]['last_amount']}))
                            await connection.fetchrow(accounts_status_tbl.update().values({
                                'start_balance': account['last_balance'],
                                'last_balance': account['last_balance']
                            }).where(PammAccountsStatus.account_id == account_id))
                            account['start_balance'] = account['last_balance']
                            # End of Loss block
                        if account['start_balance'] == account['last_balance']:
                            # Balance not changed
                            # Check deposit / withdraw requests
                            jobs_counter = 0
                            orders = await connection.fetch(orders_tbl.select().where(
                                and_(
                                    PammOrders.account_id == account_id,
                                    or_(PammOrders.order_status_id == 1, PammOrders.order_status_id == 2)
                                )
                            ))
                            for order in orders:
                                if order['order_type_id'] in (3, 4, ):
                                    for i in investors_range:
                                        if investors[i]['user_id'] == order['user_id']:
                                            if investors[i]['last_amount'] < order['amount']:
                                                investors[i]['last_amount'] = investors[i]['last_amount'] - order['amount']
                                                await connection.fetchrow(orders_tbl.update().where(
                                                    PammOrders.id == order['id']).values({'order_status_id': 4}))
                                                log.info({
                                                    'type': LogTypes.TYPE_EVENT,
                                                    'transaction': {'id': order['id']},
                                                    'message': 'PAMM_INVESTOR_INSUFFICIENT_FUNDS'
                                                }, {
                                                    'event_name': 'pamm.confirm_order.rejected',
                                                    'chain': f'wallet_{account_id}'
                                                })
                                            else:
                                                jobs_counter += 1
                                                log.info({
                                                    'type': LogTypes.TYPE_EVENT,
                                                    'transaction': {'id': order['id']}
                                                }, {'event_name': 'pamm.confirm_order.process',
                                                    'chain': f'wallet_{account_id}'})
                                else:
                                    jobs_counter += 1
                                    log.info({
                                        'type': LogTypes.TYPE_EVENT,
                                        'transaction': {'id': order['id']}
                                    }, {'event_name': 'pamm.confirm_order.process', 'chain': f'wallet_{account_id}'})
                            if jobs_counter:
                                self.add_task(account_id, self.JOB_TYPE_STOP, jobs_counter, timestamp)
                                # Exit if need to apply some transactions first
                                return False
                            new_balance = 0
                            for i in investors_range:
                                if investors[i]['status_id'] == 1:
                                    investors[i]['status_id'] = 2
                                    investors[i]['start_amount'] = investors[i]['last_amount']
                                investors[i]['updated_at'] = timestamp
                                new_balance += investors[i]['last_amount']

                            for i in investors_range:
                                investors[i]['last_percent'] = iper(investors[i]['last_amount'], new_balance)
                                await connection.fetchrow(investors_tbl.update().values(investors[i]).where(and_(
                                    PammInvestors.account_id == account_id,
                                    PammInvestors.user_id == investors[i]['user_id']
                                )))
                            # Changing account status to TRADING
                            new_stop_at = account['stop_at']
                            new_start_at = account['start_at']

                            if not is_early:
                                while new_stop_at <= timestamp:
                                    new_stop_at = new_stop_at + int(account['params']['rollover_period'])

                            await connection.fetchrow(accounts_status_tbl.update().values({
                                'start_at': new_start_at,
                                'stop_at': new_stop_at,
                                'status_code_id': 2,
                                'start_balance': new_balance,
                                'last_balance': new_balance
                            }).where(PammAccountsStatus.account_id == account_id))
                            log.info({
                                'type': LogTypes.TYPE_EVENT,
                                'account': {
                                    'id': account_id,
                                    'status': 'STATUS_TRADING',
                                    'start_at': new_start_at,
                                    'stop_at': new_stop_at
                                }
                            }, {'event_name': 'pamm.account_rollover.succeeded', 'chain': f'wallet_{account_id}'})
                            self.add_job(new_stop_at, account_id, self.JOB_TYPE_STOP)
        await self.logging_account_info(account_id)
