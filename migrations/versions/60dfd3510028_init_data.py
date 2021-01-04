"""init_data

Revision ID: 60dfd3510028
Revises: 63a5296ee01e
Create Date: 2019-09-26 15:39:38.366784

"""
from alembic import op
from pamm.dataproviders.postgresql.models import *

# revision identifiers, used by Alembic.
revision = '60dfd3510028'
down_revision = '63a5296ee01e'
branch_labels = None
depends_on = None


def upgrade():
    op.bulk_insert(
        PammAccountsStatusCode.__table__,
        [
            {'code': 'NEW'},
            {'code': 'TRADING'},
            {'code': 'ROLLOVER'},
            {'code': 'CLOSED'},
            {'code': 'DENIED'},
        ]
    )

    op.bulk_insert(
        PammInvestorStatus.__table__,
        [
            {'code': 'NEW'},
            {'code': 'INVESTOR'},
        ]
    )

    op.bulk_insert(
        PammOrdersStatus.__table__,
        [
            {'code': 'NEW'},
            {'code': 'PROCESS'},
            {'code': 'DONE'},
            {'code': 'DECLINE'},
            {'code': 'FAIL'},
        ]
    )

    op.bulk_insert(
        PammOrdersType.__table__,
        [
            {'code': 'MANAGED_IN'},
            {'code': 'INVEST_IN'},
            {'code': 'MANAGED_OUT'},
            {'code': 'INVEST_OUT'},
        ]
    )

    op.bulk_insert(
        PammTicketsStatus.__table__,
        [
            {'code': 'NEW'},
            {'code': 'PROCESS'},
            {'code': 'DONE'},
            {'code': 'DECLINE'},
            {'code': 'FAIL'},
        ]
    )

    op.bulk_insert(
        PammTicketsType.__table__,
        [
            {'code': 'PAMM_CLOSE'},
        ]
    )


def downgrade():
    pass
