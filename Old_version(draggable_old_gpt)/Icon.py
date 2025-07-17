# Icon.py
import os
import sys
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QWidget, QLabel, QApplication
from browser_window import BrowserWindow  # Import BrowserWindow from the other module

def resource_path(relative_path):
    """Get the absolute path to a resource, considering if running from PyInstaller bundle."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# Path to the icon image
image2_path = resource_path("show_icon.png")

# Directory where prompt text files are stored
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
