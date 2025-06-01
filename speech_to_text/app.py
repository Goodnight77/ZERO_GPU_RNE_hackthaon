import streamlit as st
import whisper
import tempfile
import os
import time
import threading
from audio_utils import AudioRecorder, save_recorded_audio, convert_audio_for_whisper, check_audio_devices, transcribe_audio

# Configuration de la page
st.set_page_config(
    page_title="🎙 Transcripteur Audio Whisper",
    page_icon="🎙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un style moderne
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .success-box {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(90deg, #3498db 0%, #74b9ff 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(90deg, #f39c12 0%, #f1c40f 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    
    .recording-box {
        background: linear-gradient(90deg, #e74c3c 0%, #ff6b6b 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
        text-align: center;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .recording-button {
        background: linear-gradient(90deg, #e74c3c 0%, #ff6b6b 100%) !important;
    }
    
    .stop-button {
        background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des variables de session
if 'recording' not in st.session_state:
    st.session_state.recording = False

if 'audio_recorder' not in st.session_state:
    st.session_state.audio_recorder = AudioRecorder()

# Initialisation du modèle Whisper
@st.cache_resource
def load_whisper_model():
    """Charge le modèle Whisper (mise en cache pour éviter le rechargement)"""
    try:
        with st.spinner('🔄 Chargement du modèle Whisper...'):
            model = whisper.load_model("small")
        st.success("✅ Modèle Whisper chargé avec succès!")
        return model
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du modèle: {e}")
        return None

def main():
    # Titre principal
    st.markdown("""
    <div class="main-header">
        <h1>🎙 Transcripteur Audio Intelligent</h1>
    </div>
    """, unsafe_allow_html=True)

    # Charger le modèle
    model = load_whisper_model()
    
    if model is None:
        st.error("❌ Impossible de charger le modèle Whisper. Vérifiez votre installation.")
        st.info("💡 Installez Whisper avec: pip install openai-whisper")
        return
    
    # Vérifier les périphériques audio
    audio_devices = check_audio_devices()
    
    # Sidebar avec configuration
    with st.sidebar:
        st.markdown("### ⚙ Configuration")
        
        # Sélection de la langue
        language_options = {
            'Français': 'fr',
            'English': 'en',
            'العربية': 'ar',
            'Español': 'es',
            'Deutsch': 'de',
            'Italiano': 'it',
            'Português': 'pt',
            'Русский': 'ru',
            '中文': 'zh',
            '日本語': 'ja'
        }
        
        selected_language = st.selectbox(
            "🌍 Langue de transcription:",
            options=list(language_options.keys()),
            index=0
        )
        
        language_code = language_options[selected_language]
        
        # Sélection du périphérique audio
        if audio_devices:
            device_names = [f"{device['name']} ({device['channels']} canaux)" for device in audio_devices]
            device_names.insert(0, "Périphérique par défaut")
            
            selected_device = st.selectbox(
                "🎤 Périphérique audio:",
                options=device_names,
                index=0
            )
            
            device_index = None if selected_device == "Périphérique par défaut" else audio_devices[device_names.index(selected_device) - 1]['index']
        else:
            st.error("❌ Aucun périphérique d'entrée audio détecté")
            device_index = None
        
        # Options avancées
        with st.expander("🔧 Options avancées"):
            auto_convert = st.checkbox("Conversion automatique", value=True, 
                                     help="Convertit automatiquement les fichiers pour optimiser la transcription")
            
            show_timestamps = st.checkbox("Afficher les timestamps", value=False,
                                        help="Inclut les timestamps dans la transcription")
    
    # Interface principale
    st.markdown("### 🎙 Enregistrement Vocal")
        
    # Statut de l'enregistrement
    if st.session_state.recording:
        st.markdown("""
        <div class="recording-box">
            <h3>🔴 ENREGISTREMENT EN COURS...</h3>
            <p>Parlez maintenant. Cliquez sur "Arrêter" quand vous avez terminé.</p>
        </div>
        """, unsafe_allow_html=True)
        
    # Boutons de contrôle
    col1, col2, col3 = st.columns([1, 1, 2])
        
    with col1:
        if not st.session_state.recording:
            if st.button("🎤 Commencer l'enregistrement", type="primary"):
                if audio_devices or device_index is None:
                    st.session_state.recording = True
                    st.session_state.audio_recorder = AudioRecorder()
                    
                    # Démarrer l'enregistrement dans un thread
                    recording_thread = threading.Thread(
                        target=st.session_state.audio_recorder.start_recording,
                        args=(device_index,)
                    )
                    recording_thread.daemon = True
                    recording_thread.start()
                else:
                    st.error("❌ Aucun périphérique audio disponible")
        
    with col2:
        if st.session_state.recording:
            if st.button("⏹ Arrêter l'enregistrement"):
                st.session_state.recording = False
                if hasattr(st.session_state, 'audio_recorder'):
                    st.session_state.audio_recorder.stop_recording()
                st.success("✅ Enregistrement arrêté!")
                st.rerun()
        
    with col3:
        # Vérifier si on a des données audio à transcrire
        has_audio_data = (hasattr(st.session_state, 'audio_recorder') and 
                        st.session_state.audio_recorder.audio_data and 
                        not st.session_state.recording)
        
        if has_audio_data:
            if st.button("🚀 Transcrire l'enregistrement", type="primary"):
                # Sauvegarder et transcrire l'audio
                audio_path = save_recorded_audio(st.session_state.audio_recorder.audio_data)
                
                if audio_path:
                    try:
                        # Transcription
                        start_time = time.time()
                        result = transcribe_audio(model, audio_path, language_code)
                        end_time = time.time()
                        
                        if result:
                            # Afficher les résultats
                            st.markdown("### 📝 Résultats de la transcription")
                            
                            # Texte transcrit
                            st.markdown("#### 📄 Transcription complète")
                            transcript_text = result['text'].strip()
                            
                            if transcript_text:
                                st.text_area(
                                    "Texte transcrit:",
                                    value=transcript_text,
                                    height=200,
                                    help="Vous pouvez copier ce texte"
                                )
                                
                                # Timestamps si demandés
                                if show_timestamps and 'segments' in result:
                                    st.markdown("#### ⏰ Transcription avec timestamps")
                                    for segment in result['segments']:
                                        start = segment['start']
                                        end = segment['end']
                                        text = segment['text'].strip()
                                        st.text(f"[{start:.1f}s - {end:.1f}s] {text}")
                        
                        # Nettoyage
                        os.unlink(audio_path)
                        
                        # Réinitialiser l'enregistreur
                        st.session_state.audio_recorder = AudioRecorder()
                        
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la transcription: {e}")
                        if audio_path and os.path.exists(audio_path):
                            os.unlink(audio_path)

if __name__ == "__main__":
    main()