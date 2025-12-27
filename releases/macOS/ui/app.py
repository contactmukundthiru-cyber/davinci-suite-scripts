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


# Modern dark theme stylesheet
DARK_STYLESHEET = """
QMainWindow {
    background-color: #1e1e1e;
}
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 13px;
}
QLabel {
    color: #b0b0b0;
    font-weight: 500;
}
QLabel#title {
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
}
QLabel#status-connected {
    color: #4caf50;
    font-weight: bold;
}
QLabel#status-disconnected {
    color: #ff9800;
    font-weight: bold;
}
QLabel#status-error {
    color: #f44336;
    font-weight: bold;
}
QPushButton {
    background-color: #3a3a3a;
    border: 1px solid #555;
    border-radius: 6px;
    padding: 8px 16px;
    color: #ffffff;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #4a4a4a;
    border-color: #666;
}
QPushButton:pressed {
    background-color: #2a2a2a;
}
QPushButton:disabled {
    background-color: #2a2a2a;
    color: #666;
}
QPushButton#primary {
    background-color: #2196f3;
    border-color: #1976d2;
}
QPushButton#primary:hover {
    background-color: #42a5f5;
}
QPushButton#primary:pressed {
    background-color: #1976d2;
}
QPushButton#success {
    background-color: #4caf50;
    border-color: #388e3c;
}
QPushButton#success:hover {
    background-color: #66bb6a;
}
QComboBox {
    background-color: #2a2a2a;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 6px 12px;
    color: #ffffff;
    min-width: 120px;
}
QComboBox:hover {
    border-color: #666;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #2a2a2a;
    border: 1px solid #555;
    selection-background-color: #3a3a3a;
}
QLineEdit {
    background-color: #2a2a2a;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 6px 12px;
    color: #ffffff;
}
QLineEdit:focus {
    border-color: #2196f3;
}
QPlainTextEdit {
    background-color: #252525;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 8px;
    color: #e0e0e0;
    font-family: "Consolas", "Monaco", "Courier New", monospace;
    font-size: 12px;
}
QListWidget {
    background-color: #252525;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 4px;
    outline: none;
}
QListWidget::item {
    padding: 10px 12px;
    border-radius: 4px;
    margin: 2px;
}
QListWidget::item:selected {
    background-color: #2196f3;
    color: #ffffff;
}
QListWidget::item:hover:!selected {
    background-color: #333;
}
QTableWidget {
    background-color: #252525;
    border: 1px solid #444;
    border-radius: 4px;
    gridline-color: #3a3a3a;
}
QTableWidget::item {
    padding: 6px;
}
QTableWidget::item:selected {
    background-color: #2196f3;
}
QHeaderView::section {
    background-color: #2a2a2a;
    color: #b0b0b0;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #444;
    font-weight: bold;
}
QTabWidget::pane {
    border: 1px solid #444;
    border-radius: 4px;
    background-color: #252525;
}
QTabBar::tab {
    background-color: #2a2a2a;
    color: #b0b0b0;
    padding: 10px 20px;
    border: 1px solid #444;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background-color: #252525;
    color: #ffffff;
}
QTabBar::tab:hover:!selected {
    background-color: #333;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 1px solid #555;
    background-color: #2a2a2a;
}
QCheckBox::indicator:checked {
    background-color: #2196f3;
    border-color: #1976d2;
}
QSplitter::handle {
    background-color: #333;
    width: 2px;
}
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #444;
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover {
    background-color: #555;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QMessageBox {
    background-color: #1e1e1e;
}
QMessageBox QLabel {
    color: #e0e0e0;
}
"""


