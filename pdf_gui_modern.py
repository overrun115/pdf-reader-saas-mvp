#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import subprocess
import platform
from pdf_to_tables import extract_tables_from_pdf, extract_tables_with_format, process_multiple_pdfs


class ModernPDFExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Table Extractor")
        self.root.geometry("900x750")
        self.root.configure(bg='#f8fafc')
        self.root.resizable(True, True)
        
        # Variables
        self.pdf_files = []
        self.output_dir = tk.StringVar(value=os.getcwd())
        self.output_format = tk.StringVar(value="excel")
        
        # Colores modernos
        self.colors = {
            'bg': '#f8fafc',
            'primary': '#2563eb',
            'primary_dark': '#1d4ed8',
            'secondary': '#64748b',
            'success': '#059669',
            'warning': '#d97706',
            'danger': '#dc2626',
            'white': '#ffffff',
            'gray_100': '#f1f5f9',
            'gray_200': '#e2e8f0',
            'gray_300': '#cbd5e1',
            'gray_600': '#475569',
            'gray_800': '#1e293b'
        }
        
        self.setup_styles()
        self.create_modern_ui()
        
        # Mensaje de bienvenida
        self.add_log("🎉 Bienvenido al Extractor de Tablas PDF")
        self.add_log("📂 Arrastra archivos PDF aquí o usa el botón de selección")
    
    def setup_styles(self):
        """Configurar estilos ttk modernos"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar estilos personalizados
        style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'), 
                       foreground=self.colors['primary'], background=self.colors['bg'])
        style.configure('Heading.TLabel', font=('Segoe UI', 14, 'bold'), 
                       foreground=self.colors['gray_800'], background=self.colors['white'])
        style.configure('Modern.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Card.TFrame', background=self.colors['white'], relief='flat', borderwidth=1)
    
    def create_modern_ui(self):
        # ===== CONTENEDOR PRINCIPAL =====
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # ===== HEADER =====
        header_frame = tk.Frame(main_container, bg=self.colors['bg'], height=100)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        header_frame.pack_propagate(False)
        
        # Título principal
        title_label = tk.Label(header_frame, 
                              text="📊 PDF Table Extractor",
                              font=('Segoe UI', 28, 'bold'),
                              fg=self.colors['primary'], 
                              bg=self.colors['bg'])
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(header_frame,
                                 text="Extrae tablas de archivos PDF y convierte a Excel/CSV",
                                 font=('Segoe UI', 12),
                                 fg=self.colors['secondary'],
                                 bg=self.colors['bg'])
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # ===== GRID DE TARJETAS =====
        cards_frame = tk.Frame(main_container, bg=self.colors['bg'])
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid
        cards_frame.columnconfigure(0, weight=2)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.rowconfigure(0, weight=1)
        cards_frame.rowconfigure(1, weight=1)
        
        # ===== TARJETA 1: ARCHIVOS =====
        files_card = self.create_card(cards_frame, "📁 Archivos PDF")
        files_card.grid(row=0, column=0, sticky='nsew', padx=(0, 15), pady=(0, 15))
        
        # Área de drop zone
        drop_zone = tk.Frame(files_card, bg=self.colors['gray_100'], 
                            relief=tk.SOLID, bd=2, cursor='hand2')
        drop_zone.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Configurar drop zone
        self.setup_drop_zone(drop_zone)
        
        # Lista de archivos en la drop zone
        self.files_display = tk.Frame(drop_zone, bg=self.colors['gray_100'])
        self.files_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Texto inicial
        self.empty_state = tk.Label(self.files_display,
                                   text="🎯 Arrastra archivos PDF aquí\n\nó haz clic para seleccionar",
                                   font=('Segoe UI', 14),
                                   fg=self.colors['secondary'],
                                   bg=self.colors['gray_100'],
                                   justify=tk.CENTER)
        self.empty_state.pack(expand=True)
        
        # Botones de archivos
        files_buttons = tk.Frame(files_card, bg=self.colors['white'])
        files_buttons.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.create_button(files_buttons, "📂 Seleccionar", self.select_files, 
                          self.colors['primary'], side=tk.LEFT)
        self.create_button(files_buttons, "🗑️ Limpiar", self.clear_files, 
                          self.colors['danger'], side=tk.LEFT, padx=(10, 0))
        self.create_button(files_buttons, "👁️ Vista Previa", self.preview_tables, 
                          self.colors['warning'], side=tk.LEFT, padx=(10, 0))
        
        # Contador
        self.files_count = tk.Label(files_buttons, text="0 archivos",
                                   font=('Segoe UI', 11, 'bold'),
                                   fg=self.colors['secondary'], bg=self.colors['white'])
        self.files_count.pack(side=tk.RIGHT, padx=(10, 0))
        
        # ===== TARJETA 2: CONFIGURACIÓN =====
        config_card = self.create_card(cards_frame, "⚙️ Configuración")
        config_card.grid(row=0, column=1, sticky='nsew', pady=(0, 15))
        
        config_content = tk.Frame(config_card, bg=self.colors['white'])
        config_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Carpeta de salida
        tk.Label(config_content, text="📁 Carpeta de salida",
                font=('Segoe UI', 11, 'bold'),
                fg=self.colors['gray_800'], bg=self.colors['white']).pack(anchor='w', pady=(0, 5))
        
        output_frame = tk.Frame(config_content, bg=self.colors['gray_100'], 
                               relief=tk.SOLID, bd=1)
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.output_entry = tk.Entry(output_frame, textvariable=self.output_dir,
                                    font=('Segoe UI', 10), state='readonly',
                                    bg=self.colors['white'], fg=self.colors['gray_800'],
                                    relief=tk.FLAT, bd=5)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        btn_frame = tk.Frame(output_frame, bg=self.colors['gray_100'])
        btn_frame.pack(side=tk.RIGHT, padx=5, pady=2)
        
        self.create_small_button(btn_frame, "📁", self.select_output_dir, 
                                self.colors['success'])
        self.create_small_button(btn_frame, "🗂️", self.open_output_folder, 
                                self.colors['warning'], padx=(5, 0))
        
        # Formato
        tk.Label(config_content, text="📊 Formato de salida",
                font=('Segoe UI', 11, 'bold'),
                fg=self.colors['gray_800'], bg=self.colors['white']).pack(anchor='w', pady=(0, 5))
        
        format_frame = tk.Frame(config_content, bg=self.colors['gray_100'],
                               relief=tk.SOLID, bd=1)
        format_frame.pack(fill=tk.X, pady=(0, 15))
        
        formats = [("📊 Excel", "excel"), ("📄 CSV", "csv"), ("📊📄 Ambos", "both")]
        for i, (text, value) in enumerate(formats):
            tk.Radiobutton(format_frame, text=text, variable=self.output_format, value=value,
                          font=('Segoe UI', 10), bg=self.colors['gray_100'],
                          fg=self.colors['gray_800']).pack(anchor='w', padx=10, pady=3)
        
        # ===== TARJETA 3: PROCESAMIENTO =====
        process_card = self.create_card(cards_frame, "🚀 Procesamiento")
        process_card.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 0))
        
        process_content = tk.Frame(process_card, bg=self.colors['white'])
        process_content.pack(fill=tk.X, padx=20, pady=20)
        
        # Botón principal
        self.process_button = tk.Button(process_content,
                                       text="🚀 EXTRAER TABLAS",
                                       command=self.process_files,
                                       font=('Segoe UI', 16, 'bold'),
                                       bg=self.colors['primary'], fg='white',
                                       relief=tk.FLAT, bd=0,
                                       padx=40, pady=15,
                                       cursor='hand2')
        self.process_button.pack(pady=(0, 15))
        
        # Estado y progreso
        status_frame = tk.Frame(process_content, bg=self.colors['white'])
        status_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(status_frame,
                                    text="⭐ Listo para procesar",
                                    font=('Segoe UI', 12, 'bold'),
                                    fg=self.colors['success'], bg=self.colors['white'])
        self.status_label.pack(pady=(0, 10))
        
        # Barra de progreso moderna
        progress_container = tk.Frame(status_frame, bg=self.colors['gray_200'], 
                                     relief=tk.FLAT, bd=0, height=8)
        progress_container.pack(fill=tk.X, pady=(0, 20))
        progress_container.pack_propagate(False)
        
        self.progress = ttk.Progressbar(progress_container, mode='indeterminate',
                                       style='Modern.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.BOTH, expand=True)
        
        # ===== LOG MODERNO EN LA PARTE INFERIOR =====
        log_frame = tk.Frame(main_container, bg=self.colors['white'],
                            relief=tk.SOLID, bd=1, height=200)
        log_frame.pack(fill=tk.X, pady=(30, 0))
        log_frame.pack_propagate(False)
        
        log_header = tk.Frame(log_frame, bg=self.colors['gray_100'], height=40)
        log_header.pack(fill=tk.X)
        log_header.pack_propagate(False)
        
        tk.Label(log_header, text="📋 Registro de Actividad",
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['gray_800'], bg=self.colors['gray_100']).pack(side=tk.LEFT, padx=15, pady=10)
        
        self.clear_log_btn = tk.Button(log_header, text="🗑️ Limpiar",
                                      command=self.clear_log,
                                      font=('Segoe UI', 9),
                                      bg=self.colors['gray_300'], fg=self.colors['gray_800'],
                                      relief=tk.FLAT, bd=0, padx=10, pady=5)
        self.clear_log_btn.pack(side=tk.RIGHT, padx=15, pady=7)
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                 font=('Consolas', 10),
                                                 bg=self.colors['white'],
                                                 fg=self.colors['gray_800'],
                                                 relief=tk.FLAT, bd=0,
                                                 wrap=tk.WORD,
                                                 state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
    
    def create_card(self, parent, title):
        """Crear tarjeta moderna con sombra"""
        card = tk.Frame(parent, bg=self.colors['white'], relief=tk.FLAT, bd=0)
        
        # Simulación de sombra con frames
        shadow = tk.Frame(parent, bg=self.colors['gray_300'], relief=tk.FLAT, bd=0)
        shadow.place(in_=card, x=3, y=3, relwidth=1, relheight=1)
        card.lift()
        
        # Header de la tarjeta
        header = tk.Frame(card, bg=self.colors['primary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text=title,
                              font=('Segoe UI', 14, 'bold'),
                              fg='white', bg=self.colors['primary'])
        title_label.pack(pady=15, padx=20, anchor='w')
        
        return card
    
    def create_button(self, parent, text, command, color, side=None, padx=0):
        btn = tk.Button(parent, text=text, command=command,
                       font=('Segoe UI', 10, 'bold'),
                       bg=color, fg='white',
                       relief=tk.FLAT, bd=0,
                       padx=15, pady=8,
                       cursor='hand2')
        if side:
            btn.pack(side=side, padx=padx)
        else:
            btn.pack(padx=padx)
        return btn
    
    def create_small_button(self, parent, text, command, color, padx=0):
        btn = tk.Button(parent, text=text, command=command,
                       font=('Segoe UI', 9, 'bold'),
                       bg=color, fg='white',
                       relief=tk.FLAT, bd=0,
                       padx=8, pady=6,
                       cursor='hand2')
        btn.pack(side=tk.LEFT, padx=padx)
        return btn
    
    def setup_drop_zone(self, drop_zone):
        """Configurar zona de arrastrar y soltar"""
        def on_click(event):
            self.select_files()
        
        def on_enter(event):
            drop_zone.config(bg=self.colors['gray_200'])
        
        def on_leave(event):
            drop_zone.config(bg=self.colors['gray_100'])
        
        drop_zone.bind("<Button-1>", on_click)
        drop_zone.bind("<Enter>", on_enter)
        drop_zone.bind("<Leave>", on_leave)
        
        # Hacer que todos los widgets hijos también respondan al click
        for child in drop_zone.winfo_children():
            child.bind("<Button-1>", on_click)
    
    def add_log(self, message):
        """Agregar mensaje al log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Limpiar el log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            self.empty_state.destroy()
            
            for file in files:
                if file not in self.pdf_files:
                    self.pdf_files.append(file)
                    self.add_file_widget(file)
            
            self.update_count()
            self.add_log(f"✅ Agregados {len(files)} archivo(s) PDF")
    
    def add_file_widget(self, filepath):
        """Agregar widget de archivo a la lista"""
        file_frame = tk.Frame(self.files_display, bg=self.colors['white'],
                             relief=tk.SOLID, bd=1)
        file_frame.pack(fill=tk.X, pady=2)
        
        # Nombre del archivo
        filename = os.path.basename(filepath)
        tk.Label(file_frame, text=f"📄 {filename}",
                font=('Segoe UI', 10),
                fg=self.colors['gray_800'], bg=self.colors['white']).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Botón eliminar
        remove_btn = tk.Button(file_frame, text="❌",
                              command=lambda: self.remove_file(filepath, file_frame),
                              font=('Segoe UI', 8),
                              bg=self.colors['danger'], fg='white',
                              relief=tk.FLAT, bd=0,
                              padx=5, pady=2)
        remove_btn.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def remove_file(self, filepath, widget):
        """Eliminar archivo de la lista"""
        self.pdf_files.remove(filepath)
        widget.destroy()
        self.update_count()
        
        if not self.pdf_files:
            self.empty_state = tk.Label(self.files_display,
                                       text="🎯 Arrastra archivos PDF aquí\\n\\nó haz clic para seleccionar",
                                       font=('Segoe UI', 14),
                                       fg=self.colors['secondary'],
                                       bg=self.colors['gray_100'],
                                       justify=tk.CENTER)
            self.empty_state.pack(expand=True)
        
        self.add_log(f"🗑️ Eliminado: {os.path.basename(filepath)}")
    
    def clear_files(self):
        """Limpiar todos los archivos"""
        self.pdf_files.clear()
        for widget in self.files_display.winfo_children():
            widget.destroy()
        
        self.empty_state = tk.Label(self.files_display,
                                   text="🎯 Arrastra archivos PDF aquí\n\nó haz clic para seleccionar",
                                   font=('Segoe UI', 14),
                                   fg=self.colors['secondary'],
                                   bg=self.colors['gray_100'],
                                   justify=tk.CENTER)
        self.empty_state.pack(expand=True)
        
        self.update_count()
        self.add_log("🗑️ Lista de archivos limpiada")
    
    def update_count(self):
        """Actualizar contador de archivos"""
        count = len(self.pdf_files)
        if count == 0:
            self.files_count.config(text="0 archivos", fg=self.colors['secondary'])
        elif count == 1:
            self.files_count.config(text="1 archivo", fg=self.colors['success'])
        else:
            self.files_count.config(text=f"{count} archivos", fg=self.colors['success'])
    
    def select_output_dir(self):
        directory = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if directory:
            self.output_dir.set(directory)
            self.add_log(f"📁 Carpeta cambiada: {directory}")
    
    def open_output_folder(self):
        folder_path = self.output_dir.get()
        
        if not os.path.exists(folder_path):
            messagebox.showwarning("Carpeta no encontrada", 
                                 f"La carpeta {folder_path} no existe.")
            return
        
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", folder_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", folder_path])
            
            self.add_log(f"🗂️ Carpeta abierta: {folder_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{str(e)}")
    
    def preview_tables(self):
        if not self.pdf_files:
            messagebox.showwarning("Sin archivos", 
                                 "Por favor selecciona al menos un archivo PDF primero.")
            return
        
        self.add_log("👁️ Abriendo vista previa de tablas...")
        messagebox.showinfo("Vista Previa", "Función disponible próximamente.")
    
    def process_files(self):
        if not self.pdf_files:
            messagebox.showwarning("Sin archivos", 
                                 "Por favor selecciona al menos un archivo PDF primero.")
            return
        
        # Deshabilitar botón y mostrar progreso
        self.process_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_label.config(text="🔄 Procesando archivos...", fg=self.colors['warning'])
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self._process_thread)
        thread.daemon = True
        thread.start()
    
    def _process_thread(self):
        try:
            results = []
            total_files = len(self.pdf_files)
            
            for i, pdf_file in enumerate(self.pdf_files):
                self.root.after(0, lambda i=i: self.status_label.config(
                    text=f"🔄 Archivo {i+1}/{total_files}..."))
                
                self.add_log(f"📄 Procesando: {os.path.basename(pdf_file)} ({i+1}/{total_files})")
                
                # Generar nombre de salida
                pdf_name = os.path.splitext(os.path.basename(pdf_file))[0]
                output_file = os.path.join(self.output_dir.get(), f"{pdf_name}_tablas")
                
                # Procesar archivo
                format_type = self.output_format.get()
                success = extract_tables_with_format(pdf_file, output_file + ".xlsx", format_type)
                results.append((pdf_file, output_file, success))
                
                if success:
                    self.add_log(f"✅ Exitoso: {pdf_name}_tablas")
                else:
                    self.add_log(f"❌ Error: {os.path.basename(pdf_file)}")
            
            # Resumen final
            successful = sum(1 for _, _, success in results if success)
            self.add_log(f"\n🎯 RESULTADO: {successful}/{len(results)} archivos procesados")
            
            if successful == len(results):
                self.root.after(0, lambda: messagebox.showinfo("🎉 Completado", 
                    f"¡Éxito! {successful} archivo(s) procesados."))
            elif successful > 0:
                self.root.after(0, lambda: messagebox.showwarning("⚠️ Parcial", 
                    f"{successful}/{len(results)} archivos procesados."))
            else:
                self.root.after(0, lambda: messagebox.showerror("❌ Error", 
                    "No se procesó ningún archivo."))
                    
        except Exception as e:
            self.add_log(f"💥 Error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {str(e)}"))
        
        finally:
            self.root.after(0, self._finish_processing)
    
    def _finish_processing(self):
        self.progress.stop()
        self.status_label.config(text="✅ Proceso completado", fg=self.colors['success'])
        self.process_button.config(state=tk.NORMAL)


def main():
    if len(sys.argv) > 1:
        from pdf_to_tables import main as cli_main
        cli_main()
    else:
        root = tk.Tk()
        app = ModernPDFExtractor(root)
        root.mainloop()


if __name__ == "__main__":
    main()