from sqlalchemy import Integer, String, Text, DateTime
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
    text: Mapped[str] = mapped_column(Text)


class Meet(BaseModel):
    __tablename__ = 'meets'

    date: Mapped[str] = mapped_column(DateTime)
    companion: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(Integer)
