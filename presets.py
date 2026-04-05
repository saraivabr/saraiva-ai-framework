from __future__ import annotations

import json
from pathlib import Path

PRESETS = {
    "v1_pitch_up": {
        "name": "Pitch Up",
        "desc": "Pitch leve para cima com micro-eq e ambiencia sutil",
        "filters": (
            "asetrate=44100*1.047,aresample=44100,"
            "equalizer=f=150:t=q:w=2:g=-1.5,"
            "equalizer=f=8000:t=q:w=1.5:g=1.2,"
            "adelay=37|41,aecho=0.8:0.3:17:0.15,volume=0.97"
        ),
    },
    "v4_surgical": {
        "name": "Surgical",
        "desc": "Ajuste cirurgico com pitch, tempo leve e modulacoes suaves",
        "filters": (
            "asetrate=44100*1.029,aresample=44100,atempo=0.98,"
            "flanger=delay=1.5:depth=0.3:regen=-2:width=10:speed=0.2:phase=50,"
            "tremolo=f=0.7:d=0.05,"
            "equalizer=f=200:t=q:w=3:g=-1,"
            "equalizer=f=6000:t=q:w=2:g=0.8,"
            "adelay=23|19,volume=0.97"
        ),
    },
    "v6_destroy": {
        "name": "Destroy",
        "desc": "Mudancas mais fortes de timbre e modulacao",
        "filters": (
            "asetrate=44100*0.92,aresample=44100,atempo=1.07,"
            "equalizer=f=120:t=q:w=2:g=3,equalizer=f=500:t=q:w=3:g=-3,"
            "equalizer=f=2000:t=q:w=2:g=2,equalizer=f=7000:t=q:w=1.5:g=-2.5,"
            "equalizer=f=14000:t=q:w=2:g=2,"
            "aecho=0.75:0.35:19|29|37:0.18|0.12|0.08,"
            "aphaser=in_gain=0.85:out_gain=0.85:delay=3:decay=0.35:speed=0.4,"
            "vibrato=f=5:d=0.15,adelay=53|27,volume=0.90"
        ),
    },
    "v7_obliterate": {
        "name": "Obliterate",
        "desc": "Preset mais intenso com chorus/flanger/phaser",
        "filters": (
            "asetrate=44100*1.12,aresample=44100,atempo=0.92,"
            "highpass=f=40,lowpass=f=16000,"
            "equalizer=f=200:t=q:w=4:g=-5,equalizer=f=3000:t=q:w=3:g=4,"
            "equalizer=f=8000:t=q:w=2:g=-4,"
            "aecho=0.7:0.5:11|17|29|41:0.25|0.2|0.15|0.1,"
            "chorus=0.4:0.7:15|25|35|45:0.5|0.4|0.3|0.2:0.4|0.3|0.2|0.15:1.8|2.2|1.5|2.8,"
            "flanger=delay=4:depth=2:regen=-5:width=30:speed=0.4:phase=75,"
            "aphaser=in_gain=0.8:out_gain=0.8:delay=3.5:decay=0.4:speed=0.6,"
            "volume=0.88"
        ),
    },
    "v8_warper": {
        "name": "Warper",
        "desc": "Modulacao suave com vibrato, tremolo e brilho dinamico",
        "filters": (
            "asetrate=44100*1.0204,atempo=1.0044,aresample=44100,"
            "vibrato=f=0.3:d=0.08,"
            "tremolo=f=2.0:d=0.05,"
            "aphaser=type=t:decay=0.2,"
            "extrastereo=m=1.35,"
            "chorus=0.5:0.8:60:0.4:0.25:2,"
            "firequalizer=gain='if(gt(f,3000), 2*sin(f/1000), 0)',"
            "alimiter=limit=0.92:attack=5:release=50"
        ),
    },
    "v9_ultimate": {
        "name": "Ultimate",
        "desc": "Textura avancada com flanger, phaser e ajuste espectral",
        "filters": (
            "asetrate=44100*1.0265,atempo=1.0005,aresample=44100,"
            "vibrato=f=0.6:d=0.1,"
            "aphaser=type=t:decay=0.25:speed=2,"
            "flanger=delay=3:depth=1:regen=20:width=50,"
            "extrastereo=m=1.3,"
            "firequalizer=gain='if(gt(f,4000), 1.5*sin(f/800), 0)',"
            "alimiter=limit=0.92:attack=5:release=50"
        ),
    },
    "v10_lyric_jammer": {
        "name": "Lyric Jammer",
        "desc": "Deformacao de articulacao e foco vocal com ambiencia curta",
        "filters": (
            "asetrate=44100*1.0263,atempo=1.0040,aresample=44100,"
            "vibrato=f=1.2:d=0.15,"
            "aphaser=type=t:decay=0.3,"
            "aecho=0.8:0.88:15:0.15,"
            "chorus=0.6:0.9:50:0.4:0.25:2,"
            "firequalizer=gain='if(between(f,400,3000), -2, 0)',"
            "extrastereo=m=1.4,"
            "alimiter=limit=0.90:attack=5:release=50"
        ),
    },
    "v11_spectral_morph": {
        "name": "Spectral Morph",
        "desc": "Mudanca de textura com pitch down e modelagem dinamica",
        "filters": (
            "asetrate=44100*0.9170,atempo=1.1330,aresample=44100,"
            "vibrato=f=0.2:d=0.1,"
            "tremolo=f=3.0:d=0.1,"
            "aphaser=type=t:decay=0.4:speed=0.5,"
            "aecho=0.8:0.9:30|60:0.2|0.1,"
            "extrastereo=m=1.5,"
            "firequalizer=gain='if(gt(f,2000), 2*sin(f/500), 0)',"
            "highpass=f=40,lowpass=f=16000,"
            "alimiter=limit=0.88:attack=5:release=50"
        ),
    },
    "v12_annihilator": {
        "name": "Annihilator",
        "desc": "Preset extremo com crusher, chorus e limitacao agressiva",
        "filters": (
            "asetrate=44100*0.8409,atempo=1.2846,aresample=44100,"
            "acrusher=level_in=1:level_out=1:bits=8:mode=log:aa=1,"
            "vibrato=f=6.0:d=0.35,"
            "aphaser=type=t:decay=0.5:speed=2.0,"
            "chorus=0.7:0.9:30:0.4:0.25:2,"
            "extrastereo=m=2.0,"
            "aecho=0.8:0.9:40:0.3,"
            "highpass=f=80,lowpass=f=10000,"
            "alimiter=limit=0.85:attack=5:release=50"
        ),
    },
}


def _load_extra_presets() -> dict:
    extras_path = Path(__file__).resolve().parent / "presets_extra.json"
    if not extras_path.exists():
        return {}
    with extras_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("presets_extra.json precisa ser um objeto JSON")
    valid = {}
    for preset_id, preset in data.items():
        if not isinstance(preset, dict):
            continue
        if not all(k in preset for k in ("name", "desc", "filters")):
            continue
        valid[preset_id] = {
            "name": str(preset["name"]),
            "desc": str(preset["desc"]),
            "filters": str(preset["filters"]),
        }
    return valid


PRESETS.update(_load_extra_presets())
