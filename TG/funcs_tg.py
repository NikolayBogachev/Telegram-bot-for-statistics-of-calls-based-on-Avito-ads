from typing import Any, List, Dict
from datetime import datetime
from aiogram.client.session import aiohttp
from aiohttp import ClientResponseError, ClientConnectorError
from openpyxl.workbook import Workbook

from TG.auth import decrypt_token
from TG.bot import bot
from config import config

from loguru import logger


async def get_user_id(session: aiohttp.ClientSession, tokens: str):
    """
    Получает идентификатор пользователя (user_id) с использованием токена.

    Args:
        session (aiohttp.ClientSession): Сессия для выполнения HTTP-запросов.
        tokens (str): Токен авторизации для доступа к API.

    Returns:
        int: Идентификатор пользователя, если запрос успешен; иначе None.
    """
    headers = {"Authorization": f"Bearer {tokens}"}

    async with session.get('https://api.avito.ru/core/v1/accounts/self', headers=headers) as response:
        if response.status == 200:
            user_data = await response.json()
            return user_data['id']  # Возвращаем user_id
        else:
            print(f"Error {response.status}: {await response.text()}")
            return None


async def fetch_items(session: aiohttp.ClientSession, headers: dict):
    """
    Запрашивает список объявлений пользователя.

    Args:
        session (aiohttp.ClientSession): Сессия для выполнения HTTP-запросов.
        headers (dict): Заголовки запроса, включая токен авторизации.

    Returns:
        dict: Данные с объявлениями, если запрос успешен; иначе None.
    """
    async with session.get("https://api.avito.ru/core/v1/items", headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            logger.error(f"Failed to fetch items: {response.status}")
            return None




async def fetch_call_stats(session: aiohttp.ClientSession, headers: dict, item_id: str, user_id: int):
    """
    Запрашивает статистику звонков по конкретному объявлению за указанный период.

    Args:
        session (aiohttp.ClientSession): Сессия для выполнения HTTP-запросов.
        headers (dict): Заголовки запроса, включая токен авторизации.
        item_id (str): Идентификатор объявления.
        user_id (int): Идентификатор пользователя, чьи данные запрашиваются.

    Returns:
        dict: Данные статистики звонков, если запрос успешен; иначе None.
    """
    # Устанавливаем начальную дату на начало текущего года (1 января)
    date_from = f"{datetime.now().year}-01-01"
    # Устанавливаем конечную дату на сегодняшнюю дату
    date_to = datetime.now().strftime("%Y-%m-%d")

    # Формируем тело запроса
    request_body = {
        "dateFrom": date_from,
        "dateTo": date_to,
        "itemIds": [int(item_id)]  # Преобразуем item_id в список целых чисел
    }

    async with session.post(f"https://api.avito.ru/core/v1/accounts/{user_id}/calls/stats/",
                            headers=headers, json=request_body) as response:
        if response.status == 200:
            return await response.json()
        else:
            logger.error(f"Failed to fetch call stats for item {item_id}: {response.status} - {await response.text()}")
            return None


async def parse_statistics(session: aiohttp.ClientSession, tokens: list, user_id: int):
    """
    Собирает и обрабатывает статистику звонков по объявлениям из всех кабинетов пользователей.

    Args:
        session (aiohttp.ClientSession): Сессия для выполнения HTTP-запросов.
        tokens (list): Список токенов пользователей, которые необходимо проверить.
        user_id (int): Идентификатор пользователя.

    Returns:
        dict: Обработанные данные по статистике звонков для каждого токена.
    """
    all_stats = {}

    for token in tokens:
        decrypted_token = decrypt_token(token[1], token[0])

        headers = {"Authorization": f"Bearer {decrypted_token}"}
        items_data = await fetch_items(session, headers)
        print(items_data)
        if items_data:
            all_stats[token] = []

            for item in items_data['resources']:
                item_id = item['id']
                item_name = item['title']

                # Получаем статистику по звонкам
                # stats = await fetch_call_stats(session, headers, item_id, user_id)
                stats = {
                    "result": {
                        "items": [
                            {
                                "days": [
                                    {
                                        "answered": 5,
                                        "calls": 10,
                                        "date": "2023-09-01",
                                        "new": 4,
                                        "newAnswered": 2
                                    },
                                    {
                                        "answered": 3,
                                        "calls": 8,
                                        "date": "2023-09-02",
                                        "new": 5,
                                        "newAnswered": 1
                                    },
                                    {
                                        "answered": 4,
                                        "calls": 7,
                                        "date": "2023-09-03",
                                        "new": 3,
                                        "newAnswered": 2
                                    }
                                ],
                                "employeeId": 1,
                                "itemId": 1853257996,
                                "itemName": "Продажа квартиры в центре города"
                            },
                            {
                                "days": [
                                    {
                                        "answered": 2,
                                        "calls": 5,
                                        "date": "2023-09-01",
                                        "new": 1,
                                        "newAnswered": 0
                                    },
                                    {
                                        "answered": 6,
                                        "calls": 9,
                                        "date": "2023-09-02",
                                        "new": 3,
                                        "newAnswered": 1
                                    },
                                    {
                                        "answered": 4,
                                        "calls": 10,
                                        "date": "2023-09-03",
                                        "new": 2,
                                        "newAnswered": 2
                                    }
                                ],
                                "employeeId": 2,
                                "itemId": 1853257997,
                                "itemName": "Аренда офиса на Лубянке"
                            },
                            {
                                "days": [
                                    {
                                        "answered": 0,
                                        "calls": 0,
                                        "date": "2023-09-01",
                                        "new": 0,
                                        "newAnswered": 0
                                    },
                                    {
                                        "answered": 0,
                                        "calls": 0,
                                        "date": "2023-09-02",
                                        "new": 0,
                                        "newAnswered": 0
                                    },
                                    {
                                        "answered": 1,
                                        "calls": 3,
                                        "date": "2023-09-03",
                                        "new": 1,
                                        "newAnswered": 0
                                    }
                                ],
                                "employeeId": 3,
                                "itemId": 1853257998,
                                "itemName": "Продажа автомобиля"
                            }
                        ]
                    }
                }
                # Проверяем, что данные в корректной структуре
                if stats and 'result' in stats:
                    item_stats = stats['result']['items']  # Исправляем путь к данным
                    for stat in item_stats:
                        # Проверяем наличие ключа 'itemName'
                        item_name = stat.get('itemName', 'Не указано')  # Или любое значение по умолчанию
                        if not item_name:
                            print("itemName отсутствует в:", stat)  # Логируем элементы без itemName
                            continue  # Пропускаем текущую итерацию, если itemName отсутствует

                        for day in stat['days']:
                            call_data = {
                                "itemId": item_name,
                                "date": day['date'],
                                "answered": day['answered'],
                                "calls": day['calls'],
                                "new_calls": day['new'],
                                "new_answered": day['newAnswered']
                            }
                            print(call_data)
                            all_stats[token].append(call_data)

    return all_stats


def create_xlsx_report(all_stats: dict, file_name: str = "report.xlsx"):
    """
    Создает XLSX-отчет на основе собранной статистики звонков.

    Args:
        all_stats (dict): Данные статистики звонков по каждому токену.
        file_name (str): Имя файла для сохранения отчета.

    Returns:
        str: Путь к сохраненному XLSX-отчету.
    """
    workbook = Workbook()
    # Удаляем стандартный лист, если он не нужен
    workbook.remove(workbook.active)

    for token, stats in all_stats.items():
        sheet_title = f"Кабинет {token}"[:31]
        sheet = workbook.create_sheet(title=sheet_title)  # Имя токена или ID
        sheet.append(["Название объявления", "Дата", "Ответственные звонки", "Всего звонков", "Новые звонки",
                      "Новые и одновременно отвеченные звонки"])

        # Проверяем наличие данных перед записью
        if not stats:
            print(f"Нет данных для токена {token}. Лист не будет создан.")
            continue

        for stat in stats:
            # Проверка, чтобы избежать ошибки доступа к отсутствующим ключам
            sheet.append([
                stat.get('itemId', 'Не указано'),
                stat.get('date', 'Не указана'),
                stat.get('answered', 0),
                stat.get('calls', 0),
                stat.get('new_calls', 0),
                stat.get('new_answered', 0)
            ])

    # Сохраняем файл
    workbook.save(file_name)
    print(f"Отчет сохранен в файл: {file_name}")

    return file_name