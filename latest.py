from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView


class DraggableIcon(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(50, 50)

        # Add an icon to represent the draggable item
        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(QIcon("company_logo.png").pixmap(50, 50))  # Set your icon here
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
            self.browser_window.raise_()  # Bring it to the front

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
        self.setWindowIcon(QIcon("company_logo.png"))  # Replace with your company logo

        # Add the browser widget
        self.browser = QWebEngineView(self)
        self.browser.setUrl("https://chat.openai.com/")  # Set the URL
        self.setCentralWidget(self.browser)

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
