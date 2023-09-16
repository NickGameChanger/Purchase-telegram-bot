from decorators import tg_handler
from sqlalchemy.orm import Session
from steps import NewBuyStep
from telegram import Chat, Update
from telegram.ext import CallbackContext
from .markups import get_clear_categories_markup
from models import User


@tg_handler()
async def clear_categories(db: Session, user: User, chat: Chat, update: Update, context: CallbackContext) -> None:
    # categories: Optional[list[Category]] = db.query(Category).filter(Category.user_id == user.id).all()
    categories_markup = get_clear_categories_markup(user, db)
    await context.bot.send_message(chat_id=chat.id, reply_markup=categories_markup, text='нажмите, чтобы удалить ненужную категорию')
