from sqlalchemy.orm import Session
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from models import Category, User


def get_categories_markup(
    user: User, db: Session, purchase_id: int
) -> InlineKeyboardMarkup:
    categories = db.query(
        Category.category_name,
        Category.id
    ).filter(
        Category.user_id == user.id
    ).all()
    markup_items = []
    button_line = []
    for i, (name, category_id) in enumerate(categories):
        button_line.append(
            InlineKeyboardButton(name, callback_data=f'new_buy__{category_id}__{purchase_id}'))
        if i % 2 == 1 and button_line:
            markup_items.append(button_line.copy())
            button_line = []
    if button_line:
        markup_items.append(button_line.copy())

    return InlineKeyboardMarkup(markup_items)
