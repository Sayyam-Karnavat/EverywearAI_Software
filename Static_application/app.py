import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGraphicsOpacityEffect, QMenu
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QUrl, QRect, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction
from PySide6.QtWebEngineCore import QWebEngineProfile

class FloatingBrowser(QMainWindow):
    def __init__(self, icon_geometry, close_callback):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.close_callback = close_callback
        self.icon_geometry = icon_geometry

        # Get screen dimensions
        self.screen = QApplication.primaryScreen()
        self.screen_geometry = self.screen.availableGeometry()
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        
        # Calculate initial size based on screen dimensions (medium size)
        self.browser_width = int(self.screen_width * 0.4)  # 40% of screen width
        self.browser_height = int(self.screen_height * 0.5)  # 50% of screen height
        
        # Position the window so its bottom-right corner aligns with the left side of the icon
        new_x = icon_geometry.x() - self.browser_width
        new_y = icon_geometry.y() - self.browser_height + icon_geometry.height() // 2
        
        self.setGeometry(new_x, new_y, self.browser_width, self.browser_height)
        self.init_ui()
        self.animate_open()

    def init_ui(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.browser.setStyleSheet("background-color: #1e1e1e; border-radius: 10px;")

        # Create buttons
        self.prompt_button = self.create_button("Prompt", "#0d846b")
        self.size_button = self.create_button("Size", "#0b6d58")
        self.close_button = self.create_button("Close", "#10a37f")
        self.close_button.clicked.connect(self.close_callback)

        # Create submenu layout
        submenu_layout = QHBoxLayout()
        submenu_layout.addWidget(self.prompt_button)
        submenu_layout.addWidget(self.size_button)
        
        # Set stretch to make buttons fill the entire line (50-50 split)
        submenu_layout.setStretch(0, 1)
        submenu_layout.setStretch(1, 1)
        
        # Calculate sizes based on screen dimensions
        small_width = int(self.screen_width * 0.3)  # 30% of screen width
        small_height = int(self.screen_height * 0.4)  # 40% of screen height
        
        medium_width = int(self.screen_width * 0.4)  # 40% of screen width
        medium_height = int(self.screen_height * 0.5)  # 50% of screen height
        
        large_width = int(self.screen_width * 0.5)  # 50% of screen width
        large_height = int(self.screen_height * 0.65)  # 65% of screen height
        
        # Create size menu
        self.size_menu = QMenu(self)
        self.size_menu.setStyleSheet("background-color: #1e1e1e; color: white; border-radius: 10px; border: 2px solid #0b6d58;")

        small_action = self.create_menu_action("Small", "#0b6d58", self.resize_browser, small_width, small_height)
        medium_action = self.create_menu_action("Medium", "#0b6d58", self.resize_browser, medium_width, medium_height)
        large_action = self.create_menu_action("Large", "#0b6d58", self.resize_browser, large_width, large_height)

        self.size_menu.addAction(small_action)
        self.size_menu.addAction(medium_action)
        self.size_menu.addAction(large_action)

        self.size_button.setMenu(self.size_menu)

        # Main layout
        container = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(submenu_layout)
        layout.addWidget(self.browser)
        layout.addWidget(self.close_button)
        
        container.setLayout(layout)
        container.setStyleSheet("background-color: #1e1e1e; border-radius: 10px; border: 3px solid #10a37f;")

        self.setCentralWidget(container)
        
        # Connect the showEvent to adjust menu width
        self.showEvent = self.on_show

    def on_show(self, event):
        # Set menu width to match the size button's width exactly
        self.size_menu.setFixedWidth(self.size_button.width())
        
        # Call the original showEvent if needed
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
    
    def resize_browser(self, width, height):
        # Calculate new position to keep bottom-right corner anchored to the left side of the icon
        new_x = self.icon_geometry.x() - width
        new_y = self.icon_geometry.y() - height + self.icon_geometry.height() // 2
        
        # Ensure window stays within screen boundaries
        new_x = max(0, new_x)
        new_y = max(0, new_y)
        
        # Animate the resize
        self.animated_resize(new_x, new_y, width, height)
    
    def animated_resize(self, x, y, width, height):
        # Create animation for geometry
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
        self.icon_label.setPixmap(QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
    
    icon_path = "icon.png"  # Ensure the correct path is provided
    floating_icon = FloatingIcon(icon_path)
    floating_icon.show()
    
    sys.exit(app.exec())