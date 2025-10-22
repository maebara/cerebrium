import os
import torch
from fastapi import FastAPI, UploadFile
import tempfile
from openvoice.api import ToneColorConverter, se_extractor
import torchaudio

app = FastAPI()

@app.post("/voiceclone")
async def voice_clone(file: UploadFile):
    # Configurar cache persistente (ejemplo)
    CUSTOM_CACHE_DIR = "/persistent-storage/openvoice_cache/"
    os.environ["OPENVOICE_HOME"] = CUSTOM_CACHE_DIR

    # Guardar audio temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # 1. Cargar modelo (puedes cachearlo como Whisper)
    ckpt_converter = "checkpoints/converter"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tone_color_converter = ToneColorConverter(ckpt_converter, device=device)

    # 2. Extraer embedding del audio de referencia
    src_path = tmp_path
    src_se, audio_name = se_extractor.get_se(src_path, tone_color_converter, vad=True)

    # 3. Generar salida (ejemplo simple, necesitas texto de entrada para TTS)
    out_path = tmp_path.replace(".wav", "_cloned.wav")
    tone_color_converter.convert(
        audio_src_path=src_path,
        src_se=src_se,
        tgt_se=src_se,  # aquí podrías poner otro timbre
        output_path=out_path,
    )

    return {
        "output_audio": out_path,
        "cache_dir": CUSTOM_CACHE_DIR
    }