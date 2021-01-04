import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class PammAccounts(Base):
    __tablename__ = 'pamm_accounts'

    id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    user_id = sa.Column(sa.Integer, nullable=False)
    currency = sa.Column(sa.JSON, nullable=False)
    params = sa.Column(sa.JSON, nullable=True)
    activated_at = sa.Column(sa.Integer, nullable=True)
    created_at = sa.Column(sa.Integer, nullable=False)

    pamm_accounts_status = relationship('PammAccountsStatus', uselist=False, back_populates='pamm_accounts')
    pamm_investors = relationship('PammInvestors', uselist=False, back_populates='pamm_accounts')


class PammAccountsStatusCode(Base):
    __tablename__ = 'pamm_accounts_status_code'

    id = sa.Column(sa.Integer, primary_key=True)
    code = sa.Column(sa.String(length=32), nullable=False)

    pamm_investors = relationship('PammAccountsStatus', uselist=False, back_populates='pamm_accounts_status_code')


class PammAccountsStatus(Base):
    __tablename__ = 'pamm_accounts_status'

    id = sa.Column(sa.Integer, primary_key=True)
    account_id = sa.Column(sa.Integer, sa.ForeignKey('pamm_accounts.id'))
    start_balance = sa.Column(sa.BigInteger, nullable=True)
    last_balance = sa.Column(sa.BigInteger, nullable=True)
    start_at = sa.Column(sa.Integer, nullable=False)
    stop_at = sa.Column(sa.Integer, nullable=False)
    status_code_id = sa.Column(sa.Integer, sa.ForeignKey('pamm_accounts_status_code.id'))

    pamm_accounts = relationship('PammAccounts', back_populates='pamm_accounts_status')
    pamm_accounts_status_code = relationship('PammAccountsStatusCode', back_populates='pamm_accounts_status')


class PammInvestorStatus(Base):
    __tablename__ = 'pamm_investors_status'

    id = sa.Column(sa.Integer, primary_key=True)
    code = sa.Column(sa.String(length=32), nullable=False)

    pamm_investors = relationship('PammInvestors', uselist=False, back_populates='pamm_investors_status')


class PammInvestors(Base):
    __tablename__ = 'pamm_investors'

    id = sa.Column(sa.Integer, primary_key=True)
    account_id = sa.Column(sa.Integer, sa.ForeignKey('pamm_accounts.id'))
    user_id = sa.Column(sa.Integer, nullable=False)
    start_amount = sa.Column(sa.BigInteger, nullable=False)
    last_amount = sa.Column(sa.BigInteger, nullable=False)
    last_percent = sa.Column(sa.Integer, nullable=False)
    status_id = sa.Column(sa.Integer, sa.ForeignKey('pamm_investors_status.id'))
    updated_at = sa.Column(sa.Integer, nullable=False)
    created_at = sa.Column(sa.Integer, nullable=False)

    pamm_accounts = relationship('PammAccounts', back_populates='pamm_investors')
    pamm_investors_status = relationship('PammInvestorStatus', back_populates='pamm_investors')


class PammOrdersStatus(Base):
    __tablename__ = 'pamm_orders_status'

    id = sa.Column(sa.Integer, primary_key=True)
    code = sa.Column(sa.String(length=32), nullable=False)

    pamm_investors = relationship('PammOrders', uselist=False, back_populates='pamm_orders_status')


class PammOrdersType(Base):
    __tablename__ = 'pamm_orders_type'

    id = sa.Column(sa.Integer, primary_key=True)
    code = sa.Column(sa.String(length=32), nullable=False)

    pamm_investors = relationship('PammOrders', uselist=False, back_populates='pamm_orders_type')


class PammOrders(Base):
    __tablename__ = 'pamm_orders'

    id = sa.Column(sa.Integer, primary_key=True)
    account_id = sa.Column(sa.Integer, sa.ForeignKey('pamm_accounts.id'))
    user_id = sa.Column(sa.Integer, nullable=False)
    amount = sa.Column(sa.BigInteger, nullable=False)
    currency_id = sa.Column(sa.Integer, nullable=False)
    order_type_id = sa.Column(sa.Integer, sa.ForeignKey('pamm_orders_type.id'))
    order_status_id = sa.Column(sa.Integer, sa.ForeignKey('pamm_orders_status.id'))
    updated_at = sa.Column(sa.Integer, nullable=False)
    created_at = sa.Column(sa.Integer, nullable=False)

    pamm_orders_type = relationship('PammOrdersType', back_populates='pamm_orders')
    pamm_orders_status = relationship('PammOrdersStatus', back_populates='pamm_orders')


class PammTicketsStatus(Base):
    __tablename__ = 'pamm_tickets_status'

    id = sa.Column(sa.Integer, primary_key=True)
    code = sa.Column(sa.String(length=32), nullable=False)

    pamm_investors = relationship('PammTickets', uselist=False, back_populates='pamm_tickets_status')


class PammTicketsType(Base):
    __tablename__ = 'pamm_tickets_type'

    id = sa.Column(sa.Integer, primary_key=True)
    code = sa.Column(sa.String(length=64), nullable=False)

    pamm_investors = relationship('PammTickets', uselist=False, back_populates='pamm_tickets_type')


class PammTickets(Base):
    __tablename__ = 'pamm_tickets'

    id = sa.Column(sa.Integer, primary_key=True)
    account_id = sa.Column(sa.Integer, sa.ForeignKey('pamm_accounts.id'))
    user_id = sa.Column(sa.Integer, nullable=False)
    ticket_type_id = sa.Column(sa.Integer, sa.ForeignKey('pamm_tickets_type.id'))
    ticket_status_id = sa.Column(sa.Integer, sa.ForeignKey('pamm_tickets_status.id'))
    params = sa.Column(sa.JSON, nullable=True)
    updated_at = sa.Column(sa.Integer, nullable=False)
    created_at = sa.Column(sa.Integer, nullable=False)

    pamm_tickets_type = relationship('PammTicketsType', back_populates='pamm_tickets')
    pamm_tickets_status = relationship('PammTicketsStatus', back_populates='pamm_tickets')


accounts_tbl = PammAccounts.__table__  # type: Table
accounts_status_tbl = PammAccountsStatus.__table__  # type: Table
orders_tbl = PammOrders.__table__  # type: Table
investors_tbl = PammInvestors.__table__  # type: Table
tickets_tbl = PammTickets.__table__  # type: Table
