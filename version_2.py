from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
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

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.start_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.start_position is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.start_position)

    def mouseReleaseEvent(self, event: QMouseEvent):
        pass

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.transform_to_browser()

    def transform_to_browser(self):
        self.hide()

        # Create a larger geometry for the browser window
        x, y, _, _ = self.geometry().getRect()
        browser_geometry = self.geometry()
        browser_geometry.setRect(x, y, 400, 400)  # Set default larger width and height

        self.browser_window = BrowserWindow(browser_geometry, self)  # Pass the DraggableIcon instance to BrowserWindow
        self.browser_window.show()

    def transform_to_icon(self):
        self.show()
        self.browser_window = None


class BrowserWindow(QMainWindow):
    closed_signal = Signal()

    def __init__(self, geometry, draggable_icon):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)  # Enable resizable window
        self.setGeometry(geometry)

        # Variables for dragging
        self.is_dragging = False
        self.drag_position = QPoint()
        self.draggable_icon = draggable_icon  # Save reference to DraggableIcon

        # Create a vertical layout for the custom title bar and web view
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Add a custom title bar with a different color to make buttons visible
        self.title_bar = QWidget(self)
        self.title_bar.setFixedHeight(30)
        self.title_bar.setStyleSheet("""
            background-color: #333;
            color: white;
            font-size: 14px;
            font-weight: bold;
        """)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        self.title_label = QLabel("EverywearGPT", self.title_bar)
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.setStyleSheet("color: white;")
        title_layout.addWidget(self.title_label)

        # Add the "Minimize" button with a PNG icon
        self.minimize_button = QPushButton(self.title_bar)
        self.minimize_button.setIcon(QIcon('minimize_icon.png'))  # Use your PNG icon here
        self.minimize_button.clicked.connect(self.minimize_application)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #FF5F57;
                border-radius: 5px;
            }
        """)
        self.minimize_button.setFixedSize(20, 20)
        title_layout.addWidget(self.minimize_button, alignment=Qt.AlignRight)

        # Add the "Exit" button with a PNG icon
        self.exit_button = QPushButton(self.title_bar)
        self.exit_button.setIcon(QIcon('close_icon.png'))  # Use your PNG icon here
        self.exit_button.clicked.connect(self.exit_application)
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #FF5F57;
                border-radius: 5px;
            }
        """)
        self.exit_button.setFixedSize(20, 20)
        title_layout.addWidget(self.exit_button)

        layout.addWidget(self.title_bar)

        # Embed the browser
        self.browser = QWebEngineView(self)
        self.browser.setUrl("https://chat.openai.com/")  # Set the URL
        layout.addWidget(self.browser)

        # Enable dragging from the title bar
        self.title_bar.mousePressEvent = self.start_dragging
        self.title_bar.mouseMoveEvent = self.perform_dragging
        self.title_bar.mouseReleaseEvent = self.stop_dragging

    def start_dragging(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def perform_dragging(self, event: QMouseEvent):
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)

    def stop_dragging(self, event: QMouseEvent):
        self.is_dragging = False

    def minimize_application(self):
        # Hide the browser window and return to the draggable icon
        self.hide()
        self.draggable_icon.transform_to_icon()

    def exit_application(self):
        self.close()
        QApplication.quit()

    def closeEvent(self, event):
        self.closed_signal.emit()
        event.accept()


if __name__ == "__main__":
    app = QApplication([])
    draggable_icon = DraggableIcon()
    draggable_icon.show()
    app.exec()
