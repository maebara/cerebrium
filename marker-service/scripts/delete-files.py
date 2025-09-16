import subprocess
import os
import re
import sys

def delete_all_files(remote_folder="output-files/aws-7"):
    try:
        # Listar archivos remotos
        result = subprocess.run(
            ["cerebrium", "ls", remote_folder], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        # Regex para extraer nombres de archivos de la tabla
        pattern = r'\|\s*([^|]+\.(jpeg|jpg|png|pdf|txt|md|json|py|[a-zA-Z0-9]+))\s*\|'
        files = re.findall(pattern, result.stdout, re.IGNORECASE)
        filenames = [match[0].strip() for match in files]
        
        if not filenames:
            print("No se encontraron archivos para borrar.")
            return
        
        print(f"Encontrados {len(filenames)} archivos para borrar")
        
        # Borrar cada archivo
        deleted_count = 0
        error_count = 0
        
        for filename in filenames:
            print(f"Borrando: {filename}")
            remote_path = f"{remote_folder}/{filename}"
            
            try:
                subprocess.run(
                    ["cerebrium", "rm", remote_path], 
                    check=True,
                    capture_output=True
                )
                print(f"✅ Borrado: {filename}")
                deleted_count += 1
            except subprocess.CalledProcessError as e:
                print(f" Error borrando {filename}: {e}")
                error_count += 1
        
        print(f"\n Proceso completado:")
        print(f"   - Archivos borrados: {deleted_count}")
        print(f"   - Errores: {error_count}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error listando archivos: {e}")
    except KeyboardInterrupt:
        print("\nOperación interrumpida por el usuario.")
    except Exception as e:
        print(f"Error inesperado: {e}")

# Usar el script
if __name__ == "__main__":
    delete_all_files()