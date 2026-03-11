"""Unit tests for OdooClient (no live Odoo server required)."""

import base64
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers to mock xmlrpc.client before importing odoo_client
# ---------------------------------------------------------------------------

class TestDecodeImage(unittest.TestCase):
    """Tests for OdooClient.decode_image()."""

    def setUp(self):
        # Import here so the mock is already in place for the other tests
        from odoo_client import OdooClient
        self.OdooClient = OdooClient

    def test_none_returns_none(self):
        self.assertIsNone(self.OdooClient.decode_image(None))

    def test_false_returns_none(self):
        self.assertIsNone(self.OdooClient.decode_image(False))

    def test_bytes_input(self):
        raw = b"hello"
        encoded = base64.b64encode(raw)
        result = self.OdooClient.decode_image(encoded)
        self.assertEqual(result, raw)

    def test_string_input(self):
        raw = b"world"
        encoded = base64.b64encode(raw).decode()
        result = self.OdooClient.decode_image(encoded)
        self.assertEqual(result, raw)


class TestMOStates(unittest.TestCase):
    """Tests for the MO_STATES mapping."""

    def setUp(self):
        from odoo_client import OdooClient
        self.OdooClient = OdooClient

    def test_all_required_states_present(self):
        states = self.OdooClient.MO_STATES
        for key in ("confirmed", "progress", "done", "cancel"):
            self.assertIn(key, states, f"Missing state: {key}")

    def test_state_labels_are_strings(self):
        for key, label in self.OdooClient.MO_STATES.items():
            self.assertIsInstance(label, str, f"Label for '{key}' is not a string")
            self.assertTrue(len(label) > 0, f"Label for '{key}' is empty")


class TestConnectFailure(unittest.TestCase):
    """Tests that connect() raises on invalid credentials."""

    def test_connect_raises_on_zero_uid(self):
        from odoo_client import OdooClient

        mock_common = MagicMock()
        mock_common.authenticate.return_value = 0  # Odoo returns 0 / False on failure

        with patch("xmlrpc.client.ServerProxy", return_value=mock_common):
            client = OdooClient()
            with self.assertRaises(ValueError):
                client.connect("http://localhost:8069", "mydb", "baduser", "badpass")


class TestConnectSuccess(unittest.TestCase):
    """Tests that connect() stores state on success."""

    def test_connect_stores_uid(self):
        from odoo_client import OdooClient

        mock_common = MagicMock()
        mock_common.authenticate.return_value = 5  # valid uid

        with patch("xmlrpc.client.ServerProxy", return_value=mock_common):
            client = OdooClient()
            result = client.connect("http://localhost:8069", "mydb", "user", "pass")
            self.assertTrue(result)
            self.assertEqual(client._uid, 5)
            self.assertEqual(client._db, "mydb")
            self.assertEqual(client._url, "http://localhost:8069")


if __name__ == "__main__":
    unittest.main()
