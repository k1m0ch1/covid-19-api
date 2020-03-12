from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

import os
import sys

if 'SYS_PATH' in os.environ:
    sys.path.insert(0, os.environ['SYS_PATH'])
else:
    sys.path.insert(
        0,
        os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

import models # noqa

config = context.config

fileConfig(config.config_file_name)

"""
Load models metadata. We should define schema in this class firstly,
or set schema implicit with
`__table_args__ = {'schema' : 'test'}` in model class
"""
target_metadata = models.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    if type_ == 'table' and object.schema != target_metadata.schema:
        return False

    return True


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=target_metadata.schema,
            include_schemas=True,
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
