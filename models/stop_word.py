from dataclasses import dataclass
from typing import Optional


@dataclass
class StopWord:
    word: str
    is_global: bool = True
    group_id: Optional[str] = None

    def to_dict(self):
        return {
            'word': self.word.lower(),
            'is_global': self.is_global,
            'group_id': self.group_id
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None

        return cls(
            word=data['word'],
            is_global=bool(data['is_global']),
            group_id=data['group_id']
        )
