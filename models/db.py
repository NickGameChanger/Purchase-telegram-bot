from contextlib import contextmanager
from typing import Iterator

import config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

database_dsn = (
    # f"postgresql+psycopg2://{config.DB['USER']}:{config.DB['PASSWORD']}"
    # f"@{config.DB['HOST']}:{config.DB['PORT']}/{config.DB['DATABASE']}"
    "postgresql://usr:pwd@db:5432/todos"
)

engine = create_engine(
    database_dsn, pool_size=25, max_overflow=0,
    connect_args={
        'options': '-c statement_timeout=90000'
    }
)
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def create_session() -> Iterator[Session]:
    session = None
    try:
        session = SessionLocal()
        yield session
    finally:
        if session:
            session.close()