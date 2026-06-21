from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ExecutionContext:
    connection: Any
    batch_id: str
    database_path: Path
    recovery_from_batch_id: str | None = None
    state: dict[str, Any] = field(default_factory=dict)

    def set_state(self, key: str, value: Any) -> Any:
        self.state[key] = value
        return value

    def get_state(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)
