from __future__ import annotations

import random
import subprocess
from pathlib import Path

from presets import PRESETS


def build_variation(seed: int) -> dict[str, float | int]:
    rng = random.Random(seed)
    return {
        "seed": seed,
        "tempo": round(rng.uniform(0.985, 1.015), 4),
        "volume": round(rng.uniform(0.96, 1.02), 4),
        "stereo": round(rng.uniform(0.98, 1.08), 4),
    }


def compose_filter(base_filter: str, variation: dict[str, float | int]) -> str:
    return (
        f"atempo={variation['tempo']},"
        f"extrastereo=m={variation['stereo']},"
        f"volume={variation['volume']},"
        f"{base_filter}"
    )


def generate_attempt_audio(
    source_path: Path,
    output_path: Path,
    preset_id: str,
    seed: int,
) -> dict[str, float | int]:
    preset = PRESETS[preset_id]
    variation = build_variation(seed)
    af = compose_filter(preset["filters"], variation)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(source_path),
        "-af",
        af,
        "-b:a",
        "320k",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, timeout=300)
    return variation

