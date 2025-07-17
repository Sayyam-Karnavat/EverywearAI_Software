import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QGraphicsOpacityEffect, QMenu, QLineEdit, 
                              QTextEdit, QFileDialog, QDialog, QListWidget, QListWidgetItem,
                              QSplitter, QTextBrowser)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QPixmap, QClipboard
from PySide6.QtCore import Qt, QUrl, QRect, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWebEngineCore import QWebEngineProfile

def resource_path(relative_path):
    """Get the absolute path to a resource, works for development and PyInstaller bundles."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.dirname(__file__), relative_path)

class ToastNotification(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setRuntimeFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        self.init_ui(message)
        
        if parent:
            parent_rect = parent.geometry()
            toast_width = 200
            toast_height = 50
            x = parent_rect.x() + (parent_rect.width() - toast_width) // 2
            y = parent_rect.y() + parent_rect.height() - toast_height - 50
            self.setGeometry(x, y, toast_width, toast_height)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.hide_toast)
        self.timer.setSingleShot(True)
        
        self.show()
        self.animate_show()
        self.timer.start(2000)
    
    def init_ui(self, message):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        label = QLabel(message)
        label.setStyleSheet("""
            color: #333333;
            font-size: 12px;
            font-weight: bold;
        """)
        label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(label)
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(242, 140, 56, 0.9);
                border-radius: 15px;
                border: 2px solid #FFF8E7;
            }
        """)
    
    def animate_show(self):
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()
    
    def hide_toast(self):
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.finished.connect(self.deleteLater)
        self.animation.start()

class PromptCreatorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        if parent:
            parent_geo = parent.geometry()
            dialog_width = int(parent_geo.width() * 0.9)
            dialog_height = int(parent_geo.height() * 0.8)
            x = parent_geo.x() + (parent_geo.width() - dialog_width) // 2
            y = parent_geo.y() + (parent_geo.height() - dialog_height) // 2
            self.setGeometry(x, y, dialog_width, dialog_height)
        else:
            self.setGeometry(100, 100, 500, 400)
        
        self.init_ui()
        self.animate_open()
    
    def init_ui(self):
        container = QWidget()
        main_layout = QVBoxLayout()
        
        filename_layout = QHBoxLayout()
        filename_label = QLabel("File Name:")
        filename_label.setStyleSheet("color: #333333;")
        self.filename_input = QLineEdit()
        self.filename_input.setStyleSheet("background-color: #FFF8E7; color: #333333; border-radius: 5px; padding: 5px;")
        self.filename_input.setPlaceholderText("Enter file name (without extension)")
        
        filename_layout.addWidget(filename_label)
        filename_layout.addWidget(self.filename_input)
        
        self.content_text = QTextEdit()
        self.content_text.setStyleSheet("background-color: #FFF8E7; color: #333333; border-radius: 5px; padding: 5px;")
        self.content_text.setPlaceholderText("Write your prompt here...")
        
        buttons_layout = QHBoxLayout()
        
        self.save_button = self.create_button("Save", "#F28C38")
        self.save_button.clicked.connect(self.save_prompt)
        
        self.cancel_button = self.create_button("Cancel", "#666666")
        self.cancel_button.clicked.connect(self.close)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(filename_layout)
        main_layout.addWidget(self.content_text)
        main_layout.addLayout(buttons_layout)
        
        container.setLayout(main_layout)
        container.setStyleSheet("background-color: #333333; border-radius: 10px; border: 3px solid #F28C38;")
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(container)
    
    def create_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {color}; color: #333333; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        button.enterEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #333333; border-radius: 10px; padding: 5px; border: 2px solid #FFF8E7;")
        button.leaveEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #333333; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        return button
    
    def save_prompt(self):
        filename = self.filename_input.text().strip()
        content = self.content_text.toPlainText()
        
        if not filename:
            return
        
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        save_dir = "Prompts"
        os.makedirs(save_dir, exist_ok=True)
        
        file_path = os.path.join(save_dir, filename)
        
        try:
            with open(file_path, 'w') as file:
                file.write(content)
            self.close()
        except Exception as e:
            print(f"Error saving file: {e}")
    
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

class PromptViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        if parent:
            parent_geo = parent.geometry()
            dialog_width = int(parent_geo.width() * 0.9)
            dialog_height = int(parent_geo.height() * 0.8)
            x = parent_geo.x() + (parent_geo.width() - dialog_width) // 2
            y = parent_geo.y() + (parent_geo.height() - dialog_height) // 2
            self.setGeometry(x, y, dialog_width, dialog_height)
        else:
            self.setGeometry(100, 100, 700, 500)
        
        self.init_ui()
        self.animate_open()
        self.load_prompts()
    
    def init_ui(self):
        container = QWidget()
        main_layout = QVBoxLayout()
        
        title_label = QLabel("Prompts")
        title_label.setStyleSheet("color: #333333; font-size: 16px; font-weight: bold;")
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #F28C38; width: 2px; }")
        
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #FFF8E7; 
                color: #333333; 
                border-radius: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #D3C7A1;
                background-color: #FFF8E7;
            }
            QListWidget::item:hover {
                background-color: #FFE8C2;
                color: #333333;
            }
            QListWidget::item:selected {
                background-color: #F28C38;
                color: #333333;
            }
            QListWidget::item:selected:hover {
                background-color: #D97A30;
                color: #333333;
            }
        """)
        self.file_list.itemClicked.connect(self.show_file_content)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        self.content_viewer = QTextBrowser()
        self.content_viewer.setStyleSheet("background-color: #FFF8E7; color: #333333; border-radius: 5px; padding: 5px;")
        self.content_viewer.setReadOnly(True)
        self.content_viewer.setPlaceholderText("Select a prompt to view its content")
        
        self.copy_button = self.create_button("Copy Content", "#F28C38")
        self.copy_button.clicked.connect(self.copy_content)
        self.copy_button.setEnabled(False)
        
        right_layout.addWidget(self.content_viewer)
        right_layout.addWidget(self.copy_button)
        right_widget.setLayout(right_layout)
        
        self.splitter.addWidget(self.file_list)
        self.splitter.addWidget(right_widget)
        
        self.splitter.setSizes([30, 70])
        
        self.close_button = self.create_button("Close", "#666666")
        self.close_button.clicked.connect(self.close)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.splitter)
        main_layout.addWidget(self.close_button)
        
        container.setLayout(main_layout)
        container.setStyleSheet("background-color: #333333; border-radius: 10px; border: 3px solid #F28C38;")
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(container)
    
    def create_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {color}; color: #333333; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        button.enterEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #333333; border-radius: 10px; padding: 5px; border: 2px solid #FFF8E7;")
        button.leaveEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #333333; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        return button
    
    def load_prompts(self):
        prompts_dir = "Prompts"
        if not os.path.exists(prompts_dir):
            os.makedirs(prompts_dir)
            with open(os.path.join(prompts_dir, "sample.txt"), "w") as f:
                f.write("This is a sample prompt.\nYou can create your own prompts using the Create option.")
        
        self.file_list.clear()
        
        for filename in sorted(os.listdir(prompts_dir)):
            if filename.endswith('.txt'):
                item = QListWidgetItem(filename)
                item.setData(Qt.UserRole, os.path.join(prompts_dir, filename))
                self.file_list.addItem(item)
    
    def show_file_content(self, item):
        file_path = item.data(Qt.UserRole)
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                self.content_viewer.setPlainText(content)
                self.copy_button.setEnabled(True)
        except Exception as e:
            self.content_viewer.setPlainText(f"Error opening file: {e}")
            self.copy_button.setEnabled(False)
    
    def copy_content(self):
        content = self.content_viewer.toPlainText()
        if content:
            clipboard = QApplication.clipboard()
            clipboard.setText(content)
            self.toast = ToastNotification("Content copied to clipboard!", self)
    
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
        
        self.browser_width = int(self.screen_width * 0.7)
        self.browser_height = int(self.screen_height * 0.6)
        
        new_x = icon_geometry.x() - self.browser_width
        new_y = icon_geometry.y() - self.browser_height + icon_geometry.height() // 2
        
        self.setGeometry(new_x, new_y, self.browser_width, self.browser_height)
        self.init_ui()
        self.animate_open()

    def init_ui(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://claude.ai"))
        self.browser.setStyleSheet("background-color: #333333; border-radius: 10px;")

        self.prompt_button = self.create_button("Prompt", "#666666")
        self.size_button = self.create_button("Size", "#666666")
        self.close_button = self.create_button("Close", "#F28C38")
        self.close_button.clicked.connect(self.close_callback)

        submenu_layout = QHBoxLayout()
        submenu_layout.addWidget(self.prompt_button)
        submenu_layout.addWidget(self.size_button)
        
        submenu_layout.setStretch(0, 1)
        submenu_layout.setStretch(1, 1)
        
        small_width = int(self.screen_width * 0.7)
        small_height = int(self.screen_height * 0.6)
        
        medium_width = int(self.screen_width * 0.8)
        medium_height = int(self.screen_height * 0.7)
        
        large_width = int(self.screen_width * 0.9)
        large_height = int(self.screen_height * 0.8)
        
        self.size_menu = QMenu(self)
        self.size_menu.setStyleSheet("background-color: #333333; color: #FFF8E7; border-radius: 10px; border: 2px solid #F28C38;")

        small_action = self.create_menu_action("Small", "#666666", self.resize_browser, small_width, small_height)
        medium_action = self.create_menu_action("Medium", "#666666", self.resize_browser, medium_width, medium_height)
        large_action = self.create_menu_action("Large", "#666666", self.resize_browser, large_width, large_height)

        self.size_menu.addAction(small_action)
        self.size_menu.addAction(medium_action)
        self.size_menu.addAction(large_action)

        self.size_button.setMenu(self.size_menu)
        
        self.prompt_menu = QMenu(self)
        self.prompt_menu.setStyleSheet("background-color: #333333; color: #FFF8E7; border-radius: 10px; border: 2px solid #666666;")
        
        create_action = self.create_menu_action("Create", "#666666", self.show_prompt_creator)
        open_action = self.create_menu_action("Open", "#666666", self.open_prompt)
        
        self.prompt_menu.addAction(create_action)
        self.prompt_menu.addAction(open_action)
        
        self.prompt_button.setMenu(self.prompt_menu)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(submenu_layout)
        layout.addWidget(self.browser)
        layout.addWidget(self.close_button)
        
        container.setLayout(layout)
        container.setStyleSheet("background-color: #333333; border-radius: 10px; border: 3px solid #F28C38;")

        self.setCentralWidget(container)
        
        self.showEvent = self.on_show

    def on_show(self, event):
        self.size_menu.setFixedWidth(self.size_button.width())
        self.prompt_menu.setFixedWidth(self.prompt_button.width())
        super().showEvent(event)
    
    def create_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {color}; color: #333333; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        button.enterEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #333333; border-radius: 10px; padding: 5px; border: 2px solid #FFF8E7;")
        button.leaveEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #333333; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        return button
    
    def create_menu_action(self, text, color, slot, *args):
        action = QAction(text, self)
        if args:
            action.triggered.connect(lambda: slot(*args))
        else:
            action.triggered.connect(slot)
        action.setData(color)
        return action
    
    def show_prompt_creator(self):
        self.prompt_creator = PromptCreatorDialog(self)
        self.prompt_creator.show()
    
    def open_prompt(self):
        self.prompt_viewer = PromptViewerDialog(self)
        self.prompt_viewer.show()
    
    def resize_browser(self, width, height):
        new_x = self.icon_geometry.x() - width
        new_y = self.icon_geometry.y() - height + self.icon_geometry.height() // 2
        
        new_x = max(0, new_x)
        new_y = max(0, new_y)
        
        self.animated_resize(new_x, new_y, width, height)
    
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
        
        self.setGeometry(screen_geometry.width() - 100, screen_geometry.height() - 180, 80, 80)
        
        self.init_ui(icon_path)

    def init_ui(self, icon_path):
        layout = QVBoxLayout()
        
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setStyleSheet("border-radius: 32px; background-color: rgba(242, 140, 56, 0.5);")
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
    
    icon_path = resource_path("claude.png")
    floating_icon = FloatingIcon(icon_path)
    floating_icon.show()
    
    sys.exit(app.exec())