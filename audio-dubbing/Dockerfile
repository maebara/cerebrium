FROM nvcr.io/nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Configurar debconf para modo no interactivo
ENV DEBIAN_FRONTEND=noninteractive

# Dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates curl software-properties-common \
    git ffmpeg locales && \
    rm -rf /var/lib/apt/lists/*

# Locale
RUN locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8

# Python
RUN apt-get update && apt-get install -y python3.11 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Instalar PyTorch + Whisper
RUN pip install torch==2.7.1+cu118 torchvision==0.22.1+cu118 torchaudio==2.7.1+cu118 --index-url https://download.pytorch.org/whl/cu118
RUN pip install openai-whisper==20240930  # versión estable de whisper

# FastAPI y uvicorn si vas a exponer un endpoint
RUN pip install fastapi uvicorn

EXPOSE 8192
WORKDIR /cortex
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8192"]