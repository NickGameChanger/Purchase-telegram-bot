
from sqlalchemy.orm import Session
from models import User, Purchase

from telegram import Chat, CallbackQuery, Update
from telegram.ext import CallbackContext


# TODO need to transfer it to the celery
def process_new_buy_callback(
    db: Session, user: User, chat: Chat, callback: CallbackQuery,
    path: list[str], update: Update, context: CallbackContext
) -> None:
    if not path or not path[0] or not path[1]:
        return
    try:
        category_id = int(path[0])
        purchase_id = int(path[1])
    except ValueError:
        return

    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise ValueError('purchase was deleted')
    purchase.category_id = category_id
    db.commit()
