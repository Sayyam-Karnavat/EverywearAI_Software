from PySide6.QtCore import Qt, Signal, QPoint, QEvent
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QMenuBar, QMenu
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QAction

class DraggableIcon(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(50, 50)

        # Add an icon to represent the draggable item
        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(QIcon("show_icon.png").pixmap(50, 50))  # Set your icon here
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

        self.setWindowFlags(Qt.Window)  # Allow default window behavior
        self.setGeometry(geometry)

        self.is_dragging = False
        self.drag_position = QPoint()
        self.draggable_icon = draggable_icon  # Save reference to DraggableIcon

        # Set the default title "EverywearGPT" with company logo as the window icon
        self.setWindowTitle("EverywearGPT")
        self.setWindowIcon(QIcon("company_logo.png"))  # Replace with your company logo

        # Embed the browser
        self.browser = QWebEngineView(self)
        self.browser.setUrl("https://chat.openai.com/")  # Set the URL
        self.setCentralWidget(self.browser)

        # Create the menu bar
        self.menu_bar = self.menuBar()
        self.create_menu()

    def create_menu(self):
        # Add a menu to the title bar
        file_menu = self.menu_bar.addMenu("File")

        # Add actions to the menu
        open_action = QAction("Open", self)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        file_menu.addAction(save_action)

        exit_action = QAction("Exit", self)
        file_menu.addAction(exit_action)
        exit_action.triggered.connect(self.close_application)

    def close_application(self):
        self.close()
        QApplication.quit()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.is_dragging = False

    def closeEvent(self, event):
        # Close the browser window and terminate the application
        self.draggable_icon.close()  # Close the draggable icon
        event.accept()  # Allow the window to close properly
        QApplication.quit()  # Terminate the application

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() == Qt.WindowMinimized:
                self.hide()  # Hide the window when minimized
                self.draggable_icon.transform_to_icon()  # Show the draggable icon
        super().changeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    draggable_icon = DraggableIcon()
    draggable_icon.show()
    app.exec()
