import logging
from datetime import datetime, timedelta
from typing import Callable, Optional
from uuid import uuid4

import new_buy
from decorators import tg_handler
from my_stickers import TANUKI_MONEY
from sqlalchemy import func
from sqlalchemy.orm import Session
from steps import NewBuyStep
from telegram import (CallbackQuery, Chat, ReplyKeyboardRemove, Sticker,
                      Update, constants)
from telegram.ext import (ApplicationBuilder, CallbackContext,
                          CallbackQueryHandler, CommandHandler, Defaults,
                          MessageHandler, filters)

import config
from models import Category, InviteToken, Purchase, Team, User

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


@tg_handler()
async def start(
    db: Session, user: Optional[User], chat: Chat,
    update: Update, context: CallbackContext
) -> None:
    if user:
        await context.bot.send_message(
            chat_id=chat.id, text=(
                '<b>Привет👋!</b> \n\n'
                '/new_buy — ввести новую покупку\n'
                '/spent — ввести новую покупку'
                '/start - регистрация/все команды'

            )
        )
    else:
        new_team = Team(team_name='my_family')
        db.add(new_team)
        db.commit()
        user = User.from_tg_chat(chat.username, chat.first_name, chat.id, new_team.id)
        db.add(user)
        db.commit()
        if context.args:
            sign_in_up(db, chat, update, context, user)
        await context.bot.send_message(
            chat_id=chat.id, text=(
                '<b>Регистрация прошла успешно</b>'
            )
        )
        await context.bot.send_sticker(
            chat_id=chat.id, sticker=TANUKI_MONEY
        )



@tg_handler()
async def invite_new_member(db: Session, user: User, chat: Chat, update: Update, context: CallbackContext) -> None:
    rand_token = str(uuid4())
    text = (
        f'Отправьте [эту ссылку](https://t.me/AnaliticShoppingListBot?start={rand_token}) '
        'тому кого хотите пригласить в ваше пространство человеку🤝,'
        'с которым хотите разделить бота'
    )
    invite_token = InviteToken(token=rand_token, team_id=user.team_id)
    db.add(invite_token)
    db.commit()
    await context.bot.send_message(
        chat_id=chat.id, text=text, parse_mode=constants.ParseMode.MARKDOWN_V2)


@tg_handler()
async def connect_to_family_account(db: Session, user: User, chat: Chat, update: Update, context: CallbackContext) -> None:
    return


def sign_in_up(db: Session, chat: Chat, update: Update, context: CallbackContext, user: User) -> bool:
    if context.args:
        args_splitted = context.args[0].split('__')
    if len(args_splitted) != 1:
        return False
    token = args_splitted[0]
    invite_token = db.query(
        InviteToken
     ).filter(
        InviteToken.token == token,
        InviteToken.created_at >= datetime.utcnow() - timedelta(days=1)
    ).first()
    if invite_token:
        user.team_id = invite_token.team_id

        db.commit()
        return True
    return False


@tg_handler()
async def logout(db: Session, user: User, chat: Chat, update: Update, context: CallbackContext) -> None:
    user.telegram_chat_id = None
    user.telegram = None
    db.commit()

    await context.bot.send_message(chat_id=chat.id, reply_markup=ReplyKeyboardRemove(), text='Logout. /start')


@tg_handler()
async def text(db: Session, user: Optional[User], chat: Chat, update: Update, context: CallbackContext) -> None:
    if not user:
        start(update, context)
        return
    if not (message := update.effective_message) or not (text := message.text):
        # test incoming stickers here
        # await context.bot.send_sticker(chat_id=chat.id, sticker=update.effective_message.sticker)
        # await context.bot.send_sticker(chat_id=chat.id, sticker=s)
        return

    text_processor_function = None

    if user.telegram_step:
        step, *step_parameters = user.telegram_step.split('__')

        text_processor_function = TEXT_PROCESSOR_BY_CANDIDATE_STEP.get(step)

    if text_processor_function:
        # ! TODO: make unified call
        if step_parameters:
            await text_processor_function(   # type: ignore
                db, user, chat, text, update,
                context, step_parameters=step_parameters
            )
        else:
            await text_processor_function(db, user, chat, text, update, context)
    else:
        help_text = 'WTF?'
        await context.bot.send_message(chat_id=chat.id, text=help_text)


