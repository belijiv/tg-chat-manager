from dataclasses import dataclass
from typing import List, Optional
import json


@dataclass
class GroupSettings:
    group_id: str
    group_name: str
    require_subscription: bool = True
    target_channels: List[str] = None
    slow_mode_delay: int = 15

    def __post_init__(self):
        if self.target_channels is None:
            self.target_channels = []

    def to_dict(self):
        return {
            "group_id": self.group_id,
            "group_name": self.group_name,
            "require_subscription": self.require_subscription,
            "target_channels": json.dumps(self.target_channels),
            "slow_mode_delay": self.slow_mode_delay,
        }

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return None
        return cls(
            group_id=data["group_id"],
            group_name=data["group_name"],
            require_subscription=bool(data["require_subscription"]),
            target_channels=json.loads(data["target_channels"]) if data["target_channels"] else [],
            slow_mode_delay=data["slow_mode_delay"],
        )