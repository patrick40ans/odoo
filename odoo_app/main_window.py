"""Main window with a tab widget holding all feature tabs."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QLabel,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from company_widget import CompanyWidget
from manufacturing_widget import ManufacturingWidget
from odoo_client import OdooClient
from products_widget import ProductsWidget


class MainWindow(QMainWindow):
    """Application main window displayed after successful login."""

    def __init__(self, client: OdooClient, parent=None):
        super().__init__(parent)
        self._client = client
        self._build_ui()
        self._apply_style()

    # ------------------------------------------------------------------

    def _build_ui(self):
        self.setWindowTitle("Odoo – Interface Opérateur de Production")
        self.setMinimumSize(900, 640)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Banner
        banner = QLabel("  🏭  Interface Opérateur de Production – Odoo ERP")
        banner.setFont(QFont("Segoe UI", 11, QFont.Bold))
        banner.setFixedHeight(40)
        banner.setStyleSheet(
            "background: #2c3e50; color: white; padding-left: 12px;"
        )
        root.addWidget(banner)

        # Tabs
        tabs = QTabWidget()
        tabs.setFont(QFont("Segoe UI", 10))
        tabs.addTab(CompanyWidget(self._client), "🏢  Entreprise")
        tabs.addTab(ProductsWidget(self._client), "📦  Produits")
        tabs.addTab(ManufacturingWidget(self._client), "🏭  Ordres de Fabrication")
        root.addWidget(tabs)

        # Status bar
        bar = QStatusBar()
        bar.showMessage("Connecté à Odoo.")
        self.setStatusBar(bar)

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background: #f4f6f9; }
            QTabWidget::pane {
                border: none;
                background: #f4f6f9;
            }
            QTabBar::tab {
                padding: 8px 20px;
                background: #dfe6e9;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #2980b9;
                color: white;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected { background: #b2bec3; }
            QTableWidget {
                gridline-color: #dfe6e9;
                background: white;
                alternate-background-color: #f9fbfc;
            }
            QTableWidget QHeaderView::section {
                background: #2c3e50;
                color: white;
                padding: 6px;
                border: none;
            }
            QPushButton {
                background: #2980b9;
                color: white;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover  { background: #3498db; }
            QPushButton:pressed { background: #1a5276; }
            QGroupBox {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 8px;
                padding: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                color: #2c3e50;
                font-weight: bold;
            }
        """)
