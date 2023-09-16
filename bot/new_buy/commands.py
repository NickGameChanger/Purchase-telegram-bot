from decorators import tg_handler
from sqlalchemy.orm import Session
from steps import NewBuyStep
from telegram import Chat, Update
from telegram.ext import CallbackContext

from models import User


@tg_handler()
async def command_new_buy(db: Session, user: User, chat: Chat, update: Update, context: CallbackContext) -> None:
    user.telegram_step = NewBuyStep.amount_payment.value

    db.commit()
    await context.bot.send_message(
        chat_id=chat.id, text=(
            'Введите пожалуйста <b>название покупки</b> <i>сумма</i>:'
        )
    )
