from __future__ import annotations

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
}

