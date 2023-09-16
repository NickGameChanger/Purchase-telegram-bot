import logging
from datetime import datetime, timedelta
from typing import Callable, Optional
from uuid import uuid4
from bot.messages import HELP_MESSAGE
import new_buy, categories

from decorators import tg_handler
from messages import TANUKI_MONEY, ALL_COMMANDS_MESSAGE
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
        await context.bot.send_message(chat_id=chat.id, text=ALL_COMMANDS_MESSAGE)
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
                'Приветствую, <b>{user_name}</b>! Вы успешно зарегистрировались в нашем боте аналитики расходов. '
                'Теперь вы можете отслеживать свои расходы, управлять своим бюджетом и получать полезную статистику. '
                'Если у вас есть вопросы или нужна помощь, пожалуйста, обратитесь к команде /help. Спасибо, что выбрали наш бот!'
            )
        )
        await context.bot.send_sticker(
            chat_id=chat.id, sticker=TANUKI_MONEY
        )


@tg_handler()
async def invite_new_member(db: Session, user: User, chat: Chat, update: Update, context: CallbackContext) -> None:
    rand_token = str(uuid4())
    text = (
        'Привет! Вы уже пользуетесь нашим ботом аналитики расходов и хотели бы поделиться им с семьей?'
        'Это легко - отправьте им эту [реферальную ссылку](https://t.me/AnaliticShoppingListBot?start={rand_token}), '
        'и пусть они авторизуются в боте. Если ваш друг уже использует бот, ему нужно сначала выйти из аккаунта,'
        'нажав /logout, а затем перейти по [ссылке](https://t.me/AnaliticShoppingListBot?start={rand_token}). '
        'После авторизации в боте они смогут использовать все его функции и'
        'получать аналитику, как и вы!'
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
        # ! TODO: make unified call ?WTF?
        if step_parameters:
            await text_processor_function(   # type: ignore
                db, user, chat, text, update,
                context, step_parameters=step_parameters
            )
        else:
            await text_processor_function(db, user, chat, text, update, context)
    else:
        help_text = HELP_MESSAGE.format(user_name=user.first_name or user.telegram)
        await context.bot.send_message(chat_id=chat.id, text=help_text)


@tg_handler()
async def add_new_category(db: Session, user: User, chat: Chat, update: Update, context: CallbackContext) -> None:
    if not context.args or len(context.args) != 1:
        await context.bot.send_message(
            chat_id=chat.id, text=(
                'Введите пожалуйста /new_category <b>название категории</b>'
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

    path = (callback_query.data or '').split('__')
    route = path[0]
    if callback_query.data and callback_query.data.endswith('__nocm'):
        do_clear_markup = False

    callback_process_function = CALLBACK_PROCESSOR_BY_ROUTE.get(route)

    if callback_process_function:
        await callback_process_function(
            db, user, chat, callback_query, path[1:-1], update, context)

    if do_clear_markup:
        await clear_markup(callback_query)


async def clear_markup(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.edit_message_reply_markup(reply_markup=None)


@tg_handler()
async def set_budget(db: Session, user: User, chat: Chat, update: Update, context: CallbackContext) -> None:
    return

@tg_handler()
async def unknown(chat: Chat, update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(chat_id=chat.id, text="Sorry, I didn't understand that command.")


CallbackProcessor = Callable[[Session, User, Chat,
                              CallbackQuery, list[str], Update, CallbackContext], None]

CALLBACK_PROCESSOR_BY_ROUTE: dict[str, CallbackProcessor] = {
    'new_buy': new_buy.callbacks.process_new_buy_callback,
    'clear_category': categories.callbacks.process_clear_markup_callback,
}

TextProcessor = Callable[[Session, User, Chat, str, Update, CallbackContext], None]

TEXT_PROCESSOR_BY_CANDIDATE_STEP: dict[str, TextProcessor] = {
    NewBuyStep.amount_payment.value: new_buy.replies.process_amount_payment,
}

if __name__ == '__main__':
    application = ApplicationBuilder().token(
        config.TOKEN).defaults(Defaults(parse_mode=constants.ParseMode.HTML)).build()
    start_handler = CommandHandler('start', start)
    new_buy_handler = CommandHandler('new_buy', new_buy.commands.command_new_buy)
    spent_handler = CommandHandler('spent', command_spent)
    callback_handler = CallbackQueryHandler(callback)
    new_category_handler = CommandHandler('new_category', add_new_category)
    add_new_member_handler = CommandHandler('invite_new_member', invite_new_member)
    connect_to_family_account = CommandHandler('authorize', connect_to_family_account)
    clear_categories_handler = CommandHandler('clear_categories', categories.commands.clear_categories)
    logout_handler = CommandHandler('logout', logout)

    application.add_handler(new_buy_handler)
    application.add_handler(start_handler)
    application.add_handler(spent_handler)
    application.add_handler(new_category_handler)
    application.add_handler(callback_handler)
    application.add_handler(connect_to_family_account)
    application.add_handler(add_new_member_handler)
    application.add_handler(logout_handler)
    application.add_handler(clear_categories_handler)
    text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND) | filters.Sticker.ALL, text)
    application.add_handler(text_handler)
    application.run_polling()
