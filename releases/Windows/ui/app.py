import json
import sys
from pathlib import Path
from typing import Any, Optional

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except Exception as exc:  # pragma: no cover
    raise SystemExit("PySide6 is required for the UI. Install with: pip install PySide6") from exc

from core.config import get_config, ensure_dirs
from core.logging import setup_logging, get_logger
from core.presets import list_presets, load_preset, save_preset
from resolve.resolve_api import ResolveApp, ResolveConnectionError
from tools.base import build_context
from tools.registry import TOOL_REGISTRY
from tools.utils import now_stamp


# Tool metadata with descriptions
TOOL_INFO = {
    "t1_revision_resolver": {
        "name": "Revision Resolver",
        "icon": "1",
        "desc": "Replace old assets with new revisions across all timelines while preserving clip transforms and effects.",
        "use_case": "Client sends updated logo - replace it across 50+ timelines instantly."
    },
    "t2_relink_across_projects": {
        "name": "Relink Across Projects",
        "icon": "2",
        "desc": "Apply asset replacements across multiple projects simultaneously with rollback support.",
        "use_case": "Agency rebrand - update assets across all client projects at once."
    },
    "t3_smart_reframer": {
        "name": "Smart Reframer",
        "icon": "3",
        "desc": "Convert horizontal content to vertical or square formats with intelligent face/saliency detection.",
        "use_case": "Create 9:16 TikTok/Reels versions from your 16:9 master edit."
    },
    "t4_caption_layout_protector": {
        "name": "Caption Layout Protector",
        "icon": "4",
        "desc": "Validate captions are in safe zones and don't overlap with graphics or lower thirds.",
        "use_case": "Ensure broadcast compliance and accessibility for burned-in captions."
    },
    "t5_feedback_compiler": {
        "name": "Feedback Compiler",
        "icon": "5",
        "desc": "Convert client feedback notes into timeline markers and actionable task lists.",
        "use_case": "Parse client email feedback into markers with timecodes automatically."
    },
    "t6_timeline_normalizer": {
        "name": "Timeline Normalizer",
        "icon": "6",
        "desc": "Check FPS, resolution, disabled clips, and duplicate names for clean project handoff.",
        "use_case": "Pre-delivery QC before sending to colorist or sound editor."
    },
    "t7_component_graphics": {
        "name": "Component Graphics",
        "icon": "7",
        "desc": "Manage reusable graphics with a registry system for consistent usage across projects.",
        "use_case": "Maintain a library of brand-approved lower thirds and graphics."
    },
    "t8_delivery_spec_enforcer": {
        "name": "Delivery Spec Enforcer",
        "icon": "8",
        "desc": "Validate render settings against YouTube, Vimeo, broadcast, and custom platform specs.",
        "use_case": "Pre-render validation to ensure deliverables meet platform requirements."
    },
    "t9_change_impact_analyzer": {
        "name": "Change Impact Analyzer",
        "icon": "9",
        "desc": "Compare two timeline versions to identify added, removed, and modified clips.",
        "use_case": "Review changes between v1 and v2 of an edit for client approval."
    },
    "t10_brand_drift_detector": {
        "name": "Brand Drift Detector",
        "icon": "10",
        "desc": "Audit projects for brand guideline compliance including colors, fonts, and logos.",
        "use_case": "Agency brand compliance review before delivery."
    },
}


