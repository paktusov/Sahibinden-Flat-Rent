# pylint: skip-file
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from config import postgres_config
from storage.models.postgres import DeclarativeBase
from storage.models.postgres.app import *  # noqa
from storage.models.postgres.bot import *  # noqa


config = context.config
section = config.config_ini_section

config.set_main_option("sqlalchemy.url", postgres_config.database_uri)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = DeclarativeBase.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = config.attributes.get("connection", None)
    if connectable is None:
        # only create Engine if we don't have a Connection
        # from the outside
        connectable = engine_from_config(
            config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool
        )

        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()
    else:
        context.configure(connection=connectable, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
