import os
from databases import Database
from sqlalchemy import create_engine, MetaData


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise EnvironmentError("DATABASE_URL environment variable not set")

database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)  # sync engine (for DDL like create_all)
metadata = MetaData()
