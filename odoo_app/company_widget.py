"""F2 – Company profile widget."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from odoo_client import OdooClient


class CompanyWidget(QWidget):
    """Displays the company profile fetched from Odoo."""

    def __init__(self, client: OdooClient, parent=None):
        super().__init__(parent)
        self._client = client
        self._build_ui()
        self._load()

    # ------------------------------------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("🏢  Fiche Entreprise")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        vbox = QVBoxLayout(container)
        vbox.setSpacing(16)

        # Logo
        self._logo_label = QLabel()
        self._logo_label.setAlignment(Qt.AlignCenter)
        self._logo_label.setFixedHeight(120)
        vbox.addWidget(self._logo_label)

        # Info box
        box = QGroupBox("Informations générales")
        box.setFont(QFont("Segoe UI", 10))
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(8)

        self._fields: dict[str, QLabel] = {}
        for key, label in [
            ("name", "Raison sociale"),
            ("vat", "N° TVA"),
            ("street", "Adresse"),
            ("street2", "Complément"),
            ("city", "Ville"),
            ("zip", "Code postal"),
            ("country", "Pays"),
            ("phone", "Téléphone"),
            ("email", "E-mail"),
            ("website", "Site web"),
        ]:
            lbl = QLabel()
            lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            lbl.setWordWrap(True)
            form.addRow(f"<b>{label} :</b>", lbl)
            self._fields[key] = lbl

        vbox.addWidget(box)
        vbox.addStretch()

    # ------------------------------------------------------------------

    def _load(self):
        try:
            data = self._client.get_company()
        except Exception as exc:
            self._logo_label.setText(f"Erreur : {exc}")
            return

        def _val(key):
            v = data.get(key)
            if isinstance(v, list):
                return str(v[1]) if len(v) > 1 else ""
            return str(v) if v else "—"

        self._fields["name"].setText(_val("name"))
        self._fields["vat"].setText(_val("vat"))
        self._fields["street"].setText(_val("street"))
        self._fields["street2"].setText(_val("street2"))
        self._fields["city"].setText(_val("city"))
        self._fields["zip"].setText(_val("zip"))
        self._fields["country"].setText(_val("country_id"))
        self._fields["phone"].setText(_val("phone"))
        self._fields["email"].setText(_val("email"))
        self._fields["website"].setText(_val("website"))

        logo_bytes = OdooClient.decode_image(data.get("logo"))
        if logo_bytes:
            pix = QPixmap()
            pix.loadFromData(logo_bytes)
            self._logo_label.setPixmap(
                pix.scaledToHeight(110, Qt.SmoothTransformation)
            )
        else:
            self._logo_label.setText("(pas de logo)")
