# run.py
import sys
import os
import json
import requests
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from Icon import DraggableIcon



if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon = DraggableIcon()
    icon.show()
    sys.exit(app.exec())
