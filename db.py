from contextlib import contextmanager

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker

from config.config import app_config
from entities.model import Base


pg_url = 'postgresql://{user}:{password}@{host}:{port}/{db_name}'.format(
    user=app_config['PG_USERNAME'],
    password=app_config['PG_PASSWORD'],
    host=app_config['PG_HOST'],
    port=app_config['PG_PORT'],
    db_name=app_config['PG_DB_NAME'],
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


async def create_tables(eng: Engine):
    Base.metadata.create_all(eng)
