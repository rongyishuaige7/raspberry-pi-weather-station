#!/usr/bin/env python3
"""Check the published repository has the minimum reproducible structure."""
from __future__ import annotations

from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md", "LICENSE", "SECURITY.md", "THIRD_PARTY_NOTICES.md", "HARDWARE.md",
    "raspi/.env.example", "raspi/requirements.txt", "raspi/api/app.py", "raspi/collector/config.py",
    "raspi/database/init.sql", "upper/WeatherStation.sln", "upper/WeatherStation/WeatherStation.csproj",
    "hardware/BOM.csv", "hardware/wiring-diagram.svg", "docs/SOURCE_PROVENANCE.md",
    "docs/PROJECT_STATUS.md", "docs/VERIFICATION.md", "docs/PROTOCOL.md",
    "docs/GITHUB_METADATA.md", "docs/HARDWARE_LAB_CARD.md", "scripts/verify.sh",
    "scripts/secret_scan.py", "scripts/run_mysql_integration.sh", "tests/test_source_contracts.py", "tests/test_mysql_integration.py", ".github/workflows/validate.yml",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail("missing required files: " + ", ".join(missing))
    root = ET.parse(ROOT / "hardware/wiring-diagram.svg").getroot()
    if root.tag != "{http://www.w3.org/2000/svg}svg" or not root.get("viewBox"):
        fail("wiring diagram must be a valid self-contained SVG with viewBox")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for fact in ("USE_MOCK_SENSORS=1", "不是", "HTTP"):
        if fact not in readme:
            fail(f"README is missing required boundary: {fact}")
    print("Repository structure check: PASS")


if __name__ == "__main__":
    main()
