
from sqlalchemy.orm import Session
from models import User

from telegram import Chat, CallbackQuery, Update
from telegram.ext import CallbackContext
from .markups import get_clear_categories_markup

from models import Category


async def process_clear_markup_callback(
    db: Session, user: User, chat: Chat, callback: CallbackQuery,
    path: list[str], update: Update, context: CallbackContext
) -> None:
    if not path or not path[0]:
        return
    try:
        category_id = int(path[0])
    except ValueError:
        return

    category = db.query(Category).filter(Category.id == category_id).first()
    db.delete(category)
    db.commit()
    if not category:
        raise ValueError('trying to delete deleted category')

    await callback.answer()
    await callback.edit_message_reply_markup(reply_markup=get_clear_categories_markup(user, db))
