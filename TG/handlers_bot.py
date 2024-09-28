import asyncio

from aiogram import F, Router
from aiogram.client.session import aiohttp

from aiogram.filters import CommandStart, StateFilter

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ForceReply, InputFile, FSInputFile
from loguru import logger
from openpyxl.workbook import Workbook

from TG.StatesGroup import AddTokenState
from TG.auth import generate_key, encrypt_token, decrypt_token
from TG.bot import bot
from TG.funcs_tg import parse_statistics, create_xlsx_report, get_user_id
from TG.keyboards.ReplyKeyboard import get_main_menu_keyboard
from database.db import get_db, async_session
from database.func_db import UserCRUD
from database.models import Token

router = Router()

user_messages = {}
"""
Блок основного меню.
"""


async def fetch_user_tokens(user_id):
    async with async_session() as session:
        user_crud = UserCRUD(session)
        tokens = await user_crud.get_user_tokens(user_id)
    return tokens


async def delete_user_messages(user_id: int):
    """
    Удаляет все сообщения пользователя из словаря user_messages.
    """
    if user_id in user_messages:
        for message_id in user_messages[user_id]:
            try:
                await bot.delete_message(chat_id=user_id, message_id=message_id)
            except Exception as e:
                logger.error(f"Ошибка при удалении сообщения {message_id} для пользователя {user_id}: {e}")

        # Очищаем записи сообщений пользователя, кроме сообщения с клавиатурой
        user_messages[user_id] = [msg_id for msg_id in user_messages[user_id] if msg_id not in user_messages.get('keyboard_message_ids', [])]

@router.message(CommandStart())
async def command_start_handler(message: Message):
    async with async_session() as session:  # Создаем новую сессию
        user_crud = UserCRUD(session)

        # Проверка наличия пользователя
        user = await user_crud.get_user_by_telegram_id(message.from_user.id)

        if user is None:
            # Создание нового пользователя
            user = await user_crud.create_user(
                telegram_id=message.from_user.id,
                chat_id=message.chat.id,  # Сохраняем chat_id
                name=message.from_user.full_name
            )
            welcome_message = "Добро пожаловать! Ваш аккаунт успешно создан."
        else:
            welcome_message = "Добро пожаловать обратно!"

    # Отправка приветственного сообщения и клавиатуры
    welcome_msg = await message.answer(welcome_message)
    keyboard_msg = await message.answer("Выберите опцию:", reply_markup=get_main_menu_keyboard())


@router.message(lambda message: message.text == 'ℹ️ Добавить токен')
async def add_token_handler(message: Message, state: FSMContext):
    # Сохраняем идентификатор сообщения пользователя
    user_messages.setdefault(message.from_user.id, []).append(message.message_id)

    sent_message = await message.answer("Пожалуйста, введите ваш токен:")
    # Сохраняем идентификатор сообщения бота
    user_messages.setdefault(message.from_user.id, []).append(sent_message.message_id)

    # Устанавливаем состояние ожидания токена
    await state.set_state(AddTokenState.waiting_for_token)


@router.message(AddTokenState.waiting_for_token)
async def receive_token_handler(message: Message, state: FSMContext):
    token = message.text  # Получаем токен от пользователя
    # Сохраняем идентификатор сообщения пользователя
    user_messages.setdefault(message.from_user.id, []).append(message.message_id)

    async with async_session() as session:  # Создаем новую сессию
        user_crud = UserCRUD(session)

        try:
            # Генерация ключа шифрования
            key = generate_key()
            encrypted_token = encrypt_token(key, token)

            # Сохранение токена в БД с использованием метода save_token
            await user_crud.save_token(
                telegram_id=message.from_user.id,
                token=encrypted_token,
                key=key
            )

            sent_message = await message.answer("Токен успешно добавлен и зашифрован!")

            # Сохраняем идентификатор сообщения бота
            user_messages.setdefault(message.from_user.id, []).append(sent_message.message_id)

            # Ждем 3 секунды перед удалением сообщений
            await asyncio.sleep(3)

            # Удаляем все сообщения пользователя, кроме сообщения с клавиатурой
            await delete_user_messages(message.from_user.id)

        except ValueError as e:
            await message.answer(str(e))  # Сообщаем пользователю об ошибке
        except Exception as e:
            await message.answer("Произошла ошибка при добавлении токена.")
            logger.error(f"Ошибка при добавлении токена: {e}")

    # Сброс состояния после получения токена
    await state.clear()


@router.message(lambda message: message.text == '📊 Статистика')
async def show_statistics_handler(message: Message):
    await message.answer("Запускаю парсинг объявлений...")

    async with async_session() as session:
        user_crud = UserCRUD(session)
        tokens = await user_crud.get_user_tokens(message.from_user.id)

    if not tokens:
        await message.answer("Не удалось получить токены пользователя.")
        return

    async with aiohttp.ClientSession() as session:
        decrypted_token = decrypt_token(tokens[0][1], tokens[0][0])
        print(decrypted_token)
        user_id = await get_user_id(session, decrypted_token)
        print(user_id)
        all_stats = await parse_statistics(session, tokens, user_id)

        if not all_stats:
            await message.answer("Не удалось получить статистику.")
            return

        # Создание и отправка XLSX файла
        file_path = "statistics_report.xlsx"
        workbook = create_xlsx_report(all_stats, file_path)


        print(f"Файл сохранен по пути: {file_path}")

        input_file = FSInputFile("statistics_report.xlsx")
        await message.answer_document(input_file)

    await message.answer("Парсинг завершен! Отчет отправлен.")


