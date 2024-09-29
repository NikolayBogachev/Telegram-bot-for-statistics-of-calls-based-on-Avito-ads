
from sqlalchemy import select, Row, RowMapping
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload
from database.models import Token, User


class UserCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_tokens(self, user_id: int):
        """
        Получает токены пользователя по его ID вместе с ключами шифрования.

        :param user_id: ID пользователя в Telegram
        :return: Список токенов и соответствующих ключей шифрования или None, если пользователь не найден
        """
        # Выполняем асинхронный запрос к базе данных для получения пользователя
        result = await self.db.execute(
            select(User)
            .options(joinedload(User.tokens))
            .where(User.telegram_id == user_id)
        )
        user = result.scalars().first()

        if user:
            print(
                f"User found: {user.name}, Tokens: {[(token.encrypted_token, token.encryption_key) for token in user.tokens]}")
            return [(token.encrypted_token, token.encryption_key) for token in
                    user.tokens]  # Возвращаем список кортежей (токен, ключ)
        else:
            print("User not found")
        return None  # Если пользователь не найден

    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        """
        Получить пользователя по telegram_id.
        """
        result = await self.db.execute(
            select(User).filter(User.telegram_id == telegram_id)
        )
        return result.scalars().first()

    async def create_user(self, telegram_id: int, chat_id: int, name: str) -> User:
        """
        Создать нового пользователя.
        """
        new_user = User(telegram_id=telegram_id, chat_id=chat_id, name=name)
        self.db.add(new_user)
        try:
            await self.db.commit()
            await self.db.refresh(new_user)  # Обновляем объект, чтобы получить его id
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Пользователь с таким telegram_id уже существует.")
        return new_user

    async def save_token(self, telegram_id: int, token: str, key: bytes) -> Token:
        """
        Сохранить токен для пользователя.
        """
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            raise ValueError("Пользователь не найден.")

        new_token = Token(user_id=user.id, encrypted_token=token, encryption_key=key)  # Заменяем token на encrypted_token
        self.db.add(new_token)
        try:
            await self.db.commit()
            await self.db.refresh(new_token)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Ошибка при сохранении токена.")
        return new_token
