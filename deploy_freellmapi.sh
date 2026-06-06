#!/usr/bin/env bash
set -Eeuo pipefail

REPO_URL="https://github.com/tashfeenahmed/freellmapi.git"
APP_DIR="${APP_DIR:-/root/freellmapi}"
PORT="${PORT:-3001}"
HOST_BIND="${HOST_BIND:-127.0.0.1}"
PUBLIC_MODE=0

usage() {
  cat <<'EOF'
Usage:
  bash deploy_freellmapi.sh [options]

Options:
  --public          Listen on 0.0.0.0 so http://SERVER_IP:3001 works.
                    Only use this if you understand the security risk.
  --dir PATH        Install directory. Default: /root/freellmapi
  --port PORT       Host port. Default: 3001
  -h, --help        Show help.

Recommended private use:
  bash deploy_freellmapi.sh
  ssh -L 3001:127.0.0.1:3001 root@SERVER_IP
  open http://localhost:3001

Direct IP test:
  bash deploy_freellmapi.sh --public
  open http://SERVER_IP:3001
EOF
}

log() {
  printf '\n[%s] %s\n' "$(date '+%F %T')" "$*"
}

die() {
  printf '\nERROR: %s\n' "$*" >&2
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --public)
      PUBLIC_MODE=1
      HOST_BIND="0.0.0.0"
      shift
      ;;
    --dir)
      [[ $# -ge 2 ]] || die "--dir requires a path"
      APP_DIR="$2"
      shift 2
      ;;
    --port)
      [[ $# -ge 2 ]] || die "--port requires a value"
      PORT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown option: $1"
      ;;
  esac
done

[[ "$(id -u)" -eq 0 ]] || die "Please run as root, for example: sudo bash deploy_freellmapi.sh"
[[ "$PORT" =~ ^[0-9]+$ ]] || die "PORT must be a number"

if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  log "Detected system: ${PRETTY_NAME:-Linux}"
else
  log "Detected system: Linux"
fi

export DEBIAN_FRONTEND=noninteractive

log "Installing base packages"
apt-get update
apt-get install -y ca-certificates curl gnupg git openssl

if ! command -v docker >/dev/null 2>&1; then
  log "Installing Docker Engine"
  curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
  sh /tmp/get-docker.sh
else
  log "Docker already installed"
fi

systemctl enable --now docker

if ! docker compose version >/dev/null 2>&1; then
  die "Docker Compose plugin is not available. Check Docker installation output above."
fi

if [[ -d "$APP_DIR/.git" ]]; then
  log "Updating existing FreeLLMAPI checkout at $APP_DIR"
  git -C "$APP_DIR" fetch --all --prune
  git -C "$APP_DIR" pull --ff-only
elif [[ -e "$APP_DIR" ]]; then
  die "$APP_DIR exists but is not a git checkout. Move it away or choose --dir PATH."
else
  log "Cloning FreeLLMAPI into $APP_DIR"
  mkdir -p "$(dirname "$APP_DIR")"
  git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

if [[ -f .env ]]; then
  log "Keeping existing .env so encrypted provider keys remain readable"
  if grep -q '^HOST_BIND=' .env; then
    sed -i "s/^HOST_BIND=.*/HOST_BIND=${HOST_BIND}/" .env
  else
    printf '\nHOST_BIND=%s\n' "$HOST_BIND" >> .env
  fi
  if grep -q '^PORT=' .env; then
    sed -i "s/^PORT=.*/PORT=${PORT}/" .env
  else
    printf 'PORT=%s\n' "$PORT" >> .env
  fi
else
  log "Creating .env with a fresh encryption key"
  ENCRYPTION_KEY="$(openssl rand -hex 32)"
  cat > .env <<EOF
ENCRYPTION_KEY=${ENCRYPTION_KEY}
PORT=${PORT}
HOST_BIND=${HOST_BIND}
REQUEST_ANALYTICS_RETENTION_DAYS=90
REQUEST_ANALYTICS_MAX_ROWS=100000
EOF
fi

chmod 600 .env

if [[ "$PUBLIC_MODE" -eq 1 ]] && command -v ufw >/dev/null 2>&1; then
  if ufw status | grep -qi '^Status: active'; then
    log "UFW is active; allowing TCP port ${PORT}"
    ufw allow "${PORT}/tcp"
  fi
fi

log "Starting FreeLLMAPI"
docker compose pull || true
docker compose up -d

log "Waiting for health check"
for i in {1..30}; do
  if curl -fsS "http://127.0.0.1:${PORT}/api/ping" >/dev/null 2>&1; then
    break
  fi
  sleep 2
  if [[ "$i" -eq 30 ]]; then
    docker compose logs --tail=120 freellmapi || true
    die "FreeLLMAPI did not become healthy in time"
  fi
done

log "Container status"
docker compose ps

cat <<EOF

FreeLLMAPI is deployed.

Install directory:
  ${APP_DIR}

Local-on-server URL:
  http://127.0.0.1:${PORT}

EOF

if [[ "$PUBLIC_MODE" -eq 1 ]]; then
  SERVER_IP="$(curl -fsS https://api.ipify.org 2>/dev/null || true)"
  cat <<EOF
Public mode is enabled.
Try from your computer:
  http://${SERVER_IP:-SERVER_IP}:${PORT}

Security note:
  This exposes the dashboard/API port to the internet. For long-term personal use,
  consider SSH tunneling, Tailscale, firewall allowlisting, or HTTPS reverse proxy.

EOF
else
  cat <<EOF
Private mode is enabled.
Run this on your computer to access it safely:
  ssh -L ${PORT}:127.0.0.1:${PORT} root@SERVER_IP

Then open:
  http://localhost:${PORT}

To expose it directly by IP later:
  cd ${APP_DIR}
  HOST_BIND=0.0.0.0 docker compose up -d

EOF
fi