# Professional dark theme (GitHub-inspired)
STYLESHEET = """
* {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;
}

QMainWindow, QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
}

QLabel#appTitle {
    color: #58a6ff;
    font-size: 22px;
    font-weight: 600;
}

QLabel#appSubtitle {
    color: #8b949e;
    font-size: 12px;
}

QFrame#card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
}

QLabel#sectionHeader {
    color: #f0f6fc;
    font-size: 14px;
    font-weight: 600;
    padding: 8px 0;
}

QLabel#cardTitle {
    color: #f0f6fc;
    font-size: 15px;
    font-weight: 600;
}

QFrame#statusBar {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
}

QPushButton {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #c9d1d9;
    font-weight: 500;
    padding: 8px 16px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
}

QPushButton:pressed {
    background-color: #161b22;
}

QPushButton:disabled {
    background-color: #161b22;
    color: #484f58;
    border-color: #21262d;
}

QPushButton#primaryBtn {
    background-color: #238636;
    border-color: #2ea043;
    color: #ffffff;
    font-size: 14px;
    font-weight: 600;
}

QPushButton#primaryBtn:hover {
    background-color: #2ea043;
    border-color: #3fb950;
}

QPushButton#blueBtn {
    background-color: #1f6feb;
    border-color: #388bfd;
    color: #ffffff;
}

QPushButton#blueBtn:hover {
    background-color: #388bfd;
}

QListWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    outline: none;
    padding: 4px;
}

QListWidget::item {
    background-color: #161b22;
    border: 1px solid transparent;
    border-radius: 6px;
    color: #c9d1d9;
    margin: 3px 2px;
    padding: 12px 16px;
}

QListWidget::item:selected {
    background-color: #1f6feb;
    border-color: #388bfd;
    color: #ffffff;
}

QListWidget::item:hover:!selected {
    background-color: #21262d;
    border-color: #30363d;
}

QLineEdit, QPlainTextEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #c9d1d9;
    padding: 8px 12px;
    selection-background-color: #1f6feb;
}

QLineEdit:focus, QPlainTextEdit:focus {
    border-color: #1f6feb;
}

QPlainTextEdit {
    font-family: "SF Mono", "Fira Code", "Consolas", monospace;
    font-size: 12px;
}

QComboBox {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #c9d1d9;
    padding: 8px 12px;
    min-width: 150px;
}

QComboBox:hover {
    border-color: #8b949e;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #8b949e;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #161b22;
    border: 1px solid #30363d;
    selection-background-color: #1f6feb;
    outline: none;
}

QCheckBox {
    color: #c9d1d9;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #30363d;
    border-radius: 4px;
    background-color: #0d1117;
}

QCheckBox::indicator:checked {
    background-color: #1f6feb;
    border-color: #388bfd;
}

QTabWidget::pane {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 0 0 8px 8px;
    border-top: none;
}

QTabBar::tab {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    color: #8b949e;
    padding: 10px 20px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #161b22;
    color: #f0f6fc;
}

QTabBar::tab:hover:!selected {
    background-color: #21262d;
}

QTableWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    gridline-color: #21262d;
    outline: none;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #21262d;
}

QTableWidget::item:selected {
    background-color: #1f6feb;
}

QHeaderView::section {
    background-color: #161b22;
    border: none;
    border-bottom: 1px solid #30363d;
    color: #8b949e;
    font-weight: 600;
    padding: 10px 8px;
}

QSplitter::handle {
    background-color: #30363d;
    width: 1px;
}

QScrollBar:vertical {
    background-color: #0d1117;
    border: none;
    width: 10px;
}

QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 5px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #484f58;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #0d1117;
    border: none;
    height: 10px;
}

QScrollBar::handle:horizontal {
    background-color: #30363d;
    border-radius: 5px;
    min-width: 30px;
    margin: 2px;
}

QMessageBox {
    background-color: #161b22;
}

QMessageBox QLabel {
    color: #c9d1d9;
}

QMessageBox QPushButton {
    min-width: 80px;
}

QToolTip {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #c9d1d9;
    padding: 8px;
}
"""