class StatusIndicator(QtWidgets.QWidget):
    """A visual status indicator with icon and text."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.icon = QtWidgets.QLabel("●")
        self.icon.setStyleSheet("font-size: 16px;")
        self.text = QtWidgets.QLabel("Not Connected")

        layout.addWidget(self.icon)
        layout.addWidget(self.text)
        layout.addStretch()

        self.set_status("disconnected")

    def set_status(self, status: str, message: str = None):
        if status == "connected":
            self.icon.setStyleSheet("font-size: 16px; color: #4caf50;")
            self.text.setText(message or "Connected to Resolve")
            self.text.setStyleSheet("color: #4caf50; font-weight: bold;")
        elif status == "connecting":
            self.icon.setStyleSheet("font-size: 16px; color: #ff9800;")
            self.text.setText(message or "Connecting...")
            self.text.setStyleSheet("color: #ff9800;")
        elif status == "error":
            self.icon.setStyleSheet("font-size: 16px; color: #f44336;")
            self.text.setText(message or "Connection Failed")
            self.text.setStyleSheet("color: #f44336;")
        else:  # disconnected
            self.icon.setStyleSheet("font-size: 16px; color: #666;")
            self.text.setText(message or "Not Connected")
            self.text.setStyleSheet("color: #888;")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Resolve Production Suite")
        self.resize(1280, 800)

        self.cfg = get_config()
        ensure_dirs(self.cfg)
        setup_logging(self.cfg)
        self.logger = get_logger("ui")
        self.resolve_app: Optional[ResolveApp] = None
        self.report_items: list[dict[str, Any]] = []

        self._setup_ui()
        self._apply_styling()

        # Try auto-connect after window is shown
        QtCore.QTimer.singleShot(500, self._auto_connect)

    def _setup_ui(self) -> None:
        central = QtWidgets.QWidget()
        root_layout = QtWidgets.QVBoxLayout(central)
        root_layout.setSpacing(16)
        root_layout.setContentsMargins(20, 20, 20, 20)

        # Header with title and connection controls
        header = QtWidgets.QHBoxLayout()

        title = QtWidgets.QLabel("Resolve Production Suite")
        title.setObjectName("title")

        self.status_indicator = StatusIndicator()

        self.connect_button = QtWidgets.QPushButton("Connect")
        self.connect_button.setObjectName("primary")
        self.connect_button.clicked.connect(self._connect_resolve)
        self.connect_button.setFixedWidth(100)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.status_indicator)
        header.addWidget(self.connect_button)

        # Project/Timeline selection bar
        project_bar = QtWidgets.QHBoxLayout()
        project_bar.setSpacing(12)

        project_label = QtWidgets.QLabel("Project:")
        self.project_combo = QtWidgets.QComboBox()
        self.project_combo.setMinimumWidth(200)
        self.project_combo.currentTextChanged.connect(self._project_changed)

        timeline_label = QtWidgets.QLabel("Timeline:")
        self.timeline_combo = QtWidgets.QComboBox()
        self.timeline_combo.setMinimumWidth(200)
        self.timeline_combo.currentTextChanged.connect(self._timeline_changed)

        self.refresh_button = QtWidgets.QPushButton("↻ Refresh")
        self.refresh_button.clicked.connect(self._refresh_projects)
        self.refresh_button.setFixedWidth(100)

        self.dry_run_check = QtWidgets.QCheckBox("Dry Run (Preview)")
        self.dry_run_check.setChecked(True)
        self.dry_run_check.setToolTip("Preview changes without modifying your project")

        project_bar.addWidget(project_label)
        project_bar.addWidget(self.project_combo)
        project_bar.addWidget(timeline_label)
        project_bar.addWidget(self.timeline_combo)
        project_bar.addWidget(self.refresh_button)
        project_bar.addStretch()
        project_bar.addWidget(self.dry_run_check)

        # Main content splitter
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # Tool list (left panel)
        tool_panel = QtWidgets.QWidget()
        tool_layout = QtWidgets.QVBoxLayout(tool_panel)
        tool_layout.setContentsMargins(0, 0, 0, 0)

        tool_header = QtWidgets.QLabel("Tools")
        tool_header.setStyleSheet("font-weight: bold; font-size: 14px; color: #fff; margin-bottom: 8px;")

        self.tool_list = QtWidgets.QListWidget()
        for tool_id in TOOL_REGISTRY.keys():
            # Format tool name nicely
            display_name = tool_id.replace("t", "").replace("_", " ").title()
            item = QtWidgets.QListWidgetItem(f"{display_name}")
            item.setData(QtCore.Qt.UserRole, tool_id)
            self.tool_list.addItem(item)
        self.tool_list.setCurrentRow(0)
        self.tool_list.currentItemChanged.connect(self._tool_changed)

        tool_layout.addWidget(tool_header)
        tool_layout.addWidget(self.tool_list)

        # Right panel
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # Presets row
        preset_row = QtWidgets.QHBoxLayout()
        preset_row.setSpacing(8)

        preset_label = QtWidgets.QLabel("Preset:")
        self.preset_combo = QtWidgets.QComboBox()
        self.preset_combo.setMinimumWidth(150)

        self.preset_name = QtWidgets.QLineEdit()
        self.preset_name.setPlaceholderText("New preset name...")
        self.preset_name.setFixedWidth(150)

        self.preset_load = QtWidgets.QPushButton("Load")
        self.preset_load.clicked.connect(self._load_preset)

        self.preset_save = QtWidgets.QPushButton("Save")
        self.preset_save.clicked.connect(self._save_preset)

        preset_row.addWidget(preset_label)
        preset_row.addWidget(self.preset_combo)
        preset_row.addWidget(self.preset_name)
        preset_row.addWidget(self.preset_load)
        preset_row.addWidget(self.preset_save)
        preset_row.addStretch()

        # Options editor
        options_label = QtWidgets.QLabel("Tool Options (JSON)")
        options_label.setStyleSheet("font-weight: bold; color: #fff;")

        self.options_edit = QtWidgets.QPlainTextEdit()
        self.options_edit.setPlaceholderText('{\n  "option": "value"\n}')
        self.options_edit.setMaximumHeight(150)

        # Run button row
        run_row = QtWidgets.QHBoxLayout()

        output_label = QtWidgets.QLabel("Reports folder:")
        self.output_path = QtWidgets.QLineEdit(str(self.cfg.reports_dir))
        self.output_path.setReadOnly(True)

        self.open_report_button = QtWidgets.QPushButton("Open Report...")
        self.open_report_button.clicked.connect(self._open_report)

        self.run_button = QtWidgets.QPushButton("▶ Run Tool")
        self.run_button.setObjectName("success")
        self.run_button.clicked.connect(self._run_tool)
        self.run_button.setFixedWidth(140)

        run_row.addWidget(output_label)
        run_row.addWidget(self.output_path, 1)
        run_row.addWidget(self.open_report_button)
        run_row.addWidget(self.run_button)

        # Report tabs
        self.report_tabs = QtWidgets.QTabWidget()

        self.summary_view = QtWidgets.QPlainTextEdit()
        self.summary_view.setReadOnly(True)
        self.summary_view.setPlaceholderText("Run a tool to see results here...")

        # Report items tab
        report_panel = QtWidgets.QWidget()
        report_layout = QtWidgets.QVBoxLayout(report_panel)
        report_layout.setContentsMargins(8, 8, 8, 8)

        filter_row = QtWidgets.QHBoxLayout()
        filter_label = QtWidgets.QLabel("Filter by severity:")
        self.filter_combo = QtWidgets.QComboBox()
        self.filter_combo.addItems(["All", "info", "warning", "error"])
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
        filter_row.addWidget(filter_label)
        filter_row.addWidget(self.filter_combo)
        filter_row.addStretch()

        self.report_table = QtWidgets.QTableWidget(0, 6)
        self.report_table.setHorizontalHeaderLabels([
            "Severity", "Category", "Message", "Timeline", "Clip", "Timecode"
        ])
        self.report_table.horizontalHeader().setStretchLastSection(True)
        self.report_table.setAlternatingRowColors(True)

        report_layout.addLayout(filter_row)
        report_layout.addWidget(self.report_table)

        self.report_tabs.addTab(self.summary_view, "Summary")
        self.report_tabs.addTab(report_panel, "Report Items")

        # Assemble right panel
        right_layout.addLayout(preset_row)
        right_layout.addWidget(options_label)
        right_layout.addWidget(self.options_edit)
        right_layout.addLayout(run_row)
        right_layout.addWidget(self.report_tabs, 1)

        # Add panels to splitter
        splitter.addWidget(tool_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([280, 800])

        # Assemble main layout
        root_layout.addLayout(header)
        root_layout.addLayout(project_bar)
        root_layout.addWidget(splitter, 1)

        self.setCentralWidget(central)
        self._refresh_presets()

    def _apply_styling(self) -> None:
        self.setStyleSheet(DARK_STYLESHEET)

    def _auto_connect(self) -> None:
        """Try to auto-connect to Resolve on startup."""
        self.status_indicator.set_status("connecting", "Looking for DaVinci Resolve...")
        QtWidgets.QApplication.processEvents()

        self.resolve_app = ResolveApp(self.cfg)
        try:
            self.resolve_app.connect()
            self.status_indicator.set_status("connected")
            self.connect_button.setText("Reconnect")
            self._refresh_projects()
        except ResolveConnectionError:
            self.status_indicator.set_status("disconnected", "Click Connect after opening Resolve")
            self.resolve_app = None

    def _connect_resolve(self) -> None:
        self.status_indicator.set_status("connecting", "Connecting to DaVinci Resolve...")
        self.connect_button.setEnabled(False)
        QtWidgets.QApplication.processEvents()

        self.resolve_app = ResolveApp(self.cfg)
        try:
            self.resolve_app.connect()
            self.status_indicator.set_status("connected")
            self.connect_button.setText("Reconnect")
            self._refresh_projects()
            self._show_info("Connected", "Successfully connected to DaVinci Resolve!")
        except ResolveConnectionError as exc:
            self.status_indicator.set_status("error", "Connection failed")
            self.resolve_app = None
            self._show_error("Connection Failed", str(exc))
        finally:
            self.connect_button.setEnabled(True)

    def _show_error(self, title: str, message: str) -> None:
        """Show a styled error dialog."""
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

    def _show_info(self, title: str, message: str) -> None:
        """Show a styled info dialog."""
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

    def _refresh_projects(self) -> None:
        if not self.resolve_app:
            return
        projects = self.resolve_app.list_projects()
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        if projects:
            self.project_combo.addItems(projects)
        else:
            self.project_combo.addItem("(No projects found)")
        self.project_combo.blockSignals(False)
        self._refresh_timelines()

    def _refresh_timelines(self) -> None:
        if not self.resolve_app:
            return
        self.resolve_app.refresh()
        timelines = self.resolve_app.list_timeline_names()
        self.timeline_combo.blockSignals(True)
        self.timeline_combo.clear()
        if timelines:
            self.timeline_combo.addItems(timelines)
        else:
            self.timeline_combo.addItem("(No timelines)")
        self.timeline_combo.blockSignals(False)

    def _project_changed(self, name: str) -> None:
        if not self.resolve_app or not name or name.startswith("("):
            return
        self.resolve_app.load_project(name)
        self._refresh_timelines()

    def _timeline_changed(self, name: str) -> None:
        if not self.resolve_app or not name or name.startswith("("):
            return
        timeline = self.resolve_app.find_timeline(name)
        if timeline:
            self.resolve_app.set_current_timeline(timeline)

    def _tool_changed(self, current, previous) -> None:
        self._refresh_presets()

    def _get_current_tool_id(self) -> str:
        item = self.tool_list.currentItem()
        if item:
            return item.data(QtCore.Qt.UserRole)
        return ""

    def _refresh_presets(self) -> None:
        tool_id = self._get_current_tool_id()
        if not tool_id:
            return
        presets = list_presets(self.cfg, tool_id)
        self.preset_combo.clear()
        if presets:
            self.preset_combo.addItems(presets)
        else:
            self.preset_combo.addItem("(No presets)")

    def _save_preset(self) -> None:
        tool_id = self._get_current_tool_id()
        name = self.preset_name.text().strip()
        if not name:
            self._show_error("Preset Name Required", "Please enter a name for the preset.")
            return
        options = self._parse_options()
        if options is None:
            return
        try:
            path = save_preset(self.cfg, tool_id, name, options)
            self._show_info("Preset Saved", f"Preset '{name}' saved successfully.")
            self._refresh_presets()
            self.preset_name.clear()
        except Exception as exc:
            self._show_error("Save Failed", f"Failed to save preset: {exc}")

    def _load_preset(self) -> None:
        tool_id = self._get_current_tool_id()
        name = self.preset_combo.currentText()
        if not name or name.startswith("("):
            return
        try:
            options = load_preset(self.cfg, tool_id, name)
            self.options_edit.setPlainText(json.dumps(options, indent=2))
        except Exception as exc:
            self._show_error("Load Failed", f"Failed to load preset: {exc}")

    def _parse_options(self) -> Optional[dict[str, Any]]:
        options_text = self.options_edit.toPlainText().strip()
        if not options_text:
            return {}
        try:
            return json.loads(options_text)
        except json.JSONDecodeError as exc:
            self._show_error(
                "Invalid JSON",
                f"The options JSON is invalid:\n\n{exc}\n\nPlease fix the JSON syntax and try again."
            )
            return None

    def _run_tool(self) -> None:
        tool_id = self._get_current_tool_id()
        if not tool_id:
            return

        # Check if connected
        if not self.resolve_app:
            self._show_error(
                "Not Connected",
                "Please connect to DaVinci Resolve first.\n\n"
                "1. Make sure Resolve is open and running\n"
                "2. Click the 'Connect' button"
            )
            return

        options = self._parse_options()
        if options is None:
            return

        # Update UI to show running
        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")
        QtWidgets.QApplication.processEvents()

        try:
            ctx = build_context(self.cfg, dry_run=self.dry_run_check.isChecked())
            ctx.resolve = self.resolve_app
            tool_cls = TOOL_REGISTRY[tool_id]
            tool = tool_cls(ctx)

            try:
                report = tool.run(options)
            except ResolveConnectionError as exc:
                self._show_error("Resolve Error", str(exc))
                return
            except Exception as exc:
                self._show_error(
                    "Tool Error",
                    f"The tool encountered an error:\n\n{exc}\n\n"
                    "Check your options and try again."
                )
                return

            # Save reports
            output_dir = Path(self.output_path.text())
            output_dir.mkdir(parents=True, exist_ok=True)
            base = f"{tool_id}_{now_stamp()}"

            try:
                report.to_json(output_dir / f"{base}.json")
                report.to_csv(output_dir / f"{base}.csv")
                report.to_html(output_dir / f"{base}.html")
            except Exception as exc:
                self._show_error("Save Error", f"Failed to save report: {exc}")

            self._set_report(report)

            # Show success
            mode = "DRY RUN" if self.dry_run_check.isChecked() else "COMPLETED"
            self._show_info(
                f"Tool {mode}",
                f"Tool completed successfully!\n\n"
                f"Reports saved to:\n{output_dir / base}.*"
            )

        finally:
            self.run_button.setEnabled(True)
            self.run_button.setText("▶ Run Tool")

    def _open_report(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Report",
            str(self.cfg.reports_dir),
            "JSON Files (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            self.summary_view.setPlainText(json.dumps(data.get("summary", {}), indent=2))
            self.report_items = data.get("items", [])
            self._apply_filter(self.filter_combo.currentText())
        except Exception as exc:
            self._show_error("Open Failed", f"Failed to open report:\n\n{exc}")

    def _set_report(self, report: Any) -> None:
        self.summary_view.setPlainText(json.dumps(report.summary, indent=2))
        self.report_items = [item.__dict__ for item in report.items]
        self._apply_filter(self.filter_combo.currentText())

    def _apply_filter(self, severity: str) -> None:
        items = self.report_items
        if severity != "All":
            items = [item for item in items if item.get("severity") == severity]
        self.report_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.report_table.setItem(row, 0, QtWidgets.QTableWidgetItem(item.get("severity", "")))
            self.report_table.setItem(row, 1, QtWidgets.QTableWidgetItem(item.get("category", "")))
            self.report_table.setItem(row, 2, QtWidgets.QTableWidgetItem(item.get("message", "")))
            self.report_table.setItem(row, 3, QtWidgets.QTableWidgetItem(item.get("timeline", "")))
            self.report_table.setItem(row, 4, QtWidgets.QTableWidgetItem(item.get("clip", "")))
            self.report_table.setItem(row, 5, QtWidgets.QTableWidgetItem(item.get("timecode", "")))


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for consistent cross-platform look
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
