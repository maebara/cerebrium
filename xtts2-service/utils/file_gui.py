import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import subprocess
import threading
from datetime import datetime
import os

class CerebriumFileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Cerebrium File Manager")
        self.root.geometry("800x600")
        
        self.current_path = ""  # Ruta actual
        self.path_history = []  # Historial para navegación
        self.last_items = []    # Último listado parseado (para resolver nombres truncados)
        
        self.setup_ui()
        self.log_message("Aplicación iniciada")
        self.log_message("Cargando directorio raíz...")
        self.load_directory("")  # Cargar directorio raíz

    # ---------------------------
    # Subprocess helper centralizado
    # ---------------------------
    def run_cerebrium(self, cmd, timeout=30):
        """
        Ejecuta comandos cerebrium con un entorno que evita truncado por ancho de terminal.
        """
        env = os.environ.copy()
        env["COLUMNS"] = "1000"  # Fuerza ancho grande para evitar "..."
        env["TERM"] = "dumb"     # Terminal "simple": muchas CLIs desactivan formateos
        env["CLICOLOR"] = "0"    # Desactiva colores si la CLI los usa
        self.log_message(f"Ejecutando: {' '.join(cmd)} (timeout={timeout}s)")
        return subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout, env=env)

    # ---------------------------
    # UI
    # ---------------------------
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Cambio para hacer espacio al log
        
        # Barra de navegación
        nav_frame = ttk.Frame(main_frame)
        nav_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        nav_frame.columnconfigure(2, weight=1)
        
        # Botones de navegación
        self.back_btn = ttk.Button(nav_frame, text="← Atrás", command=self.go_back)
        self.back_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.home_btn = ttk.Button(nav_frame, text="🏠 Raíz", command=self.go_home)
        self.home_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Label de ruta actual
        self.path_label = ttk.Label(nav_frame, text="Ruta: /", font=("Arial", 10, "bold"))
        self.path_label.grid(row=0, column=2, sticky=tk.W)
        
        # Botón refresh
        self.refresh_btn = ttk.Button(nav_frame, text="🔄 Actualizar", command=self.refresh)
        self.refresh_btn.grid(row=0, column=3, padx=(10, 0))
        
        # Botón upload
        self.upload_btn = ttk.Button(nav_frame, text="↑ Subir", command=self.upload_file)
        self.upload_btn.grid(row=0, column=4, padx=(10, 0))
        
        # Barra de estado
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Listo")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Progress bar (oculta inicialmente)
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
        # Treeview para mostrar archivos
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Crear Treeview con scrollbars
        self.tree = ttk.Treeview(tree_frame, columns=('Type', 'Size', 'Modified'), show='tree headings')
        
        # Configurar columnas
        self.tree.heading('#0', text='Name')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Modified', text='Last Modified')
        
        self.tree.column('#0', width=300, minwidth=200)
        self.tree.column('Type', width=80, minwidth=60)
        self.tree.column('Size', width=100, minwidth=80)
        self.tree.column('Modified', width=150, minwidth=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid del treeview y scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind eventos
        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<Motion>', self._status_tooltip_on_hover)  # tooltip simple en barra de estado
        
        # Log de debug
        log_frame = ttk.LabelFrame(main_frame, text="Debug Log", padding="5")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Botón para limpiar log
        clear_log_btn = ttk.Button(log_frame, text="Limpiar Log", command=self.clear_log)
        clear_log_btn.grid(row=1, column=0, pady=(5, 0), sticky=tk.W)
        
        # Menú contextual
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Descargar", command=self.download_selected)
        self.context_menu.add_command(label="Eliminar", command=self.delete_selected)

    # Tooltip simple en barra de estado
    def _status_tooltip_on_hover(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        full_text = self.tree.item(iid, 'text')
        self.update_status(full_text)

    # ---------------------------
    # Utilidades
    # ---------------------------
    def log_message(self, message):
        """Agregar mensaje al log de debug"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        print(f"DEBUG: {message}")  # También imprimir en consola
    
    def clear_log(self):
        """Limpiar el log de debug"""
        self.log_text.delete(1.0, tk.END)
    
    def show_context_menu(self, event):
        """Mostrar menú contextual en clic derecho"""
        item = self.tree.selection()
        if item:
            # Verificar si es archivo o carpeta para mostrar opciones relevantes
            item_type = self.tree.item(item[0], 'values')[0] if self.tree.item(item[0], 'values') else ""
            self.context_menu.entryconfig("Descargar", state=tk.NORMAL if item_type == "File" else tk.DISABLED)
            self.context_menu.post(event.x_root, event.y_root)

    def resolve_full_name(self, short_name, items_in_dir):
        """
        Si short_name contiene '...' intenta resolver el nombre completo
        buscando por prefijo dentro de items_in_dir (lista de dicts con 'name').
        Si encuentra 1 match, devuelve ese; si varios, pide confirmación.
        """
        if "..." not in short_name:
            return short_name

        prefix = short_name.split("...")[0]
        candidates = [it["name"] for it in items_in_dir if it.get("name", "").startswith(prefix)]
        self.log_message(f"Resolviendo nombre truncado '{short_name}' -> candidatos: {candidates}")
        if not candidates:
            return short_name  # no pudimos resolver, seguimos con lo que hay

        if len(candidates) == 1:
            return candidates[0]

        try:
            choice = simpledialog.askstring(
                "Seleccionar elemento",
                "Hay varios elementos que coinciden:\n" + "\n".join(candidates) + "\n\nEscribe el nombre exacto:"
            )
            if choice and choice in candidates:
                return choice
        except Exception as e:
            self.log_message(f"No se pudo mostrar diálogo de selección: {e}")

        return candidates[0]  # fallback

    # ---------------------------
    # Acciones de archivos
    # ---------------------------
    def download_selected(self):
        """Descargar archivo seleccionado al sistema local"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Selecciona un archivo para descargar.")
            return
        
        item = self.tree.item(selection[0])
        item_type = item['values'][0] if item['values'] else ""
        
        if item_type != "File":
            messagebox.showerror("Error", "Solo se pueden descargar archivos, no carpetas.")
            return
        
        # Extraer nombre del archivo (sin icono)
        filename = item['text'].replace("📄 ", "")
        if "..." in filename:
            filename = self.resolve_full_name(filename, self.last_items)

        # Construir ruta remota
        remote_path = os.path.join(self.current_path, filename).replace("\\", "/")
        if not self.current_path:
            remote_path = filename
        
        # Pedir ubicación local para guardar
        save_path = filedialog.asksaveasfilename(
            initialfile=filename,
            defaultextension="",
            filetypes=[("All files", "*.*")],
            title="Guardar archivo como"
        )
        if not save_path:
            return  # Usuario canceló
        
        self.show_loading(True)
        self.log_message(f"Descargando {remote_path} a {save_path}")
        
        def download_thread():
            try:
                cmd = ["cerebrium", "download", remote_path, save_path]
                result = self.run_cerebrium(cmd, timeout=60)
                
                self.log_message(f"Descarga exitosa: {result.stdout}")
                self.root.after(0, lambda: self.show_loading(False))
                self.root.after(0, lambda: messagebox.showinfo("Éxito", f"Archivo descargado a:\n{save_path}"))
                
            except subprocess.TimeoutExpired:
                error_msg = "Tiempo de espera agotado para la descarga"
                self.log_message(f"ERROR: {error_msg}")
                self.root.after(0, lambda: self.show_error(error_msg))
            except subprocess.CalledProcessError as e:
                error_msg = f"Error al descargar: {e.stderr.strip() or e.stdout.strip()}"
                self.log_message(f"ERROR: {error_msg}")
                self.root.after(0, lambda: self.show_error(error_msg))
            except Exception as e:
                error_msg = f"Error inesperado: {str(e)}"
                self.log_message(f"ERROR: {error_msg}")
                self.root.after(0, lambda: self.show_error(error_msg))
        
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
    
    def upload_file(self):
        """Subir un archivo desde el sistema local al almacenamiento remoto"""
        local_path = filedialog.askopenfilename(
            title="Seleccionar archivo para subir",
            filetypes=[("All files", "*.*")]
        )
        if not local_path:
            return  # Usuario canceló
        
        filename = os.path.basename(local_path)
        
        # Construir ruta remota
        remote_path = os.path.join(self.current_path, filename).replace("\\", "/")
        if not self.current_path:
            remote_path = filename
        
        self.show_loading(True)
        self.log_message(f"Subiendo {local_path} a {remote_path}")
        
        def upload_thread():
            try:
                cmd = ["cerebrium", "cp", local_path, remote_path]
                result = self.run_cerebrium(cmd, timeout=60)
                
                self.log_message(f"Subida exitosa: {result.stdout}")
                self.root.after(0, lambda: self.show_loading(False))
                self.root.after(0, lambda: messagebox.showinfo("Éxito", f"Archivo subido a:\n{remote_path}"))
                self.root.after(0, self.refresh)
                
            except subprocess.TimeoutExpired:
                error_msg = "Tiempo de espera agotado para la subida"
                self.log_message(f"ERROR: {error_msg}")
                self.root.after(0, lambda: self.show_error(error_msg))
            except subprocess.CalledProcessError as e:
                error_msg = f"Error al subir: {e.stderr.strip() or e.stdout.strip()}"
                self.log_message(f"ERROR: {error_msg}")
                self.root.after(0, lambda: self.show_error(error_msg))
            except Exception as e:
                error_msg = f"Error inesperado: {str(e)}"
                self.log_message(f"ERROR: {error_msg}")
                self.root.after(0, lambda: self.show_error(error_msg))
        
        thread = threading.Thread(target=upload_thread)
        thread.daemon = True
        thread.start()
    
    def delete_selected(self):
        """Eliminar archivo o carpeta seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Selecciona un archivo o carpeta para eliminar.")
            return
        
        item = self.tree.item(selection[0])
        item_name = item['text'].replace("📁 ", "").replace("📄 ", "")
        if "..." in item_name:
            item_name = self.resolve_full_name(item_name, self.last_items)
        
        # Construir ruta remota
        remote_path = os.path.join(self.current_path, item_name).replace("\\", "/")
        if not self.current_path:
            remote_path = item_name
        
        # Confirmar eliminación
        item_type = item['values'][0] if item['values'] else "elemento"
        msg = f"¿Eliminar {item_type.lower()} '{item_name}'?" 
        if item_type == "Folder":
            msg += "\nEsta acción es irreversible y eliminará todos sus contenidos."
        
        confirm = messagebox.askyesno("Confirmar eliminación", msg)
        if not confirm:
            return
        
        self.show_loading(True)
        self.log_message(f"Eliminando {remote_path}")
        
        def delete_thread():
            try:
                cmd = ["cerebrium", "rm", remote_path]
                result = self.run_cerebrium(cmd, timeout=30)
                
                self.log_message(f"Eliminación exitosa: {result.stdout}")
                self.root.after(0, lambda: self.show_loading(False))
                self.root.after(0, lambda: messagebox.showinfo("Éxito", f"Se eliminó {remote_path}"))
                self.root.after(0, self.refresh)
                
            except subprocess.TimeoutExpired:
                error_msg = "Tiempo de espera agotado para la eliminación"
                self.log_message(f"ERROR: {error_msg}")
                self.root.after(0, lambda: self.show_error(error_msg))
            except subprocess.CalledProcessError as e:
                error_msg = f"Error al eliminar: {e.stderr.strip() or e.stdout.strip()}"
                self.log_message(f"ERROR: {error_msg}")
                self.root.after(0, lambda: self.show_error(error_msg))
            except Exception as e:
                error_msg = f"Error inesperado: {e}"
                self.log_message(f"ERROR: {error_msg}")
                self.root.after(0, lambda: self.show_error(error_msg))
        
        thread = threading.Thread(target=delete_thread)
        thread.daemon = True
        thread.start()
    
    # ---------------------------
    # Estado y carga
    # ---------------------------
    def update_status(self, message):
        """Actualizar mensaje de estado"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def show_loading(self, show=True):
        """Mostrar/ocultar indicador de carga"""
        if show:
            self.progress.start()
            self.update_status("Procesando...")
        else:
            self.progress.stop()
            self.update_status("Listo")
    
    # ---------------------------
    # Parser de salida CLI
    # ---------------------------
    def parse_cerebrium_output(self, output):
        """Parsear la salida de cerebrium ls"""
        items = []
        self.log_message("Iniciando parseo de output...")
        
        # Dividir por líneas y buscar las filas de datos
        lines = output.split('\n')
        self.log_message(f"Total de líneas: {len(lines)}")
        
        for i, line in enumerate(lines):
            self.log_message(f"Línea {i}: '{line}'")
            
            # Buscar líneas que contienen datos (pueden tener pipes | o │)
            # Ignorar líneas de encabezado y separadores
            has_pipe = '|' in line or '│' in line
            is_header_or_separator = any(char in line for char in ['+-', '━', '┃', '┡', '┏', 'Name', '---', '==='])
            
            if has_pipe and not is_header_or_separator:
                self.log_message(f"Procesando línea de datos: '{line}'")
                
                # Dividir por pipes (tanto | como │) y limpiar espacios
                if '│' in line:
                    parts = [part.strip() for part in line.split('│') if part.strip()]
                else:
                    parts = [part.strip() for part in line.split('|') if part.strip()]
                    
                self.log_message(f"Partes encontradas: {parts}")
                
                if len(parts) >= 3:
                    name = parts[0]
                    size = parts[1] if len(parts) > 1 else ""
                    modified = parts[2] if len(parts) > 2 else ""
                    
                    # Determinar si es directorio o archivo
                    if name.endswith('/') or size.lower() == 'directory':
                        item_type = "Folder"
                        # Remover la barra final para el nombre
                        if name.endswith('/'):
                            name = name[:-1]
                    else:
                        item_type = "File"

                    if "..." in name:
                        self.log_message(f"⚠️ Nombre posiblemente truncado por CLI: '{name}'")
                    
                    item = {
                        'name': name,
                        'type': item_type,
                        'size': size,
                        'modified': modified
                    }
                    
                    items.append(item)
                    self.log_message(f"Item agregado: {item}")
                else:
                    self.log_message(f"Línea ignorada (partes insuficientes): {len(parts)}")
            else:
                if line.strip():  # Solo log si la línea no está vacía
                    self.log_message(f"Línea ignorada (header/separator): '{line}'")
        
        self.log_message(f"Parseo completado. Items encontrados: {len(items)}")
        return items
    
    # ---------------------------
    # Carga de directorios
    # ---------------------------
    def load_directory(self, path):
        """Cargar contenido de directorio en un hilo separado"""
        def load_thread():
            try:
                self.show_loading(True)
                self.log_message(f"Intentando cargar directorio: '{path}'")
                
                # Ejecutar comando cerebrium ls
                cmd = ["cerebrium", "ls", path] if path else ["cerebrium", "ls"]
                
                result = self.run_cerebrium(cmd, timeout=30)
                
                self.log_message(f"Comando ejecutado exitosamente")
                self.log_message(f"STDOUT length: {len(result.stdout)} chars")
                self.log_message(f"STDERR: {result.stderr if result.stderr else 'None'}")
                
                # Mostrar las primeras líneas del output para debug
                stdout_lines = result.stdout.split('\n')[:10]
                self.log_message(f"Primeras líneas del output:")
                for i, line in enumerate(stdout_lines):
                    self.log_message(f"  {i}: '{line}'")
                
                # Parsear resultado
                items = self.parse_cerebrium_output(result.stdout)
                self.log_message(f"Items parseados: {len(items)}")
                
                # Actualizar UI en el hilo principal
                self.root.after(0, lambda: self.update_tree(items, path))
                
            except subprocess.TimeoutExpired as e:
                error_msg = f"Timeout al ejecutar comando (>30s): {e}"
                self.log_message(f"ERROR: {error_msg}")
                self.root.after(0, lambda: self.show_error(error_msg))
            except subprocess.CalledProcessError as e:
                error_msg = f"Error al cargar directorio (código {e.returncode}): {e}"
                self.log_message(f"ERROR: {error_msg}")
                self.log_message(f"STDOUT: {e.stdout}")
                self.log_message(f"STDERR: {e.stderr}")
                self.root.after(0, lambda: self.show_error(error_msg))
            except Exception as e:
                error_msg = f"Error inesperado: {e}"
                self.log_message(f"ERROR: {error_msg}")
                self.root.after(0, lambda: self.show_error(error_msg))
        
        # Ejecutar en hilo separado para no bloquear la UI
        thread = threading.Thread(target=load_thread)
        thread.daemon = True
        thread.start()
    
    def update_tree(self, items, path):
        """Actualizar el treeview con los items"""
        # Limpiar árbol actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Guardar último listado para resolver nombres truncados
        self.last_items = items[:]
        
        # Actualizar ruta actual
        self.current_path = path
        self.path_label.config(text=f"Ruta: /{path}" if path else "Ruta: /")
        
        # Habilitar/deshabilitar botón de atrás
        self.back_btn.config(state=tk.NORMAL if self.path_history else tk.DISABLED)
        
        # Agregar items al árbol
        for item in items:
            # Icono según tipo
            icon = "📁" if item['type'] == 'Folder' else "📄"
            name_with_icon = f"{icon} {item['name']}"
            
            self.tree.insert('', tk.END, text=name_with_icon, values=(
                item['type'],
                item['size'],
                item['modified']
            ))
        
        self.show_loading(False)
        self.update_status(f"Cargados {len(items)} elementos")
    
    # ---------------------------
    # Errores y navegación
    # ---------------------------
    def show_error(self, message):
        """Mostrar mensaje de error"""
        self.show_loading(False)
        self.update_status("Error")
        messagebox.showerror("Error", message)
    
    def on_item_double_click(self, event):
        """Manejar doble clic en item"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        item_type = item['values'][0] if item['values'] else ""
        
        if item_type == 'Folder':
            # Extraer nombre de carpeta (sin icono)
            folder_name = item['text'].replace("📁 ", "")
            if "..." in folder_name:
                folder_name = self.resolve_full_name(folder_name, self.last_items)
            
            # Construir nueva ruta
            if self.current_path:
                new_path = f"{self.current_path}/{folder_name}"
            else:
                new_path = folder_name
            
            # Agregar ruta actual al historial
            self.path_history.append(self.current_path)
            
            # Cargar nueva ruta
            self.load_directory(new_path)
    
    def go_back(self):
        """Volver al directorio anterior"""
        if self.path_history:
            previous_path = self.path_history.pop()
            self.load_directory(previous_path)
    
    def go_home(self):
        """Ir al directorio raíz"""
        self.path_history.clear()
        self.load_directory("")
    
    def refresh(self):
        """Refrescar directorio actual"""
        self.load_directory(self.current_path)

def main():
    root = tk.Tk()
    app = CerebriumFileManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
