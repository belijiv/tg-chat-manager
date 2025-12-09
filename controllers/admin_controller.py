from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from database import Database
from views.messages import Messages
from config import config
from models import StopWord


class AdminController:
    def __init__(self, bot, database: Database):
        self.bot = bot
        self.db = database

    def _is_admin(self, user_id: int) -> bool:
        return user_id in config.ADMIN_IDS

    async def add_global_word(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        word = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if not word:
            await message.answer(Messages.no_word_provided())
            return

        stop_word = StopWord(word=word, is_global=True)
        self.db.add_stop_word(stop_word)
        await message.answer(Messages.stop_word_added(word, True))

    async def remove_global_word(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        word = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if not word:
            await message.answer("❌ Укажите слово: /remove_global_word слово")
            return

        self.db.remove_stop_word(word)
        await message.answer(Messages.stop_word_removed(word, True))

    async def add_group_word(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        word = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if not word:
            await message.answer("❌ Укажите слово: /add_group_word слово")
            return

        group_id = str(message.chat.id)
        stop_word = StopWord(word=word, is_global=False, group_id=group_id)
        self.db.add_stop_word(stop_word)
        await message.answer(Messages.stop_word_added(word, False))

    async def remove_group_word(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        word = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if not word:
            await message.answer("❌ Укажите слово: /remove_group_word слово")
            return

        group_id = str(message.chat.id)
        self.db.remove_stop_word(word, group_id)
        await message.answer(Messages.stop_word_removed(word, False))

    async def ban_user(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        username = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if not username or not username.startswith('@'):
            await message.answer(Messages.no_username_provided())
            return

        group_id = str(message.chat.id)
        username_clean = username[1:]  # Убираем @
        user_data = self.db.get_user_by_username(username_clean)
        if user_data:
            self.db.ban_user(user_data['user_id'], group_id)
            await message.answer(Messages.user_banned_command(username))
        else:
            await message.answer(Messages.user_not_found(username))

    async def unban_user(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        username = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if not username or not username.startswith('@'):
            await message.answer(Messages.no_username_provided())
            return

        group_id = str(message.chat.id)
        username_clean = username[1:]  # Убираем @

        user_data = self.db.get_user_by_username(username_clean)
        if user_data:
            self.db.unban_user(user_data['user_id'], group_id)
            await message.answer(Messages.user_unbanned(username))
        else:
            await message.answer(Messages.user_not_found(username))

    async def require_subscription_toggle(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        group_id = str(message.chat.id)
        group = self.db.get_group(group_id)

        if group:
            new_value = not group.require_subscription
            self.db.update_group_settings(group_id, require_subscription=new_value)
            await message.answer(Messages.subscription_toggled(new_value))
        else:
            await message.answer("❌ Группа не найдена в базе данных")

    async def set_slow_mode_delay(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        delay_str = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if not delay_str or not delay_str.isdigit():
            await message.answer("❌ Укажите задержку в секундах: /set_slow_mode_delay 60")
            return

        delay = int(delay_str)
        group_id = str(message.chat.id)
        self.db.update_group_settings(group_id, slow_mode_delay=delay)
        await message.answer(Messages.slow_mode_set(delay))

    async def add_target_channel(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        channel = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if not channel:
            await message.answer("❌ Укажите канал: /add_target_channel @channel")
            return

        group_id = str(message.chat.id)
        self.db.add_target_channel(group_id, channel)
        await message.answer(Messages.target_channel_added(channel))

    async def remove_target_channel(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        channel = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if not channel:
            await message.answer("❌ Укажите канал: /remove_target_channel @channel")
            return

        group_id = str(message.chat.id)
        self.db.remove_target_channel(group_id, channel)
        await message.answer(Messages.target_channel_removed(channel))

    async def target_channel_list(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        group_id = str(message.chat.id)
        group = self.db.get_group(group_id)

        if group:
            await message.answer(Messages.target_channel_list(group.target_channels))
        else:
            await message.answer("❌ Группа не найдена в базе данных")

    async def global_stop_words_list(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        words = self.db.get_global_stop_words()
        await message.answer(Messages.global_stop_words_list(words))

    async def group_stop_words_list(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        group_id = str(message.chat.id)
        words = self.db.get_group_stop_words(group_id)
        await message.answer(Messages.group_stop_words_list(words))

    async def admin_help(self, message: types.Message):
        if not self._is_admin(message.from_user.id):
            await message.answer(Messages.not_admin())
            return

        await message.answer(Messages.admin_help())

    def register_handlers(self, dp: Dispatcher):
        dp.message.register(self.add_global_word, Command("add_global_word"))
        dp.message.register(self.remove_global_word, Command("remove_global_word"))
        dp.message.register(self.add_group_word, Command("add_group_word"))
        dp.message.register(self.remove_group_word, Command("remove_group_word"))
        dp.message.register(self.ban_user, Command("ban"))
        dp.message.register(self.unban_user, Command("unban"))
        dp.message.register(self.require_subscription_toggle, Command("require_subscription_toggle"))
        dp.message.register(self.set_slow_mode_delay, Command("set_slow_mode_delay"))
        dp.message.register(self.add_target_channel, Command("add_target_channel"))
        dp.message.register(self.remove_target_channel, Command("remove_target_channel"))
        dp.message.register(self.target_channel_list, Command("target_channel_list"))
        dp.message.register(self.global_stop_words_list, Command("global_stop_words_list"))
        dp.message.register(self.group_stop_words_list, Command("group_stop_words_list"))
        dp.message.register(self.admin_help, Command("admin", "start", "help"))