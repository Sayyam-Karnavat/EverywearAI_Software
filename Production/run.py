# run.py
import sys
import os
import json
import requests
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from Icon import DraggableIcon

# Configuration
SERVER_URL = "http://127.0.0.1:1111/validate_token"  # Replace with actual server API
TOKEN_FILE = "token.json"  # Local storage for authenticated users


# First check if token file exists or not and check its validity
def validate_token_from_file():
    """Check if token file exists and validate it."""
    if os.path.exists(TOKEN_FILE):
        try:
            # Open and read the stored token
            with open(TOKEN_FILE, "r") as file:
                token_data = json.load(file)

            # Ensure token_data contains "token" key
            if "token" in token_data:
                validity_response = check_token_validity(token_data["token"])
                if validity_response:
                    return 1  # Valid token
                else:
                    os.remove(TOKEN_FILE)  # Remove invalid token file
                    return -1  # Invalid token
            else:
                os.remove(TOKEN_FILE)  # Corrupt token file, delete it
                return -1

        except Exception as e:
            print(f"Error reading token file: {e}")
            return -1  # Prevent any unexpected errors

    else:
        print("Token file does not exist!")
        return 0  # File does not exist


def check_token_validity(token):
    """Check the token with the server."""
    try:
        response = requests.post(SERVER_URL, json={"token": token}, timeout=5)

        if response.status_code == 200 and response.json().get("valid") == "success":
            return True
    except requests.exceptions.RequestException as e:
        print(f"Server connection error: {e}")
    
    return False


class AuthWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Access Token")
        self.setFixedSize(400, 200)
        
        # UI Elements
        layout = QVBoxLayout(self)
        self.label = QLabel("Enter your access token:", self)
        self.token_input = QLineEdit(self)
        self.token_input.setPlaceholderText("Enter token here")
        self.token_input.setEchoMode(QLineEdit.Password)  # Hide input

        self.submit_button = QPushButton("Validate", self)
        self.submit_button.clicked.connect(self.validate_user)

        layout.addWidget(self.label)
        layout.addWidget(self.token_input)
        layout.addWidget(self.submit_button)

    def validate_user(self):
        """Validate the token entered by the user."""
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "Error", "Token cannot be empty!")
            return

        if check_token_validity(token):
            # Save the validated token
            with open(TOKEN_FILE, "w") as file:
                json.dump({"token": token}, file)

            self.accept()  # Close auth window and start main app
        else:
            QMessageBox.critical(self, "Invalid Token", "The token you entered is not valid.")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    result = validate_token_from_file()

    # Case 1: If token is valid, launch the main app
    if result == 1:
        icon = DraggableIcon()
        icon.show()
        sys.exit(app.exec())

    # Case 2: If token file does not exist, show auth window
    elif result == 0:
        auth_window = AuthWindow()
        if auth_window.exec() != QDialog.Accepted:
            sys.exit(0)  # Exit if authentication fails

    # Case 3: If token is invalid, delete file and exit
    elif result == -1:
        print("Invalid token. Exiting...")
        sys.exit(0)
