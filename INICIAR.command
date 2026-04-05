#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv || exit 1
fi

. .venv/bin/activate || exit 1
python -m pip install --quiet -r requirements.txt || exit 1

echo ""
echo "========================================="
echo "  SARAIVA.AI"
echo "  Abrindo em http://localhost:5555"
echo "  Ctrl+C para fechar"
echo "========================================="
echo ""
python app.py
