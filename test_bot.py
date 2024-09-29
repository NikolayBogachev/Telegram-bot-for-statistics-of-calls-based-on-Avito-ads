import unittest
from unittest.mock import AsyncMock, patch
import aiohttp

from TG.funcs_tg import fetch_call_stats, fetch_items, get_user_id
from date import FAKE_USER_DATA, FAKE_ITEMS_DATA, FAKE_CALL_STATS
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestAvitoBot(unittest.IsolatedAsyncioTestCase):

    @patch("TG.funcs_tg.aiohttp.ClientSession.get")
    async def test_get_user_id(self, mock_get):
        # Настройка мокового ответа от API для получения user_id
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = FAKE_USER_DATA

        mock_get.return_value.__aenter__.return_value = mock_response

        async with aiohttp.ClientSession() as session:
            user_id = await get_user_id(session, "fake_token")
            self.assertEqual(user_id, 123456)

    @patch("TG.funcs_tg.aiohttp.ClientSession.get")
    async def test_fetch_items(self, mock_get):
        # Настройка мокового ответа от API для получения объявлений
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = FAKE_ITEMS_DATA

        mock_get.return_value.__aenter__.return_value = mock_response

        async with aiohttp.ClientSession() as session:
            items = await fetch_items(session, {"Authorization": "Bearer fake_token"})
            self.assertEqual(items, FAKE_ITEMS_DATA)

    @patch("TG.funcs_tg.aiohttp.ClientSession.post")
    async def test_fetch_call_stats(self, mock_post):
        # Настройка мокового ответа от API для получения статистики звонков
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = FAKE_CALL_STATS

        mock_post.return_value.__aenter__.return_value = mock_response

        async with aiohttp.ClientSession() as session:
            stats = await fetch_call_stats(session, {"Authorization": "Bearer fake_token"}, "1853257996", 123456)
            self.assertEqual(stats, FAKE_CALL_STATS)


if __name__ == "__main__":
    unittest.main()
