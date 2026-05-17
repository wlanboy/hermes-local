# Hermes Local

Lokale KI-Assistenten-Umgebung auf Basis von [Hermes](https://github.com/NousResearch/hermes-agent) und [Ollama](https://ollama.com). Läuft vollständig offline — keine Cloud-Abhängigkeit, keine Daten verlassen den Rechner.

## Überblick

| Komponente | Beschreibung | Port |
|---|---|---|
| **Ollama** | Lokaler LLM-Server | `11434` |
| **Hermes** | KI-Agent mit Web-Dashboard | `9119` |
| **Hermes Gateway** | OpenAI-kompatibler API-Server | `8642` |

Das Standard-Modell ist `qwen3.5:4b` — CPU-tauglich und benötigt ca. 3 GB RAM.

## Voraussetzungen

- [Docker](https://docs.docker.com/get-docker/) und [Docker Compose](https://docs.docker.com/compose/install/)
- ca. 5 GB freier Speicherplatz (Modell + Images)

## Schritt-für-Schritt

### 1. Repository klonen

```bash
git clone <repo-url> hermes-local
cd hermes-local
```

### 2. Umgebungsvariablen anlegen

```bash
cp .env.example .env
```

Die `.env` steuert den Docker-Image-Tag. Telegram und Hermes-Einstellungen gehören in `config/.env`:

| Datei | Zweck |
|---|---|
| `.env` | Docker-Level — Image-Tag (`HERMES_TAG`) |
| `config/.env` | Hermes-intern — Telegram-Bot, Verhalten |

Telegram-Bot in `config/.env` eintragen:

```env
TELEGRAM_BOT_TOKEN=dein-token
TELEGRAM_ALLOWED_USERS=123456789
TELEGRAM_HOME_CHANNEL=-100123456789
TELEGRAM_HOME_CHANNEL_NAME=MeinKanal
```

### 3. Container starten

```bash
docker compose up -d
```

Beim ersten Start wird das Hermes-Image gepullt (~500 MB).

### 4. Modell herunterladen

```bash
docker exec ollama ollama pull qwen3.5:4b
docker exec ollama ollama pull google/gemma-4-e2b
```

Das Modell wird in `~/.ollama` gespeichert und steht nach einem Neustart sofort zur Verfügung.

### 5. Dashboard öffnen

```
http://localhost:9119
```

Der Chat-Tab ist über das Dashboard erreichbar.

## LM Studio verwenden (Linux)

Wer [LM Studio](https://lmstudio.ai) statt Ollama nutzt, kann Hermes ohne Docker Compose starten. Voraussetzung: LM Studio läuft lokal und hat den Server auf Port `1234` aktiviert.

```bash
chmod -R a+rw ./config
docker run --rm \
  --name hermes \
  --network=host \
  -e HERMES_DASHBOARD=1 \
  -e HERMES_DASHBOARD_TUI=1 \
  -v ./config:/opt/data \
  nousresearch/hermes-agent:latest \
  gateway run
```

In [config/config.yaml](config/config.yaml) den LM Studio-Endpunkt eintragen:

```yaml
model:
  provider: custom
  default: "google/gemma-4-e2b"   # exakter Name aus LM Studio (z.B. lmstudio-community/Qwen3-4B-GGUF)
  base_url: "http://localhost:1234/v1"
  api_key: "lm-studio"
```

Dashboard öffnen: `http://localhost:9119`

Für einen interaktiven Chat direkt im Terminal:

```bash
docker exec -it hermes /opt/hermes/.venv/bin/hermes chat
```

## Modell wechseln

In [config/config.yaml](config/config.yaml) den Modellnamen anpassen:

```yaml
model:
  provider: custom
  default: "google/gemma-4-e2b"
  base_url: "http://ollama:11434/v1"
  api_key: "none"
```

Anschließend das Modell pullen und den Container neu starten:

```bash
docker exec ollama ollama pull google/gemma-4-e2b
docker compose restart hermes
```

## Hermes aktualisieren

`HERMES_TAG` in der `.env` bestimmt, welches Image von Docker Hub genutzt wird. Das mitgelieferte Script listet die verfügbaren Tags und schreibt den gewählten automatisch in die `.env`:

```bash
python3 select-hermes-commit.py
```

Danach das Image aktualisieren:

```bash
docker compose pull && docker compose up -d
```

## Nützliche Befehle

```bash
# Logs anzeigen
docker compose logs -f hermes

# Container neu starten
docker compose restart hermes

# Alle Container stoppen
docker compose down

# Verfügbare Modelle in Ollama anzeigen
docker exec ollama ollama list
```

## Projektstruktur

```
hermes-local/
├── docker-compose.yml        # Orchestrierung
├── select-hermes-commit.py   # Interaktives Update-Script
├── .env                      # Aktive Konfiguration (nicht eingecheckt)
├── .env.example              # Vorlage für Umgebungsvariablen
└── config/                   # Persistentes Hermes-Datenverzeichnis (/opt/data)
    ├── config.yaml           # Hermes-Konfiguration (Modell, Memory, …)
    ├── SOUL.md               # Agenten-Persona
    ├── .env                  # Hermes-Secrets (Telegram, Verhalten)
    ├── memories/
    ├── sessions/
    └── skills/
```
