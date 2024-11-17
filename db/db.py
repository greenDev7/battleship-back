from sqlalchemy import create_engine, Engine

from db.model import Base

pg_url = 'postgresql://{user}:{password}@{host}:{port}/{db_name}'.format(
    user='postgres',
    password='12345',
    host='postgres-dbms',
    port='5432',
    db_name='postgres',
)


def initialize_engine() -> Engine:
    return create_engine(pg_url, echo=True)


def create_tables(engine: Engine):
    Base.metadata.create_all(bind=engine)
