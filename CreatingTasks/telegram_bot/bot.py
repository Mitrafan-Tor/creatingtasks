import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import aiohttp
import asyncio

logging.basicConfig(level=logging.INFO)


class TaskStates(StatesGroup):
    waiting_for_auth = State()
    main_menu = State()
    viewing_tasks = State()


class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)
        self.api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
        self.handlers()

    def handlers(self):
        self.dp.register_message_handler(self.start, commands=['start'])
        self.dp.register_message_handler(self.handle_auth, state=TaskStates.waiting_for_auth)
        self.dp.register_message_handler(self.show_main_menu, commands=['menu'])
        self.dp.register_message_handler(self.show_my_tasks, commands=['tasks'])
        self.dp.register_callback_query_handler(self.handle_task_action, lambda c: c.data.startswith('task_'))

    async def start(self, message: types.Message):
        """Start command handler"""
        user = message.from_user
        await message.answer(
            f"Привет, {user.first_name}! 👋\n\n"
            "Я бот для управления задачами в команде.\n"
            "Для начала работы необходимо авторизоваться.\n\n"
            "Пожалуйста, введите ваш email для аутентификации:"
        )
        await TaskStates.waiting_for_auth.set()

    async def handle_auth(self, message: types.Message, state: FSMContext):
        """Handle user authentication"""
        email = message.text.strip()

        async with aiohttp.ClientSession() as session:
            try:
                # Request authentication token
                async with session.post(
                        f"{self.api_base_url}/auth/telegram-login/",
                        json={
                            'email': email,
                            'telegram_id': message.from_user.id,
                            'telegram_username': message.from_user.username
                        }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        await state.update_data(token=data.get('token'))

                        await message.answer(
                            "✅ Авторизация прошла успешно!\n\n"
                            "Доступные команды:\n"
                            "/menu - Главное меню\n"
                            "/tasks - Мои задачи\n"
                            "/help - Помощь"
                        )
                        await TaskStates.main_menu.set()
                    else:
                        await message.answer(
                            "❌ Ошибка авторизации. Пожалуйста, проверьте ваш email "
                            "и убедитесь, что вы зарегистрированы в системе.\n\n"
                            "Попробуйте еще раз:"
                        )
            except Exception as e:
                logging.error(f"Auth error: {e}")
                await message.answer(
                    "❌ Произошла ошибка при авторизации. Попробуйте позже."
                )

    async def show_main_menu(self, message: types.Message, state: FSMContext):
        """Show main menu"""
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton("📋 Мои задачи"))
        keyboard.add(types.KeyboardButton("ℹ️ Помощь"))

        await message.answer(
            "Главное меню:\n\n"
            "Выберите действие:",
            reply_markup=keyboard
        )

    async def show_my_tasks(self, message: types.Message, state: FSMContext):
        """Show user's tasks"""
        user_data = await state.get_data()
        token = user_data.get('token')

        if not token:
            await message.answer("❌ Сначала необходимо авторизоваться. Используйте /start")
            return

        async with aiohttp.ClientSession() as session:
            try:
                headers = {'Authorization': f'Token {token}'}
                async with session.get(
                        f"{self.api_base_url}/tasks/my_tasks/",
                        headers=headers
                ) as response:
                    if response.status == 200:
                        tasks = await response.json()
                        await self.send_tasks_list(message, tasks)
                    else:
                        await message.answer("❌ Ошибка при загрузке задач")
            except Exception as e:
                logging.error(f"Error loading tasks: {e}")
                await message.answer("❌ Ошибка при загрузке задач")

    async def send_tasks_list(self, message: types.Message, tasks):
        """Send tasks list to user"""
        if not tasks:
            await message.answer("📭 У вас нет назначенных задач")
            return

        for task in tasks:
            task_text = self.format_task_message(task)
            keyboard = types.InlineKeyboardMarkup()

            if task['status'] != 'completed':
                keyboard.add(types.InlineKeyboardButton(
                    "✅ Завершить",
                    callback_data=f"task_complete_{task['id']}"
                ))

            keyboard.add(types.InlineKeyboardButton(
                "📋 Подробности",
                callback_data=f"task_details_{task['id']}"
            ))

            await message.answer(task_text, reply_markup=keyboard)

    def format_task_message(self, task):
        """Format task data for Telegram message"""
        status_emojis = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅',
            'cancelled': '❌'
        }

        priority_emojis = {
            'low': '🔵',
            'medium': '🟡',
            'high': '🟠',
            'urgent': '🔴'
        }

        status_emoji = status_emojis.get(task['status'], '📝')
        priority_emoji = priority_emojis.get(task['priority'], '⚪')

        due_date = task.get('due_date')
        if due_date:
            from datetime import datetime
            due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            due_text = due_date.strftime('%d.%m.%Y %H:%M')
        else:
            due_text = "Не установлен"

        return (
            f"{status_emoji} <b>{task['title']}</b>\n\n"
            f"📋 Описание: {task['description'] or 'Нет описания'}\n"
            f"📁 Список: {task['task_list']}\n"
            f"{priority_emoji} Приоритет: {self.get_priority_text(task['priority'])}\n"
            f"⏰ Срок: {due_text}\n"
            f"👤 Создал: {task['created_by']['username']}\n"
            f"📊 Статус: {self.get_status_text(task['status'])}"
        )

    async def handle_task_action(self, callback_query: types.CallbackQuery, state: FSMContext):
        """Handle task actions from inline keyboard"""
        data = callback_query.data
        user_data = await state.get_data()
        token = user_data.get('token')

        if not token:
            await callback_query.answer("❌ Ошибка авторизации")
            return

        if data.startswith('task_complete_'):
            task_id = data.split('_')[2]
            await self.complete_task(callback_query, task_id, token)

        elif data.startswith('task_details_'):
            task_id = data.split('_')[2]
            await self.show_task_details(callback_query, task_id, token)

    async def complete_task(self, callback_query: types.CallbackQuery, task_id: str, token: str):
        """Mark task as completed"""
        async with aiohttp.ClientSession() as session:
            try:
                headers = {'Authorization': f'Token {token}'}
                async with session.post(
                        f"{self.api_base_url}/tasks/{task_id}/complete/",
                        headers=headers
                ) as response:
                    if response.status == 200:
                        await callback_query.answer("✅ Задача завершена!")
                        await callback_query.message.edit_reply_markup(reply_markup=None)

                        # Update message text
                        task_data = await response.json()
                        updated_text = self.format_task_message(task_data)
                        await callback_query.message.edit_text(updated_text, parse_mode='HTML')
                    else:
                        await callback_query.answer("❌ Ошибка при завершении задачи")
            except Exception as e:
                logging.error(f"Error completing task: {e}")
                await callback_query.answer("❌ Ошибка при завершении задачи")

    async def show_task_details(self, callback_query: types.CallbackQuery, task_id: str, token: