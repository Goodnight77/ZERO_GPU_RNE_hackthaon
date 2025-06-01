# 🎙 Transcripteur Audio Whisper

Une application Streamlit pour la transcription audio en temps réel utilisant OpenAI Whisper.

## 📋 Fonctionnalités

- ✅ Enregistrement audio en temps réel
- ✅ Transcription multilingue (10 langues supportées)
- ✅ Interface utilisateur moderne et intuitive
- ✅ Support de multiples périphériques audio
- ✅ Affichage des timestamps (optionnel)
- ✅ Conversion automatique des fichiers audio

## 🛠 Installation

### Prérequis système

**Sur Ubuntu/Debian :**
```bash
sudo apt update
sudo apt install portaudio19-dev python3-pyaudio ffmpeg
```

**Sur macOS :**
```bash
brew install portaudio ffmpeg
```

**Sur Windows :**
- Téléchargez et installez [FFmpeg](https://ffmpeg.org/download.html)
- Ajoutez FFmpeg au PATH système

### Installation Python

1. **Clonez le repository :**
```bash
git clone <this repo>
cd speech_to_text
```

2. **Créez un environnement virtuel (recommandé) :**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installez les dépendances :**
```bash
pip install -r requirements.txt
```

### Installation alternative avec conda

```bash
conda create -n whisper-transcriber python=3.9
conda activate whisper-transcriber
conda install pytorch torchaudio -c pytorch
pip install -r requirements.txt
```

## 🚀 Utilisation

1. **Lancez l'application :**
```bash
streamlit run app.py
```

2. **Accédez à l'interface :**
   - Ouvrez votre navigateur à l'adresse `http://localhost:8501`

3. **Configuration :**
   - Sélectionnez la langue de transcription dans la barre latérale
   - Choisissez votre périphérique audio
   - Configurez les options avancées si nécessaire

4. **Enregistrement :**
   - Cliquez sur "🎤 Commencer l'enregistrement"
   - Parlez dans votre microphone
   - Cliquez sur "⏹ Arrêter l'enregistrement"
   - Cliquez sur "🚀 Transcrire l'enregistrement"

## 📁 Structure du projet

```
whisper-transcriber/
├── app.py              # Application principale Streamlit
├── audio_utils.py      # Utilitaires audio et enregistrement
├── requirements.txt    # Dépendances Python
└── README.md          # Documentation
```

## 🌍 Langues supportées

- 🇫🇷 Français
- 🇬🇧 English
- 🇸🇦 العربية (Arabe)
- 🇪🇸 Español
- 🇩🇪 Deutsch
- 🇮🇹 Italiano
- 🇵🇹 Português
- 🇷🇺 Русский
- 🇨🇳 中文 (Chinois)
- 🇯🇵 日本語 (Japonais)

## ⚙ Configuration avancée

### Modèles Whisper disponibles

L'application utilise le modèle `small` par défaut. Vous pouvez modifier cela dans `app.py` :

```python
model = whisper.load_model("base")  # tiny, base, small, medium, large
```

**Tailles des modèles :**
- `tiny` : ~39 MB, le plus rapide
- `base` : ~74 MB, bon compromis
- `small` : ~244 MB, qualité correcte (par défaut)
- `medium` : ~769 MB, bonne qualité
- `large` : ~1550 MB, meilleure qualité

### Paramètres audio

Dans `audio_utils.py`, vous pouvez ajuster :

```python
CHUNK = 1024        # Taille du buffer
RATE = 16000        # Fréquence d'échantillonnage
CHANNELS = 1        # Mono
```

## 🐛 Résolution des problèmes

### Erreur PyAudio
```bash
# Ubuntu/Debian
sudo apt-get install portaudio19-dev

# macOS
brew install portaudio

# Puis réinstallez PyAudio
pip uninstall pyaudio
pip install pyaudio
```

### Erreur FFmpeg
Assurez-vous que FFmpeg est installé et accessible depuis le PATH :
```bash
ffmpeg -version
```

### Problèmes de microphone
- Vérifiez les permissions microphone de votre navigateur
- Testez avec différents périphériques audio dans les paramètres
- Sur macOS, autorisez l'accès microphone dans Préférences Système

### Modèle Whisper ne se charge pas
```bash
# Forcer le téléchargement du modèle
python -c "import whisper; whisper.load_model('small')"
```

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

