from telegram import Sticker


TANUKI_MONEY = Sticker(
    file_id='CAACAgIAAxkBAAIBgGQHzPD8WJ8b7CxziMESV-suUh2LAAJoAAPANk8TTP09o-fEaYcuBA',
    file_unique_id='AgADaAADwDZPEw', width=512, height=512, is_animated=True, is_video=False, type='regular'
)

ALL_COMMANDS_MESSAGE = (
    '<b>Добро пожаловать 👋!</b> \n\n'
    '/start - вход/регистрация/все команды'
    '/new_buy — добавить новую покупку\n'
    '/spent optional[<b>category</b>] optional[<b>период</b>] — сколько вы потратили\n'
    '/invite_new_member - добавить человека в семейный аккаунт'
    '/new_category - управлять категориями покупок\n'
    '/set_budget - управлять бюджетом WIP\n'
    # '/statistics - получить статистику по расходам WIP\n'
    '/clear_categories - очистить все категории и связанные с ними данные\n\n'
)

HELP_MESSAGE = (
    'Привет, <b>{user_name}</b>! Вот список доступных команд в нашем боте аналитики расходов:\n'
    '/start - начать использование бота\n'
    '/new_buy - добавить новую покупку\n'
    '/new_category - управлять категориями покупок\n'
    '/budget - управлять бюджетом WIP\n'
    '/statistics - получить статистику по расходам WIP\n'
    '/clear_categories - очистить все категории и связанные с ними данные\n\n'

    'Если не нашли ответ на свой вопрос жди /human чтобы задать свой вопрос'
)


# start - начать использование бота
# new_buy - добавить новую покупку
# new_category - управлять категориями покупок
# set_budget - управлять бюджетом WIP
# statistics - получить статистику по расходам WIP
# clear_categories - очистить все категории и связанные с ними данные