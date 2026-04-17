#!/usr/bin/env bash
# Usage: ./deploy.sh user@your-vps-ip
# Pulls latest code on VPS and restarts the bot container.

set -euo pipefail

TARGET="${1:-}"
if [[ -z "$TARGET" ]]; then
  echo "Usage: $0 user@host"
  exit 1
fi

REMOTE_DIR="/opt/BankConverterBot"

echo "==> Deploying to $TARGET:$REMOTE_DIR"

ssh "$TARGET" bash -s << EOF
  set -euo pipefail

  # Clone on first deploy, pull on subsequent ones
  if [ ! -d "$REMOTE_DIR" ]; then
    git clone https://github.com/hronicasync/BankConverterBot.git "$REMOTE_DIR"
  fi

  cd "$REMOTE_DIR"
  git pull origin main

  # Rebuild image and restart container
  docker compose up -d --build

  echo "==> Done. Container status:"
  docker compose ps
EOF
