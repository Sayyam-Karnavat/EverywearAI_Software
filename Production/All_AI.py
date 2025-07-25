import sys
import os
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QGraphicsOpacityEffect, QMenu, QLineEdit, 
                              QTextEdit, QFileDialog, QDialog, QListWidget, QListWidgetItem,
                              QSplitter, QTextBrowser, QMessageBox)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QPixmap, QClipboard
from PySide6.QtCore import Qt, QUrl, QRect, QPropertyAnimation, QEasingCurve, QTimer, QSize
from PySide6.QtGui import QAction
from PySide6.QtWebEngineCore import QWebEngineProfile
import hashlib
import uuid

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
        self.secret_key = "SANYAMsuyashKARNAVATallai"
        
        dialog_width = 400
        dialog_height = 200
        
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - dialog_width) // 2
        y = (screen.height() - dialog_height) // 2
        self.setGeometry(x, y, dialog_width, dialog_height)
        
        self.init_ui()
        self.animate_open()

    def init_ui(self):
        container = QWidget()
        main_layout = QVBoxLayout()
        
        title_label = QLabel("API Token Registration")
        title_label.setStyleSheet("color: #F5F5F5; font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        
        self.token_input = QLineEdit()
        self.token_input.setStyleSheet("background-color: #2A2A2A; color: #F5F5F5; border-radius: 5px; padding: 5px; border: 1px solid #4A4A4A;")
        self.token_input.setPlaceholderText("Paste your API token here")
        
        buttons_layout = QHBoxLayout()
        self.activate_button = self.create_button("Activate", "#F28C38")
        self.activate_button.clicked.connect(self.verify_token)
        self.close_button = self.create_button("Close", "#2A2A2A")
        self.close_button.clicked.connect(QApplication.quit)
        
        buttons_layout.addWidget(self.activate_button)
        buttons_layout.addWidget(self.close_button)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.token_input)
        main_layout.addLayout(buttons_layout)
        
        container.setLayout(main_layout)
        container.setStyleSheet("background-color: #1E1E1E; border-radius: 10px; border: 2px solid #F28C38;")
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(container)

    def create_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #F5F5F5;
                border-radius: 10px;
                padding: 5px;
                border: 2px solid transparent;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: #F5F5F5;
                border: 2px solid #F5F5F5;
            }}
        """)
        return button

    def generate_filename(self, user_secret: str, ext="txt"):
        nonce = uuid.uuid4().hex
        hash_part = hashlib.sha256((nonce + user_secret).encode()).hexdigest()[:16]
        return f"file_{nonce}_{hash_part}.{ext}"

    def validate_filename(self ,filename: str, user_secret: str):
        try:
            parts = filename.split("_")
            if len(parts) != 3:
                return False
            nonce = parts[1]
            hash_in_file = parts[2].split(".")[0]
            expected_hash = hashlib.sha256((nonce + user_secret).encode()).hexdigest()[:16]
            return hash_in_file == expected_hash
        except Exception:
            return False
    
    def verify_token(self):
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "Error", "Please enter an API token.")
            return
        
        # Send verification request to server
        try:

            config_dir = "config"
            os.makedirs(config_dir , exist_ok=True)
            all_files = os.listdir(config_dir)

            if not any(self.validate_filename(filename=filename, user_secret=self.secret_key) for filename in all_files):
                response = requests.post("https://everywearai-website.onrender.com/register", json={"token": token})
                response_data = response.json()
                
                if response_data.get("verified") == "yes":
                    random_filename = self.generate_filename(user_secret=self.secret_key)
                    with open(os.path.join(config_dir, random_filename), "w") as f:
                        f.write(token)
                    self.close()
                    if self.on_success_callback:
                        self.on_success_callback()
                else:
                    QMessageBox.critical(self, "Error", "Invalid API token. Please try again.")
            else:
                if self.on_success_callback:
                    self.on_success_callback()
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
            color: #F5F5F5;
            font-size: 12px;
            font-weight: bold;
        """)
        label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(label)
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 0.9);
                border-radius: 15px;
                border: 2px solid #F28C38;
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

class IconSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        screen_geometry = QApplication.primaryScreen().geometry()
        dialog_width = 450
        dialog_height = 150
        x = (screen_geometry.width() - dialog_width) // 2
        y = (screen_geometry.height() - dialog_height) // 2
        self.setGeometry(x, y, dialog_width, dialog_height)
        
        self.init_ui()
        self.selected_url = None
        self.selected_theme = None
    
    def init_ui(self):
        container = QWidget()
        main_layout = QVBoxLayout()
        
        title_label = QLabel("Select AI Assistant")
        title_label.setStyleSheet("color: #F5F5F5; font-size: 16px; font-weight: bold; text-align: center;")
        title_label.setAlignment(Qt.AlignCenter)
        
        icons_layout = QHBoxLayout()
        
        # ChatGPT button
        self.chatgpt_button = QPushButton()
        self.chatgpt_button.setFixedSize(100, 100)
        self.chatgpt_button.setStyleSheet("""
            QPushButton {
                background-color: #202123;
                border-radius: 10px;
                border: 2px solid #10a37f;
                padding: 5px;
            }
            QPushButton:hover {
                border: 2px solid #F5F5F5;
                background-color: #343541;
            }
        """)
        
        if os.path.exists(resource_path("chatgpt.png")):
            chatgpt_icon = QPixmap(resource_path("chatgpt.png")).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.chatgpt_button.setIcon(chatgpt_icon)
            self.chatgpt_button.setIconSize(QSize(80, 80))
        else:
            self.chatgpt_button.setText("ChatGPT")
            self.chatgpt_button.setStyleSheet(self.chatgpt_button.styleSheet() + "color: #F5F5F5; font-weight: bold;")
        
        chatgpt_label = QLabel("ChatGPT")
        chatgpt_label.setStyleSheet("color: #F5F5F5; text-align: center;")
        chatgpt_label.setAlignment(Qt.AlignCenter)
        
        chatgpt_layout = QVBoxLayout()
        chatgpt_layout.addWidget(self.chatgpt_button)
        chatgpt_layout.addWidget(chatgpt_label)
        
        # Grok button
        self.grok_button = QPushButton()
        self.grok_button.setFixedSize(100, 100)
        self.grok_button.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                border-radius: 10px;
                border: 2px solid #1DA1F2;
                padding: 5px;
            }
            QPushButton:hover {
                border: 2px solid #F5F5F5;
                background-color: #15202B;
            }
        """)
        
        if os.path.exists(resource_path("grok.png")):
            grok_icon = QPixmap(resource_path("grok.png")).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.grok_button.setIcon(grok_icon)
            self.grok_button.setIconSize(QSize(80, 80))
        else:
            self.grok_button.setText("Grok")
            self.grok_button.setStyleSheet(self.grok_button.styleSheet() + "color: #F5F5F5; font-weight: bold;")
        
        grok_label = QLabel("Grok")
        grok_label.setStyleSheet("color: #F5F5F5; text-align: center;")
        grok_label.setAlignment(Qt.AlignCenter)
        
        grok_layout = QVBoxLayout()
        grok_layout.addWidget(self.grok_button)
        grok_layout.addWidget(grok_label)
        
        # Claude button
        self.claude_button = QPushButton()
        self.claude_button.setFixedSize(100, 100)
        self.claude_button.setStyleSheet("""
            QPushButton {
                background-color: #1E1E1E;
                border-radius: 10px;
                border: 2px solid #F28C38;
                padding: 5px;
            }
            QPushButton:hover {
                border: 2px solid #F5F5F5;
                background-color: #2A2A2A;
            }
        """)
        
        if os.path.exists(resource_path("claude.png")):
            claude_icon = QPixmap(resource_path("claude.png")).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.claude_button.setIcon(claude_icon)
            self.claude_button.setIconSize(QSize(80, 80))
        else:
            self.claude_button.setText("Claude")
            self.claude_button.setStyleSheet(self.claude_button.styleSheet() + "color: #F5F5F5; font-weight: bold;")
        
        claude_label = QLabel("Claude")
        claude_label.setStyleSheet("color: #F5F5F5; text-align: center;")
        claude_label.setAlignment(Qt.AlignCenter)
        
        claude_layout = QVBoxLayout()
        claude_layout.addWidget(self.claude_button)
        claude_layout.addWidget(claude_label)
        
        icons_layout.addLayout(chatgpt_layout)
        icons_layout.addLayout(grok_layout)
        icons_layout.addLayout(claude_layout)
        
        self.chatgpt_button.clicked.connect(self.select_chatgpt)
        self.grok_button.clicked.connect(self.select_grok)
        self.claude_button.clicked.connect(self.select_claude)
        
        main_layout.addWidget(title_label)
        main_layout.addLayout(icons_layout)
        
        container.setLayout(main_layout)
        container.setStyleSheet("background-color: #1E1E1E; border-radius: 10px; border: 2px solid #F28C38;")
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(container)
    
    def select_chatgpt(self):
        self.selected_url = "https://chat.openai.com"
        self.selected_theme = {
            "border_color": "#10a37f",
            "button_color": "#10a37f",
            "submenu_color": "#0d846b",
            "size_color": "#0b6d58"
        }
        self.accept()
    
    def select_grok(self):
        self.selected_url = "https://grok.com/"
        self.selected_theme = {
            "border_color": "#1DA1F2",
            "button_color": "#1DA1F2",
            "submenu_color": "#0C7ABF",
            "size_color": "#0A5C8F"
        }
        self.accept()
    
    def select_claude(self):
        self.selected_url = "https://claude.ai"
        self.selected_theme = {
            "border_color": "#F28C38",
            "button_color": "#F28C38",
            "submenu_color": "#D97530",
            "size_color": "#C1622A"
        }
        self.accept()

class PromptCreatorDialog(QDialog):
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.theme = theme if theme else {"button_color": "#10a37f", "border_color": "#10a37f"}
        
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
        filename_label.setStyleSheet("color: #F5F5F5;")
        self.filename_input = QLineEdit()
        self.filename_input.setStyleSheet("background-color: #2A2A2A; color: #F5F5F5; border-radius: 5px; padding: 5px; border: 1px solid #4A4A4A;")
        self.filename_input.setPlaceholderText("Enter file name (without extension)")
        
        filename_layout.addWidget(filename_label)
        filename_layout.addWidget(self.filename_input)
        
        self.content_text = QTextEdit()
        self.content_text.setStyleSheet("background-color: #2A2A2A; color: #F5F5F5; border-radius: 5px; padding: 5px; border: 1px solid #4A4A4A;")
        self.content_text.setPlaceholderText("Write your prompt here...")
        
        buttons_layout = QHBoxLayout()
        
        self.save_button = self.create_button("Save", self.theme["button_color"])
        self.save_button.clicked.connect(self.save_prompt)
        
        self.cancel_button = self.create_button("Cancel", "#2A2A2A")
        self.cancel_button.clicked.connect(self.close)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(filename_layout)
        main_layout.addWidget(self.content_text)
        main_layout.addLayout(buttons_layout)
        
        container.setLayout(main_layout)
        container.setStyleSheet(f"background-color: #1E1E1E; border-radius: 10px; border: 2px solid {self.theme['border_color']};")
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(container)
    
    def create_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {color}; color: #F5F5F5; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        button.enterEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #F5F5F5; border-radius: 10px; padding: 5px; border: 2px solid #F5F5F5;")
        button.leaveEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #F5F5F5; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        return button
    
    def save_prompt(self):
        filename = self.filename_input.text().strip()
        content = self.content_text.toPlainText()
        
        if not filename:
            QMessageBox.warning(self, "Error", "Please enter a file name.")
            return
        
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        save_dir = resource_path("Prompts")
        os.makedirs(save_dir, exist_ok=True)
        
        file_path = os.path.join(save_dir, filename)
        
        try:
            with open(file_path, 'w') as file:
                file.write(content)
            self.close()
        except Exception as e:
            print(f"Error saving file: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save prompt: {e}")
    
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
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.theme = theme if theme else {"button_color": "#10a37f", "border_color": "#10a37f"}
        
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
        title_label.setStyleSheet("color: #F5F5F5; font-size: 16px; font-weight: bold;")
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {self.theme['submenu_color']}; width: 2px; }}")
        
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #2A2A2A; 
                color: #F5F5F5; 
                border-radius: 5px;
                outline: none;
                border: 1px solid #4A4A4A;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #4A4A4A;
                background-color: #2A2A2A;
            }
            QListWidget::item:hover {
                background-color: #3A3A3A;
                color: #F5F5F5;
            }
            QListWidget::item:selected {
                background-color: #F28C38;
                color: #F5F5F5;
            }
            QListWidget::item:selected:hover {
                background-color: #E07B30;
                color: #F5F5F5;
            }
        """)
        self.file_list.itemClicked.connect(self.show_file_content)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        self.content_viewer = QTextBrowser()
        self.content_viewer.setStyleSheet("background-color: #2A2A2A; color: #F5F5F5; border-radius: 5px; padding: 5px; border: 1px solid #4A4A4A;")
        self.content_viewer.setReadOnly(True)
        self.content_viewer.setPlaceholderText("Select a prompt to view its content")
        
        self.copy_button = self.create_button("Copy Content", self.theme["button_color"])
        self.copy_button.clicked.connect(self.copy_content)
        self.copy_button.setEnabled(False)
        
        right_layout.addWidget(self.content_viewer)
        right_layout.addWidget(self.copy_button)
        right_widget.setLayout(right_layout)
        
        self.splitter.addWidget(self.file_list)
        self.splitter.addWidget(right_widget)
        
        self.splitter.setSizes([30, 70])
        
        self.close_button = self.create_button("Close", "#2A2A2A")
        self.close_button.clicked.connect(self.close)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.splitter)
        main_layout.addWidget(self.close_button)
        
        container.setLayout(main_layout)
        container.setStyleSheet(f"background-color: #1E1E1E; border-radius: 10px; border: 2px solid {self.theme['border_color']};")
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(container)
    
    def create_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {color}; color: #F5F5F5; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        button.enterEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #F5F5F5; border-radius: 10px; padding: 5px; border: 2px solid #F5F5F5;")
        button.leaveEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #F5F5F5; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        return button
    
    def load_prompts(self):
        prompts_dir = resource_path("Prompts")
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
    def __init__(self, icon_geometry, close_callback, url="https://www.google.com", theme=None):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.close_callback = close_callback
        self.icon_geometry = icon_geometry
        self.url = url
        self.theme = theme if theme else {
            "border_color": "#10a37f",
            "button_color": "#10a37f",
            "submenu_color": "#0d846b",
            "size_color": "#0b6d58"
        }
        
        self.screen = QApplication.primaryScreen()
        self.screen_geometry = self.screen.availableGeometry()
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        
        self.browser_width = int(self.screen_width * 0.5)
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
        self.browser.setUrl(QUrl(self.url))
        self.browser.setStyleSheet("background-color: #1E1E1E; border-radius: 10px;")

        self.prompt_button = self.create_button("Prompt", self.theme["submenu_color"])
        self.size_button = self.create_button("Size", self.theme["size_color"])
        # self.back_button = self.create_button("Back", "#2A2A2A")
        # self.back_button.clicked.connect(self.return_to_selection)
        self.close_button = self.create_button("Close", self.theme["button_color"])
        self.close_button.clicked.connect(self.close_callback)

        submenu_layout = QHBoxLayout()
        submenu_layout.addWidget(self.prompt_button)
        submenu_layout.addWidget(self.size_button)
        # submenu_layout.addWidget(self.back_button)
        
        submenu_layout.setStretch(0, 1)
        submenu_layout.setStretch(1, 1)
        submenu_layout.setStretch(2, 1)
        
        small_width = int(self.screen_width * 0.5)
        small_height = int(self.screen_height * 0.6)
        medium_width = int(self.screen_width * 0.7)
        medium_height = int(self.screen_height * 0.8)
        large_width = int(self.screen_width * 0.8)
        large_height = int(self.screen_height * 0.9)
        
        self.size_menu = QMenu(self)
        self.size_menu.setStyleSheet(f"background-color: #1E1E1E; color: #F5F5F5; border-radius: 10px; border: 2px solid {self.theme['size_color']};")

        small_action = self.create_menu_action("Small", self.theme["size_color"], self.resize_browser, small_width, small_height)
        medium_action = self.create_menu_action("Medium", self.theme["size_color"], self.resize_browser, medium_width, medium_height)
        large_action = self.create_menu_action("Large", self.theme["size_color"], self.resize_browser, large_width, large_height)

        self.size_menu.addAction(small_action)
        self.size_menu.addAction(medium_action)
        self.size_menu.addAction(large_action)
        self.size_button.setMenu(self.size_menu)
        
        self.prompt_menu = QMenu(self)
        self.prompt_menu.setStyleSheet(f"background-color: #1E1E1E; color: #F5F5F5; border-radius: 10px; border: 2px solid {self.theme['submenu_color']};")
        
        create_action = self.create_menu_action("Create", self.theme["submenu_color"], self.show_prompt_creator)
        open_action = self.create_menu_action("Open", self.theme["submenu_color"], self.open_prompt)
        
        self.prompt_menu.addAction(create_action)
        self.prompt_menu.addAction(open_action)
        self.prompt_button.setMenu(self.prompt_menu)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addLayout(submenu_layout)
        layout.addWidget(self.browser)
        layout.addWidget(self.close_button)
        
        container.setLayout(layout)
        container.setStyleSheet(f"background-color: #1E1E1E; border-radius: 10px; border: 2px solid {self.theme['border_color']};")
        self.setCentralWidget(container)
        
        self.showEvent = self.on_show

    def on_show(self, event):
        self.size_menu.setFixedWidth(self.size_button.width())
        self.prompt_menu.setFixedWidth(self.prompt_button.width())
        super().showEvent(event)
    
    def create_button(self, text, color):
        button = QPushButton(text)
        button.setStyleSheet(f"background-color: {color}; color: #F5F5F5; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
        button.enterEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #F5F5F5; border-radius: 10px; padding: 5px; border: 2px solid #F5F5F5;")
        button.leaveEvent = lambda event: button.setStyleSheet(f"background-color: {color}; color: #F5F5F5; border-radius: 10px; padding: 5px; border: 2px solid transparent;")
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
        self.prompt_creator = PromptCreatorDialog(self, self.theme)
        self.prompt_creator.show()
    
    def open_prompt(self):
        self.prompt_viewer = PromptViewerDialog(self, self.theme)
        self.prompt_viewer.show()
    
    def return_to_selection(self):
        self.animate_close(self.hide)
    
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
        self.setGeometry(screen_geometry.width() - 100, screen_geometry.height() - 100, 80, 80)
        self.secret_key = "SANYAMsuyashKARNAVATallai"

        self.icon_path = icon_path
        self.browser_window = None
        self.selected_url = None
        self.selected_theme = None
        self.check_token()

    def init_ui(self):
        layout = QVBoxLayout()
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QPixmap(self.icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setStyleSheet("border-radius: 32px; background-color: rgba(30, 30, 30, 0.5);")
        layout.addWidget(self.icon_label)
        self.setLayout(layout)
        self.icon_label.mousePressEvent = self.toggle_browser

    def validate_filename(self, filename: str, user_secret: str):
        try:
            parts = filename.split("_")
            if len(parts) != 3:
                return False
            nonce = parts[1]
            hash_in_file = parts[2].split(".")[0]
            expected_hash = hashlib.sha256((nonce + user_secret).encode()).hexdigest()[:16]
            return hash_in_file == expected_hash
        except Exception:
            return False

    def check_token(self):
        config_dir = "config"
        os.makedirs(config_dir, exist_ok=True)
        all_files = os.listdir(config_dir)
        
        # Check if any file in config directory is valid
        if any(self.validate_filename(filename=filename, user_secret=self.secret_key) for filename in all_files):
            self.show_main_ui()
        else:
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
            if not self.selected_url:
                selection_dialog = IconSelectionDialog()
                if selection_dialog.exec() == QDialog.Accepted:
                    self.selected_url = selection_dialog.selected_url
                    self.selected_theme = selection_dialog.selected_theme
                else:
                    return
            
            self.browser_window = FloatingBrowser(
                self.geometry(), 
                self.close_application, 
                self.selected_url, 
                self.selected_theme
            )
            self.browser_window.show()
    
    def close_application(self):
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    icon_path = resource_path("icon.png")
    floating_icon = FloatingIcon(icon_path)
    
    sys.exit(app.exec())