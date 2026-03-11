"""F3 – Products list widget."""

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from odoo_client import OdooClient

_IMG_SIZE = 64


class ProductsWidget(QWidget):
    """Shows the product catalogue with an image column."""

    def __init__(self, client: OdooClient, parent=None):
        super().__init__(parent)
        self._client = client
        self._all_rows: list[dict] = []
        self._build_ui()
        self._load()

    # ------------------------------------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Header row
        header = QHBoxLayout()
        title = QLabel("📦  Liste des Produits")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        self._search = QLineEdit()
        self._search.setPlaceholderText("Rechercher un produit…")
        self._search.setFixedWidth(220)
        self._search.textChanged.connect(self._filter)
        header.addWidget(self._search)

        btn_refresh = QPushButton("↻ Actualiser")
        btn_refresh.clicked.connect(self._load)
        header.addWidget(btn_refresh)

        layout.addLayout(header)

        # Table
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels([
            "Image", "Référence", "Nom", "Catégorie", "Prix", "Unité",
        ])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setDefaultSectionSize(_IMG_SIZE + 4)
        self._table.setColumnWidth(0, _IMG_SIZE + 8)
        self._table.setColumnWidth(1, 100)
        self._table.setColumnWidth(2, 260)
        self._table.setColumnWidth(3, 160)
        self._table.setColumnWidth(4, 80)
        layout.addWidget(self._table)

        self._status = QLabel("")
        self._status.setStyleSheet("color: grey; font-style: italic;")
        layout.addWidget(self._status)

    # ------------------------------------------------------------------

    def _load(self):
        self._status.setText("Chargement…")
        self._table.setRowCount(0)
        try:
            self._all_rows = self._client.get_products()
            self._populate(self._all_rows)
            self._status.setText(f"{len(self._all_rows)} produit(s) chargé(s).")
        except Exception as exc:
            self._status.setText(f"Erreur : {exc}")

    def _filter(self, text: str):
        text = text.lower()
        filtered = [
            r for r in self._all_rows
            if text in (r.get("name") or "").lower()
            or text in (r.get("default_code") or "").lower()
        ]
        self._populate(filtered)

    def _populate(self, rows: list[dict]):
        self._table.setRowCount(0)
        for row_data in rows:
            row = self._table.rowCount()
            self._table.insertRow(row)

            # Image
            img_bytes = OdooClient.decode_image(row_data.get("image_128"))
            img_lbl = QLabel()
            img_lbl.setAlignment(Qt.AlignCenter)
            if img_bytes:
                pix = QPixmap()
                pix.loadFromData(img_bytes)
                img_lbl.setPixmap(
                    pix.scaled(
                        _IMG_SIZE, _IMG_SIZE,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                )
            else:
                img_lbl.setText("—")
            self._table.setCellWidget(row, 0, img_lbl)

            # Text columns
            ref = row_data.get("default_code") or "—"
            name = row_data.get("name") or "—"
            categ = row_data.get("categ_id")
            categ_name = categ[1] if isinstance(categ, list) and len(categ) > 1 else "—"
            price = f"{row_data.get('list_price', 0):.2f} €"
            uom = row_data.get("uom_id")
            uom_name = uom[1] if isinstance(uom, list) and len(uom) > 1 else "—"

            for col, val in enumerate([ref, name, categ_name, price, uom_name], start=1):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self._table.setItem(row, col, item)
