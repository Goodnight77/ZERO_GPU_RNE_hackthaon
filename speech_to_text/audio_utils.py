import streamlit as st
import pyaudio
import wave
import tempfile
import subprocess
import os

# Configuration audio pour l'enregistrement
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

@st.cache_data
def check_audio_devices():
    """Vérifie la disponibilité des périphériques audio"""
    try:
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        devices = []
        
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels']
                })
        
        p.terminate()
        return devices
    except Exception as e:
        st.error(f"Erreur lors de la vérification des périphériques audio: {e}")
        return []

class AudioRecorder:
    """Classe pour gérer l'enregistrement audio"""
    
    def __init__(self):
        self.audio_data = []
        self.recording = False
        self.stream = None
        self.p = None
    
    def start_recording(self, device_index=None):
        """Démarre l'enregistrement audio"""
        try:
            self.p = pyaudio.PyAudio()
            
            self.stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK
            )
            
            self.audio_data = []
            self.recording = True
            
            # Enregistrement dans une boucle simple
            while self.recording:
                try:
                    data = self.stream.read(CHUNK, exception_on_overflow=False)
                    self.audio_data.append(data)
                except Exception as e:
                    print(f"Erreur lecture audio: {e}")
                    break
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'enregistrement: {e}")
            return False
        finally:
            self.cleanup()
    
    def stop_recording(self):
        """Arrête l'enregistrement"""
        self.recording = False
    
    def cleanup(self):
        """Nettoie les ressources audio"""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.p:
                self.p.terminate()
        except:
            pass

def save_recorded_audio(audio_data):
    """Sauvegarde l'audio enregistré dans un fichier temporaire"""
    try:
        if not audio_data:
            return None
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # Écrire les données audio
        wf = wave.open(temp_path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(audio_data))
        wf.close()
        
        return temp_path
        
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde: {e}")
        return None

def convert_audio_for_whisper(audio_file, target_format="wav"):
    """Convertit un fichier audio pour optimiser la transcription Whisper"""
    try:
        # Créer un fichier temporaire pour la sortie
        with tempfile.NamedTemporaryFile(suffix=f".{target_format}", delete=False) as temp_file:
            output_path = temp_file.name
        
        # Commande ffmpeg pour conversion optimisée
        cmd = [
            'ffmpeg', '-i', audio_file,
            '-ar', '16000',  # Fréquence 16kHz (optimal pour Whisper)
            '-ac', '1',      # Mono
            '-acodec', 'pcm_s16le',  # Format WAV 16-bit
            '-y',            # Remplacer si existe
            output_path
        ]
        
        # Exécuter la conversion
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return output_path
        else:
            st.error(f"Erreur ffmpeg: {result.stderr}")
            return None
            
    except Exception as e:
        st.error(f"Erreur lors de la conversion: {e}")
        return None

def transcribe_audio(model, audio_file, language='fr'):
    """Transcrit un fichier audio avec Whisper"""
    try:
        with st.spinner('🔄 Transcription en cours...'):
            result = model.transcribe(
                audio_file,
                language=language,
                fp16=False,
                verbose=False
            )
        
        return result
    except Exception as e:
        st.error(f"Erreur lors de la transcription: {e}")
        return None