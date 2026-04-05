#!/usr/bin/env python3
"""
Saraiva.AI - fluxo local de tentativa/aprovacao com historico.
Uso: python3 app.py
Abre: http://localhost:5555
"""

from __future__ import annotations

import random
import subprocess
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


def validate_selected_presets(selected: list[str]) -> tuple[list[str] | None, str | None]:
    if not selected:
        return None, "Selecione ao menos 1 preset"
    invalid = [p for p in selected if p not in PRESETS]
    if invalid:
        return None, f"Preset invalido: {', '.join(invalid)}"
    return selected, None


def create_job_with_first_attempt(source_path: Path, source_filename: str, selected: list[str]) -> dict:
    job_id = uuid.uuid4().hex[:10]
    final_source_path = UPLOADS_DIR / f"{job_id}{source_path.suffix or '.mp3'}"
    if source_path != final_source_path:
        source_path.replace(final_source_path)

    create_job(DB_PATH, job_id, source_filename, str(final_source_path), selected)
    job = get_job(DB_PATH, job_id)
    if job is None:
        raise RuntimeError("Falha ao criar job")
    first_attempt = generate_next_attempt(job)
    return {"success": True, "job": job, "current_attempt": first_attempt}


def download_youtube_to_mp3(url: str, temp_id: str) -> tuple[Path, str]:
    out_template = str(UPLOADS_DIR / f"{temp_id}_yt.%(ext)s")
    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--no-playlist",
        "--restrict-filenames",
        "--output",
        out_template,
        url,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
    matches = sorted(UPLOADS_DIR.glob(f"{temp_id}_yt.*"))
    if not matches:
        raise RuntimeError("Nao foi possivel gerar o MP3 do link informado")
    source_path = matches[0]
    return source_path, source_path.name


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
    selected, err = validate_selected_presets(request.form.getlist("presets"))
    if err:
        return jsonify({"error": err}), 400

    ext = Path(file.filename or "audio.mp3").suffix or ".mp3"
    source_filename = file.filename or f"audio{ext}"
    temp_id = uuid.uuid4().hex[:8]
    source_path = UPLOADS_DIR / f"{temp_id}{ext}"
    file.save(source_path)

    try:
        result = create_job_with_first_attempt(source_path, source_filename, selected or [])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(result)


@app.route("/api/jobs/from-youtube", methods=["POST"])
def api_create_job_from_youtube():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    selected_raw = data.get("presets") or []
    if not url:
        return jsonify({"error": "Informe a URL do YouTube"}), 400

    selected, err = validate_selected_presets(list(selected_raw))
    if err:
        return jsonify({"error": err}), 400

    temp_id = uuid.uuid4().hex[:8]
    try:
        source_path, source_filename = download_youtube_to_mp3(url, temp_id)
        result = create_job_with_first_attempt(source_path, source_filename, selected or [])
        return jsonify(result)
    except subprocess.CalledProcessError as e:
        detail = e.stderr.strip() if e.stderr else str(e)
        return jsonify({"error": f"Falha ao baixar audio: {detail}"}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Timeout ao baixar audio do YouTube"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
