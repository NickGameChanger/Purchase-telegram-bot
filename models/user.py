from __future__ import annotations

from typing import Optional

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlalchemy.orm import Session, relationship

from .base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer(), primary_key=True)

    source = Column(String(50), nullable=True)  # TODO migration

    email = Column(String, nullable=True)
    first_name = Column(TEXT, nullable=True)
    last_name = Column(TEXT, nullable=True)

    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    team = relationship('Team', primaryjoin='User.team_id == Team.id')

    telegram = Column(String(255), nullable=True)
    telegram_chat_id = Column(Integer, nullable=True)
    telegram_bot_stopped_at = Column(DateTime, nullable=True)
    registration_completed_at = Column(Date, nullable=True)
    telegram_step = Column(TEXT, nullable=True)

    @classmethod
    def by_chat_id(clt, db: Session, chat_id: int) -> Optional[User]:
        return db.query(User).filter(User.telegram_chat_id == chat_id).first()

    @classmethod
    def from_tg_chat(cls, username: Optional[str], first_name: Optional[str], chat_id: int, team_id: int) -> User:
        return cls(
            telegram=username,
            telegram_chat_id=chat_id,
            first_name=first_name,
            team_id=team_id
        )


class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer(), primary_key=True)
    team_name = Column(String(100), nullable=True)
    google_sheet_url = Column(TEXT, nullable=True)
