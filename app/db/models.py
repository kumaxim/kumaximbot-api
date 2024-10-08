from sqlalchemy import Integer, String, Text, DateTime, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Post(BaseModel):
    __tablename__ = 'posts'

    command: Mapped[str] = mapped_column(String, unique=True)
    callback_query: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(Text)


class Meet(BaseModel):
    __tablename__ = 'meets'

    date: Mapped[str] = mapped_column(DateTime)
    companion: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(Integer)


class StorageFSM(Base):
    __tablename__ = 'storage_fsm'
    __table_args__ = (PrimaryKeyConstraint('chat_id', 'user_id'),)

    bot_id: Mapped[int] = mapped_column(Integer)
    chat_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    thread_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    business_connection_id: Mapped[str | None] = mapped_column(String, nullable=True)
    destiny: Mapped[str] = mapped_column(String, default='default')
    state: Mapped[str | None] = mapped_column(String, nullable=True)
    data: Mapped[str | None] = mapped_column(Text, nullable=True)
