#!/usr/bin/env sh
# Starts llama-server once, keeping the model resident in RAM.
# The chatbot app talks to this over HTTP instead of spawning llama-cli
# per message. Run this as its own systemd service (see setup_service.sh),
# not from inside the chatbot process.
#
# Required environment variables:
#   CHATBOT_MODEL              Path to the GGUF model file.
# Optional environment variables (defaults shown):
#   CHATBOT_LLAMA_SERVER_BINARY=llama-server
#   CHATBOT_LLAMA_SERVER_HOST=127.0.0.1
#   CHATBOT_LLAMA_SERVER_PORT=8080
#   CHATBOT_LLAMA_CTX_SIZE=2048

set -eu

if [ -z "${CHATBOT_MODEL:-}" ]; then
    echo "CHATBOT_MODEL must point at a .gguf file" >&2
    exit 1
fi

BINARY="${CHATBOT_LLAMA_SERVER_BINARY:-llama-server}"
HOST="${CHATBOT_LLAMA_SERVER_HOST:-127.0.0.1}"
PORT="${CHATBOT_LLAMA_SERVER_PORT:-8080}"
CTX_SIZE="${CHATBOT_LLAMA_CTX_SIZE:-2048}"

exec "$BINARY" \
    --model "$CHATBOT_MODEL" \
    --host "$HOST" \
    --port "$PORT" \
    --ctx-size "$CTX_SIZE"
