from dataclasses import dataclass
from typing import List


@dataclass
class Config:
    BOT_TOKEN: str = ""
    ADMIN_IDS: List[int] = None

    def __post_init__(self):
        if self.ADMIN_IDS is None:
            self.ADMIN_IDS = [5365397216]


config = Config()