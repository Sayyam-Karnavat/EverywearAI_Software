import sys
import os
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QGraphicsOpacityEffect, QMenu, QLineEdit, 
                              QTextEdit, QFileDialog, QDialog, QListWidget, QListWidgetItem,
                              QSplitter, QTextBrowser, QMessageBox)
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

class RegistrationDialog(QDialog):
    def __init__(self, parent=None, on_success_callback=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.on_success_callback = on_success_callback
        
        # Set dialog size
        dialog_width = 400
        dialog_height = 200
        
        # Center dialog on the screen
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - dialog_width) // 2
        y = (screen.height() - dialog_height) // 2
        self.setGeometry(x, y, dialog_width, dialog_height)
        
        self.init_ui()
        self.animate_open()

    def init_ui(self):
        container = QWidget()
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("API Token Registration")
        title_label.setStyleSheet("color: #ECECF1; font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # API token input
        self.token_input = QLineEdit()
        self.token_input.setStyleSheet("background-color: #40414F; color: #ECECF1; border-radius: 5px; padding: 5px;")
        self.token_input.setPlaceholderText("Paste your API token here")
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.activate_button = self.create_button("Activate", "#10A37F")
        self.activate_button.clicked.connect(self.verify_token)
        self.close_button = self.create_button("Close", "#40414F")
        self.close_button.clicked.connect(QApplication.quit)
        
        buttons_layout.addWidget(self.activate_button)
        buttons_layout.addWidget(self.close_button)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.token_input)
        main_layout.addLayout(buttons_layout)
        
        container.setLayout(main_layout)
        container.setStyleSheet("background-color: #343541; border-radius: 10px; border: 3px solid #10A37F;")
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(container)

    def create_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {color}; color: #ECECF1; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        button.enterEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #ECECF1; border-radius: 10px; padding: 5px; border: 2px solid #ECECF1;")
        button.leaveEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #ECECF1; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        return button

    def verify_token(self):
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "Error", "Please enter an API token.")
            return
        
        # Send verification request to server
        try:
            response = requests.post("https://c38718d276c1.ngrok-free.app/verify", json={"token": token})
            response_data = response.json()
            print(f"Response received: {response_data}")
            
            if response_data.get("verified") == "yes":
                # Save token to file
                config_dir = "config"
                os.makedirs(config_dir, exist_ok=True)
                with open(os.path.join(config_dir, "api_token.txt"), "w") as f:
                    f.write(token)
                self.close()
                if self.on_success_callback:
                    self.on_success_callback()
            else:
                QMessageBox.critical(self, "Error", "Invalid API token. Please try again.")
        except Exception as e:
            print(f"Verification error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to verify token: {e}")

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

