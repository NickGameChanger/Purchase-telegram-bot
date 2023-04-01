
from bot.new_buy.markups import get_categories_markup
from bot.new_buy.messages import WRONG_NEW_BUY_MESSAGE
from bot.steps import NewBuyStep

from sqlalchemy.orm import Session
from telegram import Chat, Update
from telegram.ext import CallbackContext
from models import User, Purchase


async def process_amount_payment(
    db: Session, user: User, chat: Chat, text: str,
    update: Update, context: CallbackContext
) -> None:
    if not text or not text.split() or len(text.split()) != 2:
        await context.bot.send_message(
            chat_id=chat.id, text=WRONG_NEW_BUY_MESSAGE)
        return
    try:
        purchase_name, amount = text.split()
        amount = int(amount)  # type: ignore
    except ValueError:
        await context.bot.send_message(
            chat_id=chat.id, text=(WRONG_NEW_BUY_MESSAGE))
        return
    new_purchase = Purchase(
        purchase_name=purchase_name,
        price=amount, user_id=user.id)  # type: ignore
    db.add(new_purchase)
    user.telegram_step = NewBuyStep.category.value

    db.commit()
    await context.bot.send_message(
        chat_id=chat.id, text='Выберите категорию',
        reply_markup=get_categories_markup(user, db, new_purchase.id)
    )


async def process_category_payment(
    db: Session, user: User, chat: Chat, text: str,
    update: Update, context: CallbackContext
) -> None:

    return
