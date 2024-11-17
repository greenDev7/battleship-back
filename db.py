from contextlib import contextmanager

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker

from entities.model import Base

pg_url = 'postgresql://{user}:{password}@{host}:{port}/{db_name}'.format(
    user='postgres',
    password='12345',
    host='postgres-dbms',
    port='5432',
    db_name='postgres',
)

engine = create_engine(pg_url, echo=True)

OurSession = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope():
    session = OurSession()

    try:
        yield session

        print('1111')
        session.commit()
    except Exception as ex:
        print('2222 ex')
        session.rollback()

        raise ex
    finally:
        print('3333 session.close')
        session.close()


def get_engine() -> Engine:
    return engine


def create_tables(eng: Engine):
    Base.metadata.create_all(eng)
