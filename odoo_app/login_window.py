"""F1 – Login window."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from odoo_client import OdooClient


class LoginWindow(QDialog):
    """Modal login dialog that authenticates against an Odoo server."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.client: OdooClient | None = None
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        self.setWindowTitle("Connexion Odoo – Opérateur de production")
        self.setMinimumWidth(420)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setSpacing(16)
        root.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("🔐  Connexion à l'ERP Odoo")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        # Form
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(10)

        self._url_edit = QLineEdit("http://localhost:8069")
        self._db_edit = QLineEdit()
        self._user_edit = QLineEdit("production")
        self._pwd_edit = QLineEdit()
        self._pwd_edit.setEchoMode(QLineEdit.Password)

        for lbl, widget in [
            ("URL du serveur :", self._url_edit),
            ("Base de données :", self._db_edit),
            ("Identifiant :", self._user_edit),
            ("Mot de passe :", self._pwd_edit),
        ]:
            form.addRow(lbl, widget)

        root.addLayout(form)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn_connect = QPushButton("Se connecter")
        self._btn_connect.setDefault(True)
        self._btn_connect.setFixedWidth(140)
        self._btn_connect.clicked.connect(self._on_connect)
        btn_row.addWidget(self._btn_connect)
        root.addLayout(btn_row)

        # Status label
        self._status = QLabel("")
        self._status.setAlignment(Qt.AlignCenter)
        self._status.setStyleSheet("color: #c0392b;")
        root.addWidget(self._status)

        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog { background: #f4f6f9; }
            QLabel  { color: #2c3e50; }
            QLineEdit {
                padding: 6px 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
            }
            QLineEdit:focus { border: 1px solid #3498db; }
            QPushButton {
                background: #2980b9;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover  { background: #3498db; }
            QPushButton:pressed { background: #1a5276; }
        """)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_connect(self):
        url = self._url_edit.text().strip()
        db = self._db_edit.text().strip()
        user = self._user_edit.text().strip()
        pwd = self._pwd_edit.text()

        if not all([url, db, user, pwd]):
            self._status.setText("Veuillez remplir tous les champs.")
            return

        self._btn_connect.setEnabled(False)
        self._status.setText("Connexion en cours…")

        try:
            client = OdooClient()
            client.connect(url, db, user, pwd)
            self.client = client
            self.accept()
        except Exception as exc:
            self._status.setText(str(exc))
            QMessageBox.critical(self, "Erreur de connexion", str(exc))
        finally:
            self._btn_connect.setEnabled(True)