class ToastNotification(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
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
            color: #ECECF1;
            font-size: 12px;
            font-weight: bold;
        """)
        label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(label)
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(52, 53, 65, 0.9);
                border-radius: 15px;
                border: 2px solid #10A37F;
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
        filename_label.setStyleSheet("color: #ECECF1;")
        self.filename_input = QLineEdit()
        self.filename_input.setStyleSheet("background-color: #40414F; color: #ECECF1; border-radius: 5px; padding: 5px;")
        self.filename_input.setPlaceholderText("Enter file name (without extension)")
        
        filename_layout.addWidget(filename_label)
        filename_layout.addWidget(self.filename_input)
        
        self.content_text = QTextEdit()
        self.content_text.setStyleSheet("background-color: #40414F; color: #ECECF1; border-radius: 5px; padding: 5px;")
        self.content_text.setPlaceholderText("Write your prompt here...")
        
        buttons_layout = QHBoxLayout()
        
        self.save_button = self.create_button("Save", "#10A37F")
        self.save_button.clicked.connect(self.save_prompt)
        
        self.cancel_button = self.create_button("Cancel", "#40414F")
        self.cancel_button.clicked.connect(self.close)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(filename_layout)
        main_layout.addWidget(self.content_text)
        main_layout.addLayout(buttons_layout)
        
        container.setLayout(main_layout)
        container.setStyleSheet("background-color: #343541; border-radius: 10px; border: 3px solid #10A37F;")
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(container)
    
    def create_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {color}; color: #ECECF1; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        button.enterEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #ECECF1; border-radius: 10px; padding: 5px; border: 2px solid #ECECF1;")
        button.leaveEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #ECECF1; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
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
        title_label.setStyleSheet("color: #ECECF1; font-size: 16px; font-weight: bold;")
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #40414F; width: 2px; }")
        
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #40414F; 
                color: #ECECF1; 
                border-radius: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3e3e3e;
                background-color: #40414F;
            }
            QListWidget::item:hover {
                background-color: #4a4a4a;
                color: #ECECF1;
            }
            QListWidget::item:selected {
                background-color: #10A37F;
                color: #ECECF1;
            }
            QListWidget::item:selected:hover {
                background-color: #40414F;
                color: #ECECF1;
            }
        """)
        self.file_list.itemClicked.connect(self.show_file_content)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        self.content_viewer = QTextBrowser()
        self.content_viewer.setStyleSheet("background-color: #40414F; color: #ECECF1; border-radius: 5px; padding: 5px;")
        self.content_viewer.setReadOnly(True)
        self.content_viewer.setPlaceholderText("Select a prompt to view its content")
        
        self.copy_button = self.create_button("Copy Content", "#10A37F")
        self.copy_button.clicked.connect(self.copy_content)
        self.copy_button.setEnabled(False)
        
        right_layout.addWidget(self.content_viewer)
        right_layout.addWidget(self.copy_button)
        right_widget.setLayout(right_layout)
        
        self.splitter.addWidget(self.file_list)
        self.splitter.addWidget(right_widget)
        
        self.splitter.setSizes([30, 70])
        
        self.close_button = self.create_button("Close", "#40414F")
        self.close_button.clicked.connect(self.close)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.splitter)
        main_layout.addWidget(self.close_button)
        
        container.setLayout(main_layout)
        container.setStyleSheet("background-color: #343541; border-radius: 10px; border: 3px solid #10A37F;")
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(container)
    
    def create_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {color}; color: #ECECF1; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        button.enterEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #ECECF1; border-radius: 10px; padding: 5px; border: 2px solid #ECECF1;")
        button.leaveEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #ECECF1; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
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
        new_y = icon_geometry.y() - self.browser_height + self.icon_geometry.height() // 2
        
        self.setGeometry(new_x, new_y, self.browser_width, self.browser_height)
        self.init_ui()
        self.animate_open()

    def init_ui(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://chat.openai.com"))
        self.browser.setStyleSheet("background-color: #343541; border-radius: 10px;")

        self.prompt_button = self.create_button("Prompt", "#40414F")
        self.size_button = self.create_button("Size", "#40414F")
        self.close_button = self.create_button("Close", "#10A37F")
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
        self.size_menu.setStyleSheet("background-color: #343541; color: #ECECF1; border-radius: 10px; border: 2px solid #40414F;")

        small_action = self.create_menu_action("Small", "#40414F", self.resize_browser, small_width, small_height)
        medium_action = self.create_menu_action("Medium", "#40414F", self.resize_browser, medium_width, medium_height)
        large_action = self.create_menu_action("Large", "#40414F", self.resize_browser, large_width, large_height)

        self.size_menu.addAction(small_action)
        self.size_menu.addAction(medium_action)
        self.size_menu.addAction(large_action)

        self.size_button.setMenu(self.size_menu)
        
        self.prompt_menu = QMenu(self)
        self.prompt_menu.setStyleSheet("background-color: #343541; color: #ECECF1; border-radius: 10px; border: 2px solid #40414F;")
        
        create_action = self.create_menu_action("Create", "#40414F", self.show_prompt_creator)
        open_action = self.create_menu_action("Open", "#40414F", self.open_prompt)
        
        self.prompt_menu.addAction(create_action)
        self.prompt_menu.addAction(open_action)
        
        self.prompt_button.setMenu(self.prompt_menu)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(submenu_layout)
        layout.addWidget(self.browser)
        layout.addWidget(self.close_button)
        
        container.setLayout(layout)
        container.setStyleSheet("background-color: #343541; border-radius: 10px; border: 3px solid #10A37F;")

        self.setCentralWidget(container)
        
        self.showEvent = self.on_show

    def on_show(self, event):
        self.size_menu.setFixedWidth(self.size_button.width())
        self.prompt_menu.setFixedWidth(self.prompt_button.width())
        super().showEvent(event)
    
    def create_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {color}; color: #ECECF1; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        button.enterEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #ECECF1; border-radius: 10px; padding: 5px; border: 2px solid #ECECF1;")
        button.leaveEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #ECECF1; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
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
        
        self.icon_path = icon_path
        self.check_token()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QPixmap(self.icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setStyleSheet("border-radius: 32px; background-color: rgba(52, 53, 65, 0.5);")
        layout.addWidget(self.icon_label)
        
        self.setLayout(layout)
        self.icon_label.mousePressEvent = self.toggle_browser
        
        self.browser_window = None

    def check_token(self):
        config_dir = "config"
        token_file = os.path.join(config_dir, "api_token.txt")
        
        if os.path.exists(token_file):
            try:
                with open(token_file, "r") as f:
                    token = f.read().strip()
                if token:
                    self.verify_token(token)
                else:
                    self.show_registration()
            except Exception as e:
                print(f"Error reading token: {e}")
                self.show_registration()
        else:
            self.show_registration()

    def verify_token(self, token):
        try:
            response = requests.post("https://c38718d276c1.ngrok-free.app/verify", json={"token": token})
            response_data = response.json()
            print(f"Response received: {response_data}")
            
            if response_data.get("verified") == "yes":
                self.show_main_ui()
            else:
                QMessageBox.critical(self, "Error", "Invalid API token. Please enter a valid token.")
                # Delete invalid token file
                config_dir = "config"
                token_file = os.path.join(config_dir, "api_token.txt")
                if os.path.exists(token_file):
                    os.remove(token_file)
                self.show_registration()
        except Exception as e:
            print(f"Verification error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to verify token: {e}")
            self.show_registration()

    def show_registration(self):
        self.registration_dialog = RegistrationDialog(self, self.show_main_ui)
        self.registration_dialog.show()

    def show_main_ui(self):
        self.init_ui()
        self.show()

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
    
    icon_path = resource_path("chatgpt.png")
    floating_icon = FloatingIcon(icon_path)
    
    sys.exit(app.exec())