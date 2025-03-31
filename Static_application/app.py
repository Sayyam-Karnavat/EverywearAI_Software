import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGraphicsOpacityEffect, QMenu, QDialog, QLineEdit, QTextEdit
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QUrl, QRect, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction
from PySide6.QtWebEngineCore import QWebEngineProfile

# Helper function to get the correct path for bundled resources
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # Running as bundled executable
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running as script
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

class CreatePromptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.init_ui()
        
        if parent:
            parent_geo = parent.geometry()
            self.move(parent_geo.x() + 50, parent_geo.y() + 50)

    def init_ui(self):
        container = QWidget()
        container.setStyleSheet("""
            background-color: #1e1e1e; 
            border-radius: 10px; 
            border: 3px solid #10a37f;
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel("Create New Prompt")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("Enter file name (.txt will be added)")
        self.filename_input.setStyleSheet("""
            background-color: #2d2d2d;
            color: white;
            border: 2px solid #0d846b;
            border-radius: 5px;
            padding: 5px;
        """)
        layout.addWidget(self.filename_input)

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Enter your prompt content here...")
        self.content_input.setStyleSheet("""
            background-color: #2d2d2d;
            color: white;
            border: 2px solid #0d846b;
            border-radius: 5px;
            padding: 5px;
        """)
        layout.addWidget(self.content_input)

        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet("""
            background-color: #0d846b;
            color: white;
            border-radius: 5px;
            padding: 8px;
            border: 2px solid transparent;
        """)
        self.save_button.enterEvent = lambda event: self.save_button.setStyleSheet("""
            background-color: #0d846b;
            color: white;
            border-radius: 5px;
            padding: 8px;
            border: 2px solid white;
        """)
        self.save_button.leaveEvent = lambda event: self.save_button.setStyleSheet("""
            background-color: #0d846b;
            color: white;
            border-radius: 5px;
            padding: 8px;
            border: 2px solid transparent;
        """)
        self.save_button.clicked.connect(self.save_prompt)
        layout.addWidget(self.save_button)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff5555; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        container.setLayout(layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        self.setFixedSize(400, 500)

    def save_prompt(self):
        filename = self.filename_input.text().strip()
        content = self.content_input.toPlainText().strip()

        if not filename:
            self.error_label.setText("File name cannot be empty")
            return
        
        if not content:
            self.error_label.setText("Prompt content cannot be empty")
            return

        if not filename.endswith('.txt'):
            filename += '.txt'

        if os.path.exists(filename):
            self.error_label.setText("File already exists")
            return

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            self.accept()
        except Exception as e:
            self.error_label.setText(f"Error saving file: {str(e)}")

class FloatingBrowser(QMainWindow):
    def __init__(self, icon_geometry, close_callback):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.close_callback = close_callback
        self.icon_geometry = icon_geometry

        self.screen = QApplication.primaryScreen()
        self.screen_geometry = self.screen.availableGeometry()
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        
        self.browser_width = int(self.screen_width * 0.4)
        self.browser_height = int(self.screen_height * 0.5)
        
        new_x = icon_geometry.x() - self.browser_width
        new_y = icon_geometry.y() - self.browser_height + icon_geometry.height() // 2
        
        self.setGeometry(new_x, new_y, self.browser_width, self.browser_height)
        self.init_ui()
        self.animate_open()

    def init_ui(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://chat.openai.com"))
        self.browser.setStyleSheet("background-color: #1e1e1e; border-radius: 10px;")

        self.prompt_button = self.create_button("Prompt", "#0d846b")
        self.size_button = self.create_button("Size", "#0b6d58")
        self.close_button = self.create_button("Close", "#10a37f")
        self.close_button.clicked.connect(self.close_callback)

        submenu_layout = QHBoxLayout()
        submenu_layout.addWidget(self.prompt_button)
        submenu_layout.addWidget(self.size_button)
        
        submenu_layout.setStretch(0, 1)
        submenu_layout.setStretch(1, 1)
        
        small_width = int(self.screen_width * 0.3)
        small_height = int(self.screen_height * 0.4)
        medium_width = int(self.screen_width * 0.4)
        medium_height = int(self.screen_height * 0.5)
        large_width = int(self.screen_width * 0.5)
        large_height = int(self.screen_height * 0.65)
        
        self.size_menu = QMenu(self)
        self.size_menu.setStyleSheet("background-color: #1e1e1e; color: white; border-radius: 10px; border: 2px solid #0b6d58;")
        small_action = self.create_menu_action("Small", "#0b6d58", self.resize_browser, small_width, small_height)
        medium_action = self.create_menu_action("Medium", "#0b6d58", self.resize_browser, medium_width, medium_height)
        large_action = self.create_menu_action("Large", "#0b6d58", self.resize_browser, large_width, large_height)
        self.size_menu.addAction(small_action)
        self.size_menu.addAction(medium_action)
        self.size_menu.addAction(large_action)
        self.size_button.setMenu(self.size_menu)

        self.prompt_menu = QMenu(self)
        self.prompt_menu.setStyleSheet("background-color: #1e1e1e; color: white; border-radius: 10px; border: 2px solid #0d846b;")
        
        create_action = self.create_simple_action("Create", "#0d846b", self.create_prompt)
        open_action = self.create_simple_action("Open", "#0d846b", self.open_prompt)
        
        self.prompt_menu.addAction(create_action)
        self.prompt_menu.addAction(open_action)
        self.prompt_button.setMenu(self.prompt_menu)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(submenu_layout)
        layout.addWidget(self.browser)
        layout.addWidget(self.close_button)
        
        container.setLayout(layout)
        container.setStyleSheet("background-color: #1e1e1e; border-radius: 10px; border: 3px solid #10a37f;")
        self.setCentralWidget(container)
        
        self.showEvent = self.on_show

    def on_show(self, event):
        self.size_menu.setFixedWidth(self.size_button.width())
        self.prompt_menu.setFixedWidth(self.prompt_button.width())
        super().showEvent(event)
    
    def create_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {color}; color: white; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        button.enterEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: white; border-radius: 10px; padding: 5px; border: 2px solid white;")
        button.leaveEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: white; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        return button
    
    def create_menu_action(self, text, color, slot, width, height):
        action = QAction(text, self)
        action.triggered.connect(lambda: slot(width, height))
        action.setData(color)
        return action
    
    def create_simple_action(self, text, color, slot):
        action = QAction(text, self)
        action.triggered.connect(slot)
        action.setData(color)
        return action
    
    def resize_browser(self, width, height):
        new_x = self.icon_geometry.x() - width
        new_y = self.icon_geometry.y() - height + self.icon_geometry.height() // 2
        new_x = max(0, new_x)
        new_y = max(0, new_y)
        self.animated_resize(new_x, new_y, width, height)
    
    def create_prompt(self):
        print("Create prompt clicked")
        dialog = CreatePromptDialog(self)
        dialog.raise_()
        dialog.exec()
        
    def open_prompt(self):
        print("Open prompt clicked")
    
    def animated_resize(self, x, y, width, height):
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(300)
        animation.setStartValue(self.geometry())
        animation.setEndValue(QRect(x, y, width, height))
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        self.resize_animation = animation
    
    def animate_open(self):
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        self.animation = animation
    
    def animate_close(self, callback):
        effect = self.graphicsEffect()
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(300)
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.finished.connect(callback)
        animation.start()
        self.animation = animation

class FloatingIcon(QWidget):
    def __init__(self, icon_path):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry.width() - 100, screen_geometry.height() - 100, 80, 80)
        
        self.init_ui(icon_path)

    def init_ui(self, icon_path):
        layout = QVBoxLayout()
        
        self.icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        if pixmap.isNull():
            print(f"Error: Could not load icon at {icon_path}")
        self.icon_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setStyleSheet("border-radius: 32px; background-color: rgba(0, 0, 0, 0.5);")
        layout.addWidget(self.icon_label)
        
        self.setLayout(layout)
        self.icon_label.mousePressEvent = self.toggle_browser
        
        self.browser_window = None

    def toggle_browser(self, event):
        if self.browser_window and self.browser_window.isVisible():
            self.browser_window.animate_close(self.browser_window.hide)
        else:
            self.browser_window = FloatingBrowser(self.geometry(), self.close_application)
            self.browser_window.show()
    
    def close_application(self):
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Use the resource_path function to get the correct icon path
    icon_path = resource_path("icon.png")
    floating_icon = FloatingIcon(icon_path)
    floating_icon.show()
    
    sys.exit(app.exec())