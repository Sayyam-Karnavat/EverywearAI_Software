import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,QPushButton, QLabel ,  QGraphicsOpacityEffect
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QUrl, QRect, QPropertyAnimation, QEasingCurve

from PySide6.QtWebEngineCore import QWebEngineProfile

class FloatingBrowser(QMainWindow):
    def __init__(self, icon_geometry, close_callback):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.close_callback = close_callback
        
        # Position the UI to the left and slightly above the icon
        browser_width, browser_height = 800, 600
        new_x = icon_geometry.x() - browser_width  # Align closely with the icon
        new_y = max(50, icon_geometry.y() - browser_height + 50)  # Ensure it stays above the icon
        
        self.setGeometry(new_x, new_y, browser_width, browser_height)
        
        self.init_ui()
        self.animate_open()

    def init_ui(self):
        # Use the Chrome browser for rendering
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.browser.setStyleSheet("background-color: #1e1e1e; border-radius: 10px;")
        
        self.prompt_button = self.create_button("Prompt", "#0d846b")
        self.size_button = self.create_button("Size", "#0b6d58")
        self.close_button = self.create_button("Close", "#10a37f")
        self.close_button.clicked.connect(self.close_callback)
        
        container = QWidget()
        layout = QVBoxLayout()
        
        # Create a horizontal layout for submenu buttons and move them to the top
        submenu_layout = QHBoxLayout()
        submenu_layout.addWidget(self.prompt_button)
        submenu_layout.addWidget(self.size_button)
        layout.addLayout(submenu_layout)
        
        layout.addWidget(self.browser)
        layout.addWidget(self.close_button)
        
        container.setLayout(layout)
        container.setStyleSheet("background-color: #1e1e1e; border-radius: 10px; border: 3px solid #10a37f;")

        self.setCentralWidget(container)

    def create_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {color}; color: white; border-radius: 10px; padding: 5px;")
        button.setGraphicsEffect(QGraphicsOpacityEffect())
        
        # Adding simple hover effect with a shadow depth effect
        button.setStyleSheet(f"background-color: {color}; color: white; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        button.enterEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: white; border-radius: 10px; padding: 5px; border: 2px solid white;")
        button.leaveEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: white; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        return button
    
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
