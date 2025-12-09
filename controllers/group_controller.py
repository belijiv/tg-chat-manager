import asyncio
from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from database import Database
from views.messages import Messages
from models import GroupSettings, UserViolation, UserMessage, StopWord
from datetime import datetime
from utils import Helpers
from views import messages


class GroupController:
    def __init__(self, bot, database: Database):
        self.bot = bot
        self.db = database

    async def check_subscription(self, user_id: int, channels: list) -> bool:
        for channel in channels:
            try:
                chat_member = await self.bot.get_chat_member(channel, user_id)
                if chat_member.status not in ['member', 'administrator', 'creator']:
                    return False
            except Exception as e:
                print(f"Ошибка проверки подписки: {e}")
                return False
        return True

    def contains_stop_words(self, text: str, group_id: str) -> bool:
        stop_words = self.db.get_stop_words(group_id)
        text_lower = text.lower()
        return any(word.word in text_lower for word in stop_words)

    async def handle_message(self, message: types.Message):
        print(f"🔔 Бот получил сообщение в группе {message.chat.id}")
        print(f"📝 Текст: {message.text}")
        print(f"👤 От: {message.from_user.id}")

        if message.from_user.is_bot:
            print("🤖 Игнорируем сообщение от бота")
            return

        user = message.from_user
        self.db.save_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

        user_id = message.from_user.id
        group_id = str(message.chat.id)

        group_settings = self.db.get_group(group_id)
        if not group_settings:
            group_settings = GroupSettings(
                group_id=group_id,
                group_name=message.chat.title
            )
            self.db.save_group(group_settings)

        print(f"⚙️ Настройки группы: require_subscription={group_settings.require_subscription}, "
              f"slow_mode_delay={group_settings.slow_mode_delay}, "
              f"target_channels={group_settings.target_channels}")

        user_violations = self.db.get_user_violations(user_id, group_id)
        if user_violations and user_violations.violations_count >= 5:
            print("🗑 Сообщение удалено: 5 нарушений")
            await message.delete()
            return

        user_banned = self.db.get_user_banned(user_id, group_id)
        if user_banned:
            print("🗑 Сообщение удалено: пользователь забанен")
            await message.delete()
            return

        if group_settings.require_subscription and group_settings.target_channels:
            print("🔍 Проверяем подписку...")
            is_subscribed = await self.check_subscription(user_id, group_settings.target_channels)
            if not is_subscribed:
                print("🗑 Сообщение удалено: нет подписки на каналы")
                await message.delete()
                warning = await message.answer(
                    Messages.subscription_required(
                        message.from_user.first_name,
                        group_settings.target_channels
                    )
                )
                asyncio.create_task(Helpers.delete_message_after(warning, 15))
                return

        user_message = self.db.get_user_message_time(user_id, group_id)
        if user_message:
            last_time = datetime.fromisoformat(user_message.last_message_time)
            time_diff = (datetime.now() - last_time).total_seconds()
            print(f"⏰ Время с последнего сообщения: {time_diff:.1f} сек, лимит: {group_settings.slow_mode_delay} сек")
            if time_diff < group_settings.slow_mode_delay:
                print("🗑 Сообщение удалено: медленный режим")
                await message.delete()
                remaining_time = int(group_settings.slow_mode_delay - time_diff)
                slow_mode_warning = await message.answer(
                    Messages.slow_mode_warning(remaining_time)
                )
                asyncio.create_task(Helpers.delete_message_after(slow_mode_warning, min(2, remaining_time)))
                return

        if message.text and self.contains_stop_words(message.text, group_id):
            print("🗑 Сообщение удалено: содержит стоп-слово")
            await message.delete()

            if user_violations:
                user_violations.violations_count += 1
                user_violations.last_violation_time = datetime.now().isoformat()
            else:
                user_violations = UserViolation(
                    user_id=user_id,
                    group_id=group_id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    violations_count=1
                )

            self.db.save_user_violations(user_violations)

            warning = await message.answer(Messages.stop_word_warning())
            asyncio.create_task(Helpers.delete_message_after(warning, 15))

            if user_violations.violations_count >= 5:
                ban_msg = await message.answer(Messages.user_banned())
                asyncio.create_task(Helpers.delete_message_after(ban_msg, 15))
            return

        print("✅ Сообщение разрешено")
        new_user_message = UserMessage(
            user_id=user_id,
            group_id=group_id,
            last_message_time=datetime.now().isoformat()
        )
        self.db.save_user_message_time(new_user_message)

    def register_handlers(self, dp: Dispatcher):
        dp.message.register(self.handle_message, F.chat.type.in_(["group", "supergroup"]))