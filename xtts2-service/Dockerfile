FROM nvcr.io/nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Configurar debconf para modo no interactivo
ENV DEBIAN_FRONTEND=noninteractive

# Dependencias del sistema esenciales
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.11 python3-pip python3-venv \
    git ffmpeg libsndfile1 sox \
    && rm -rf /var/lib/apt/lists/*

# Crear enlace simbólico para python3
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3

# Upgrade pip
RUN pip install --upgrade pip

# 🔹 Instalar PyTorch (versión compatible con CUDA 11.8)
RUN pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118

# 🔹 Instalar Coqui-TTS actualizado (soporta XTTS-v2)
RUN pip uninstall -y TTS || true && \
    rm -rf /usr/local/lib/python3.11/dist-packages/TTS* && \
    rm -rf /usr/lib/python3/dist-packages/TTS* && \
    pip install --no-cache-dir coqui-tts==0.27.2 librosa>=0.10.0 soundfile>=0.12.0

# 🔹 Dependencias de audio y ciencia
RUN pip install librosa>=0.10.0 soundfile>=0.12.0 numpy>=1.21.0 scipy>=1.7.0

# 🔹 FastAPI y Uvicorn
RUN pip install fastapi==0.104.1 uvicorn==0.24.0

# Crear directorio para cache de modelos (opcional)
RUN mkdir -p /root/.local/share/tts

# Puerto expuesto
EXPOSE 8192

# Directorio de trabajo
WORKDIR /cortex

# Copiar el código fuente
COPY . .

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8192"]