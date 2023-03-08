from typing import Any

from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import Bundle


@as_declarative()
class Base:
    id: Any
