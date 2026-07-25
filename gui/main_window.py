"""
Desktop GUI for the ATJ Facebook Catalog Generator, built with PySide6.
Launch via: python gui/main_window.py  (from project root, or use run_gui.py)
"""
import logging
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QProgressBar, QTextEdit,
    QCheckBox, QMessageBox, QGroupBox, QFrame,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import APP_NAME, APP_VERSION, INPUT_FOLDER  # noqa: E402
from core.excel_reader import ERPReader  # noqa: E402
from core.facebook_mapper import FacebookMapper  # noqa: E402
from core.image_matcher import ImageMatcher  # noqa: E402
from core.validator import CatalogValidator  # noqa: E402
from core.exporter import CatalogExporter  # noqa: E402

logger = logging.getLogger("ATJ.gui")


class ConversionWorker(QThread):
    """Runs the ERP -> Facebook catalog pipeline on a background thread."""

    progress = Signal(str)
    finished_ok = Signal(dict)
    failed = Signal(str)

    def __init__(self, file_path: Path, verify_images: bool):
        super().__init__()
        self.file_path = file_path
        self.verify_images = verify_images

    def run(self):
        try:
            self.progress.emit(f"Reading {self.file_path.name}...")
            reader = ERPReader(self.file_path)
            records = reader.get_records()
            self.progress.emit(f"Loaded {len(records):,} records.")

            self.progress.emit("Mapping fields to Facebook Catalog schema...")
            mapper = FacebookMapper()
            products = mapper.map_all(records)

            if self.verify_images:
                self.progress.emit("Verifying image URLs (this may take a while)...")
                matcher = ImageMatcher(verify=True)
                products = matcher.verify_all(products)

            self.progress.emit("Validating rows...")
            validator = CatalogValidator()
            result = validator.validate_all(products)
            self.progress.emit(result.summary())

            export_rows = result.valid_rows if result.valid_rows else products
            self.progress.emit("Writing output files...")
            exporter = CatalogExporter()
            out = exporter.export(export_rows)
            out["invalid_count"] = len(result.invalid_rows)
            out["errors"] = result.errors[:20]  # cap for display

            self.finished_ok.emit(out)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Conversion failed")
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_file: Path | None = None
        self.worker: ConversionWorker | None = None
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(640, 520)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Afridi Trading Japan \u2014 Facebook Catalog Generator")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        subtitle = QLabel("Convert your ERP vehicle export into a Meta-ready product catalog.")
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        # File selection group
        file_group = QGroupBox("1. Select ERP Excel File")
        file_layout = QHBoxLayout(file_group)
        self.file_label = QLabel("No file selected.")
        self.file_label.setStyleSheet("color: #333;")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_label, stretch=1)
        file_layout.addWidget(browse_btn)
        layout.addWidget(file_group)

        # Options group
        options_group = QGroupBox("2. Options")
        options_layout = QVBoxLayout(options_group)
        self.verify_checkbox = QCheckBox("Verify image URLs before export (slower, more accurate)")
        options_layout.addWidget(self.verify_checkbox)
        layout.addWidget(options_group)

        # Run button + progress
        self.run_btn = QPushButton("Generate Catalog")
        self.run_btn.setMinimumHeight(40)
        self.run_btn.setStyleSheet(
            "QPushButton { background-color: #1877F2; color: white; font-weight: bold; "
            "border-radius: 6px; } QPushButton:disabled { background-color: #a0c3f5; }"
        )
        self.run_btn.clicked.connect(self.start_conversion)
        self.run_btn.setEnabled(False)
        layout.addWidget(self.run_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # indeterminate
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Log output
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        log_layout.addWidget(self.log_output)
        layout.addWidget(log_group, stretch=1)

    def browse_file(self):
        start_dir = str(INPUT_FOLDER) if INPUT_FOLDER.exists() else str(Path.home())
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select ERP Excel Export", start_dir, "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.selected_file = Path(file_path)
            self.file_label.setText(self.selected_file.name)
            self.run_btn.setEnabled(True)

    def log(self, message: str):
        self.log_output.append(message)

    def start_conversion(self):
        if not self.selected_file:
            QMessageBox.warning(self, "No file", "Please select an ERP Excel file first.")
            return

        self.run_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.log_output.clear()
        self.log(f"Starting conversion of {self.selected_file.name}...")

        self.worker = ConversionWorker(self.selected_file, self.verify_checkbox.isChecked())
        self.worker.progress.connect(self.log)
        self.worker.finished_ok.connect(self.on_finished)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def on_finished(self, result: dict):
        self.progress_bar.setVisible(False)
        self.run_btn.setEnabled(True)
        self.log(f"\nSUCCESS: {result['total_records']} rows exported.")
        self.log(f"Excel: {result['excel']}")
        self.log(f"CSV:   {result['csv']}")
        if result.get("invalid_count"):
            self.log(f"\n{result['invalid_count']} rows had validation warnings:")
            for err in result.get("errors", []):
                self.log(f"  - {err}")

        QMessageBox.information(
            self, "Done",
            f"Catalog generated successfully!\n\n{result['total_records']} rows exported to:\n{result['excel'].parent}"
        )

    def on_failed(self, error_message: str):
        self.progress_bar.setVisible(False)
        self.run_btn.setEnabled(True)
        self.log(f"\nFAILED: {error_message}")
        QMessageBox.critical(self, "Conversion Failed", error_message)


def launch():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch()
