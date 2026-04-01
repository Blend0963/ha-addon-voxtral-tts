# Wyoming Voxtral TTS

Cet addon permet d'utiliser la synthèse vocale **Voxtral** de Mistral AI dans Home Assistant via le protocole Wyoming.

## Prérequis

- Un compte Mistral AI avec une clé API valide
- Home Assistant avec l'intégration Wyoming

## Configuration

### Clé API Mistral (`mistral_api_key`)

Votre clé API Mistral. Obtenez-la sur [console.mistral.ai](https://console.mistral.ai/).

### Voix custom (`voice_id`)

Optionnel. Si vous avez créé une voix personnalisée via l'API Mistral, entrez son identifiant ici. Si vide, les voix prédéfinies seront utilisées.

### Modèle (`model`)

Le modèle TTS à utiliser. Par défaut : `voxtral-mini-tts-2603`.

### Format audio (`response_format`)

Format de sortie audio demandé à l'API Mistral :
- `wav` (défaut) — Meilleure compatibilité
- `mp3` — Plus compact
- `pcm` — Audio brut
- `flac` — Sans perte
- `opus` — Compact et bonne qualité

> Note : quel que soit le format demandé, l'audio est converti en WAV PCM 16-bit pour le protocole Wyoming.

### Langue (`language`)

Langue des voix prédéfinies : `fr`, `en`, `de`, `es`, `nl`, `pt`, `it`, `hi`, `ar`.

### Port Wyoming (`wyoming_port`)

Port TCP du serveur Wyoming. Par défaut : `10400`.

## Intégration avec Home Assistant

Après démarrage de l'addon :

1. Allez dans **Paramètres** → **Appareils et services** → **Ajouter une intégration**
2. Cherchez **Wyoming Protocol**
3. Entrez `localhost` et le port configuré (par défaut `10400`)
4. La synthèse vocale Voxtral apparaîtra comme option TTS dans Assist

## Dépannage

- Vérifiez les logs de l'addon pour les erreurs API
- Assurez-vous que votre clé API Mistral est valide et dispose de crédits
- Le port configuré doit être libre et non utilisé par un autre addon
