import json
import sys
from pathlib import Path
from typing import Any, Optional

try:
    from PySide6 import QtCore, QtWidgets
except Exception as exc:  # pragma: no cover
    raise SystemExit("PySide6 is required for the UI. Install with: pip install PySide6") from exc

from core.config import get_config, ensure_dirs
from core.logging import setup_logging, get_logger
from core.presets import list_presets, load_preset, save_preset
from resolve.resolve_api import ResolveApp, ResolveConnectionError
from tools.base import build_context
from tools.registry import TOOL_REGISTRY
from tools.utils import now_stamp


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Resolve Production Suite v2")
        self.resize(1200, 760)

        self.cfg = get_config()
        ensure_dirs(self.cfg)
        setup_logging(self.cfg)
        self.logger = get_logger("ui")
        self.resolve_app: Optional[ResolveApp] = None
        self.report_items: list[dict[str, Any]] = []

        central = QtWidgets.QWidget()
        root_layout = QtWidgets.QVBoxLayout(central)

        top_bar = QtWidgets.QHBoxLayout()
        self.connect_button = QtWidgets.QPushButton("Connect Resolve")
        self.connect_button.clicked.connect(self._connect_resolve)
        self.status_label = QtWidgets.QLabel("Status: Disconnected")
        self.project_combo = QtWidgets.QComboBox()
        self.project_combo.currentTextChanged.connect(self._project_changed)
        self.timeline_combo = QtWidgets.QComboBox()
        self.timeline_combo.currentTextChanged.connect(self._timeline_changed)
        self.refresh_button = QtWidgets.QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._refresh_projects)
        self.dry_run_check = QtWidgets.QCheckBox("Dry Run")
        self.dry_run_check.setChecked(True)

        top_bar.addWidget(self.connect_button)
        top_bar.addWidget(self.status_label)
        top_bar.addStretch(1)
        top_bar.addWidget(QtWidgets.QLabel("Project"))
        top_bar.addWidget(self.project_combo)
        top_bar.addWidget(QtWidgets.QLabel("Timeline"))
        top_bar.addWidget(self.timeline_combo)
        top_bar.addWidget(self.refresh_button)
        top_bar.addWidget(self.dry_run_check)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        self.tool_list = QtWidgets.QListWidget()
        for tool_id in TOOL_REGISTRY.keys():
            self.tool_list.addItem(tool_id)
        self.tool_list.setCurrentRow(0)
        self.tool_list.currentTextChanged.connect(self._refresh_presets)

        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)

        preset_row = QtWidgets.QHBoxLayout()
        self.preset_combo = QtWidgets.QComboBox()
        self.preset_name = QtWidgets.QLineEdit()
        self.preset_name.setPlaceholderText("Preset name")
        self.preset_load = QtWidgets.QPushButton("Load Preset")
        self.preset_load.clicked.connect(self._load_preset)
        self.preset_save = QtWidgets.QPushButton("Save Preset")
        self.preset_save.clicked.connect(self._save_preset)

        preset_row.addWidget(QtWidgets.QLabel("Presets"))
        preset_row.addWidget(self.preset_combo)
        preset_row.addWidget(self.preset_name)
        preset_row.addWidget(self.preset_load)
        preset_row.addWidget(self.preset_save)

        self.options_edit = QtWidgets.QPlainTextEdit()
        self.options_edit.setPlaceholderText("{\n  \"example\": \"option\"\n}")

        self.run_button = QtWidgets.QPushButton("Run Tool")
        self.run_button.clicked.connect(self._run_tool)

        output_row = QtWidgets.QHBoxLayout()
        self.output_path = QtWidgets.QLineEdit(str(self.cfg.reports_dir))
        self.open_report_button = QtWidgets.QPushButton("Open Report")
        self.open_report_button.clicked.connect(self._open_report)
        output_row.addWidget(QtWidgets.QLabel("Reports output"))
        output_row.addWidget(self.output_path)
        output_row.addWidget(self.open_report_button)

        self.report_tabs = QtWidgets.QTabWidget()
        self.summary_view = QtWidgets.QPlainTextEdit()
        self.summary_view.setReadOnly(True)
        self.report_table = QtWidgets.QTableWidget(0, 6)
        self.report_table.setHorizontalHeaderLabels([
            "Severity", "Category", "Message", "Timeline", "Clip", "Timecode"
        ])
        self.report_table.horizontalHeader().setStretchLastSection(True)

        filter_row = QtWidgets.QHBoxLayout()
        self.filter_combo = QtWidgets.QComboBox()
        self.filter_combo.addItems(["All", "info", "warning", "error"])
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
        filter_row.addWidget(QtWidgets.QLabel("Filter"))
        filter_row.addWidget(self.filter_combo)
        filter_row.addStretch(1)

        report_panel = QtWidgets.QWidget()
        report_layout = QtWidgets.QVBoxLayout(report_panel)
        report_layout.addLayout(filter_row)
        report_layout.addWidget(self.report_table)

        self.report_tabs.addTab(self.summary_view, "Summary")
        self.report_tabs.addTab(report_panel, "Report Items")

        right_layout.addLayout(preset_row)
        right_layout.addWidget(QtWidgets.QLabel("Tool Options (JSON)"))
        right_layout.addWidget(self.options_edit)
        right_layout.addLayout(output_row)
        right_layout.addWidget(self.run_button)
        right_layout.addWidget(self.report_tabs)

        splitter.addWidget(self.tool_list)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 2)

        root_layout.addLayout(top_bar)
        root_layout.addWidget(splitter)

        self.setCentralWidget(central)
        self._refresh_presets()

    def _connect_resolve(self) -> None:
        self.resolve_app = ResolveApp(self.cfg)
        try:
            self.resolve_app.connect()
            self.status_label.setText("Status: Connected")
            self._refresh_projects()
        except ResolveConnectionError as exc:
            self.status_label.setText(f"Status: Error - {exc}")

    def _refresh_projects(self) -> None:
        if not self.resolve_app:
            return
        projects = self.resolve_app.list_projects()
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        self.project_combo.addItems(projects)
        self.project_combo.blockSignals(False)
        self._refresh_timelines()

    def _refresh_timelines(self) -> None:
        if not self.resolve_app:
            return
        self.resolve_app.refresh()
        timelines = self.resolve_app.list_timeline_names()
        self.timeline_combo.blockSignals(True)
        self.timeline_combo.clear()
        self.timeline_combo.addItems(timelines)
        self.timeline_combo.blockSignals(False)

    def _project_changed(self, name: str) -> None:
        if not self.resolve_app or not name:
            return
        self.resolve_app.load_project(name)
        self._refresh_timelines()

    def _timeline_changed(self, name: str) -> None:
        if not self.resolve_app or not name:
            return
        timeline = self.resolve_app.find_timeline(name)
        if timeline:
            self.resolve_app.set_current_timeline(timeline)

    def _refresh_presets(self) -> None:
        tool_id = self.tool_list.currentItem().text()
        presets = list_presets(self.cfg, tool_id)
        self.preset_combo.clear()
        self.preset_combo.addItems(presets)

    def _save_preset(self) -> None:
        tool_id = self.tool_list.currentItem().text()
        name = self.preset_name.text().strip()
        if not name:
            self.summary_view.setPlainText("Preset name required")
            return
        options = self._parse_options()
        if options is None:
            return
        path = save_preset(self.cfg, tool_id, name, options)
        self.summary_view.setPlainText(f"Preset saved to {path}")
        self._refresh_presets()

    def _load_preset(self) -> None:
        tool_id = self.tool_list.currentItem().text()
        name = self.preset_combo.currentText()
        if not name:
            return
        try:
            options = load_preset(self.cfg, tool_id, name)
        except Exception as exc:
            self.summary_view.setPlainText(f"Failed to load preset: {exc}")
            return
        self.options_edit.setPlainText(json.dumps(options, indent=2))

    def _parse_options(self) -> Optional[dict[str, Any]]:
        options_text = self.options_edit.toPlainText().strip()
        if not options_text:
            return {}
        try:
            return json.loads(options_text)
        except json.JSONDecodeError as exc:
            self.summary_view.setPlainText(f"Invalid JSON options: {exc}")
            return None

    def _run_tool(self) -> None:
        tool_id = self.tool_list.currentItem().text()
        options = self._parse_options()
        if options is None:
            return
        ctx = build_context(self.cfg, dry_run=self.dry_run_check.isChecked())
        if self.resolve_app:
            ctx.resolve = self.resolve_app
        tool_cls = TOOL_REGISTRY[tool_id]
        tool = tool_cls(ctx)
        try:
            report = tool.run(options)
        except ResolveConnectionError as exc:
            self.summary_view.setPlainText(f"Resolve error: {exc}")
            return
        output_dir = Path(self.output_path.text())
        output_dir.mkdir(parents=True, exist_ok=True)
        base = f"{tool_id}_{now_stamp()}"
        report.to_json(output_dir / f"{base}.json")
        report.to_csv(output_dir / f"{base}.csv")
        report.to_html(output_dir / f"{base}.html")
        self._set_report(report)

    def _open_report(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Report", str(self.cfg.reports_dir), "JSON Files (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception as exc:
            self.summary_view.setPlainText(f"Failed to open report: {exc}")
            return
        self.summary_view.setPlainText(json.dumps(data.get("summary", {}), indent=2))
        self.report_items = data.get("items", [])
        self._apply_filter(self.filter_combo.currentText())

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
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
