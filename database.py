# database.py
import sqlite3
from typing import List, Optional
from models import GroupSettings, UserViolation, UserMessage, StopWord
from datetime import datetime


class Database:
    def __init__(self, db_path="bot.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица настроек групп
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups
            (
                group_id TEXT PRIMARY KEY,
                group_name TEXT,
                require_subscription BOOLEAN DEFAULT 1,
                target_channels TEXT DEFAULT '[]',
                slow_mode_delay INTEGER DEFAULT 15
            )
        ''')

        # Таблица стоп-слов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stop_words
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                is_global BOOLEAN DEFAULT 0,
                group_id TEXT
            )
        ''')

        # Таблица нарушений пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_violations
            (
                user_id INTEGER,
                group_id TEXT,
                username TEXT,
                first_name TEXT,
                banned BOOLEAN DEFAULT 0,
                violations_count INTEGER DEFAULT 0,
                last_violation_time TEXT,
                PRIMARY KEY (user_id, group_id)
            )
        ''')

        # Таблица времени сообщений для медленного режима
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_messages
            (
                user_id INTEGER,
                group_id TEXT,
                last_message_time TEXT,
                PRIMARY KEY (user_id, group_id)
            )
        ''')

        # Таблица пользователей для поиска по username
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users
            (
                user_id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                first_name TEXT,
                last_name TEXT,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    # === Методы для групп ===
    def get_group(self, group_id: str) -> Optional[GroupSettings]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM groups WHERE group_id = ?', (group_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return GroupSettings.from_dict({
                'group_id': result[0],
                'group_name': result[1],
                'require_subscription': result[2],
                'target_channels': result[3],
                'slow_mode_delay': result[4]
            })
        return None

    def save_group(self, group: GroupSettings):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        data = group.to_dict()
        cursor.execute('''
            INSERT OR REPLACE INTO groups 
            (group_id, group_name, require_subscription, target_channels, slow_mode_delay)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['group_id'], data['group_name'], data['require_subscription'],
              data['target_channels'], data['slow_mode_delay']))

        conn.commit()
        conn.close()

    def update_group_settings(self, group_id: str, **kwargs):
        group = self.get_group(group_id)
        if not group:
            return

        for key, value in kwargs.items():
            if hasattr(group, key):
                setattr(group, key, value)

        self.save_group(group)

    # === Методы для стоп-слов ===
    def get_stop_words(self, group_id: str = None) -> List[StopWord]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if group_id:
            cursor.execute('''
                SELECT word, is_global, group_id
                FROM stop_words
                WHERE is_global = 1 OR group_id = ?
            ''', (group_id,))
        else:
            cursor.execute('SELECT word, is_global, group_id FROM stop_words WHERE is_global = 1')

        words = []
        for row in cursor.fetchall():
            words.append(StopWord.from_dict({
                'word': row[0],
                'is_global': row[1],
                'group_id': row[2]
            }))

        conn.close()
        return words

    def add_stop_word(self, stop_word: StopWord):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        data = stop_word.to_dict()
        cursor.execute('''
            INSERT OR IGNORE INTO stop_words (word, is_global, group_id)
            VALUES (?, ?, ?)
        ''', (data['word'], data['is_global'], data['group_id']))

        conn.commit()
        conn.close()

    def remove_stop_word(self, word: str, group_id: str = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if group_id:
            cursor.execute('DELETE FROM stop_words WHERE word = ? AND group_id = ?', (word.lower(), group_id))
        else:
            cursor.execute('DELETE FROM stop_words WHERE word = ? AND is_global = 1', (word.lower(),))

        conn.commit()
        conn.close()

    def get_global_stop_words(self) -> List[StopWord]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT word, is_global, group_id FROM stop_words WHERE is_global = 1')

        words = []
        for row in cursor.fetchall():
            words.append(StopWord.from_dict({
                'word': row[0],
                'is_global': row[1],
                'group_id': row[2]
            }))

        conn.close()
        return words

    def get_group_stop_words(self, group_id: str) -> List[StopWord]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT word, is_global, group_id FROM stop_words WHERE group_id = ?', (group_id,))

        words = []
        for row in cursor.fetchall():
            words.append(StopWord.from_dict({
                'word': row[0],
                'is_global': row[1],
                'group_id': row[2]
            }))

        conn.close()
        return words

    # === Методы для нарушений и банов ===
    def get_user_violations(self, user_id: int, group_id: str) -> Optional[UserViolation]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_violations WHERE user_id = ? AND group_id = ?', (user_id, group_id))
        result = cursor.fetchone()
        conn.close()

        if result:
            return UserViolation.from_dict({
                'user_id': result[0],
                'group_id': result[1],
                'username': result[2],
                'first_name': result[3],
                'banned': result[4],
                'violations_count': result[5],
                'last_violation_time': result[6]
            })
        return None

    def save_user_violations(self, violation: UserViolation):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        data = violation.to_dict()
        cursor.execute('''
            INSERT OR REPLACE INTO user_violations 
            (user_id, group_id, username, first_name, banned, violations_count, last_violation_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['user_id'], data['group_id'], data['username'],
            data['first_name'], data['banned'], data['violations_count'],
            data['last_violation_time']
        ))

        conn.commit()
        conn.close()

    def ban_user(self, user_id: int, group_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        violations = self.get_user_violations(user_id, group_id)
        if violations:
            cursor.execute('UPDATE user_violations SET banned = 1 WHERE user_id = ? AND group_id = ?', 
                         (user_id, group_id))
        else:
            cursor.execute('INSERT INTO user_violations (user_id, group_id, banned, violations_count) VALUES (?, ?, 1, 0)', 
                         (user_id, group_id))

        conn.commit()
        conn.close()

    def unban_user(self, user_id: int, group_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE user_violations SET banned = 0 WHERE user_id = ? AND group_id = ?', 
                     (user_id, group_id))
        conn.commit()
        conn.close()

    def reset_violations(self, user_id: int, group_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_violations WHERE user_id = ? AND group_id = ?', (user_id, group_id))
        conn.commit()
        conn.close()

    def get_user_banned(self, user_id: int, group_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT banned FROM user_violations WHERE user_id = ? AND group_id = ? AND banned = 1', 
                     (user_id, group_id))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    # === Методы для медленного режима ===
    def get_user_message_time(self, user_id: int, group_id: str) -> Optional[UserMessage]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_messages WHERE user_id = ? AND group_id = ?', (user_id, group_id))
        result = cursor.fetchone()
        conn.close()

        if result:
            return UserMessage.from_dict({
                'user_id': result[0],
                'group_id': result[1],
                'last_message_time': result[2]
            })
        return None

    def save_user_message_time(self, user_message: UserMessage):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        data = user_message.to_dict()
        cursor.execute('''
            INSERT OR REPLACE INTO user_messages 
            (user_id, group_id, last_message_time) VALUES (?, ?, ?)
        ''', (data['user_id'], data['group_id'], data['last_message_time']))

        conn.commit()
        conn.close()

    # === Методы для пользователей ===
    def save_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        conn.commit()
        conn.close()

    def get_user_by_username(self, username: str) -> Optional[dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'user_id': result[0],
                'username': result[1],
                'first_name': result[2],
                'last_name': result[3]
            }
        return None

    # === Методы для каналов подписки ===
    def add_target_channel(self, group_id: str, channel: str):
        group = self.get_group(group_id)
        if not group:
            return

        if channel not in group.target_channels:
            group.target_channels.append(channel)
            self.save_group(group)

    def remove_target_channel(self, group_id: str, channel: str):
        group = self.get_group(group_id)
        if not group:
            return

        if channel in group.target_channels:
            group.target_channels.remove(channel)
            self.save_group(group)