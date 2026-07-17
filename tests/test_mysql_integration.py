"""Opt-in isolated MySQL integration test for the public API contract.

This test never connects to a user database. It runs only when
RUN_MYSQL_INTEGRATION=1 and expects an ephemeral database supplied by CI or a
local disposable Docker container.
"""
from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest

RUN = os.environ.get("RUN_MYSQL_INTEGRATION") == "1"
ROOT = Path(__file__).resolve().parents[1]
RASPI = ROOT / "raspi"
sys.path.insert(0, str(RASPI))


@unittest.skipUnless(RUN, "set RUN_MYSQL_INTEGRATION=1 with an ephemeral MySQL database")
class MysqlIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import pymysql

        cls.pymysql = pymysql
        cls.root_connection = pymysql.connect(
            host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            user="root",
            password=os.environ["MYSQL_ROOT_PASSWORD"],
            charset="utf8mb4",
            autocommit=True,
        )
        script = (RASPI / "database" / "init.sql").read_text(encoding="utf-8")
        statements = []
        buffer: list[str] = []
        for line in script.splitlines():
            if line.lstrip().startswith("--"):
                continue
            buffer.append(line)
        for statement in "\n".join(buffer).split(";"):
            statement = statement.strip()
            if statement:
                statements.append(statement)
        with cls.root_connection.cursor() as cur:
            for statement in statements:
                cur.execute(statement)
        from api.app import create_app

        cls.client = create_app().test_client()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.root_connection.close()

    def _token(self) -> str:
        response = self.client.post(
            "/api/auth/register",
            json={"username": "ci_user", "password": "ci_integration_password"},
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        response = self.client.post(
            "/api/auth/login",
            json={"username": "ci_user", "password": "ci_integration_password"},
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        return response.get_json()["data"]["token"]

    def test_mock_data_api_and_settings_round_trip(self) -> None:
        from collector.sensors import read_all
        from db import connection

        reading = read_all()
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO sensor_data (temperature, humidity, light_intensity) VALUES (%s, %s, %s)",
                    (reading.temperature, reading.humidity, reading.light_lux),
                )
        token = self._token()
        headers = {"Authorization": f"Bearer {token}"}
        health = self.client.get("/api/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.get_json()["message"], "ok")
        realtime = self.client.get("/api/realtime", headers=headers)
        self.assertEqual(realtime.status_code, 200, realtime.get_json())
        data = realtime.get_json()["data"]
        self.assertIsNotNone(data)
        self.assertIn("temperature", data)
        settings = self.client.post(
            "/api/settings",
            headers=headers,
            json={"collect_interval": 11, "temp_high": 33},
        )
        self.assertEqual(settings.status_code, 200, settings.get_json())
        confirmed = self.client.get("/api/settings", headers=headers)
        self.assertEqual(confirmed.status_code, 200, confirmed.get_json())
        self.assertEqual(confirmed.get_json()["data"]["collect_interval"], "11")


if __name__ == "__main__":
    unittest.main()
