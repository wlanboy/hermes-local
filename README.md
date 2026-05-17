# Hermes Local

Lokale KI-Assistenten-Umgebung auf Basis von [Hermes](https://github.com/NousResearch/hermes-agent) und [Ollama](https://ollama.com). Läuft vollständig offline — keine Cloud-Abhängigkeit, keine Daten verlassen den Rechner.

## Überblick

| Komponente | Beschreibung | Port |
|---|---|---|
| **Ollama** | Lokaler LLM-Server | `11434` |
| **Hermes** | KI-Agent mit Web-Dashboard | `9119` |

Das Standard-Modell ist `gemma4:4b` — CPU-tauglich und benötigt ca. 3 GB RAM.

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

Die `.env` kann leer bleiben — Ollama wird ohne API-Key genutzt. Nur bei Bedarf ausfüllen:

```env
# Optional: Telegram Bot
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWED_USERS=
TELEGRAM_HOME_CHANNEL=
TELEGRAM_HOME_CHANNEL_NAME=
```

### 3. Container bauen und starten

```bash
docker compose up --build -d
```

Beim ersten Start wird das Hermes-Image gebaut (~2–3 Minuten).

### 4. Modell herunterladen

```bash
docker exec ollama ollama pull gemma4:4b
```

Das Modell wird in `~/.ollama` gespeichert und steht nach einem Neustart sofort zur Verfügung.

### 5. Dashboard öffnen

```
http://localhost:9119
```

Der Chat-Tab ist über das Dashboard erreichbar.

## Modell wechseln

In [hermes/cli-config.yaml](hermes/cli-config.yaml) das Modell anpassen:

```yaml
model:
  default: "gemma4:4b"   # z.B. auf llama3.2:3b ändern
  provider: "ollama"
```

Anschließend das Modell pullen und den Container neu starten:

```bash
docker exec ollama ollama pull llama3.2:3b
docker compose restart hermes
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
├── Dockerfile           # Hermes Image
├── docker-compose.yml   # Orchestrierung
├── entrypoint.sh        # Startskript (Konfig + Dashboard)
├── .env.example         # Vorlage für Umgebungsvariablen
├── hermes/
│   ├── cli-config.yaml  # Hermes-Konfiguration (Modell, Memory, …)
│   └── SOUL.md          # Agenten-Persona
└── config/              # Laufzeit-Konfiguration (wird automatisch angelegt)
```
