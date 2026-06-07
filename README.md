# Hermes Local – Lokale KI‑Assistenten‑Umgebung (offline)

Hermes Local ist eine vollständig offline laufende KI‑Assistenten‑Umgebung auf Basis von Hermes und Ollama.
Keine Cloud‑Dienste, keine externen Abhängigkeiten — alle Daten bleiben lokal auf dem Rechner.

Das Setup kombiniert einen lokalen LLM‑Server, ein Web‑Dashboard und eine OpenAI‑kompatible API, sodass sich KI‑Modelle wie in der Cloud nutzen lassen, aber komplett lokal betrieben werden.

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

Konfiguration ist auf zwei Dateien aufgeteilt:

| Datei | Zweck |
|---|---|
| `.env` | Docker-Level — Image-Tag und Hermes-Verhalten |
| `config/.env` | Hermes-intern — Telegram-, Signal- und Mattermost-Secrets |

Die `.env` enthält folgende Variablen:

| Variable | Beschreibung | Standardwert |
|---|---|---|
| `HERMES_TAG` | Docker-Image-Tag für Hermes | `latest` |
| `OLLAMA_TAG` | Docker-Image-Tag für Ollama | `latest` |

Messenger-Secrets in `config/.env` eintragen:

```bash
cp config/.env.example config/.env
```

Dann `config/.env` editieren und die gewünschten Werte befüllen — Telegram, Signal oder beides.

### 3. Container starten

```bash
docker compose up -d
```

Beim ersten Start wird das Hermes-Image gepullt (~500 MB).

### 4. Modell herunterladen

```bash
docker exec ollama ollama pull qwen3.5:2b
docker exec ollama ollama pull qwen3.5:4b
docker exec ollama ollama pull qwen3.5:9b
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

Vor dem Start muss die mitgelieferte Konfiguration kopiert werden:

```bash
cp llm-studio-config.yaml config/config.yaml
```

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

## Aktualisieren

Die mitgelieferten Skripte listen die verfügbaren Releases und schreiben den gewählten Tag automatisch in die `.env`:

```bash
# Hermes-Release auswählen
python3 select-hermes-commit.py

# Ollama-Release auswählen
python3 select-ollama-tag.py
```

Danach die Images aktualisieren:

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
├── select-hermes-commit.py   # Interaktives Release-Auswahl-Script für Hermes
├── select-ollama-tag.py      # Interaktives Release-Auswahl-Script für Ollama
├── llm-studio-config.yaml    # Vorlage für LM Studio statt Ollama
├── .env                      # Aktive Konfiguration (nicht eingecheckt)
├── .env.example              # Vorlage für Umgebungsvariablen
└── config/                   # Persistentes Hermes-Datenverzeichnis (/opt/data)
    ├── config.yaml           # Hermes-Konfiguration (Modell, Memory, …)
    ├── SOUL.md               # Agenten-Persona
    ├── .env.example          # Vorlage für Telegram-, Signal- und Mattermost-Secrets
    └── .env                  # Hermes-Secrets (Telegram-Bot-Token, nicht eingecheckt)
```

## Modellvergleich

Alle Werte für Q4_K_M-Quantisierung bei vollem 128K Kontext (float16 KV-Cache). RAM-Werte schließen Modellgewichte, KV-Cache und Ollama-Overhead ein.

| Modell | Parameter | Gewichte | KV-Cache (128K) | RAM gesamt | CPU-tauglich |
|---|---|---|---|---|---|
| `google/gemma-4-e2b` | 2B | ~1,3 GB | ~4 GB | ~6 GB | langsam |
| `qwen3.5:2b` | 2B | ~1,4 GB | ~6 GB | ~8 GB | langsam |
| `qwen3.5:4b` | 4B | ~2,5 GB | ~10 GB | ~13 GB | ✗ |
| `qwen3.5:9b` | 9B | ~5,5 GB | ~18 GB | ~24 GB | ✗ |

