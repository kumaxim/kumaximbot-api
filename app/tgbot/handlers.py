from os import path
from base64 import b64decode
from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import (
    Message,
    KeyboardButton,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    FSInputFile,
    CallbackQuery)
from app.db.repositories.post import PostRepository
from app.db.repositories.contact import ContactRepository
from app.db.models import PostType
from app.logger import logger
from app.config import config

router = Router()


class MenuNavigate(StatesGroup):
    command = State()


@router.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext, db: AsyncSession) -> None:
    # Telegram бот часовым поиском всех сообщений выставляет UTC. Поскольку, моим ботом будут пользоваться
    # преимущественно люди из МСК, к текущему часу добавлю +3, для того чтобы приветственное сообщение более
    # соответствовало реальному времени суток пользователя
    greeting = f'Доброй ночи'

    if 5 <= (message.date.hour + 3) < 12:
        greeting = f'Доброе утро'
    elif 12 <= (message.date.hour + 3) < 18:
        greeting = f'Добрый день'
    elif 18 <= (message.date.hour + 3) < 23:
        greeting = f'Добрый вечер'

    introduce = await PostRepository(db).get_by_command_name('start')

    text = f'{greeting}, {html.quote(message.from_user.full_name)}. \n\n{introduce.text}'

    await state.clear()
    await message.answer(text)


@router.callback_query()
async def callback_handler(callback: CallbackQuery, state: FSMContext, db: AsyncSession) -> None:
    await callback.message.edit_reply_markup(reply_markup=None)

    command, _, query = callback.data.partition(':')

    posts = await PostRepository(db).filter_by(command=command, callback_query=query)

    if len(posts) == 0:
        await callback.message.answer(f'[{callback.data}]: Post not found')

    await state.set_state(MenuNavigate.command)
    await state.update_data(command=command)

    keyboard_markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Назад')]],
        one_time_keyboard=True,
        resize_keyboard=True
    )

    for post in posts:
        if post.type == PostType.TEXT:
            await callback.message.answer(post.text, reply_markup=keyboard_markup)
        elif post.type == PostType.CONTACT:
            contact = await ContactRepository(db).get(int(post.text))

            await callback.message.answer_contact(
                phone_number=f'+{contact.phone_number}',
                first_name=contact.first_name,
                last_name=contact.last_name,
                reply_markup=keyboard_markup)
        elif post.type == PostType.DOCUMENT:
            filename = path.join(config.assets_path, post.text)

            if not path.isfile(filename):
                await callback.message.answer('Извините, файл не найден', reply_markup=keyboard_markup)
                await logger.warning(f'[{command}:{query}]: File "{post.text}" not found in assets directory')
            else:
                pdf = FSInputFile(path=filename, filename=post.text)
                await callback.message.answer_document(document=pdf, reply_markup=keyboard_markup)

    await callback.answer()


@router.message()
async def message_handler(message: Message, state: FSMContext, db: AsyncSession) -> None:
    try:
        menu_position = await state.get_data()
        message_text = message.text

        if message.text == 'Назад' and menu_position and menu_position['command']:
            message_text = '@' + menu_position['command']

        if not message_text.startswith('/') and not message_text.startswith('@'):
            await message.answer('Unrecognized input command', reply_markup=ReplyKeyboardRemove())
        else:
            command = message_text.lstrip('/').lstrip('@')
            post = await PostRepository(db).get_by_command_name(command)

            kb = InlineKeyboardBuilder()
            queries = await PostRepository(db).get_by_command_name(command, True)

            for q in queries:
                if q.callback_query is not None:
                    kb.add(InlineKeyboardButton(text=q.title, callback_data=f'{q.command}:{q.callback_query}'))

            await state.clear()

            await message.answer(
                text=post.text if post else f'[{command}]: Handler not found',
                reply_markup=kb.adjust(2).as_markup() if sum(1 for _ in kb.buttons) else ReplyKeyboardRemove()
            )
    except TypeError:
        await message.answer('Unrecognized input command', reply_markup=ReplyKeyboardRemove())
