#!/usr/bin/env python3
"""
Saraiva.AI - fluxo local de tentativa/aprovacao com historico.
Uso: python3 app.py
Abre: http://localhost:5555
"""

from __future__ import annotations

import random
import threading
import uuid
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory

from presets import PRESETS
from processor import generate_attempt_audio
from storage import (
    approve_job,
    create_attempt,
    create_job,
    get_attempt,
    get_job,
    init_db,
    list_attempts,
    next_attempt_index,
    set_attempt_status,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
OUTPUTS_DIR = DATA_DIR / "outputs"
DB_PATH = DATA_DIR / "app.db"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
init_db(DB_PATH)

app = Flask(__name__)


def serialize_attempt(attempt: dict) -> dict:
    out = dict(attempt)
    out["size"] = Path(attempt["output_path"]).stat().st_size if Path(attempt["output_path"]).exists() else 0
    return out


def generate_next_attempt(job: dict) -> dict:
    attempt_index = next_attempt_index(DB_PATH, job["id"])
    preset_id = random.choice(job["selected_presets"])
    seed = random.randint(1000, 999999)

    base_name = Path(job["source_filename"]).stem
    output_filename = f"{base_name}__try_{attempt_index:02d}_{preset_id}.mp3"
    output_path = OUTPUTS_DIR / job["id"] / output_filename

    variation = generate_attempt_audio(
        source_path=Path(job["source_path"]),
        output_path=output_path,
        preset_id=preset_id,
        seed=seed,
    )
    attempt_id = create_attempt(
        db_path=DB_PATH,
        job_id=job["id"],
        attempt_index=attempt_index,
        preset_id=preset_id,
        output_filename=output_filename,
        output_path=str(output_path),
        params=variation,
    )
    attempt = get_attempt(DB_PATH, attempt_id)
    if attempt is None:
        raise RuntimeError("Falha ao registrar tentativa")
    return serialize_attempt(attempt)


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "ui.html")


@app.route("/api/presets")
def api_presets():
    return jsonify(
        [{"id": pid, "name": p["name"], "desc": p["desc"]} for pid, p in PRESETS.items()]
    )


@app.route("/api/jobs", methods=["POST"])
def api_create_job():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files["file"]
    selected = request.form.getlist("presets")
    if not selected:
        return jsonify({"error": "Selecione ao menos 1 preset"}), 400

    invalid = [p for p in selected if p not in PRESETS]
    if invalid:
        return jsonify({"error": f"Preset invalido: {', '.join(invalid)}"}), 400

    ext = Path(file.filename or "audio.mp3").suffix or ".mp3"
    source_filename = file.filename or f"audio{ext}"
    job_id = uuid.uuid4().hex[:10]
    source_path = UPLOADS_DIR / f"{job_id}{ext}"
    file.save(source_path)

    create_job(DB_PATH, job_id, source_filename, str(source_path), selected)
    job = get_job(DB_PATH, job_id)
    if job is None:
        return jsonify({"error": "Falha ao criar job"}), 500

    first_attempt = generate_next_attempt(job)
    return jsonify({"success": True, "job": job, "current_attempt": first_attempt})


@app.route("/api/jobs/<job_id>")
def api_job(job_id: str):
    job = get_job(DB_PATH, job_id)
    if job is None:
        return jsonify({"error": "Job nao encontrado"}), 404
    attempts = [serialize_attempt(a) for a in list_attempts(DB_PATH, job_id)]
    current_attempt = next((a for a in reversed(attempts) if a["status"] == "pending"), None)
    return jsonify({"success": True, "job": job, "attempts": attempts, "current_attempt": current_attempt})


@app.route("/api/jobs/<job_id>/next", methods=["POST"])
def api_next_attempt(job_id: str):
    job = get_job(DB_PATH, job_id)
    if job is None:
        return jsonify({"error": "Job nao encontrado"}), 404
    if job["status"] == "approved":
        return jsonify({"error": "Job ja aprovado"}), 400

    attempt = generate_next_attempt(job)
    return jsonify({"success": True, "attempt": attempt})


@app.route("/api/attempts/<int:attempt_id>/status", methods=["POST"])
def api_attempt_status(attempt_id: int):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in {"approved", "rejected"}:
        return jsonify({"error": "Status invalido"}), 400

    attempt = get_attempt(DB_PATH, attempt_id)
    if attempt is None:
        return jsonify({"error": "Tentativa nao encontrada"}), 404

    set_attempt_status(DB_PATH, attempt_id, status)
    if status == "approved":
        approve_job(DB_PATH, attempt["job_id"], attempt_id)

    return jsonify({"success": True})


@app.route("/api/attempts/<int:attempt_id>/download")
def api_download_attempt(attempt_id: int):
    attempt = get_attempt(DB_PATH, attempt_id)
    if attempt is None:
        return jsonify({"error": "Tentativa nao encontrada"}), 404
    output_path = Path(attempt["output_path"])
    if not output_path.exists():
        return jsonify({"error": "Arquivo nao encontrado"}), 404
    return send_file(output_path, as_attachment=True, download_name=attempt["output_filename"])


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  SARAIVA.AI")
    print("  Abra: http://localhost:5555")
    print("=" * 50 + "\n")
    threading.Timer(1.2, lambda: webbrowser.open("http://localhost:5555")).start()
    app.run(host="0.0.0.0", port=5555, debug=False)
