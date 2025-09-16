FROM nvcr.io/nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Configurar debconf para modo no interactivo
ENV DEBIAN_FRONTEND=noninteractive

# Dependencias del sistema
RUN apt-get update && \
    apt-get install -y ca-certificates curl software-properties-common && \
    apt-get install -y poppler-utils poppler-data && \
     # IMPORTANTE: Configurar la EULA ANTES de instalar las fuentes
    echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections && \
    apt-get install -y ttf-mscorefonts-installer msttcorefonts && \
    apt-get install -y fonts-crosextra-caladea fonts-crosextra-carlito && \
    apt-get install -y gsfonts lcdf-typetools locales

# Locale
RUN locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8
ENV CACHE_BUST=20250911
# Python
RUN apt-get install -y python3.11 python3-pip

# FIX: instalar pydantic primero
RUN pip install --upgrade pip && \
    pip install pydantic>=2.4.2

# FastAPI y uvicorn
RUN pip install fastapi uvicorn

# Stack PyTorch + Marker
RUN pip install torch==2.7.1+cu118 torchvision==0.22.1+cu118 torchaudio==2.7.1+cu118 --index-url https://download.pytorch.org/whl/cu118 && \
    pip install marker-pdf[full]==1.9.1

# Dependencias adicionales
RUN pip install pdfplumber==0.11.7 PyMuPDF==1.26.4 PyPDF2==3.0.1 python-docx==1.2.0 reportlab==4.4.3 tiktoken==0.11.0


EXPOSE 8192
WORKDIR /cortex
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8192"]