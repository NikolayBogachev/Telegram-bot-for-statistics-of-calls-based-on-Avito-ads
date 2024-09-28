from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает и возвращает постоянную клавиатуру с основными кнопками меню.
    """
    # Создаем кнопки
    kb = [
        [
            KeyboardButton(text="📊 Статистика")
        ],
        [
            KeyboardButton(text='ℹ️ Добавить токен')

        ]
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=False  # Не скрывать клавиатуру после нажатия
    )

    return keyboard