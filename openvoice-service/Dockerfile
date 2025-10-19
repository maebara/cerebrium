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

# Instalar PyTorch (versión compatible con CUDA 11.8)
RUN pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118

# Instalar TTS y dependencias específicas para XTTSv2
RUN pip install TTS==0.20.0
RUN pip install librosa>=0.10.0 soundfile>=0.12.0

# Dependencias adicionales que pueden ser necesarias
RUN pip install numpy>=1.21.0 scipy>=1.7.0

# FastAPI y uvicorn para el endpoint
RUN pip install fastapi==0.104.1 uvicorn==0.24.0

# Crear directorio para cache de modelos
RUN mkdir -p /root/.local/share/tts

# Puerto expuesto
EXPOSE 8192

# Directorio de trabajo
WORKDIR /cortex

# Copiar código (asegúrate de tener main.py con la lógica de XTTSv2)
COPY . .

# Comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8192"]