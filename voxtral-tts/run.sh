#!/usr/bin/with-contenv bashio

# Lecture des options de configuration
MISTRAL_API_KEY=$(bashio::config 'mistral_api_key')
VOICE_ID=$(bashio::config 'voice_id')
MODEL=$(bashio::config 'model')
RESPONSE_FORMAT=$(bashio::config 'response_format')
LANGUAGE=$(bashio::config 'language')
WYOMING_PORT=$(bashio::config 'wyoming_port')

# Validation de la clé API
if bashio::var.is_empty "${MISTRAL_API_KEY}"; then
    bashio::log.fatal "La clé API Mistral est requise. Configurez-la dans les options de l'addon."
    exit 1
fi

bashio::log.info "Démarrage de Wyoming Voxtral TTS..."
bashio::log.info "Modèle: ${MODEL}"
bashio::log.info "Format: ${RESPONSE_FORMAT}"
bashio::log.info "Langue: ${LANGUAGE}"
bashio::log.info "Port Wyoming: ${WYOMING_PORT}"

# Configuration du PYTHONPATH
export PYTHONPATH="/usr/share:${PYTHONPATH:-}"

# Construction des arguments
ARGS=(
    --uri "tcp://0.0.0.0:${WYOMING_PORT}"
    --api-key "${MISTRAL_API_KEY}"
    --model "${MODEL}"
    --response-format "${RESPONSE_FORMAT}"
    --language "${LANGUAGE}"
)

# Ajout de la voix custom si configurée
if bashio::var.has_value "${VOICE_ID}"; then
    bashio::log.info "Voix custom: ${VOICE_ID}"
    ARGS+=(--voice-id "${VOICE_ID}")
fi

exec python3 -m voxtral_tts "${ARGS[@]}"
