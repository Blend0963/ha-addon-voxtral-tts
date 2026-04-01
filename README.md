# Wyoming Voxtral TTS — Add-on Home Assistant

Addon Home Assistant qui fait le pont entre le protocole **Wyoming** (TTS de Home Assistant Assist) et l'API cloud **Mistral Voxtral TTS**.

## Architecture

```
Home Assistant → Wyoming Protocol → Cet Addon (Python) → API Mistral Cloud → base64 decode → Audio WAV → retour à HA
```

## Pourquoi cet addon ?

L'API Mistral TTS (`POST https://api.mistral.ai/v1/audio/speech`) retourne l'audio en **base64 dans un JSON** (champ `audio_data`), contrairement à l'API OpenAI qui retourne du binaire brut. Les bridges Wyoming existants ne sont donc pas compatibles.

## Installation

1. Ajoutez ce dépôt comme dépôt d'add-ons dans Home Assistant :
   - **Paramètres** → **Modules complémentaires** → **Boutique des modules complémentaires** → **⋮** → **Dépôts**
   - URL : `https://github.com/jefedi/ha-addon-voxtral-tts`
2. Installez l'addon **Wyoming Voxtral TTS**
3. Configurez votre clé API Mistral dans les options
4. Démarrez l'addon
5. Ajoutez l'intégration Wyoming dans HA pointant vers `localhost:10400`

## Configuration

| Option | Description | Défaut |
|--------|-------------|--------|
| `mistral_api_key` | Clé API Mistral (requise) | — |
| `voice_id` | ID de voix custom Mistral | — |
| `model` | Modèle TTS | `voxtral-mini-tts-2603` |
| `response_format` | Format audio (wav/mp3/pcm/flac/opus) | `wav` |
| `language` | Langue | `fr` |
| `wyoming_port` | Port du serveur Wyoming | `10400` |

## Voix disponibles

- **Français** : `french_female`, `french_male`
- **Anglais** : `british_female`, `british_male`, `neutral_female`, `neutral_male`
- **Allemand** : `german_female`, `german_male`
- **Espagnol** : `spanish_female`, `spanish_male`
- **Italien** : `italian_female`, `italian_male`
- **Portugais** : `portuguese_female`, `portuguese_male`
- **Néerlandais** : `dutch_female`, `dutch_male`
- **Hindi** : `hindi_female`, `hindi_male`
- **Arabe** : `arabic_female`, `arabic_male`
- **Casual** : `casual_female`, `casual_male`

## Coûts

L'API Mistral TTS est facturée à l'usage. Consultez la [tarification Mistral](https://mistral.ai/pricing/) pour les détails.

## Licence

MIT
