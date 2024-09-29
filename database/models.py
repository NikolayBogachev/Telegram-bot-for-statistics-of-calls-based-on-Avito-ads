from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Text,
    String,
    UniqueConstraint, TIMESTAMP, Date, Boolean, LargeBinary,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    name = Column(String, nullable=False)
    chat_id = Column(Integer, unique=True, index=True)

    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")


class Token(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    encrypted_token = Column(String)  # Храните зашифрованный токен
    encryption_key = Column(LargeBinary)    # Храните ключ для шифрования

    user = relationship('User', back_populates='tokens')