@tg_handler()
async def command_new_buy(db: Session, user: User, chat: Chat, update: Update, context: CallbackContext) -> None:
    user.telegram_step = NewBuyStep.amount_payment.value

    db.commit()
    await context.bot.send_message(
        chat_id=chat.id, text=(
            'Введите пожалуйста название_покупки сумма:'
        )
    )


@tg_handler()
async def add_new_category(db: Session, user: User, chat: Chat, update: Update, context: CallbackContext) -> None:
    if not context.args or len(context.args) != 1:
        await context.bot.send_message(
            chat_id=chat.id, text=(
                'Введите пожалуйста /new_category название категории'
            )
        )
        return

    db.add(
        Category(
            category_name=context.args[0],
            user_id=user.id
        )
    )

    db.commit()
    await context.bot.send_message(
        chat_id=chat.id, text=(
            f'вы добавили категорию {context.args[0]}'
        )
    )


@tg_handler()
async def command_spent(db: Session, user: User, chat: Chat, update: Update, context: CallbackContext) -> None:
    amount_money = db.query(  # type: ignore
        func.sum(Purchase.price)
    ).filter(
        Purchase.created_at >= datetime.utcnow().replace(day=1)
    ).first()[0] or 0
    await context.bot.send_message(
        chat_id=chat.id, text=(f'В этом месяце вы потратили {amount_money}')
    )


@tg_handler()
async def callback(db: Session, user: User, chat: Chat, update: Update, context: CallbackContext) -> None:
    if not (callback_query := update.callback_query):
        raise ValueError('Not a callback query')
    do_clear_markup = True

    if callback_query.data and callback_query.data.endswith('_nocm'):
        do_clear_markup = False

    path = (callback_query.data or '').split('__')
    route = path[0]

    callback_process_function = CALLBACK_PROCESSOR_BY_ROUTE.get(route)

    if callback_process_function:
        callback_process_function(
            db, user, chat, callback_query, path[1:], update, context)

    if do_clear_markup:
        await clear_markup(callback_query)


async def clear_markup(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.edit_message_reply_markup(reply_markup=None)


@tg_handler()
async def unknown(chat: Chat, update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(chat_id=chat.id, text="Sorry, I didn't understand that command.")


CallbackProcessor = Callable[[Session, User, Chat,
                              CallbackQuery, list[str], Update, CallbackContext], None]

CALLBACK_PROCESSOR_BY_ROUTE: dict[str, CallbackProcessor] = {
    'new_buy': new_buy.callbacks.process_new_buy_callback,
}

TextProcessor = Callable[[Session, User, Chat, str, Update, CallbackContext], None]

TEXT_PROCESSOR_BY_CANDIDATE_STEP: dict[str, TextProcessor] = {
    NewBuyStep.amount_payment.value: new_buy.replies.process_amount_payment,
}

if __name__ == '__main__':
    application = ApplicationBuilder().token(
        config.TOKEN).defaults(Defaults(parse_mode=constants.ParseMode.HTML)).build()
    start_handler = CommandHandler('start', start)
    new_buy_handler = CommandHandler('new_buy', command_new_buy)
    spent_handler = CommandHandler('spent', command_spent)
    callback_handler = CallbackQueryHandler(callback)
    new_category_handler = CommandHandler('new_category', add_new_category)
    add_new_member_handler = CommandHandler('invite_new_member', invite_new_member)
    connect_to_family_account = CommandHandler('authorize', connect_to_family_account)
    logout_handler = CommandHandler('logout', logout)

    application.add_handler(new_buy_handler)
    application.add_handler(start_handler)
    application.add_handler(spent_handler)
    application.add_handler(new_category_handler)
    application.add_handler(callback_handler)
    application.add_handler(connect_to_family_account)
    application.add_handler(add_new_member_handler)
    application.add_handler(logout_handler)
    text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND) | filters.Sticker.ALL, text)
    application.add_handler(text_handler)
    application.run_polling()
