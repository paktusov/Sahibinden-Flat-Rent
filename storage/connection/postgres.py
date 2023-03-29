from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import postgres_config


class SessionManager:
    def __init__(self) -> None:
        self.engine = create_engine(postgres_config.database_uri, pool_pre_ping=True)
        self.session_local = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SessionManager, cls).__new__(cls)
        return cls.instance

    def get_session(self) -> Session:
        return self.session_local()

    def refresh(self) -> None:
        self.engine = create_engine(postgres_config.database_uri, pool_pre_ping=True)
        self.session_local = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)


def get_db() -> Session:
    database = SessionManager().get_session()
    return database


postgres_db = get_db()
