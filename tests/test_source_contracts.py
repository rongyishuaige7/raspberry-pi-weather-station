from __future__ import annotations

import ast
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RASPI = ROOT / "raspi"
sys.path.insert(0, str(RASPI))


class SourceContractsTest(unittest.TestCase):
    def test_no_deployment_secret_defaults(self) -> None:
        config = (RASPI / "collector/config.py").read_text(encoding="utf-8")
        app = (RASPI / "api/app.py").read_text(encoding="utf-8")
        self.assertNotIn("weather_secret", config)
        self.assertNotIn("change-me-in-production", app)
        self.assertIn("_required(\"MYSQL_PASSWORD\")", config)
        self.assertIn("len(JWT_SECRET) < 32", app)

    def test_no_permissive_cors_or_public_bind_default(self) -> None:
        app = (RASPI / "api/app.py").read_text(encoding="utf-8")
        self.assertNotIn("flask_cors", app)
        self.assertIn('os.environ.get("FLASK_HOST", "127.0.0.1")', app)

    def test_ui_does_not_claim_generic_normal_status(self) -> None:
        dashboard = (
            ROOT / "upper/WeatherStation/ViewModels/DashboardViewModel.cs"
        ).read_text(encoding="utf-8")
        self.assertNotIn('StatusText = "正常"', dashboard)
        self.assertIn("已收到最近一条记录", dashboard)

    def test_mock_sensor_values_are_explicitly_random(self) -> None:
        sensors = (RASPI / "collector/sensors.py").read_text(encoding="utf-8")
        self.assertIn("USE_MOCK_SENSORS", sensors)
        self.assertIn("random.uniform", sensors)

    def test_python_sources_parse(self) -> None:
        for path in RASPI.rglob("*.py"):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_config_requires_credentials_when_imported_without_env(self) -> None:
        saved = {name: os.environ.pop(name, None) for name in ("MYSQL_USER", "MYSQL_PASSWORD")}
        try:
            sys.modules.pop("collector.config", None)
            with self.assertRaises(RuntimeError):
                __import__("collector.config")
        finally:
            for name, value in saved.items():
                if value is not None:
                    os.environ[name] = value
            sys.modules.pop("collector.config", None)


if __name__ == "__main__":
    unittest.main()
