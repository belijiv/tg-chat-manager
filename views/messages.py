class Messages:
    @staticmethod
    def subscription_required(user_name: str, channels: list) -> str:
        channels_str = ", ".join(channels)
        return f"Уважаемый {user_name}!\nДля того, чтобы писать в группу – подпишитесь на: {channels_str}"

    @staticmethod
    def stop_word_warning() -> str:
        return "❌ Использовано запрещенное слово"

    @staticmethod
    def user_banned() -> str:
        return "🚫 Вы заблокированы за многократные нарушения"

    @staticmethod
    def admin_help() -> str:
        return """🤖 КОМАНДЫ АДМИНИСТРАТОРА:

📋 Управление стоп-словами:
/add_global_word слово - добавить глобальное стоп-слово
/remove_global_word слово - удалить глобальное стоп-слово
/add_group_word слово - добавить стоп-слово для этой группы  
/remove_group_word слово - удалить стоп-слово для этой группы

👤 Управление пользователями:
/ban @username - заблокировать пользователя
/unban @username - разблокировать пользователя

⚙️ Настройки группы:
/require_subscription_toggle - вкл/выкл проверку подписки
/set_slow_mode_delay 60 - установить медл-режим (секунды)
/add_target_channel @channel - добавить канал для подписки
/remove_target_channel @channel - удалить канал для подписки
/target_channel_list - список каналов для подписки

ℹ️ Справка:
/admin - показать это сообщение
/help - показать это сообщение
/start - показать это сообщение"""

    @staticmethod
    def stop_word_added(word: str, is_global: bool = True) -> str:
        scope = "глобальные" if is_global else "группы"
        return f"✅ Слово '{word}' добавлено в {scope} стоп-слова"

    @staticmethod
    def stop_word_removed(word: str, is_global: bool = True) -> str:
        scope = "глобальных" if is_global else "группы"
        return f"✅ Слово '{word}' удалено из {scope} стоп-слов"

    @staticmethod
    def user_banned_command(username: str) -> str:
        return f"🚫 Пользователь {username} забанен"

    @staticmethod
    def user_unbanned(username: str) -> str:
        return f"✅ Пользователь {username} разбанен"

    @staticmethod
    def no_username_provided() -> str:
        return "❌ Укажите username: /ban @username или /unban @username"

    @staticmethod
    def no_word_provided() -> str:
        return "❌ Укажите слово: /add_global_word слово"

    @staticmethod
    def not_admin() -> str:
        return "⛔ У вас нет прав администратора"

    @staticmethod
    def subscription_toggled(enabled: bool) -> str:
        status = "включена" if enabled else "выключена"
        return f"✅ Проверка подписки {status}"

    @staticmethod
    def slow_mode_set(delay: int) -> str:
        return f"✅ Медл-режим установлен на {delay} секунд"

    @staticmethod
    def slow_mode_warning(remaining_time: int) -> str:
        return f"⏳ Медленный режим! Подождите еще {remaining_time} секунд(у) перед отправкой следующего сообщения."
    @staticmethod
    def target_channel_added(channel: str) -> str:
        return f"✅ Канал {channel} добавлен для проверки подписки"

    @staticmethod
    def target_channel_removed(channel: str) -> str:
        return f"✅ Канал {channel} удален из проверки подписки"

    @staticmethod
    def target_channel_list(channels: list) -> str:
        if not channels:
            return "📭 Каналы для подписки не настроены"

        channels_text = "\n".join([f"• {channel}" for channel in channels])
        return f"📋 Каналы для подписки:\n{channels_text}"

    @staticmethod
    def user_not_found(username: str) -> str:
        return f"❌ Пользователь {username} не найден в базе данных"

    @staticmethod
    def user_saved() -> str:
        return "✅ Данные пользователя сохранены"

    @staticmethod
    def global_stop_words_list(words: list) -> str:
        if not words:
            return "📭 Глобальные стоп-слова не настроены"

        words_text = "\n".join([f"• {word.word}" for word in words])
        return f"📋 Глобальные стоп-слова:\n{words_text}"

    @staticmethod
    def group_stop_words_list(words: list) -> str:
        if not words:
            return "📭 Стоп-слова для этой группы не настроены"

        words_text = "\n".join([f"• {word.word}" for word in words])
        return f"📋 Стоп-слова этой группы:\n{words_text}"