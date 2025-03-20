from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton
from PySide6.QtWebEngineWidgets import QWebEngineView


class DraggableIcon(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(50, 50)

        # Add an icon to represent the draggable item
        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(QIcon("show_icon.png").pixmap(50, 50))
        self.icon_label.setScaledContents(True)

        self.start_position = None
        self.browser_window = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Save the initial position of the mouse for dragging
            self.start_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.start_position is not None and event.buttons() == Qt.LeftButton:
            # Move the icon based on the mouse movement
            self.move(event.globalPos() - self.start_position)

    def mouseReleaseEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        # Show the browser window when the icon is double-clicked
        self.transform_to_browser()

    def transform_to_browser(self):
        # Hide the icon and show the browser window
        self.hide()

        # Create a larger geometry for the browser window, keeping the same position as the icon
        x, y, _, _ = self.geometry().getRect()
        browser_geometry = self.geometry()
        browser_geometry.setRect(x, y, 400, 400)  # Set larger width and height

        self.browser_window = BrowserWindow(browser_geometry)
        self.browser_window.show()
        self.browser_window.closed_signal.connect(self.transform_to_icon)

    def transform_to_icon(self):
        # Show the icon back at the same position
        self.browser_window = None
        self.show()


class BrowserWindow(QMainWindow):
    from PySide6.QtCore import Signal

    closed_signal = Signal()

    def __init__(self, geometry):
        super().__init__()
        self.setWindowTitle("EverywearGPT")  # Set the window title to ChatGPT
        self.setGeometry(geometry)  # Set the window's position and size

        # Embed full-featured browser
        self.browser = QWebEngineView(self)
        self.browser.setUrl("https://chat.openai.com/")  # Open the ChatGPT page
        self.setCentralWidget(self.browser)

        # Add an exit button inside the browser window
        self.exit_button = QPushButton("Exit", self)
        self.exit_button.clicked.connect(self.exit_application)
        self.update_exit_button_position()  # Set initial position

        # Style the exit button to match ChatGPT's dark theme
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #444654;  /* Dark background */
                color: white;  /* White text */
                border: none;
                border-radius: 12px;  /* Rounded corners */
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #666D76;  /* Slightly lighter on hover */
            }
        """)

    def exit_application(self):
        # Close the browser window and quit the application
        self.close()
        QApplication.quit()

    def resizeEvent(self, event):
        # Recalculate the position of the exit button when the window is resized
        self.update_exit_button_position()
        super().resizeEvent(event)

    def update_exit_button_position(self):
        # Dynamically position the button at the bottom center of the window
        button_width = self.exit_button.width()
        window_width = self.width()
        x_position = (window_width - button_width) // 2  # Center horizontally
        y_position = self.height() - 50  # Position 50 pixels from the bottom
        self.exit_button.move(x_position, y_position)  # Update position

    def closeEvent(self, event):
        # Emit the closed signal when the browser window is closed
        self.closed_signal.emit()
        event.accept()


if __name__ == "__main__":
    app = QApplication([])
    draggable_icon = DraggableIcon()
    draggable_icon.show()
    app.exec()
