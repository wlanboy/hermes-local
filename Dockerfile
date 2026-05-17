FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl bash git nodejs npm build-essential tini \
    && rm -rf /var/lib/apt/lists/*

# Install Hermes — pinned to a specific commit for reproducibility
# Update this SHA when you want to upgrade Hermes
ARG HERMES_COMMIT
RUN curl -fsSL "https://raw.githubusercontent.com/NousResearch/hermes-agent/${HERMES_COMMIT}/scripts/install.sh" \
    | bash -s -- --skip-setup \
    && pip install --no-cache-dir 'hermes-agent[web,pty]'

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
COPY . .

# Sanity check — verify install succeeded
RUN hermes --version

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8443

# tini as PID 1 to handle zombie subprocess cleanup
ENTRYPOINT ["/usr/bin/tini", "-g", "--", "/entrypoint.sh"]