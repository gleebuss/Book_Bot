import os
from dotenv import load_dotenv
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from database.dbapi import DatabaseConnector

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = DatabaseConnector(os.getenv('USER_NAME'))

class Add_book(StatesGroup):
    book_name = State()
    author = State()
    published = State()

class Delete_book(StatesGroup):
    book_name = State()
    author = State()
    published = State()
    action_approve = State()

class Borrow_book(StatesGroup):
    book_name = State()
    author = State()
    published = State()
    action_approve = State()


class Find_book(StatesGroup):
    book_name = State()
    author = State()
    published = State()

class Stats_book(StatesGroup):
    book_name = State()
    author = State()
    published = State()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Добро пожаловать! напишите /help для получения справки")


@dp.message_handler(state='*', commands=['cancel'])
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Отмена операции. Зачем начинали то?')


@dp.message_handler(commands=['add'])
async def add_command(message: types.Message):
    await message.reply("Введите название книги")
    await Add_book.book_name.set()

@dp.message_handler(state=Add_book.book_name)
async def add_book_name(message: types.Message, state: FSMContext):
    await state.update_data(book_name=message.text)
    await message.reply("Введите имя автора")
    await Add_book.next()

@dp.message_handler(state=Add_book.author)
async def add_author(message: types.Message, state: FSMContext):
    await state.update_data(author=message.text)
    await message.reply("Введите год издания")
    await Add_book.next()

@dp.message_handler(state=Add_book.published)
async def add_published(message: types.Message, state: FSMContext):
    await state.update_data(published=int(message.text))
    data = await state.get_data()
    await message.reply("Добавляем книгу в базу данных")
    result = db.add(data['book_name'], data['author'], data['published'])
    if result:
        await message.reply(f"Книга успешно добавлена ({result})")
    else:
        await message.reply("Ошибка при добавлении книги")
    await state.finish()



@dp.message_handler(commands=['delete'])
async def delete_command(message: types.Message):
    await message.reply("Введите название книги")
    await Delete_book.book_name.set()

@dp.message_handler(state=Delete_book.book_name)
async def delete_book_name(message: types.Message, state: FSMContext):
    await state.update_data(book_name=message.text)
    await message.reply("Введите имя автора")
    await Delete_book.next()

@dp.message_handler(state=Delete_book.author)
async def delete_author(message: types.Message, state: FSMContext):
    await state.update_data(author=message.text)
    await message.reply("Введите год издания")
    await Delete_book.next()

@dp.message_handler(state=Delete_book.published)
async def delete_published(message: types.Message, state: FSMContext):
    await state.update_data(published=int(message.text))
    data = await state.get_data()
    await message.reply("Удаляем книгу из базы данных")
    result = db.get_book(data['book_name'], data['author'], data['published'])
    if result:
        await message.reply(f"Найдена книга {data['book_name']} {data['author']} {data['published']}. Удаляем?")
        await Delete_book.action_approve.set()
    else:
        await message.reply("Книга не найдена")
        await state.finish()

