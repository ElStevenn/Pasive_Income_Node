from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# Adjust import based in my project through sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from services.database.models import Base

# Set path of .env 
dotenv_path = os.path.join(os.path.dirname(__file__), '../../../app/.env')
load_dotenv(dotenv_path)

# Environment variables
DB_NAME="main_db"
DB_USER="postgres"
DB_PASS="mierda69"
DB_HOST="18.116.69.127"

# Alembic Config object
config = context.config

# Use synchronous driver for Alembic migrations
database_url_sync = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}'
config.set_main_option('sqlalchemy.url', database_url_sync)

# Interpret the config file for Python logging
fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
