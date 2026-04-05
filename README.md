# Saraiva.AI

App web local em Flask para iteracao de processamento de audio com historico persistente.

## Stack

- Python + Flask
- FFmpeg
- SQLite (persistencia local)
- Frontend HTML/CSS/JS

## Rodar local

```bash
./INICIAR.command
```

Ou manual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Acesse: `http://localhost:5555`

## Deploy no Render

Este repo ja inclui `render.yaml`.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/saraivabr/saraiva-ai-framework)

1. Crie um novo Web Service no Render conectando este repositorio.
2. O Render vai usar:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
3. Deploy.

## Estrutura

- `app.py` -> rotas/API
- `storage.py` -> SQLite
- `processor.py` -> pipeline de processamento
- `presets.py` -> presets base
- `ui.html` -> interface
