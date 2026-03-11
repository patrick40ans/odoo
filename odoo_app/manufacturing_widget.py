"""F4 + F5 – Manufacturing Orders widget."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from odoo_client import OdooClient

_STATE_COLORS = {
    "confirmed": "#f39c12",
    "progress":  "#2980b9",
    "done":      "#27ae60",
    "cancel":    "#95a5a6",
}


class ManufacturingWidget(QWidget):
    """Lists Manufacturing Orders (F4) and allows qty updates for confirmed OFs (F5)."""

    def __init__(self, client: OdooClient, parent=None):
        super().__init__(parent)
        self._client = client
        self._rows: list[dict] = []
        self._build_ui()
        self._load()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        title = QLabel("🏭  Ordres de Fabrication")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        lbl_state = QLabel("État :")
        header.addWidget(lbl_state)
        self._state_combo = QComboBox()
        self._state_combo.addItem("Tous les états", "")
        for key, label in OdooClient.MO_STATES.items():
            self._state_combo.addItem(label, key)
        self._state_combo.currentIndexChanged.connect(self._load)
        header.addWidget(self._state_combo)

        btn_refresh = QPushButton("↻ Actualiser")
        btn_refresh.clicked.connect(self._load)
        header.addWidget(btn_refresh)

        layout.addLayout(header)

        # Table
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels([
            "N° OF", "Produit", "Qté commandée",
            "Qté produite", "État", "Action",
        ])
        self._table.horizontalHeader().setStretchLastSection(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setColumnWidth(0, 110)
        self._table.setColumnWidth(1, 260)
        self._table.setColumnWidth(2, 110)
        self._table.setColumnWidth(3, 110)
        self._table.setColumnWidth(4, 100)
        self._table.setColumnWidth(5, 140)
        layout.addWidget(self._table)

        self._status = QLabel("")
        self._status.setStyleSheet("color: grey; font-style: italic;")
        layout.addWidget(self._status)

        # Hint
        hint = QLabel(
            "💡 Pour les OF <b>Confirmé</b>, cliquez sur « Produire » "
            "pour saisir la quantité produite."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------

    def _load(self):
        self._status.setText("Chargement…")
        self._table.setRowCount(0)
        state = self._state_combo.currentData()
        try:
            self._rows = self._client.get_manufacturing_orders(state or None)
            self._populate()
            self._status.setText(f"{len(self._rows)} OF chargé(s).")
        except Exception as exc:
            self._status.setText(f"Erreur : {exc}")

    def _populate(self):
        self._table.setRowCount(0)
        for mo in self._rows:
            row = self._table.rowCount()
            self._table.insertRow(row)

            state = mo.get("state", "")
            color = QColor(_STATE_COLORS.get(state, "#ecf0f1"))

            product = mo.get("product_id")
            product_name = product[1] if isinstance(product, list) and len(product) > 1 else "—"

            for col, val in enumerate([
                mo.get("name", "—"),
                product_name,
                str(mo.get("product_qty", 0)),
                str(mo.get("qty_producing", 0)),
                OdooClient.MO_STATES.get(state, state),
            ]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                item.setBackground(color)
                self._table.setItem(row, col, item)

            # Action button – only for "confirmed" MOs
            if state == "confirmed":
                btn = QPushButton("Produire")
                btn.setAccessibleName("Produire cet ordre de fabrication")
                btn.setStyleSheet(
                    "background:#b7590a; color:white; border-radius:3px; padding:4px 8px;"
                )
                mo_id = mo["id"]
                qty_ordered = mo.get("product_qty", 0)
                btn.clicked.connect(
                    lambda checked, _id=mo_id, _qty=qty_ordered: self._on_produce(_id, _qty)
                )
                self._table.setCellWidget(row, 5, btn)

    # ------------------------------------------------------------------
    # F5 – Produce dialog
    # ------------------------------------------------------------------

    def _on_produce(self, mo_id: int, qty_ordered: float):
        dlg = _ProduceDialog(qty_ordered, self)
        if dlg.exec_() != QDialog.Accepted:
            return

        qty = dlg.quantity()
        try:
            self._client.update_mo_quantity(mo_id, qty)
            if qty >= qty_ordered:
                # All products manufactured → mark as done
                self._client.produce_mo(mo_id, qty)
                QMessageBox.information(
                    self, "OF terminé",
                    f"L'OF a été marqué <b>Fait</b> (qté : {qty}).",
                )
            else:
                # Partial production → move to "En cours"
                self._client.set_mo_in_progress(mo_id, qty)
                QMessageBox.information(
                    self, "OF en cours",
                    f"L'OF est passé à l'état <b>En cours</b> (qté produite : {qty} / {qty_ordered}).",
                )
            self._load()
        except Exception as exc:
            QMessageBox.critical(self, "Erreur", str(exc))


class _ProduceDialog(QDialog):
    """Small dialog to enter the produced quantity."""

    def __init__(self, qty_ordered: float, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Saisie de la quantité produite")
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        self._spin = QDoubleSpinBox()
        self._spin.setMinimum(0.01)
        self._spin.setMaximum(qty_ordered * 10)
        self._spin.setValue(qty_ordered)
        self._spin.setDecimals(2)
        form.addRow("Quantité produite :", self._spin)
        layout.addLayout(form)

        note = QLabel(
            f"Quantité commandée : <b>{qty_ordered}</b><br>"
            "Si qté produite ≥ qté commandée → <b>Fait</b><br>"
            "Sinon → <b>En cours</b>"
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def quantity(self) -> float:
        return self._spin.value()
