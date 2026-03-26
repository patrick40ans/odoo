"""Odoo XML-RPC API client."""

import base64
import xmlrpc.client


class OdooClient:
    """Thin wrapper around Odoo's XML-RPC endpoints."""

    # Manufacturing-order state labels used in Odoo 16/17
    MO_STATES = {
        "confirmed": "Confirmé",
        "progress": "En cours",
        "done": "Fait",
        "cancel": "Annulé",
    }

    def __init__(self):
        self._url = ""
        self._db = ""
        self._uid = None
        self._password = ""
        self._common = None
        self._models = None

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def connect(self, url: str, db: str, username: str, password: str) -> bool:
        """Authenticate against Odoo and store credentials.

        Returns True on success, raises an exception on failure.
        """
        url = url.rstrip("/")
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        uid = common.authenticate(db, username, password, {})
        if not uid:
            raise ValueError("Identifiant ou mot de passe incorrect.")
        self._url = url
        self._db = db
        self._uid = uid
        self._password = password
        self._common = common
        self._models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
        return True

    def _execute(self, model: str, method: str, *args, **kwargs):
        """Shortcut for models.execute_kw."""
        return self._models.execute_kw(
            self._db, self._uid, self._password,
            model, method, list(args), kwargs,
        )

    # ------------------------------------------------------------------
    # F2 – Company
    # ------------------------------------------------------------------

    def get_company(self) -> dict:
        """Return information about the current user's company."""
        fields = [
            "name", "street", "street2", "city", "zip",
            "country_id", "phone", "email", "website",
            "logo", "vat",
        ]
        records = self._execute(
            "res.company", "search_read",
            [[]], fields=fields, limit=1,
        )
        return records[0] if records else {}

    # ------------------------------------------------------------------
    # F3 – Products
    # ------------------------------------------------------------------

    def get_products(self) -> list[dict]:
        """Return the list of storable/consumable products."""
        fields = [
            "name", "default_code", "type",
            "list_price", "uom_id",
            "categ_id", "description",
            "image_128",
        ]
        return self._execute(
            "product.template", "search_read",
            [[["active", "=", True]]],
            fields=fields,
            order="name asc",
        )

    # ------------------------------------------------------------------
    # F4 – Manufacturing Orders
    # ------------------------------------------------------------------

    def get_manufacturing_orders(self, state: str | None = None) -> list[dict]:
        """Return manufacturing orders, optionally filtered by state."""
        domain: list = []
        if state:
            domain.append(["state", "=", state])
        fields = [
            "name", "product_id", "product_qty",
            "qty_producing", "state",
            "date_planned_start", "date_finished",
        ]
        return self._execute(
            "mrp.production", "search_read",
            [domain],
            fields=fields,
            order="name desc",
        )

    # ------------------------------------------------------------------
    # F5 – Update quantity / progress a Confirmed MO
    # ------------------------------------------------------------------

    def update_mo_quantity(self, mo_id: int, qty_producing: float) -> None:
        """Set qty_producing on a Manufacturing Order."""
        self._execute(
            "mrp.production", "write",
            [[mo_id]], {"qty_producing": qty_producing},
        )

    def set_mo_in_progress(self, mo_id: int, qty_producing: float) -> None:
        """Mark a *confirmed* MO as in-progress with the given qty."""
        self._execute(
            "mrp.production", "write",
            [[mo_id]], {"qty_producing": qty_producing},
        )
        # button_mark_done / action_confirm are standard Odoo buttons.
        # We call the low-level state write compatible with Odoo 16.
        try:
            self._execute("mrp.production", "button_mark_done", [[mo_id]])
        except Exception:
            # Fallback: just update qty_producing; state transition
            # depends on Odoo version / installed modules.
            pass

    def produce_mo(self, mo_id: int, qty_producing: float) -> None:
        """Set qty_producing and call button_mark_done to finish the MO."""
        self._execute(
            "mrp.production", "write",
            [[mo_id]], {"qty_producing": qty_producing},
        )
        self._execute("mrp.production", "button_mark_done", [[mo_id]])

    @staticmethod
    def decode_image(b64_data) -> bytes | None:
        """Decode a base-64 image field returned by Odoo."""
        if not b64_data or b64_data is False:
            return None
        if isinstance(b64_data, bytes):
            return base64.b64decode(b64_data)
        return base64.b64decode(b64_data.encode())
