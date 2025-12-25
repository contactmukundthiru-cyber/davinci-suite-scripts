from dataclasses import dataclass
from typing import Any

from core.config import Config
from core.logging import get_logger
from core.reports import Report
from core.transactions import Transaction
from resolve.resolve_api import ResolveApp


@dataclass
class ToolContext:
    cfg: Config
    resolve: ResolveApp
    transaction: Transaction
    logger: Any


class BaseTool:
    tool_id = "base"
    title = "Base Tool"

    def __init__(self, ctx: ToolContext) -> None:
        self.ctx = ctx

    def run(self, options: dict[str, Any]) -> Report:
        raise NotImplementedError


def build_context(cfg: Config, dry_run: bool) -> ToolContext:
    resolve = ResolveApp(cfg)
    tx = Transaction(name="tool", dry_run=dry_run)
    logger = get_logger("tool", tool_id="generic", tx_id=tx.transaction_id)
    return ToolContext(cfg=cfg, resolve=resolve, transaction=tx, logger=logger)
