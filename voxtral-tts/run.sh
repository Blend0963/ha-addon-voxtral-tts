#!/bin/sh

CONFIG="/data/options.json"

# Lecture des options depuis options.json
MISTRAL_API_KEY=$(jq -r '.mistral_api_key' "$CONFIG")
VOICE_ID=$(jq -r '.voice_id // empty' "$CONFIG")
MODEL=$(jq -r '.model' "$CONFIG")
RESPONSE_FORMAT=$(jq -r '.response_format' "$CONFIG")
LANGUAGE=$(jq -r '.language' "$CONFIG")
WYOMING_PORT=$(jq -r '.wyoming_port' "$CONFIG")

# Validation de la clé API
if [ -z "$MISTRAL_API_KEY" ]; then
    echo "[FATAL] La clé API Mistral est requise. Configurez-la dans les options de l'addon."
    exit 1
fi

echo "[INFO] Démarrage de Wyoming Voxtral TTS..."
echo "[INFO] Modèle: ${MODEL}"
echo "[INFO] Format: ${RESPONSE_FORMAT}"
echo "[INFO] Langue: ${LANGUAGE}"
echo "[INFO] Port Wyoming: ${WYOMING_PORT}"

# Configuration du PYTHONPATH
export PYTHONPATH="/usr/share:${PYTHONPATH:-}"

# Construction des arguments
ARGS="--uri tcp://0.0.0.0:${WYOMING_PORT} --api-key ${MISTRAL_API_KEY} --model ${MODEL} --response-format ${RESPONSE_FORMAT} --language ${LANGUAGE}"

# Ajout de la voix custom si configurée
if [ -n "$VOICE_ID" ]; then
    echo "[INFO] Voix custom: ${VOICE_ID}"
    ARGS="${ARGS} --voice-id ${VOICE_ID}"
fi

exec python3 -m voxtral_tts $ARGS
