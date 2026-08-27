#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-localhost}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

BACKEND_PID=""
FRONTEND_PID=""

fail() {
    printf 'run.sh: %s\n' "$1" >&2
    exit 1
}

port_is_available() {
    ! (echo > "/dev/tcp/127.0.0.1/$1") 2>/dev/null
}

cleanup() {
    local exit_code=$?
    trap - EXIT INT TERM

    for pid in "$BACKEND_PID" "$FRONTEND_PID"; do
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
        fi
    done

    for pid in "$BACKEND_PID" "$FRONTEND_PID"; do
        if [[ -n "$pid" ]]; then
            wait "$pid" 2>/dev/null || true
        fi
    done

    exit "$exit_code"
}

trap cleanup EXIT INT TERM

command -v uv >/dev/null 2>&1 || fail "uv is required. Install it from https://docs.astral.sh/uv/"
command -v npm >/dev/null 2>&1 || fail "npm is required. Install Node.js 20 or newer."
command -v setsid >/dev/null 2>&1 || fail "setsid is required to manage both application processes gracefully."

[[ -f "$BACKEND_DIR/pyproject.toml" ]] || fail "backend/pyproject.toml was not found."
[[ -f "$FRONTEND_DIR/package.json" ]] || fail "frontend/package.json was not found."
[[ -d "$FRONTEND_DIR/node_modules" ]] || fail "frontend dependencies are missing. Run 'cd frontend && npm install' first."
[[ "$BACKEND_PORT" =~ ^[0-9]+$ ]] || fail "BACKEND_PORT must be a number."
[[ "$FRONTEND_PORT" =~ ^[0-9]+$ ]] || fail "FRONTEND_PORT must be a number."

port_is_available "$BACKEND_PORT" || fail "backend port $BACKEND_PORT is already in use."
while ! port_is_available "$FRONTEND_PORT"; do
    FRONTEND_PORT=$((FRONTEND_PORT + 1))
done

BACKEND_CORS_ORIGINS="${CORS_ALLOWED_ORIGINS:-[\"http://localhost:${FRONTEND_PORT}\",\"http://127.0.0.1:${FRONTEND_PORT}\"]}"

printf 'Applying backend database migrations...\n'
(
    cd -- "$BACKEND_DIR"
    env -u VIRTUAL_ENV uv run alembic upgrade head
)

printf 'Starting backend at http://%s:%s\n' "$BACKEND_HOST" "$BACKEND_PORT"
setsid env -u VIRTUAL_ENV CORS_ALLOWED_ORIGINS="$BACKEND_CORS_ORIGINS" bash -c \
    'cd -- "$1" && exec uv run uvicorn l1_support_bot.interface.api.main:app --reload --host "$2" --port "$3"' \
    run-backend "$BACKEND_DIR" "$BACKEND_HOST" "$BACKEND_PORT" &
BACKEND_PID=$!

printf 'Starting frontend at http://%s:%s\n' "$FRONTEND_HOST" "$FRONTEND_PORT"
setsid bash -c \
    'cd -- "$1" && exec npm run dev -- --host "$2" --port "$3"' \
    run-frontend "$FRONTEND_DIR" "$FRONTEND_HOST" "$FRONTEND_PORT" &
FRONTEND_PID=$!

printf 'Application is running. Press Ctrl+C to stop both services.\n'

if wait -n "$BACKEND_PID" "$FRONTEND_PID"; then
    exit 0
fi

exit_code=$?
printf 'run.sh: one of the services stopped unexpectedly (exit code %s).\n' "$exit_code" >&2
exit "$exit_code"
