import subprocess
import os
import re

def download_all_files(remote_folder="", local_folder="./downloaded_files"):
    """
    Descarga todos los archivos de una carpeta de Cerebrium
    """
    # Crear directorio local si no existe
    os.makedirs(local_folder, exist_ok=True)
    
    # Listar archivos remotos
    try:
        result = subprocess.run(
            ["cerebrium", "ls", remote_folder], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
               # Regex para extraer nombres de archivos de la tabla
        pattern = r'\|\s*([^|]+\.(jpeg|jpg|png|pdf|txt|md|json|[a-zA-Z0-9]+))\s*\|'
        files = re.findall(pattern, result.stdout, re.IGNORECASE)
        filenames = [match[0].strip() for match in files]
        
        print(f"Encontrados {len(filenames)} archivos")
        
        
        # Descargar cada archivo
        for filename in filenames:
            print(f"Descargando: {filename}")
            remote_path = f"{remote_folder}/{filename}"
            local_path = os.path.join(local_folder, filename)

            subprocess.run(
                ["cerebrium", "download", remote_path, local_path], 
                check=True
            )
        
        print(f"Descarga completada en {local_folder}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# Usar el script
download_all_files("output-files/aws-complete", "./carpeta")