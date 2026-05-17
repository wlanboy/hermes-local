
#!/bin/bash
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

# Create all directories Hermes expects (volume may be empty on first deploy)
mkdir -p "$HERMES_HOME/memories" \
         "$HERMES_HOME/skills" \
         "$HERMES_HOME/sessions" \
         "$HERMES_HOME/cron" \
         "$HERMES_HOME/cron/output" \
         "$HERMES_HOME/hooks" \
         "$HERMES_HOME/logs"

# Write config to BOTH filenames — CLI uses cli-config.yaml, gateway uses config.yaml
cp /app/config/cli-config.yaml "$HERMES_HOME/cli-config.yaml"
cp /app/config/cli-config.yaml "$HERMES_HOME/config.yaml"

# Write SOUL.md — agent identity/persona
cp /app/config/SOUL.md "$HERMES_HOME/SOUL.md"

# Write ALL secrets to ~/.hermes/.env — Hermes reads from here, not system env
cat > "$HERMES_HOME/.env" << EOF
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
TELEGRAM_ALLOWED_USERS=${TELEGRAM_ALLOWED_USERS:-}
TELEGRAM_HOME_CHANNEL=${TELEGRAM_HOME_CHANNEL:-}
TELEGRAM_HOME_CHANNEL_NAME=${TELEGRAM_HOME_CHANNEL_NAME:-}
HERMES_HUMAN_DELAY_MODE=${HERMES_HUMAN_DELAY_MODE:-natural}
HERMES_ACCEPT_HOOKS=${HERMES_ACCEPT_HOOKS:-1}
EOF
chmod 600 "$HERMES_HOME/.env"

echo "Hermes config ready. Starting dashboard..."
exec hermes dashboard --host 0.0.0.0 --port 9119 --tui --no-open --insecure