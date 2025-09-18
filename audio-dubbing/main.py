from fastapi import FastAPI

app = FastAPI()

@app.post("/transcribe")
def transcribe(filename: str):
    import os
    import whisper
    import json
    print("whisper y os importados!")

    # 👇 Seteamos la variable de entorno ANTES de cargar el modelo
    CUSTOM_CACHE_DIR = "/persistent-storage/whisper_cache/"  # o cualquier path persistente que montes en tu contenedor
    os.environ["XDG_CACHE_HOME"] = CUSTOM_CACHE_DIR
    # Ahora cargamos el modelo
    model = whisper.load_model("large", device="cuda")  # usa el cache overrideado
    print("Modelo large cargado!")

    audio_path = os.path.join("/persistent-storage/audio-files/", filename)
    if not os.path.exists(audio_path):
        return {"error": "Archivo no encontrado"}
    
    print(f"Transcribiendo {audio_path}...")
    result = model.transcribe(audio_path, language="es")
    text = result["text"]

    print("Transcripción completada, guardando resultado...")
    # Guardar resultado en TXT
    txt_filename = os.path.splitext(filename)[0] + ".txt"
    txt_path = os.path.join("/persistent-storage/output-files/whisper/", txt_filename)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Guardar resultado completo como JSON
    json_filename = os.path.splitext(filename)[0] + ".json"
    json_path = os.path.join("/persistent-storage/output-files/whisper/", json_filename)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Archivos guardados en {txt_path} y {json_path}")
    file_size_txt = os.path.getsize(txt_path)
    file_size_json = os.path.getsize(json_path)
    return {
        "text_file": txt_path,
        "json_file": json_path,
        "text_file_size": file_size_txt,
        "json_file_size": file_size_json
    }


@app.get("/health")
def health():
    return "OK"

@app.get("/ready")
def ready():
    return "OK"