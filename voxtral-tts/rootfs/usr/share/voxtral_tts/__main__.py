"""Serveur Wyoming TTS pour Voxtral (Mistral AI).

Point d'entrée principal : parse les arguments, déclare les voix
disponibles et lance le serveur async Wyoming.
"""

import argparse
import asyncio
import logging
from functools import partial

from wyoming.info import Attribution, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncServer

from .handler import VoxtralTtsHandler

_LOGGER = logging.getLogger(__name__)

_ATTRIBUTION = Attribution(name="Mistral AI", url="https://mistral.ai")


def _voice(name: str, description: str, languages: list[str]) -> TtsVoice:
    """Crée une TtsVoice avec les champs requis par wyoming 1.5."""
    return TtsVoice(
        name=name,
        description=description,
        attribution=_ATTRIBUTION,
        installed=True,
        version="1.0",
        languages=languages,
    )


# Voix prédéfinies Voxtral par langue
VOICES_BY_LANGUAGE: dict[str, list[TtsVoice]] = {
    "fr": [
        _voice("french_female", "Française (femme)", ["fr"]),
        _voice("french_male", "Français (homme)", ["fr"]),
    ],
    "en": [
        _voice("british_female", "British (female)", ["en"]),
        _voice("british_male", "British (male)", ["en"]),
        _voice("neutral_female", "Neutral (female)", ["en"]),
        _voice("neutral_male", "Neutral (male)", ["en"]),
    ],
    "de": [
        _voice("german_female", "Deutsche (Frau)", ["de"]),
        _voice("german_male", "Deutscher (Mann)", ["de"]),
    ],
    "es": [
        _voice("spanish_female", "Española (mujer)", ["es"]),
        _voice("spanish_male", "Español (hombre)", ["es"]),
    ],
    "it": [
        _voice("italian_female", "Italiana (donna)", ["it"]),
        _voice("italian_male", "Italiano (uomo)", ["it"]),
    ],
    "pt": [
        _voice("portuguese_female", "Portuguesa (mulher)", ["pt"]),
        _voice("portuguese_male", "Português (homem)", ["pt"]),
    ],
    "nl": [
        _voice("dutch_female", "Nederlandse (vrouw)", ["nl"]),
        _voice("dutch_male", "Nederlands (man)", ["nl"]),
    ],
    "hi": [
        _voice("hindi_female", "हिन्दी (महिला)", ["hi"]),
        _voice("hindi_male", "हिन्दी (पुरुष)", ["hi"]),
    ],
    "ar": [
        _voice("arabic_female", "عربية (أنثى)", ["ar"]),
        _voice("arabic_male", "عربي (ذكر)", ["ar"]),
    ],
}

# Voix casual (disponibles quelle que soit la langue)
CASUAL_VOICES = [
    _voice("casual_female", "Casual (female)", ["fr", "en"]),
    _voice("casual_male", "Casual (male)", ["fr", "en"]),
]


async def main() -> None:
    """Point d'entrée principal du serveur Wyoming Voxtral TTS."""
    parser = argparse.ArgumentParser(description="Wyoming Voxtral TTS")
    parser.add_argument("--uri", required=True, help="URI du serveur Wyoming (ex: tcp://0.0.0.0:10400)")
    parser.add_argument("--api-key", required=True, help="Clé API Mistral")
    parser.add_argument("--model", default="voxtral-mini-tts-2603", help="Modèle TTS Mistral")
    parser.add_argument("--response-format", default="wav", help="Format audio (wav/mp3/pcm/flac/opus)")
    parser.add_argument("--language", default="fr", help="Langue des voix prédéfinies")
    parser.add_argument("--voice-id", default=None, help="ID de voix custom Mistral")
    parser.add_argument("--debug", action="store_true", help="Active les logs de debug")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    )

    # Construction de la liste de voix annoncées
    if args.voice_id:
        voices = [_voice(args.voice_id, f"Voix custom ({args.voice_id})", [args.language])]
        _LOGGER.info("Mode voix custom : %s", args.voice_id)
    else:
        voices = list(VOICES_BY_LANGUAGE.get(args.language, [])) + CASUAL_VOICES
        _LOGGER.info("Voix annoncées pour la langue '%s' : %d", args.language, len(voices))

    wyoming_info = Info(
        tts=[
            TtsProgram(
                name="voxtral-tts",
                description="Voxtral TTS (Mistral AI)",
                attribution=_ATTRIBUTION,
                installed=True,
                voices=voices,
            )
        ]
    )

    server = AsyncServer.from_uri(args.uri)
    _LOGGER.info("Serveur Wyoming Voxtral TTS démarré sur %s", args.uri)

    await server.run(
        partial(
            VoxtralTtsHandler,
            wyoming_info,
            args,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
