import functools
from typing import Callable

from telegram.ext import CallbackContext
from telegram import Update

from models.db import create_session
from models import User
# context manager


def tg_handler() -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper_func(
            update: Update, context: CallbackContext
        ) -> None:
            chat = update.effective_chat
            print('chat is gotten')
            if not chat:
                raise ValueError('No chat in update')
            with create_session() as db:
                user = User.by_chat_id(db, chat.id)
                return await func(db, user, chat, update, context)

        return wrapper_func

    return decorator
