from fastapi import FastAPI

app = FastAPI()

@app.post("/marker")
def hello(filename: str):
    import os
    import subprocess

    # Configurar variables para GPU y directorio de caché personalizado
    env_vars = os.environ.copy()
    env_vars.update({
        "TORCH_DEVICE": "cuda",
        "CUDA_VISIBLE_DEVICES": "0",
        "HF_HOME": "/persistent-storage/models_cache",  # Directorio personalizado para caché de modelos
        "XDG_CACHE_HOME": "/persistent-storage/models_cache",  # Variable alternativa de caché
        "MODEL_CACHE_DIR": "/persistent-storage/models_cache"  # Variable personalizada para caché de modelos
    })
    
    # Configuración
    pdf_file = f"/persistent-storage/pdf-files/{filename}"
    output_base_dir = "/persistent-storage/output-files"

    if not os.path.exists(pdf_file):
        return {"status": "error", "message": f"File not found: {pdf_file}"}

    try:
        print(f"🚀 Iniciando procesamiento de {pdf_file}...")
        # Ejecutar marker
        result = subprocess.run([
                "marker_single", 
                pdf_file,
                # dpi scan and output options
                "--lowres_image_dpi", "120",
                "--highres_image_dpi", "300", 
                "--output_format", "markdown",
                "--output_dir", output_base_dir,
                
                # Batch sizes (más altos para aprovechar VRAM de 24 GB)
                "--detection_batch_size", "8",           
                "--recognition_batch_size", "8",         
                "--LayoutBuilder_layout_batch_size", "4", 
                "--table_rec_batch_size", "8",

                # Mejor uso de CPU
                "--pdftext_workers", "2",   
                
                # Form como Pictures
                "--block_relabel_str", "Form:Picture:1",
            ], capture_output=True, text=True, timeout=3600, env=env_vars)
            
        print("📋 Resultado de la ejecución:")
        print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")

        if result.returncode != 0:
            raise Exception(f"Marker falló con código de salida: {result.returncode}")
        
        return {"status": "success", "message": "PDF procesado correctamente."}
        
    except subprocess.TimeoutExpired:
        print(f"Timeout procesando {pdf_file}")
        return {"status": "error", "message": f"Timeout procesando {pdf_file}"}
        
    except Exception as e:
        print(f"Error ejecutando Marker para {pdf_file}: {e}")
        return {"status": "error", "message": f"Error ejecutando Marker: {str(e)}"}

@app.get("/health")
def health():
    return "OK"

@app.get("/ready")
def ready():
    return "OK"