import asyncio
from datetime import datetime, timedelta
from typing import Union


class Helpers:
    @staticmethod
    async def delete_message_after(message, delay: int):
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except Exception:
            pass

    @staticmethod
    def parse_time_string(time_str: str) -> int:
        multipliers = {
            's': 1, 'sec': 1, 'сек': 1,
            'm': 60, 'min': 60, 'мин': 60,
            'h': 3600, 'hour': 3600, 'ч': 3600
        }

        if time_str.isdigit():
            return int(time_str)

        for unit, multiplier in multipliers.items():
            if time_str.endswith(unit):
                num = time_str[:-len(unit)]
                if num.isdigit():
                    return int(num) * multiplier

        return 60

    @staticmethod
    def extract_username(user) -> str:
        if user.username:
            return f"@{user.username}"
        elif user.first_name:
            return user.first_name
        else:
            return "Пользователь"

    @staticmethod
    def format_time_delta(seconds: int) -> str:
        if seconds < 60:
            return f"{seconds} сек"
        elif seconds < 3600:
            return f"{seconds // 60} мин"
        else:
            return f"{seconds // 3600} ч"

    @staticmethod
    def get_current_time() -> str:
        return datetime.now().isoformat()

    @staticmethod
    def is_time_passed(last_time: str, delay: int) -> bool:
        if not last_time:
            return True
        last = datetime.fromisoformat(last_time)
        now = datetime.now()
        return (now - last).total_seconds() >= delay