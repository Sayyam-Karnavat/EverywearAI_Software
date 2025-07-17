import PySide6
import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets
import PySide6.QtWebEngineWidgets
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QWidget,
    QMenu,
    QVBoxLayout,
    QDialog,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox
)
from PySide6.QtGui import QAction
from PySide6.QtWebEngineWidgets import QWebEngineView
import sys
import os

def resource_path(relative_path):
    """Get the absolute path to a resource, considering if running from PyInstaller bundle."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Construct the paths to the images using resource_path
image1_path = resource_path("company_logo.png")
image2_path = resource_path("show_icon.png")

# Define the Prompts directory
prompts_dir = "Prompts"


class DraggableIcon(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(50, 50)

        # Add an icon to represent the draggable item
        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(QIcon(image2_path).pixmap(50, 50))
        self.icon_label.setScaledContents(True)

        self.start_position = None
        self.browser_window = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.start_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.start_position is not None and event.buttons() == Qt.LeftButton:
            new_position = event.globalPos() - self.start_position
            self.move(new_position)
            # Move the browser window together with the icon
            if self.browser_window is not None and self.browser_window.isVisible():
                self.browser_window.move(new_position.x() + self.width(), new_position.y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        pass

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if self.browser_window is None:
            self.transform_to_browser()
        else:
            self.browser_window.showNormal()  # Restore browser if minimized
            self.browser_window.raise_()       # Bring it to the front

    def transform_to_browser(self):
        # Create a larger geometry for the browser window, placing it beside the icon
        x, y, _, _ = self.geometry().getRect()
        browser_geometry = self.geometry()
        browser_geometry.setRect(x + self.width(), y, 400, 400)
        self.browser_window = BrowserWindow(browser_geometry, self)  # Pass the icon instance
        self.browser_window.show()

    def moveEvent(self, event):
        if self.browser_window is not None and self.browser_window.isVisible():
            # Ensure the browser window moves with the icon
            self.browser_window.move(self.x() + self.width(), self.y())

    def close_application(self):
        QApplication.quit()  # Ensure the application closes fully


class CreatePromptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Prompt")
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(400, 300)

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
        self.setWindowTitle("EverywearGPT")
        self.setWindowIcon(QIcon(image1_path))  # Replace with your company logo

        # Add the browser widget as the central widget
        self.browser = QWebEngineView(self)
        self.browser.setUrl("https://chat.openai.com/")  # Set the URL
        self.setCentralWidget(self.browser)

        # Add Menu Bar
        self.add_menu_bar()

    def add_menu_bar(self):
        menu_bar = self.menuBar()
        prompts_menu = QMenu("Prompts", self)

        # Create an "Open" submenu and connect its aboutToShow signal
        self.open_menu = QMenu("Open", self)
        self.open_menu.aboutToShow.connect(self.populate_open_menu)

        create_action = QAction("Create", self)
        create_action.triggered.connect(self.create_prompt)

        prompts_menu.addMenu(self.open_menu)
        prompts_menu.addAction(create_action)
        menu_bar.addMenu(prompts_menu)

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


if __name__ == "__main__":
    app = QApplication([])
    draggable_icon = DraggableIcon()
    draggable_icon.show()
    app.exec()
    
