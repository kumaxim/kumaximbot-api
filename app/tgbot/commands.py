from os import path
from aiogram import Router, html, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import (
    Message,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    FSInputFile,
    CallbackQuery)
from app.db.repositories import PostRepository


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


@router.message(Command('resume'))
async def resume_handler(message: Message) -> None:
    kb = [
        [
            InlineKeyboardButton(text='Ссылка на hh.ru', callback_data='resume-url-to-hh.ru'),
            InlineKeyboardButton(text='Скачать .pdf', callback_data='resume-download-pdf'),
        ]
    ]

    await message.answer(text='Какой вариант предпочтительнее', reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))


@router.callback_query(F.data == 'resume-url-to-hh.ru')
async def handler_resume_from_headhunter(callback: CallbackQuery) -> None:
    url = '***REMOVED***'

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text=url)


@router.callback_query(F.data == 'resume-download-pdf')
async def handler_resume_download_pdf(callback: CallbackQuery) -> None:
    pdf = FSInputFile(path=path.abspath('assets/resume.pdf'), filename='***REMOVED***')

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer_document(document=pdf)


@router.message(Command('schedule'))
async def schedule_handler(message: Message) -> None:
    await message.answer(text='Согласовать дату/время интервью. Открыть календарь')


@router.message(Command('contacts'))
async def contacts_handler(message: Message) -> None:
    text = f'Приоритетный способ связи - Telegram. Если нужно что-то переслать - email.'

    kb = [
        [
            InlineKeyboardButton(text='Telegram', callback_data='contact-telegram'),
            InlineKeyboardButton(text='Email', callback_data='contact-email'),
        ]
    ]

    await message.answer(
        text='Какой способ связи для Вас предпочтительнее?',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )


@router.callback_query(F.data == 'contact-telegram')
async def handler_contact_telegram(callback: CallbackQuery) -> None:
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer_contact(phone_number='***REMOVED***', first_name='***REMOVED***', last_name='***REMOVED***')
    await callback.answer()


@router.callback_query(F.data == 'contact-email')
async def handler_contact_telegram(callback: CallbackQuery) -> None:
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text='***REMOVED***')
    await callback.answer()


@router.callback_query()
async def callback_handler(callback: CallbackQuery, state: FSMContext, db: AsyncSession) -> None:
    await callback.message.edit_reply_markup(reply_markup=None)

    command, _, query = callback.data.partition(':')

    posts = await PostRepository(db).filter_by(command=command, callback_query=query)
    await state.update_data(command=command, query=query)

    if len(posts) == 0:
        await callback.message.answer(f'[{callback.data}]: Post not found')

    await state.set_state(MenuNavigate.command)
    await state.update_data(command=command)

    for post in posts:
        await callback.message.answer(
            post.text,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text='Назад')]],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )

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
                reply_markup=kb.adjust(2).as_markup()
            )
    except TypeError:
        await message.answer('Nice try!')
