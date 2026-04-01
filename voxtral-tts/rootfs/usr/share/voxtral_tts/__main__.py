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

# Voix prédéfinies Voxtral par langue
VOICES_BY_LANGUAGE: dict[str, list[TtsVoice]] = {
    "fr": [
        TtsVoice(name="french_female", description="Française (femme)", languages=["fr"]),
        TtsVoice(name="french_male", description="Français (homme)", languages=["fr"]),
    ],
    "en": [
        TtsVoice(name="british_female", description="British (female)", languages=["en"]),
        TtsVoice(name="british_male", description="British (male)", languages=["en"]),
        TtsVoice(name="neutral_female", description="Neutral (female)", languages=["en"]),
        TtsVoice(name="neutral_male", description="Neutral (male)", languages=["en"]),
    ],
    "de": [
        TtsVoice(name="german_female", description="Deutsche (Frau)", languages=["de"]),
        TtsVoice(name="german_male", description="Deutscher (Mann)", languages=["de"]),
    ],
    "es": [
        TtsVoice(name="spanish_female", description="Española (mujer)", languages=["es"]),
        TtsVoice(name="spanish_male", description="Español (hombre)", languages=["es"]),
    ],
    "it": [
        TtsVoice(name="italian_female", description="Italiana (donna)", languages=["it"]),
        TtsVoice(name="italian_male", description="Italiano (uomo)", languages=["it"]),
    ],
    "pt": [
        TtsVoice(name="portuguese_female", description="Portuguesa (mulher)", languages=["pt"]),
        TtsVoice(name="portuguese_male", description="Português (homem)", languages=["pt"]),
    ],
    "nl": [
        TtsVoice(name="dutch_female", description="Nederlandse (vrouw)", languages=["nl"]),
        TtsVoice(name="dutch_male", description="Nederlands (man)", languages=["nl"]),
    ],
    "hi": [
        TtsVoice(name="hindi_female", description="हिन्दी (महिला)", languages=["hi"]),
        TtsVoice(name="hindi_male", description="हिन्दी (पुरुष)", languages=["hi"]),
    ],
    "ar": [
        TtsVoice(name="arabic_female", description="عربية (أنثى)", languages=["ar"]),
        TtsVoice(name="arabic_male", description="عربي (ذكر)", languages=["ar"]),
    ],
}

# Voix casual (disponibles quelle que soit la langue)
CASUAL_VOICES = [
    TtsVoice(name="casual_female", description="Casual (female)", languages=["fr", "en"]),
    TtsVoice(name="casual_male", description="Casual (male)", languages=["fr", "en"]),
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
        voices = [TtsVoice(name=args.voice_id, description=f"Voix custom ({args.voice_id})", languages=[args.language])]
        _LOGGER.info("Mode voix custom : %s", args.voice_id)
    else:
        voices = list(VOICES_BY_LANGUAGE.get(args.language, [])) + CASUAL_VOICES
        _LOGGER.info("Voix annoncées pour la langue '%s' : %d", args.language, len(voices))

    wyoming_info = Info(
        tts=[
            TtsProgram(
                name="voxtral-tts",
                description="Voxtral TTS (Mistral AI)",
                attribution=Attribution(name="Mistral AI", url="https://mistral.ai"),
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
