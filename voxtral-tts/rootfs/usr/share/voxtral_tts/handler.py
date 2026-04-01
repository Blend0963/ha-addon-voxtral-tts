"""Handler Wyoming pour Voxtral TTS.

Gère les événements Synthesize : appelle l'API Mistral, décode la réponse
base64, convertit en PCM 16-bit et renvoie l'audio via le protocole Wyoming.
"""

import argparse
import base64
import io
import logging
import struct
import subprocess
import wave

import httpx
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler
from wyoming.tts import Synthesize

_LOGGER = logging.getLogger(__name__)

# Constantes audio Voxtral
VOXTRAL_SAMPLE_RATE = 24000
VOXTRAL_SAMPLE_WIDTH = 2  # 16-bit
VOXTRAL_CHANNELS = 1      # mono

# Taille des blocs envoyés via Wyoming
AUDIO_CHUNK_SIZE = 4096

# Timeout pour l'appel API
API_TIMEOUT = 60.0

MISTRAL_API_URL = "https://api.mistral.ai/v1/audio/speech"


class VoxtralTtsHandler(AsyncEventHandler):
    """Gestionnaire d'événements Wyoming pour la synthèse vocale Voxtral."""

    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.wyoming_info = wyoming_info
        self.cli_args = cli_args
        self.http_client = httpx.AsyncClient(timeout=API_TIMEOUT)

    async def handle_event(self, event: Event) -> bool:
        """Traite un événement Wyoming entrant."""
        if Synthesize.is_type(event.type):
            synthesize = Synthesize.from_event(event)
            _LOGGER.debug("Requête de synthèse : %s", synthesize.text)

            # Détermination de la voix à utiliser
            voice = self.cli_args.voice_id
            if not voice and synthesize.voice and synthesize.voice.name:
                voice = synthesize.voice.name
            if not voice:
                voice = "french_female"

            await self._synthesize(synthesize.text, voice)
            return True

        if Describe.is_type(event.type):
            self.write_event(self.wyoming_info.event())
            return True

        return True

    async def _synthesize(self, text: str, voice: str) -> None:
        """Appelle l'API Mistral et envoie l'audio via Wyoming."""
        _LOGGER.info("Synthèse : voix=%s, texte='%s'", voice, text[:80])

        # Appel à l'API Mistral
        payload = {
            "model": self.cli_args.model,
            "input": text,
            "voice_id": voice,
            "response_format": self.cli_args.response_format,
        }

        try:
            response = await self.http_client.post(
                MISTRAL_API_URL,
                headers={
                    "Authorization": f"Bearer {self.cli_args.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            _LOGGER.error("Erreur API Mistral (%d) : %s", exc.response.status_code, exc.response.text)
            return
        except httpx.HTTPError as exc:
            _LOGGER.error("Erreur réseau lors de l'appel API Mistral : %s", exc)
            return

        # Extraction et décodage de l'audio base64
        data = response.json()
        audio_b64 = data.get("audio_data")
        if not audio_b64:
            _LOGGER.error("Réponse API sans champ 'audio_data'")
            return

        audio_bytes = base64.b64decode(audio_b64)
        _LOGGER.debug("Audio décodé : %d octets", len(audio_bytes))

        # Conversion en PCM 16-bit
        pcm_data, sample_rate = self._extract_pcm(audio_bytes)
        if pcm_data is None:
            _LOGGER.error("Impossible d'extraire le PCM de l'audio")
            return

        # Envoi via Wyoming
        self.write_event(
            AudioStart(
                rate=sample_rate,
                width=VOXTRAL_SAMPLE_WIDTH,
                channels=VOXTRAL_CHANNELS,
            ).event()
        )

        # Envoi par blocs
        for offset in range(0, len(pcm_data), AUDIO_CHUNK_SIZE):
            chunk = pcm_data[offset : offset + AUDIO_CHUNK_SIZE]
            self.write_event(
                AudioChunk(
                    audio=chunk,
                    rate=sample_rate,
                    width=VOXTRAL_SAMPLE_WIDTH,
                    channels=VOXTRAL_CHANNELS,
                ).event()
            )

        self.write_event(AudioStop().event())
        _LOGGER.info("Synthèse terminée (%d octets PCM)", len(pcm_data))

    def _extract_pcm(self, audio_bytes: bytes) -> tuple[bytes | None, int]:
        """Extrait le PCM 16-bit mono depuis les données audio.

        Retourne (pcm_data, sample_rate) ou (None, 0) en cas d'erreur.
        """
        fmt = self.cli_args.response_format

        if fmt == "wav":
            return self._parse_wav(audio_bytes)
        elif fmt == "pcm":
            return self._convert_float32_to_int16(audio_bytes), VOXTRAL_SAMPLE_RATE
        else:
            # mp3, flac, opus → conversion via ffmpeg
            return self._ffmpeg_to_wav(audio_bytes)

    def _parse_wav(self, data: bytes) -> tuple[bytes | None, int]:
        """Parse un fichier WAV et retourne le PCM brut."""
        try:
            with wave.open(io.BytesIO(data), "rb") as wf:
                sample_rate = wf.getframerate()
                sample_width = wf.getsampwidth()
                channels = wf.getnchannels()
                pcm_data = wf.readframes(wf.getnframes())

                # Conversion en mono si nécessaire
                if channels == 2:
                    pcm_data = self._stereo_to_mono(pcm_data, sample_width)

                # Conversion en 16-bit si nécessaire
                if sample_width == 4:
                    pcm_data = self._convert_float32_to_int16(pcm_data)
                elif sample_width == 1:
                    # 8-bit unsigned → 16-bit signed
                    pcm_data = bytes(
                        b
                        for sample in pcm_data
                        for b in struct.pack("<h", (sample - 128) << 8)
                    )

                return pcm_data, sample_rate
        except wave.Error as exc:
            _LOGGER.error("Erreur parsing WAV : %s", exc)
            return None, 0

    @staticmethod
    def _convert_float32_to_int16(data: bytes) -> bytes:
        """Convertit du PCM float32 little-endian en int16."""
        num_samples = len(data) // 4
        samples = struct.unpack(f"<{num_samples}f", data)
        # Clamp entre -1.0 et 1.0 puis conversion
        int16_samples = [
            int(max(-1.0, min(1.0, s)) * 32767)
            for s in samples
        ]
        return struct.pack(f"<{num_samples}h", *int16_samples)

    @staticmethod
    def _stereo_to_mono(data: bytes, sample_width: int) -> bytes:
        """Convertit du stéréo en mono en moyennant les canaux."""
        fmt_char = {1: "b", 2: "h", 4: "i"}[sample_width]
        num_samples = len(data) // sample_width
        samples = struct.unpack(f"<{num_samples}{fmt_char}", data)
        mono = [
            (samples[i] + samples[i + 1]) // 2
            for i in range(0, num_samples, 2)
        ]
        return struct.pack(f"<{len(mono)}{fmt_char}", *mono)

    def _ffmpeg_to_wav(self, data: bytes) -> tuple[bytes | None, int]:
        """Convertit un flux audio en WAV via ffmpeg."""
        try:
            result = subprocess.run(
                [
                    "ffmpeg", "-i", "pipe:0",
                    "-f", "wav",
                    "-acodec", "pcm_s16le",
                    "-ac", "1",
                    "-ar", str(VOXTRAL_SAMPLE_RATE),
                    "pipe:1",
                ],
                input=data,
                capture_output=True,
                check=True,
            )
            return self._parse_wav(result.stdout)
        except subprocess.CalledProcessError as exc:
            _LOGGER.error("Erreur ffmpeg : %s", exc.stderr.decode(errors="replace"))
            return None, 0
        except FileNotFoundError:
            _LOGGER.error("ffmpeg introuvable — installez ffmpeg")
            return None, 0
