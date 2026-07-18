#!/usr/bin/env python3
"""Reject local secrets, generated outputs, and unsafe publication leftovers."""
from __future__ import annotations

from pathlib import Path
import re

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PATH_PARTS = {".idea", ".venv", "bin", "obj", "__pycache__"}
FORBIDDEN_NAMES = {".env", "grants.sql", "avalonia-logo.ico"}
FORBIDDEN_SUFFIXES = {".apk", ".ipa", ".exe", ".dll", ".pdb", ".zip", ".tar", ".gz"}
SUSPICIOUS = (
    re.compile(r'''(?i)\b(jwt_secret|admin_pass|mysql_password)\s*=\s*["'](?!replace_with_)[^"']+'''),
    re.compile(
        r'''(?i)\b(jwt_secret|admin_pass|mysql_password|mysql_root_password)\s*:\s*(?!\$\{|replace_with_|test_)[A-Za-z0-9_!@#$%.-]{12,}'''
    ),
    re.compile(r'''(?i)\b(sk|api)[_-]?(key|token)\b\s*[:=]\s*["'][A-Za-z0-9_\-]{12,}'''),
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    checked = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if any(part in FORBIDDEN_PATH_PARTS for part in path.relative_to(ROOT).parts):
            fail(f"generated/editor path is tracked: {rel}")
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            fail(f"forbidden local or binary file is tracked: {rel}")
        if path.stat().st_size > 2 * 1024 * 1024:
            fail(f"file exceeds 2 MiB publication limit: {rel}")
        if rel.startswith("assets/") and path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    if len(image.getexif()) != 0:
                        fail(f"public image contains EXIF metadata: {rel}")
                    allowed_info = {"jfif", "jfif_version", "jfif_unit", "jfif_density", "progressive", "progression", "transparency"}
                    if set(image.info) - allowed_info:
                        fail(f"public image contains unexpected metadata: {rel}")
            except OSError as exc:
                fail(f"invalid public image {rel}: {exc}")
            checked += 1
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            fail(f"unexpected binary file is tracked: {rel}")
        for pattern in SUSPICIOUS:
            if pattern.search(text):
                fail(f"possible credential in {rel}")
        checked += 1
    print(f"Secret/publication scan: PASS ({checked} text files checked)")


if __name__ == "__main__":
    main()