class ToolCard(QtWidgets.QFrame):
    """Card showing selected tool info."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet("QFrame#card { padding: 16px; }")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header with number badge and title
        header = QtWidgets.QHBoxLayout()

        self.badge = QtWidgets.QLabel()
        self.badge.setFixedSize(32, 32)
        self.badge.setAlignment(QtCore.Qt.AlignCenter)
        self.badge.setStyleSheet("""
            background-color: #1f6feb;
            color: white;
            font-weight: bold;
            font-size: 14px;
            border-radius: 6px;
        """)

        self.title = QtWidgets.QLabel()
        self.title.setObjectName("cardTitle")

        header.addWidget(self.badge)
        header.addSpacing(12)
        header.addWidget(self.title, 1)

        # Description
        self.desc = QtWidgets.QLabel()
        self.desc.setWordWrap(True)
        self.desc.setStyleSheet("color: #8b949e; font-size: 13px; line-height: 1.5;")

        # Use case example
        self.example = QtWidgets.QLabel()
        self.example.setWordWrap(True)
        self.example.setStyleSheet("""
            color: #58a6ff;
            font-size: 12px;
            background-color: #0d1117;
            padding: 10px 12px;
            border-radius: 6px;
            border-left: 3px solid #1f6feb;
        """)

        layout.addLayout(header)
        layout.addWidget(self.desc)
        layout.addWidget(self.example)

    def set_tool(self, tool_id: str):
        info = TOOL_INFO.get(tool_id, {})
        self.badge.setText(info.get("icon", "?"))
        self.title.setText(info.get("name", tool_id))
        self.desc.setText(info.get("desc", ""))
        self.example.setText(f"Example: {info.get('use_case', '')}")


class StatusBar(QtWidgets.QFrame):
    """Connection status indicator."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusBar")
        self.setFixedHeight(44)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)

        self.dot = QtWidgets.QLabel()
        self.dot.setFixedSize(10, 10)

        self.text = QtWidgets.QLabel()

        layout.addWidget(self.dot)
        layout.addSpacing(8)
        layout.addWidget(self.text)
        layout.addStretch()

        self.set_status("disconnected")

    def set_status(self, status: str, message: str = None):
        if status == "connected":
            self.dot.setStyleSheet("background-color: #3fb950; border-radius: 5px;")
            self.text.setText(message or "Connected to DaVinci Resolve")
            self.text.setStyleSheet("color: #3fb950; font-weight: 600;")
        elif status == "connecting":
            self.dot.setStyleSheet("background-color: #d29922; border-radius: 5px;")
            self.text.setText(message or "Connecting...")
            self.text.setStyleSheet("color: #d29922; font-weight: 600;")
        else:
            self.dot.setStyleSheet("background-color: #484f58; border-radius: 5px;")
            self.text.setText(message or "Not connected - Open Resolve and click Connect")
            self.text.setStyleSheet("color: #8b949e;")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Resolve Production Suite")
        self.resize(1400, 900)
        self.setMinimumSize(1000, 700)

        self.cfg = get_config()
        ensure_dirs(self.cfg)
        setup_logging(self.cfg)
        self.logger = get_logger("ui")
        self.resolve_app: Optional[ResolveApp] = None
        self.report_items: list[dict[str, Any]] = []

        self._setup_ui()
        self.setStyleSheet(STYLESHEET)

        QtCore.QTimer.singleShot(500, self._auto_connect)

    def _setup_ui(self) -> None:
        central = QtWidgets.QWidget()
        main = QtWidgets.QVBoxLayout(central)
        main.setSpacing(16)
        main.setContentsMargins(24, 20, 24, 20)

        # Header
        header = QtWidgets.QHBoxLayout()

        title_block = QtWidgets.QVBoxLayout()
        title_block.setSpacing(2)
        title = QtWidgets.QLabel("Resolve Production Suite")
        title.setObjectName("appTitle")
        subtitle = QtWidgets.QLabel("10 Workflow Automation Tools for DaVinci Resolve")
        subtitle.setObjectName("appSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        self.connect_btn = QtWidgets.QPushButton("Connect to Resolve")
        self.connect_btn.setObjectName("blueBtn")
        self.connect_btn.clicked.connect(self._connect_resolve)
        self.connect_btn.setFixedHeight(36)

        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh_projects)
        self.refresh_btn.setFixedHeight(36)

        header.addLayout(title_block)
        header.addStretch()
        header.addWidget(self.connect_btn)
        header.addSpacing(8)
        header.addWidget(self.refresh_btn)

        # Status bar
        self.status_bar = StatusBar()

        # Project/Timeline bar
        proj_frame = QtWidgets.QFrame()
        proj_frame.setObjectName("card")
        proj_layout = QtWidgets.QHBoxLayout(proj_frame)
        proj_layout.setContentsMargins(16, 12, 16, 12)
        proj_layout.setSpacing(16)

        proj_label = QtWidgets.QLabel("Project:")
        proj_label.setStyleSheet("font-weight: 600;")
        self.project_combo = QtWidgets.QComboBox()
        self.project_combo.setMinimumWidth(200)
        self.project_combo.currentTextChanged.connect(self._project_changed)

        tl_label = QtWidgets.QLabel("Timeline:")
        tl_label.setStyleSheet("font-weight: 600;")
        self.timeline_combo = QtWidgets.QComboBox()
        self.timeline_combo.setMinimumWidth(200)
        self.timeline_combo.currentTextChanged.connect(self._timeline_changed)

        self.dry_run_check = QtWidgets.QCheckBox("Dry Run (preview only)")
        self.dry_run_check.setChecked(True)
        self.dry_run_check.setToolTip("Preview changes without modifying your project")

        proj_layout.addWidget(proj_label)
        proj_layout.addWidget(self.project_combo)
        proj_layout.addSpacing(20)
        proj_layout.addWidget(tl_label)
        proj_layout.addWidget(self.timeline_combo)
        proj_layout.addStretch()
        proj_layout.addWidget(self.dry_run_check)

        # Main content
        content = QtWidgets.QHBoxLayout()
        content.setSpacing(20)

        # Left: Tool list
        left = QtWidgets.QVBoxLayout()
        left.setSpacing(12)

        tools_lbl = QtWidgets.QLabel("Select a Tool")
        tools_lbl.setObjectName("sectionHeader")

        self.tool_list = QtWidgets.QListWidget()
        self.tool_list.setMinimumWidth(280)
        self.tool_list.setMaximumWidth(320)

        for tool_id in TOOL_REGISTRY.keys():
            info = TOOL_INFO.get(tool_id, {})
            text = f"  {info.get('icon', '?')}.  {info.get('name', tool_id)}"
            item = QtWidgets.QListWidgetItem(text)
            item.setData(QtCore.Qt.UserRole, tool_id)
            self.tool_list.addItem(item)

        self.tool_list.setCurrentRow(0)
        self.tool_list.currentItemChanged.connect(self._tool_changed)

        left.addWidget(tools_lbl)
        left.addWidget(self.tool_list, 1)

        # Right: Details
        right = QtWidgets.QVBoxLayout()
        right.setSpacing(16)

        self.tool_card = ToolCard()

        # Options section
        opts_lbl = QtWidgets.QLabel("Tool Options")
        opts_lbl.setObjectName("sectionHeader")

        opts_frame = QtWidgets.QFrame()
        opts_frame.setObjectName("card")
        opts_layout = QtWidgets.QVBoxLayout(opts_frame)
        opts_layout.setContentsMargins(16, 16, 16, 16)
        opts_layout.setSpacing(12)

        preset_row = QtWidgets.QHBoxLayout()
        preset_lbl = QtWidgets.QLabel("Preset:")
        self.preset_combo = QtWidgets.QComboBox()
        self.preset_combo.setMinimumWidth(150)
        self.preset_name = QtWidgets.QLineEdit()
        self.preset_name.setPlaceholderText("New preset name...")
        self.preset_name.setMaximumWidth(150)
        self.load_btn = QtWidgets.QPushButton("Load")
        self.load_btn.clicked.connect(self._load_preset)
        self.save_btn = QtWidgets.QPushButton("Save")
        self.save_btn.clicked.connect(self._save_preset)

        preset_row.addWidget(preset_lbl)
        preset_row.addWidget(self.preset_combo)
        preset_row.addWidget(self.preset_name)
        preset_row.addWidget(self.load_btn)
        preset_row.addWidget(self.save_btn)
        preset_row.addStretch()

        json_lbl = QtWidgets.QLabel("Options (JSON):")
        json_lbl.setStyleSheet("color: #8b949e; font-size: 12px;")

        self.options_edit = QtWidgets.QPlainTextEdit()
        self.options_edit.setPlaceholderText('{\n  "option": "value"\n}')
        self.options_edit.setMaximumHeight(100)

        opts_layout.addLayout(preset_row)
        opts_layout.addWidget(json_lbl)
        opts_layout.addWidget(self.options_edit)

        # Run button row
        run_row = QtWidgets.QHBoxLayout()
        self.run_btn = QtWidgets.QPushButton("Run Tool")
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.clicked.connect(self._run_tool)
        self.run_btn.setFixedHeight(44)
        self.run_btn.setMinimumWidth(140)

        self.open_btn = QtWidgets.QPushButton("Open Report...")
        self.open_btn.clicked.connect(self._open_report)

        run_row.addWidget(self.run_btn)
        run_row.addWidget(self.open_btn)
        run_row.addStretch()

        # Results
        res_lbl = QtWidgets.QLabel("Results")
        res_lbl.setObjectName("sectionHeader")

        self.tabs = QtWidgets.QTabWidget()

        self.summary = QtWidgets.QPlainTextEdit()
        self.summary.setReadOnly(True)
        self.summary.setPlaceholderText(
            "Run a tool to see results here...\n\n"
            "Tip: Enable 'Dry Run' to preview changes without modifying your project."
        )

        items_w = QtWidgets.QWidget()
        items_l = QtWidgets.QVBoxLayout(items_w)
        items_l.setContentsMargins(8, 8, 8, 8)

        filt_row = QtWidgets.QHBoxLayout()
        filt_lbl = QtWidgets.QLabel("Filter:")
        self.filter_combo = QtWidgets.QComboBox()
        self.filter_combo.addItems(["All", "info", "warning", "error"])
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
        filt_row.addWidget(filt_lbl)
        filt_row.addWidget(self.filter_combo)
        filt_row.addStretch()

        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Severity", "Category", "Message", "Timeline", "Timecode"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        items_l.addLayout(filt_row)
        items_l.addWidget(self.table)

        self.tabs.addTab(self.summary, "Summary")
        self.tabs.addTab(items_w, "Details")

        right.addWidget(self.tool_card)
        right.addWidget(opts_lbl)
        right.addWidget(opts_frame)
        right.addLayout(run_row)
        right.addWidget(res_lbl)
        right.addWidget(self.tabs, 1)

        content.addLayout(left)
        content.addLayout(right, 1)

        main.addLayout(header)
        main.addWidget(self.status_bar)
        main.addWidget(proj_frame)
        main.addLayout(content, 1)

        self.setCentralWidget(central)
        self._update_tool_card()
        self._refresh_presets()

    def _update_tool_card(self):
        tool_id = self._get_tool_id()
        if tool_id:
            self.tool_card.set_tool(tool_id)

    def _auto_connect(self):
        self.status_bar.set_status("connecting", "Looking for DaVinci Resolve...")
        QtWidgets.QApplication.processEvents()

        self.resolve_app = ResolveApp(self.cfg)
        try:
            self.resolve_app.connect()
            self.status_bar.set_status("connected")
            self.connect_btn.setText("Reconnect")
            self._refresh_projects()
        except ResolveConnectionError:
            self.status_bar.set_status("disconnected")
            self.resolve_app = None

    def _connect_resolve(self):
        self.status_bar.set_status("connecting", "Connecting...")
        self.connect_btn.setEnabled(False)
        QtWidgets.QApplication.processEvents()

        self.resolve_app = ResolveApp(self.cfg)
        try:
            self.resolve_app.connect()
            self.status_bar.set_status("connected")
            self.connect_btn.setText("Reconnect")
            self._refresh_projects()
            self._show_info("Connected!", "Successfully connected to DaVinci Resolve.")
        except ResolveConnectionError as e:
            self.status_bar.set_status("disconnected", "Connection failed")
            self.resolve_app = None
            self._show_error("Connection Failed", str(e))
        finally:
            self.connect_btn.setEnabled(True)

    def _show_error(self, title: str, msg: str):
        box = QtWidgets.QMessageBox(self)
        box.setIcon(QtWidgets.QMessageBox.Critical)
        box.setWindowTitle(title)
        box.setText(msg)
        box.exec()

    def _show_info(self, title: str, msg: str):
        box = QtWidgets.QMessageBox(self)
        box.setIcon(QtWidgets.QMessageBox.Information)
        box.setWindowTitle(title)
        box.setText(msg)
        box.exec()

    def _refresh_projects(self):
        if not self.resolve_app:
            return
        projs = self.resolve_app.list_projects()
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        self.project_combo.addItems(projs if projs else ["(No projects)"])
        self.project_combo.blockSignals(False)
        self._refresh_timelines()

    def _refresh_timelines(self):
        if not self.resolve_app:
            return
        self.resolve_app.refresh()
        tls = self.resolve_app.list_timeline_names()
        self.timeline_combo.blockSignals(True)
        self.timeline_combo.clear()
        self.timeline_combo.addItems(tls if tls else ["(No timelines)"])
        self.timeline_combo.blockSignals(False)

    def _project_changed(self, name: str):
        if not self.resolve_app or not name or name.startswith("("):
            return
        self.resolve_app.load_project(name)
        self._refresh_timelines()

    def _timeline_changed(self, name: str):
        if not self.resolve_app or not name or name.startswith("("):
            return
        tl = self.resolve_app.find_timeline(name)
        if tl:
            self.resolve_app.set_current_timeline(tl)

    def _tool_changed(self, cur, prev):
        self._update_tool_card()
        self._refresh_presets()

    def _get_tool_id(self) -> str:
        item = self.tool_list.currentItem()
        return item.data(QtCore.Qt.UserRole) if item else ""

    def _refresh_presets(self):
        tid = self._get_tool_id()
        if not tid:
            return
        ps = list_presets(self.cfg, tid)
        self.preset_combo.clear()
        self.preset_combo.addItems(ps if ps else ["(No presets)"])

    def _save_preset(self):
        tid = self._get_tool_id()
        name = self.preset_name.text().strip()
        if not name:
            self._show_error("Name Required", "Enter a preset name.")
            return
        opts = self._parse_opts()
        if opts is None:
            return
        try:
            save_preset(self.cfg, tid, name, opts)
            self._show_info("Saved", f"Preset '{name}' saved.")
            self._refresh_presets()
            self.preset_name.clear()
        except Exception as e:
            self._show_error("Save Failed", str(e))

    def _load_preset(self):
        tid = self._get_tool_id()
        name = self.preset_combo.currentText()
        if not name or name.startswith("("):
            return
        try:
            opts = load_preset(self.cfg, tid, name)
            self.options_edit.setPlainText(json.dumps(opts, indent=2))
        except Exception as e:
            self._show_error("Load Failed", str(e))

    def _parse_opts(self) -> Optional[dict]:
        txt = self.options_edit.toPlainText().strip()
        if not txt:
            return {}
        try:
            return json.loads(txt)
        except json.JSONDecodeError as e:
            self._show_error("Invalid JSON", f"JSON error:\n{e}")
            return None

    def _run_tool(self):
        tid = self._get_tool_id()
        if not tid:
            return

        if not self.resolve_app:
            self._show_error("Not Connected",
                "Please connect first.\n\n1. Open DaVinci Resolve\n2. Click 'Connect to Resolve'")
            return

        opts = self._parse_opts()
        if opts is None:
            return

        self.run_btn.setEnabled(False)
        self.run_btn.setText("Running...")
        QtWidgets.QApplication.processEvents()

        try:
            ctx = build_context(self.cfg, dry_run=self.dry_run_check.isChecked())
            ctx.resolve = self.resolve_app
            tool = TOOL_REGISTRY[tid](ctx)

            try:
                report = tool.run(opts)
            except ResolveConnectionError as e:
                self._show_error("Resolve Error", str(e))
                return
            except Exception as e:
                self._show_error("Tool Error", f"Error:\n{e}")
                return

            out = self.cfg.reports_dir
            out.mkdir(parents=True, exist_ok=True)
            base = f"{tid}_{now_stamp()}"
            try:
                report.to_json(out / f"{base}.json")
                report.to_csv(out / f"{base}.csv")
                report.to_html(out / f"{base}.html")
            except Exception as e:
                self._show_error("Save Error", str(e))

            self._set_report(report)
            mode = "DRY RUN" if self.dry_run_check.isChecked() else "COMPLETED"
            self._show_info(f"Tool {mode}", f"Done! Reports saved to:\n{out}")

        finally:
            self.run_btn.setEnabled(True)
            self.run_btn.setText("Run Tool")

    def _open_report(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Report", str(self.cfg.reports_dir), "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.summary.setPlainText(json.dumps(data.get("summary", {}), indent=2))
            self.report_items = data.get("items", [])
            self._apply_filter(self.filter_combo.currentText())
        except Exception as e:
            self._show_error("Open Failed", str(e))

    def _set_report(self, report):
        self.summary.setPlainText(json.dumps(report.summary, indent=2))
        self.report_items = [i.__dict__ for i in report.items]
        self._apply_filter(self.filter_combo.currentText())

    def _apply_filter(self, sev: str):
        items = self.report_items
        if sev != "All":
            items = [i for i in items if i.get("severity") == sev]
        self.table.setRowCount(len(items))
        for r, i in enumerate(items):
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(i.get("severity", "")))
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(i.get("category", "")))
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(i.get("message", "")))
            self.table.setItem(r, 3, QtWidgets.QTableWidgetItem(i.get("timeline", "")))
            self.table.setItem(r, 4, QtWidgets.QTableWidgetItem(i.get("timecode", "")))


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
