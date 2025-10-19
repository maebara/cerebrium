from fastapi import FastAPI, HTTPException
from TTS.api import TTS
import os
import traceback

app = FastAPI(title="XTTSv2 Voice Clone API")
os.environ["TTS_HOME"] = "/persistent-storage/tts_models"
os.environ["COQUI_TOS_AGREED"] = "1"  # Aceptar términos automáticamente

@app.post("/clone-voice")
async def clone_voice():
    try:
        # Asumimos que el audio de referencia está en un path conocido
        reference_audio = "/persistent-storage/audio-files/ciencia.mp3"
        text_to_speech = """I read books to my friend with a disability.
I'm going to have surgery soon and won't be able to speak much for a few months.
I'd like to clone my voice first so I can record audiobooks for him.
Can you recommend a good and free tool that doesn't have a word count limit? It doesn't have to be online, I have a good computer. But I'm very weak in AI and tools like that..."""
        
        if not os.path.exists(reference_audio):
            raise HTTPException(status_code=404, detail="Reference audio not found")
        
        # Asegurar que el directorio de resultados existe
        output_dir = "/persistent-storage/audio-files/results"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar output path
        output_filename = f"{output_dir}/ciencia.wav"
        
        print("🔧 Loading XTTSv2 model...")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        print("✅ Model loaded successfully!")

        # Generar audio clonado
        tts.tts_to_file(
            text=text_to_speech,
            speaker_wav=reference_audio,
            language="en",
            file_path=output_filename
        )
        
        return {
            "status": "success",
            "output_file": output_filename,
            "message": "Voice cloning completed"
        }
        
    except Exception as e:
        # Imprimir el traceback completo para debug
        print("ERROR DETAILS:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Cloning failed: {str(e)}")

@app.get("/health")
def health():
    return "OK"

@app.get("/ready")
def ready():
    return "OK"