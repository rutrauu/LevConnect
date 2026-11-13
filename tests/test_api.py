"""
LevConnect - Suíte de Testes Automatizados (Engenharia de Software - Projeto Dev II)
Compatível tanto com `python tests/test_api.py` (unittest nativo) quanto com `pytest`.
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from fastapi import HTTPException
import backend.main as api_main
import backend.database as db


class TestLevConnectSuite(unittest.TestCase):
    def setUp(self):
        """Reseta o banco SQLite antes de cada teste para garantir estado determinístico."""
        db.init_db(force_reset=True)

    def test_01_health_and_sqlite_diagnostics(self):
        health = api_main.health_check()
        self.assertEqual(health["status"], "ok")
        self.assertEqual(health["persistence"], "SQLite3")

        diag = api_main.database_status()
        tables = diag["tables"]
        self.assertEqual(tables["products"], 5)
        self.assertEqual(tables["customers"], 5)
        self.assertEqual(tables["sellers"], 5)

    def test_02_cross_store_reservation_decrements_sqlite_stock(self):
        prod_before = api_main.get_product("PROD-001")["product"]
        self.assertEqual(prod_before["stock"]["Minas do Leão"]["37"], 3)

        payload = api_main.ReservationCreate(
            customer_id="CUST-001",
            product_id="PROD-001",
            size="37",
            pickup_store="Charqueadas",
            source_store="Minas do Leão",
            chat_id="CHAT-101",
            seller_name="Mariana Santos"
        )
        res = api_main.create_reservation(payload)
        created = res["reservation"]
        self.assertTrue(created["is_inter_store"])
        self.assertEqual(created["status"], "em_transito")

        # Recarrega diretamente do arquivo SQLite para comprovar persistência em disco
        db.load_from_sqlite()
        prod_after = api_main.get_product("PROD-001")["product"]
        self.assertEqual(prod_after["stock"]["Minas do Leão"]["37"], 2)

    def test_03_prevent_reservation_when_out_of_stock(self):
        payload = api_main.ReservationCreate(
            customer_id="CUST-001",
            product_id="PROD-001",
            size="37",
            pickup_store="Charqueadas",
            source_store="Charqueadas"
        )
        with self.assertRaises(HTTPException) as ctx:
            api_main.create_reservation(payload)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Saldo insuficiente", ctx.exception.detail)

    def test_04_malote_logistics_advancement_triggers_whatsapp_notification(self):
        chat_before = api_main.get_chat("CHAT-101")["chat"]
        msg_count_before = len(chat_before["messages"])

        body = api_main.update_reservation_status(
            "RES-8901",
            api_main.StatusUpdate(status="pronto_retirada")
        )
        self.assertEqual(body["reservation"]["status"], "pronto_retirada")
        self.assertIsNotNone(body["auto_notification"])

        chat_after = api_main.get_chat("CHAT-101")["chat"]
        self.assertEqual(len(chat_after["messages"]), msg_count_before + 1)
        self.assertIn("pronta para você provar", chat_after["messages"][-1]["text"])

    def test_05_lev_ai_copilot_suggestion(self):
        data = api_main.copilot_suggest(api_main.CopilotRequest(
            chat_id="CHAT-101",
            active_store="Charqueadas",
            seller_name="Mariana Santos"
        ))
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["primary_recommendation"]["size"], "37")
        self.assertIn("cross_sell_recommendation", data)
        self.assertIn("Juliana", data["suggested_reply"])

    def test_06_vip_campaign_by_size(self):
        data = api_main.send_vip_campaign(api_main.VipCampaignRequest(
            product_id="PROD-005",
            size="38",
            active_store="Charqueadas",
            seller_name="Mariana Santos"
        ))
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["sent_count"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
