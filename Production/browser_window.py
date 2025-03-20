# browser_window.py
import os
import sys
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QMenu,
    QApplication,
    QLabel,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QMessageBox,
)

from PySide6.QtGui import QAction
from PySide6.QtWebEngineWidgets import QWebEngineView

def resource_path(relative_path):
    """Get the absolute path to a resource, considering if running from PyInstaller bundle."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Path to the company logo image
image1_path = resource_path("company_logo.png")


# Directory where prompt text files are stored
prompts_dir = "Prompts"


class CreatePromptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Prompt")
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(700, 500)

        layout = QVBoxLayout(self)

        # File name input
        self.filename_label = QLabel("Enter file name (without extension):", self)
        self.filename_edit = QLineEdit(self)

        # Prompt content input
        self.content_label = QLabel("Enter prompt content:", self)
        self.content_edit = QTextEdit(self)

        # Buttons layout
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save", self)
        self.cancel_button = QPushButton("Cancel", self)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addWidget(self.filename_label)
        layout.addWidget(self.filename_edit)
        layout.addWidget(self.content_label)
        layout.addWidget(self.content_edit)
        layout.addLayout(button_layout)

        self.save_button.clicked.connect(self.save_prompt)
        self.cancel_button.clicked.connect(self.reject)

    def save_prompt(self):
        filename = self.filename_edit.text().strip()
        content = self.content_edit.toPlainText()
        if not filename:
            QMessageBox.warning(self, "Error", "File name cannot be empty")
            return

        # Ensure the prompts directory exists
        if not os.path.exists(prompts_dir):
            os.makedirs(prompts_dir)
        file_path = os.path.join(prompts_dir, filename + ".txt")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.accept()  # Close the dialog
            # If parent is a BrowserWindow, show a toast message
            if self.parent():
                self.parent().show_toast("Prompt saved")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save prompt: {e}")

class BrowserWindow(QMainWindow):
    def __init__(self, geometry, draggable_icon):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setGeometry(geometry)

        self.draggable_icon = draggable_icon  # Reference to the draggable icon
        self.is_dragging = False
        self.drag_position = QPoint()

        # Set the title and icon
        self.setWindowTitle("✨ EverywearGPT ✨")
        self.setWindowIcon(QIcon(image1_path))  # Replace with your company logo

        # Add the browser widget as the central widget
        self.browser = QWebEngineView(self)
        self.browser.setUrl("https://chat.openai.com/")  # Set the URL
        self.setCentralWidget(self.browser)

        # Add Menu Bar
        self.add_menu_bar()

    def add_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #2D2D2D;
                color: white;
                padding: 6px;
                font-size: 14px;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 6px;
            }
            QMenuBar::item:selected {
                background-color: #555;
            }
            QMenu {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #666;
            }
        """)

        prompts_menu = QMenu("📝 Prompts", self)
        self.open_menu = QMenu("📂 Open", self)
        self.open_menu.aboutToShow.connect(self.populate_open_menu)

        create_action = QAction("➕ Create", self)
        create_action.triggered.connect(self.create_prompt)

        prompts_menu.addMenu(self.open_menu)
        prompts_menu.addAction(create_action)
        menu_bar.addMenu(prompts_menu)

        size_menu = QMenu("📏 Size", self)
        size_menu.addAction(QAction("🔹 Small", self, triggered=self.set_small_size))
        size_menu.addAction(QAction("🔸 Medium", self, triggered=self.set_medium_size))
        size_menu.addAction(QAction("🔺 Large", self, triggered=self.set_large_size))
        menu_bar.addMenu(size_menu)

    def populate_open_menu(self):
        # Ensure the "Prompts" directory exists
        if not os.path.exists(prompts_dir):
            os.makedirs(prompts_dir)

        # Clear any existing menu items
        self.open_menu.clear()

        # Get all .txt files in the "Prompts" directory
        txt_files = [f for f in os.listdir(prompts_dir) if f.endswith(".txt")]

        if not txt_files:
            no_files_action = QAction("No files found", self)
            no_files_action.setEnabled(False)
            self.open_menu.addAction(no_files_action)
        else:
            for file_name in txt_files:
                action = QAction(file_name, self)
                # Use a lambda to pass the file name to the open_file method
                action.triggered.connect(lambda checked, fn=file_name: self.open_file(fn))
                self.open_menu.addAction(action)

    def open_file(self, file_name):
        # Build the file path and read its content
        file_path = os.path.join(prompts_dir, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Copy content to clipboard
            QApplication.clipboard().setText(content)
            # Show a toast message
            self.show_toast("Content copied to clipboard")
        except Exception as e:
            print(f"Error opening file {file_name}: {e}")

    def show_toast(self, message):
        # Create a label to serve as a toast message
        toast = QLabel(message, self)
        toast.setStyleSheet(
            "background-color: rgba(0, 0, 0, 180); color: white; padding: 8px; border-radius: 5px;"
        )
        toast.setWindowFlags(Qt.ToolTip)
        toast.adjustSize()
        # Position the toast at the bottom center of the window
        window_rect = self.geometry()
        x = window_rect.x() + (window_rect.width() - toast.width()) // 2
        y = window_rect.y() + window_rect.height() - toast.height() - 20
        toast.move(x, y)
        toast.show()
        # Hide the toast after 2 seconds
        QTimer.singleShot(2000, toast.close)

    def create_prompt(self):
        # Open the Create Prompt dialog
        dialog = CreatePromptDialog(self)
        dialog.exec()

    def set_small_size(self):
        # Set the browser window size to small
        self.setFixedSize(700, 500)

    def set_medium_size(self):
        # Set the browser window size to medium
        self.setFixedSize(900,700)

    def set_large_size(self):
        # Set the browser window size to large
        self.setFixedSize(1100,900)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            new_position = event.globalPos() - self.drag_position
            self.move(new_position)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.is_dragging = False

    def moveEvent(self, event):
        # Ensure the draggable icon moves with the browser window
        if self.draggable_icon is not None:
            self.draggable_icon.move(self.x() - self.draggable_icon.width(), self.y())

    def closeEvent(self, event):
        # Close the entire application when the browser window is closed
        self.draggable_icon.close_application()