@dp.message_handler(state=Delete_book.action_approve)
async def delete_approve(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        data = await state.get_data()
        result = db.delete(db.get_book(data['book_name'], data['author'], data['published']))
        if result:
            await message.reply(f"Книга успешно удалена ({result})")
        else:
            await message.reply("Невозможно удалить книгу")
    else:
        await message.reply("Отмена операции")
    await state.finish()



@dp.message_handler(commands=['list'])
async def list_command(message: types.Message):
    await message.reply("Список книг:")
    books = db.list_books()
    reply = ""
    for book in books:
        reply += f"{book['title']} {book['author']} {book['published']}{' (удалена);' if not book['deleted'] else ';'}\n"
    await message.reply(reply)



@dp.message_handler(commands=['find'])
async def find_command(message: types.Message):
    await message.reply("Введите название книги")
    await Find_book.book_name.set()

@dp.message_handler(state=Find_book.book_name)
async def find_book_name(message: types.Message, state: FSMContext):
    await state.update_data(book_name=message.text)
    await message.reply("Введите имя автора")
    await Find_book.next()

@dp.message_handler(state=Find_book.author)
async def find_author(message: types.Message, state: FSMContext):
    await state.update_data(author=message.text)
    await message.reply("Введите год издания")
    await Find_book.next()

@dp.message_handler(state=Find_book.published)
async def find_published(message: types.Message, state: FSMContext):
    await state.update_data(published=int(message.text))
    data = await state.get_data()
    result = db.get_book(data['book_name'], data['author'], data['published'])
    if result:
        await message.reply(f"Найдена книга {data['book_name']} {data['author']} {data['published']}")
    else:
        await message.reply("Книга не найдена")
    await state.finish()

@dp.message_handler(commands=['borrow'])
async def borrow_command(message: types.Message):
    await message.reply("Введите название книги")
    await Borrow_book.book_name.set()

@dp.message_handler(state=Borrow_book.book_name)
async def borrow_book_name(message: types.Message, state: FSMContext):
    await state.update_data(book_name=message.text)
    await message.reply("Введите имя автора")
    await Borrow_book.next()

@dp.message_handler(state=Borrow_book.author)
async def borrow_author(message: types.Message, state: FSMContext):
    await state.update_data(author=message.text)
    await message.reply("Введите год издания")
    await Borrow_book.next()

@dp.message_handler(state=Borrow_book.published)
async def borrow_published(message: types.Message, state: FSMContext):
    await state.update_data(published=int(message.text))
    data = await state.get_data()
    result = db.get_book(data['book_name'], data['author'], data['published'])
    if result:
        await message.reply(f"Найдена книга {data['book_name']} {data['author']} {data['published']}. Берем?")
        await Borrow_book.action_approve.set()
    else:
        await message.reply("Книга не найдена")
        await state.finish()

@dp.message_handler(state=Borrow_book.action_approve)
async def borrow_approve(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        data = await state.get_data()
        result = db.borrow(
            book_id=db.get_book(data['book_name'], data['author'], data['published']),
            user_id=message.from_user.id
        )
        if result:
            await message.reply(f"Книга успешно взята ({result})")
        else:
            await message.reply("Невозможно взять книгу")
    else:
        await message.reply("Отмена операции")
    await state.finish()

@dp.message_handler(commands=['retrieve'])
async def retrieve_command(message: types.Message):
    borrow_id = db.get_borrow(message.from_user.id)
    if borrow_id:
        result = db.retrieve(borrow_id)
        if result:
            await message.reply(f"Вы вернули книгу {result['title']} {result['author']} {result['published']}")
        else:
            await message.reply("Невозможно вернуть книгу. Очень интересно...")
    else:
        await message.reply("У вас нет взятых книг")

@dp.message_handler(commands=['stats'])
async def stats_command(message: types.Message):
    await message.reply("Введите название книги")
    await Stats_book.book_name.set()

@dp.message_handler(state=Stats_book.book_name)
async def stats_book_name(message: types.Message, state: FSMContext):
    await state.update_data(book_name=message.text)
    await message.reply("Введите имя автора")
    await Stats_book.next()

@dp.message_handler(state=Stats_book.author)
async def stats_author(message: types.Message, state: FSMContext):
    await state.update_data(author=message.text)
    await message.reply("Введите год издания")
    await Stats_book.next()

@dp.message_handler(state=Stats_book.published)
async def stats_published(message: types.Message, state: FSMContext):
    await state.update_data(published=int(message.text))
    data = await state.get_data()
    result = db.get_book(data['book_name'], data['author'], data['published'])
    if result:
        await message.reply(f"Статистика доступна по адресу: http://localhost:8080/download/{result}/")
        await state.finish()
    else:
        await message.reply("Книга не найдена")
        await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)