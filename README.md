# Saraiva.AI

App web local em Flask para iteracao de processamento de audio com historico persistente.

## Stack

- Python + Flask
- FFmpeg
- yt-dlp
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

## Fluxo com link do YouTube

Na tela inicial, cole o link em **"Cole aqui o link do YouTube"** e clique em **"Baixar YouTube + Iniciar"**.
A app baixa o audio em MP3 e ja inicia o job automaticamente com os presets selecionados.

Use apenas links e conteudos para os quais voce tenha autorizacao.

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
- `presets.py` -> presets base (catalogo expandido)
- `ui.html` -> interface

## Adicionar mais presets sem mexer no codigo

1. Copie `presets_extra.example.json` para `presets_extra.json`.
2. Adicione seus presets no formato:

```json
{
  "id_unico": {
    "name": "Nome do preset",
    "desc": "Descricao",
    "filters": "cadeia_ffmpeg"
  }
}
```

3. Reinicie a app. Os presets extras aparecerao automaticamente na interface.
