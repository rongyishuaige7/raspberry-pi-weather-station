#!/usr/bin/env bash
# 简易联调：需已启动 Flask（默认 http://127.0.0.1:5000）
set -e
BASE="${1:-http://127.0.0.1:5000}"
echo "GET $BASE/api/health"
curl -sf "$BASE/api/health" | head -c 200 || { echo "Flask 未就绪"; exit 1; }
echo
echo "OK"
