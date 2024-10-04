from os import path
from aiogram import Router, html, F
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import (Message, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, FSInputFile, CallbackQuery)

from app.db.repositories import PostRepository

router = Router()


@router.message(CommandStart())
async def send_welcome(message: Message, db: AsyncSession) -> None:
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

    await message.answer(text)


@router.message(Command('about'))
async def handler_about(message: Message, db: AsyncSession) -> None:
    about = await PostRepository(db).get_by_command_name('about')
    await message.answer(text=about.text if about else '[about]: Handler not found')


@router.message(Command('skills'))
async def handler_skills(message: Message, db: AsyncSession) -> None:
    skills = await PostRepository(db).get_by_command_name('skills')
    await message.answer(text=skills.text if skills is not None else '[skills]: Handler not found')


@router.message(Command('experience'))
async def handler_experience(message: Message, db: AsyncSession) -> None:
    experience = await PostRepository(db).get_by_command_name('experience')
    await message.answer(text=experience.text if experience else '[experience]: Handler not found')


@router.message(Command('projects'))
async def handler_projects(message: Message, db: AsyncSession) -> None:
    projects = await PostRepository(db).get_by_command_name('projects')
    await message.answer(text=projects.text if projects else '[projects]: Handler not found')


@router.message(Command('education'))
async def handler_education(message: Message, db: AsyncSession) -> None:
    education = await PostRepository(db).get_by_command_name('education')
    await message.answer(text=education.text if education else '[education]: Handler not found')


@router.message(Command('expectations'))
async def handler_expectations(message: Message, db: AsyncSession) -> None:
    expectations = await PostRepository(db).get_by_command_name('expectations')
    await message.answer(text=expectations.text if expectations else '[expectations]: Handler not found')


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


@router.message()
async def echo(message: Message, db: AsyncSession) -> None:
    try:
        default = await PostRepository(db).get_by_command_name('default')
        await message.answer(text=default.text if default else '[default]: Handler not found')
    except TypeError:
        await message.answer('Nice try!')
