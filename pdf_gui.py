#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import os
import sys
import subprocess
import platform
from pdf_to_tables import extract_tables_from_pdf, extract_tables_with_format, process_multiple_pdfs


class SimplePDFExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Table Extractor")
        self.root.geometry("750x650")
        self.root.configure(bg='white')
        
        # Variables
        self.pdf_files = []
        self.output_dir = tk.StringVar(value=os.getcwd())
        self.output_format = tk.StringVar(value="excel")
        
        self.create_interface()
        self.add_log("🎉 Extractor de Tablas PDF - Listo para usar")
    
    def create_interface(self):
        # === TÍTULO ===
        title_frame = tk.Frame(self.root, bg='navy', height=70)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="📊 EXTRACTOR DE TABLAS PDF", 
                font=('Arial', 18, 'bold'), fg='white', bg='navy').pack(expand=True)
        
        # === CONTENIDO PRINCIPAL ===
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === SECCIÓN 1: ARCHIVOS ===
        files_section = tk.LabelFrame(main_frame, text=" 📁 ARCHIVOS PDF ",
                                     font=('Arial', 12, 'bold'), fg='navy',
                                     bg='white', relief=tk.GROOVE, bd=3)
        files_section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Lista de archivos
        list_frame = tk.Frame(files_section, bg='lightgray', relief=tk.SUNKEN, bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.files_listbox = tk.Listbox(list_frame, font=('Arial', 11), height=6,
                                       bg='white', fg='black', relief=tk.FLAT)
        scrollbar = tk.Scrollbar(list_frame, command=self.files_listbox.yview)
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 2), pady=2)
        
        # Texto inicial
        self.files_listbox.insert(0, "🎯 Selecciona archivos PDF usando los botones de abajo")
        self.files_listbox.config(fg='gray')
        
        # Botones de archivos
        btn_frame = tk.Frame(files_section, bg='white')
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(btn_frame, text="📂 Seleccionar PDFs", command=self.select_files,
                 bg='dodgerblue', fg='white', font=('Arial', 10, 'bold'),
                 relief=tk.RAISED, bd=2, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🗑️ Limpiar", command=self.clear_files,
                 bg='red', fg='white', font=('Arial', 10, 'bold'),
                 relief=tk.RAISED, bd=2, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Contador
        self.count_label = tk.Label(btn_frame, text="0 archivos seleccionados",
                                   font=('Arial', 11, 'bold'), fg='navy', bg='white')
        self.count_label.pack(side=tk.RIGHT, padx=10)
        
        # === SECCIÓN 2: CONFIGURACIÓN ===
        config_section = tk.LabelFrame(main_frame, text=" ⚙️ CONFIGURACIÓN ",
                                      font=('Arial', 12, 'bold'), fg='navy',
                                      bg='white', relief=tk.GROOVE, bd=3)
        config_section.pack(fill=tk.X, pady=(0, 15))
        
        # Carpeta de salida
        output_frame = tk.Frame(config_section, bg='white')
        output_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(output_frame, text="📁 Carpeta de salida:",
                font=('Arial', 11, 'bold'), fg='black', bg='white').pack(anchor='w')
        
        path_container = tk.Frame(output_frame, bg='lightgray', relief=tk.SUNKEN, bd=2)
        path_container.pack(fill=tk.X, pady=(5, 10))
        
        self.output_entry = tk.Entry(path_container, textvariable=self.output_dir,
                                    font=('Arial', 10), state='readonly',
                                    bg='white', fg='black', relief=tk.FLAT)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        tk.Button(path_container, text="📁", command=self.select_output_dir,
                 bg='green', fg='white', font=('Arial', 9, 'bold'),
                 relief=tk.RAISED, bd=1, padx=8, pady=3).pack(side=tk.RIGHT, padx=2, pady=2)
        
        tk.Button(path_container, text="🗂️", command=self.open_output_folder,
                 bg='purple', fg='white', font=('Arial', 9, 'bold'),
                 relief=tk.RAISED, bd=1, padx=8, pady=3).pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Formato de salida
        format_frame = tk.Frame(config_section, bg='white')
        format_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(format_frame, text="📊 Formato de salida:",
                font=('Arial', 11, 'bold'), fg='black', bg='white').pack(anchor='w')
        
        radio_container = tk.Frame(format_frame, bg='lightgray', relief=tk.SUNKEN, bd=2)
        radio_container.pack(fill=tk.X, pady=(5, 0))
        
        tk.Radiobutton(radio_container, text=" 📊 Solo Excel (.xlsx) ",
                      variable=self.output_format, value="excel",
                      font=('Arial', 10), bg='white', fg='black').pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Radiobutton(radio_container, text=" 📄 Solo CSV (.csv) ",
                      variable=self.output_format, value="csv",
                      font=('Arial', 10), bg='white', fg='black').pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Radiobutton(radio_container, text=" 📊📄 Ambos formatos ",
                      variable=self.output_format, value="both",
                      font=('Arial', 10), bg='white', fg='black').pack(side=tk.LEFT, padx=10, pady=5)
        
        # === SECCIÓN 3: PROCESAMIENTO ===
        process_section = tk.LabelFrame(main_frame, text=" 🚀 PROCESAMIENTO ",
                                       font=('Arial', 12, 'bold'), fg='navy',
                                       bg='white', relief=tk.GROOVE, bd=3)
        process_section.pack(fill=tk.X, pady=(0, 15))
        
        # Botón principal
        button_container = tk.Frame(process_section, bg='white')
        button_container.pack(pady=15)
        
        self.process_button = tk.Button(button_container, text="🚀 EXTRAER TABLAS DE TODOS LOS PDFs",
                                       command=self.process_files,
                                       font=('Arial', 14, 'bold'),
                                       bg='orange', fg='white',
                                       relief=tk.RAISED, bd=3,
                                       padx=30, pady=12)
        self.process_button.pack()
        
        # Estado
        self.status_label = tk.Label(process_section, text="⭐ Listo para procesar archivos",
                                    font=('Arial', 12, 'bold'), fg='green', bg='white')
        self.status_label.pack(pady=(0, 10))
        
        # === SECCIÓN 4: LOG ===
        log_section = tk.LabelFrame(main_frame, text=" 📋 REGISTRO DE ACTIVIDAD ",
                                   font=('Arial', 12, 'bold'), fg='navy',
                                   bg='white', relief=tk.GROOVE, bd=3)
        log_section.pack(fill=tk.BOTH, expand=True)
        
        # Header del log
        log_header = tk.Frame(log_section, bg='lightgray', height=35)
        log_header.pack(fill=tk.X, padx=2, pady=2)
        log_header.pack_propagate(False)
        
        tk.Label(log_header, text="Mensajes del sistema:",
                font=('Arial', 10, 'bold'), fg='black', bg='lightgray').pack(side=tk.LEFT, padx=10, pady=8)
        
        tk.Button(log_header, text="🗑️ Limpiar Log", command=self.clear_log,
                 bg='gray', fg='white', font=('Arial', 8, 'bold'),
                 relief=tk.RAISED, bd=1, padx=10, pady=5).pack(side=tk.RIGHT, padx=10, pady=3)
        
        # Área de texto del log
        log_container = tk.Frame(log_section, bg='black', relief=tk.SUNKEN, bd=2)
        log_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(log_container, font=('Courier', 10),
                                                 height=6, bg='black', fg='green',
                                                 relief=tk.FLAT, bd=0, wrap=tk.WORD,
                                                 state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    def add_log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.add_log("🗑️ Log limpiado")
    
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            # Limpiar texto inicial si existe
            if len(self.pdf_files) == 0:
                self.files_listbox.delete(0, tk.END)
                self.files_listbox.config(fg='black')
            
            for file in files:
                if file not in self.pdf_files:
                    self.pdf_files.append(file)
                    filename = os.path.basename(file)
                    self.files_listbox.insert(tk.END, f"📄 {filename}")
            
            self.update_count()
            self.add_log(f"✅ Agregados {len(files)} archivo(s) PDF")
    
    def clear_files(self):
        self.pdf_files.clear()
        self.files_listbox.delete(0, tk.END)
        self.files_listbox.insert(0, "🎯 Selecciona archivos PDF usando los botones de abajo")
        self.files_listbox.config(fg='gray')
        self.update_count()
        self.add_log("🗑️ Lista de archivos limpiada")
    
    def update_count(self):
        count = len(self.pdf_files)
        if count == 0:
            self.count_label.config(text="0 archivos seleccionados", fg='gray')
        elif count == 1:
            self.count_label.config(text="1 archivo seleccionado", fg='green')
        else:
            self.count_label.config(text=f"{count} archivos seleccionados", fg='green')
    
    def select_output_dir(self):
        directory = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if directory:
            self.output_dir.set(directory)
            self.add_log(f"📁 Carpeta de salida: {directory}")
    
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
            
            self.add_log(f"🗂️ Abriendo carpeta: {folder_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{str(e)}")
    
    def process_files(self):
        if not self.pdf_files:
            messagebox.showwarning("Sin archivos", 
                                 "Por favor selecciona al menos un archivo PDF primero.")
            return
        
        # Deshabilitar botón
        self.process_button.config(state=tk.DISABLED, text="🔄 PROCESANDO...", bg='red')
        self.status_label.config(text="🔄 Procesando archivos PDF...", fg='orange')
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self._process_thread)
        thread.daemon = True
        thread.start()
    
    def _process_thread(self):
        try:
            results = []
            total_files = len(self.pdf_files)
            
            for i, pdf_file in enumerate(self.pdf_files):
                # Actualizar estado
                self.root.after(0, lambda i=i: self.status_label.config(
                    text=f"🔄 Procesando archivo {i+1} de {total_files}..."))
                
                self.add_log(f"📄 Archivo {i+1}/{total_files}: {os.path.basename(pdf_file)}")
                
                # Generar nombre de salida
                pdf_name = os.path.splitext(os.path.basename(pdf_file))[0]
                output_file = os.path.join(self.output_dir.get(), f"{pdf_name}_tablas")
                
                # Procesar archivo
                format_type = self.output_format.get()
                success = extract_tables_with_format(pdf_file, output_file + ".xlsx", format_type)
                results.append((pdf_file, output_file, success))
                
                if success:
                    self.add_log(f"✅ EXITOSO: {pdf_name}_tablas")
                else:
                    self.add_log(f"❌ ERROR: {os.path.basename(pdf_file)}")
            
            # Resumen final
            successful = sum(1 for _, _, success in results if success)
            self.add_log(f"\n{'='*50}")
            self.add_log(f"🎯 RESUMEN FINAL: {successful}/{len(results)} archivos procesados")
            self.add_log(f"{'='*50}")
            
            if successful == len(results):
                self.root.after(0, lambda: messagebox.showinfo("🎉 ¡COMPLETADO!", 
                    f"¡Éxito total! Se procesaron los {successful} archivos PDF.\n\n"
                    f"📁 Archivos guardados en:\n{self.output_dir.get()}"))
            elif successful > 0:
                self.root.after(0, lambda: messagebox.showwarning("⚠️ Parcialmente completado", 
                    f"Se procesaron {successful} de {len(results)} archivos.\n\n"
                    f"Revisa el registro para ver detalles de errores."))
            else:
                self.root.after(0, lambda: messagebox.showerror("❌ Error total", 
                    "No se pudo procesar ningún archivo.\n\n"
                    "Revisa el registro para ver los errores."))
                    
        except Exception as e:
            self.add_log(f"💥 ERROR CRÍTICO: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error Crítico", 
                f"Ocurrió un error inesperado:\n{str(e)}"))
        
        finally:
            # Rehabilitar botón
            self.root.after(0, self._finish_processing)
    
    def _finish_processing(self):
        self.process_button.config(state=tk.NORMAL, text="🚀 EXTRAER TABLAS DE TODOS LOS PDFs", bg='orange')
        self.status_label.config(text="✅ Proceso completado - Listo para procesar más archivos", fg='green')


def main():
    if len(sys.argv) > 1:
        # Modo línea de comandos
        from pdf_to_tables import main as cli_main
        cli_main()
    else:
        # Modo GUI
        root = tk.Tk()
        app = SimplePDFExtractor(root)
        root.mainloop()


if __name__ == "__main__":
    main()