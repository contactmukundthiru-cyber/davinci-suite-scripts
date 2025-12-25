import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class Transaction:
    name: str
    dry_run: bool
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    actions: list[dict[str, Any]] = field(default_factory=list)
    rollback: list[dict[str, Any]] = field(default_factory=list)

    def record(self, action: dict[str, Any]) -> None:
        self.actions.append(action)

    def record_rollback(self, rollback_action: dict[str, Any]) -> None:
        self.rollback.append(rollback_action)


class TransactionManager:
    def __init__(self) -> None:
        self.active: Optional[Transaction] = None

    def begin(self, name: str, dry_run: bool) -> Transaction:
        self.active = Transaction(name=name, dry_run=dry_run)
        return self.active

    def end(self) -> Optional[Transaction]:
        tx = self.active
        self.active = None
        return tx
