"""Entry point for the Odoo Production-Operator GUI application.

Usage
-----
    pip install PyQt5
    python main.py
"""

import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from login_window import LoginWindow
from main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Odoo Opérateur de Production")
    app.setFont(QFont("Segoe UI", 10))

    login = LoginWindow()
    if login.exec_() != LoginWindow.Accepted or login.client is None:
        sys.exit(0)

    window = MainWindow(login.client)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
