import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool
from alembic import context
from pamm.config import Config
from pamm.dataproviders.postgresql.models import *

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
alembic_config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(alembic_config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = [PammAccounts.metadata]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_postgresql_url():
    try:
        app_conf = Config()
        repository_type = app_conf.repo.type
        repository_options = app_conf.repo.options
        if repository_type == 'postgresql':
            return repository_options.get('dsn', None)
        return None
    except Exception as e:
        print(e)


def run_migrations_offline(url=None):
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    if url is None:
        url = alembic_config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online(url=None):
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    if url is None:
        connectable = engine_from_config(
            alembic_config.get_section(alembic_config.config_ini_section),
            poolclass=pool.NullPool,
        )
    else:
        connectable = create_engine(url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


postgresql_url = get_postgresql_url()

if context.is_offline_mode():
    run_migrations_offline(url=postgresql_url)
else:
    run_migrations_online(url=postgresql_url)
