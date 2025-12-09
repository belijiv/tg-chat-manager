from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserViolation:
    user_id: int
    group_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    banned: bool = False
    violations_count: int = 0
    last_violation_time: Optional[str] = None

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "group_id": self.group_id,
            "username": self.username,
            "first_name": self.first_name,
            "banned": self.banned,
            "violations_count": self.violations_count,
            "last_violation_time": self.last_violation_time,
        }

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        return cls(
            user_id=data["user_id"],
            group_id=data["group_id"],
            username=data["username"],
            first_name=data["first_name"],
            banned=data["banned"],
            violations_count=data["violations_count"],
            last_violation_time=data["last_violation_time"],
        )


@dataclass
class UserMessage:
    user_id: int
    group_id: str
    last_message_time: str

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'group_id': self.group_id,
            'last_message_time': self.last_message_time
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None

        return cls(
            user_id=data['user_id'],
            group_id=data['group_id'],
            last_message_time=data['last_message_time']
        )
