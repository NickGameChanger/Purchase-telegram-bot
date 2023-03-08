from sqlalchemy import (Column, DateTime, ForeignKey,
                        Integer)
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import relationship

from datetime import datetime
from .base import Base


class InviteToken(Base):
    __tablename__ = 'invite_tokens'
    id = Column(Integer, primary_key=True)
    token = Column(TEXT, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow())
    team = relationship('Team', primaryjoin='Team.id == InviteToken.team_id')
