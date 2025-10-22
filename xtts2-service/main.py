from fastapi import FastAPI, HTTPException
import torch
import traceback
import time
import os, glob
from fastapi import Query
from pydantic import BaseModel, Field
from TTS.utils.synthesizer import Synthesizer

app = FastAPI(title="XTTSv2 Voice Clone API")
os.environ["TTS_HOME"] = "/persistent-storage/tts_models"
os.environ["COQUI_TOS_AGREED"] = "1"  # Aceptar términos automáticamente
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
MODEL_DIR = "/persistent-storage/tts_models/tts/tts_models--multilingual--multi-dataset--xtts_v2"
VOICES_DIR = "/persistent-storage/xtts_voices"
STARTUP_FIXED_DELAY = 60

class CloneVoiceRequest(BaseModel):
    filename: str = Field(..., description="Nombre de archivo bajo /persistent-storage/audio-files")
    text: str = Field(..., description="Texto a sintetizar")
    language: str = Field("en", description="Código de idioma (XTTS v2)")
    speaker_name: str = Field("voice1", description="Nombre/ID para cachear la voz clonada")
  
@app.post("/clone-voice")
def clone_voice(req: CloneVoiceRequest):
    try:
        print(" Esperando delay de arranque fijo...")
        time.sleep(STARTUP_FIXED_DELAY)
        print(" Cargando modelo XTTSv2...")
        print(f" Buscando modelo en: {MODEL_DIR}")
        
        # Verificar que los archivos clave existen
        required_files = ["config.json", "model.pth", "vocab.json"]
        for file in required_files:
            file_path = f"{MODEL_DIR}/{file}"
            if not os.path.exists(file_path):
                raise Exception(f"Archivo faltante: {file_path}")
            else:
                print(f" {file} encontrado")
        
        synth = Synthesizer(
            tts_checkpoint=MODEL_DIR,  # ✅ directorio
            tts_config_path=os.path.join(MODEL_DIR, "config.json"),
            tts_speakers_file=os.path.join(MODEL_DIR, "speakers_xtts.pth"),
            use_cuda=torch.cuda.is_available(),
        )
        dev = next(synth.tts_model.parameters()).device
        print("[gpu] synth model device:", dev)        # debería decir cuda:0
        print("XTTSv2 cargado correctamente")
        # Asumimos que el audio de referencia está en un path conocido
        reference_audio = f"/persistent-storage/audio-files/{req.filename}"
        text_to_speech = req.text
        if not os.path.exists(reference_audio):
            raise HTTPException(status_code=404, detail="Reference audio not found")
        
        # Asegurar que el directorio de resultados existe
        output_dir = "/persistent-storage/audio-files/results"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar output path
        output_filename = f"{output_dir}/{req.speaker_name}.wav"
        
        # Generar audio clonado
        wav = synth.tts(
            text=text_to_speech,
            speaker_wav=reference_audio,   # tu mp3/wav de referencia
            language_name=req.language,
            speaker_name=req.speaker_name,        # 👈 nombre de la voz (no 'speaker')
            voice_dir=VOICES_DIR,          # 👈 dónde cachear ciencia.pth
            split_sentences=True
        )
        synth.save_wav(wav, output_filename)
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

@app.get("/debug/exists")
def debug_exists(
    path: str = Query("/persistent-storage/tts_models/tts/tts_models--multilingual--multi-dataset--xtts_v2/config.json")
):
    return {
        "path": path,
        "exists": os.path.exists(path),
        "is_dir": os.path.isdir(path),
    }

@app.get("/debug/peek")
def debug_peek():
    # Miramos 3 niveles: /persistent-storage, /persistent-storage/tts_models, /persistent-storage/tts_models/tts
    levels = [
        "/persistent-storage",
        "/persistent-storage/tts_models",
        "/persistent-storage/tts_models/tts",
    ]
    out = {}
    for d in levels:
        try:
            out[d] = sorted(os.listdir(d))[:200] if os.path.isdir(d) else f"<NO_DIR>"
        except Exception as e:
            out[d] = f"<ERROR listando: {e}>"
    return out

@app.get("/debug/find-xtts")
def debug_find_xtts():
    # Busca el config de xtts_v2 en TODO /persistent-storage (rápido, sólo rutas)
    patt = "/persistent-storage/**/tts_models--multilingual--multi-dataset--xtts_v2/config.json"
    hits = glob.glob(patt, recursive=True)
    return {
        "pattern": patt,
        "count": len(hits),
        "hits": hits[:50],  # limitar salida
    }

@app.get("/health")
def health():
    return "OK"

@app.get("/ready")
def ready():
    return "OK"