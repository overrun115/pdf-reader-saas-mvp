import os
import pandas as pd
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from pytesseract import Output
from typing import List, Tuple, Optional
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline

def preprocess_image_for_ocr(image_path: str) -> np.ndarray:
    """
    Preprocesa la imagen para mejorar la calidad del OCR.
    """
    print(f"[IMAGE_EXTRACTOR] Preprocesando imagen: {image_path}")
    
    # Cargar imagen con OpenCV
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen: {image_path}")
    
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aplicar filtro bilateral para reducir ruido preservando bordes
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Mejorar contraste usando CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # Aplicar filtro de enfoque
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    # Binarización adaptativa
    binary = cv2.adaptiveThreshold(sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    # Operaciones morfológicas para limpiar
    kernel = np.ones((1,1), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    print("[IMAGE_EXTRACTOR] Preprocesamiento completado")
    return cleaned

def detect_table_structure_cv(image: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """
    Detecta estructuras de tabla usando OpenCV.
    """
    print("[IMAGE_EXTRACTOR] Detectando estructura de tabla...")
    
    # Detectar líneas horizontales
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel)
    
    # Detectar líneas verticales
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel)
    
    # Combinar líneas
    table_structure = cv2.add(horizontal_lines, vertical_lines)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(table_structure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    cells = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if 20 < w < image.shape[1] * 0.8 and 10 < h < image.shape[0] * 0.8:
            cells.append((x, y, w, h))
    
    print(f"[IMAGE_EXTRACTOR] Detectadas {len(cells)} celdas potenciales")
    return cells

def extract_text_enhanced_ocr(image: np.ndarray, lang='eng+spa') -> str:
    """
    Extrae texto con configuración optimizada.
    """
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,:-/()$%'
    
    try:
        text = pytesseract.image_to_string(image, lang=lang, config=custom_config)
        return text.strip()
    except Exception as e:
        print(f"[IMAGE_EXTRACTOR] Error en OCR: {e}")
        try:
            text = pytesseract.image_to_string(image, lang=lang, config=r'--oem 3 --psm 6')
            return text.strip()
        except:
            return ""

def extract_table_data_from_cells_cv(image: np.ndarray, cells: List[Tuple[int, int, int, int]]) -> List[List[str]]:
    """
    Extrae datos de celdas detectadas.
    """
    print("[IMAGE_EXTRACTOR] Extrayendo datos de celdas...")
    
    cell_data = []
    for i, (x, y, w, h) in enumerate(cells):
        cell_img = image[y:y+h, x:x+w]
        cell_text = extract_text_enhanced_ocr(cell_img)
        
        if cell_text:
            cell_data.append({
                'text': cell_text,
                'x': x, 'y': y, 'w': w, 'h': h
            })
    
    if not cell_data:
        return []
    
    # Organizar en filas
    cell_data.sort(key=lambda c: (c['y'], c['x']))
    
    rows = []
    current_row = []
    current_y = cell_data[0]['y']
    y_tolerance = 20
    
    for cell in cell_data:
        if abs(cell['y'] - current_y) <= y_tolerance:
            current_row.append(cell['text'])
        else:
            if current_row:
                rows.append(current_row)
            current_row = [cell['text']]
            current_y = cell['y']
    
    if current_row:
        rows.append(current_row)
    
    print(f"[IMAGE_EXTRACTOR] Organizadas {len(rows)} filas de datos")
    return rows

def extract_tables_from_image(image_path, output_path=None, format_type='csv', **kwargs):
    """
    Extrae tablas de una imagen usando múltiples métodos mejorados.
    """
    print(f"[IMAGE_EXTRACTOR] Procesando imagen: {image_path}")
    
    if not os.path.exists(image_path):
        raise RuntimeError(f"Archivo de imagen no encontrado: {image_path}")
    
    try:
        # Método 1: OCR mejorado con detección de estructura
        processed_img = preprocess_image_for_ocr(image_path)
        cells = detect_table_structure_cv(processed_img)
        table_rows = []
        
        if cells:
            table_rows = extract_table_data_from_cells_cv(processed_img, cells)
        
        # Método 2: Fallback con texto completo
        if not table_rows:
            print("[IMAGE_EXTRACTOR] Fallback: Procesando texto completo...")
            full_text = extract_text_enhanced_ocr(processed_img)
            if full_text:
                table_rows = process_text_to_tables(full_text)
        
        # Método 3: Docling como respaldo
        if not table_rows:
            print("[IMAGE_EXTRACTOR] Fallback: Probando con Docling...")
            table_rows = extract_with_docling(image_path)
        
        # Método 4: OCR básico línea por línea
        if not table_rows:
            print("[IMAGE_EXTRACTOR] Último fallback: OCR básico...")
            img_pil = Image.fromarray(processed_img)
            tsv = pytesseract.image_to_data(img_pil, output_type=Output.DATAFRAME, lang='eng+spa')
            tsv = tsv[tsv['text'].notnull() & (tsv['text'].str.strip() != '')]
            
            line_data = []
            for line_num, line_df in tsv.groupby('line_num'):
                row = list(line_df['text'])
                if len(row) >= 2:
                    line_data.append(row)
            
            table_rows = line_data
        
        if not table_rows:
            raise RuntimeError("No se pudo extraer contenido de la imagen.")
        
        # Crear DataFrame normalizado
        tables = []
        if table_rows:
            max_cols = max(len(row) for row in table_rows)
            normalized_rows = []
            for row in table_rows:
                while len(row) < max_cols:
                    row.append('')
                normalized_rows.append(row[:max_cols])
            
            columns = [f"Columna_{i+1}" for i in range(max_cols)]
            df = pd.DataFrame(normalized_rows, columns=columns)
            df = df.replace('', pd.NA).dropna(how='all').fillna('')
            tables = [df]
        
        # Guardar resultados
        if output_path and tables:
            save_tables_to_file(tables, output_path, format_type)
        
        print(f"[IMAGE_EXTRACTOR] Procesamiento completado. Tablas encontradas: {len(tables)}")
        return True
        
    except Exception as e:
        print(f"[IMAGE_EXTRACTOR] Error en procesamiento: {e}")
        return False

def extract_with_docling(image_path):
    """
    Método de extracción usando Docling.
    """
    try:
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.do_cell_matching = True
        
        converter = DocumentConverter(
            format_options={
                InputFormat.IMAGE: pipeline_options,
            }
        )
        
        result = converter.convert(image_path)
        text_content = result.document.export_to_text()
        
        tables = []
        if hasattr(result.document, 'tables') and result.document.tables:
            for i, table in enumerate(result.document.tables):
                try:
                    table_data = convert_docling_table_to_dataframe(table)
                    if table_data is not None and not table_data.empty:
                        tables.append(table_data)
                except Exception as e:
                    print(f"[IMAGE_EXTRACTOR] Error procesando tabla Docling {i+1}: {e}")
        
        if not tables and text_content.strip():
            tables = process_text_to_tables(text_content)
        
        return tables
        
    except Exception as e:
        print(f"[IMAGE_EXTRACTOR] Error con Docling: {e}")
        return []

def convert_docling_table_to_dataframe(docling_table):
    """Convierte una tabla de Docling a DataFrame de pandas"""
    try:
        # Extraer datos de la tabla de Docling
        if hasattr(docling_table, 'data') and docling_table.data:
            # Si la tabla tiene datos estructurados
            rows = []
            for row in docling_table.data:
                if isinstance(row, list):
                    rows.append([str(cell) for cell in row])
                else:
                    rows.append([str(row)])
            
            if rows:
                return pd.DataFrame(rows)
        
        # Si no tiene datos estructurados, intentar con el texto
        if hasattr(docling_table, 'text') and docling_table.text:
            return process_text_to_tables(docling_table.text)
        
        return None
        
    except Exception as e:
        print(f"[IMAGE_EXTRACTOR] Error convirtiendo tabla de Docling: {e}")
        return None

def extract_with_fallback(image_path, output_path=None, format_type='csv'):
    """Método de respaldo usando OCR básico"""
    print(f"[IMAGE_EXTRACTOR] Usando método de respaldo para: {image_path}")
    
    try:
        import pytesseract
        from PIL import Image
        
        # Leer imagen
        img = Image.open(image_path)
        
        # OCR básico
        text = pytesseract.image_to_string(img, lang='eng+spa')
        
        if text.strip():
            tables = process_text_to_tables(text)
            
            if not tables:
                # Crear tabla con texto completo
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if lines:
                    df = pd.DataFrame({'Texto': lines})
                    tables = [df]
            
            if tables and output_path:
                save_tables_to_file(tables, output_path, format_type)
            
            return True if tables else False
        
        return False
        
    except Exception as e:
        print(f"[IMAGE_EXTRACTOR] Error en método de respaldo: {e}")
        raise RuntimeError(f"No se pudo procesar la imagen: {e}")

def process_text_to_tables(text):
    """Procesa texto para encontrar estructuras tabulares"""
    tables = []
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Buscar patrones de tabla (líneas con múltiples elementos separados)
    potential_rows = []
    for line in lines:
        # Detectar separadores comunes
        separators = ['\t', '|', ';', '  ', ',']
        for sep in separators:
            if sep in line:
                parts = [p.strip() for p in line.split(sep) if p.strip()]
                if len(parts) >= 2:  # Al menos 2 columnas
                    potential_rows.append(parts)
                break
    
    if len(potential_rows) >= 2:  # Al menos 2 filas
        # Normalizar número de columnas
        max_cols = max(len(row) for row in potential_rows)
        normalized_rows = []
        for row in potential_rows:
            while len(row) < max_cols:
                row.append("")
            normalized_rows.append(row[:max_cols])
        
        df = pd.DataFrame(normalized_rows[1:], columns=normalized_rows[0] if normalized_rows else None)
        tables.append(df)
    
    return tables

def detect_table_by_lines(img):
    """Detecta tablas por líneas en la imagen"""
    tables = []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    
    # Detectar líneas horizontales y verticales
    kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_h)
    vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_v)
    mask = cv2.add(horizontal, vertical)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 100 and h > 50:  # Filtro más flexible
            roi = img[y:y+h, x:x+w]
            
            # OCR en la región
            try:
                roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(roi_gray, config=r'--oem 3 --psm 6')
                
                if text.strip():
                    table_data = process_text_to_tables(text)
                    tables.extend(table_data)
            except Exception as e:
                print(f"[IMAGE_EXTRACTOR] Error en OCR de región: {e}")
                continue
    
    return tables

def detect_tabular_patterns(text):
    """Detecta patrones tabulares en texto"""
    tables = []
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Buscar patrones numéricos o fechas que sugieran tablas
    numeric_lines = []
    for line in lines:
        # Contar números, fechas, y patrones similares
        import re
        numbers = re.findall(r'\d+[.,]?\d*', line)
        if len(numbers) >= 2:  # Línea con al menos 2 números
            numeric_lines.append(line)
    
    if len(numeric_lines) >= 2:
        # Intentar crear tabla con estas líneas
        rows = []
        for line in numeric_lines[:10]:  # Máximo 10 filas
            # Dividir por espacios múltiples o caracteres especiales
            import re
            parts = re.split(r'\s{2,}|[|;,]', line)
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) >= 2:
                rows.append(parts)
        
        if rows:
            max_cols = max(len(row) for row in rows)
            normalized_rows = []
            for row in rows:
                while len(row) < max_cols:
                    row.append("")
                normalized_rows.append(row[:max_cols])
            
            df = pd.DataFrame(normalized_rows)
            tables.append(df)
    
    return tables

def save_tables_to_file(tables, output_path, format_type):
    """Guarda las tablas en el formato especificado"""
    if not tables:
        return
    
    try:
        if format_type.lower() == 'excel':
            output_file = f"{output_path}.xlsx"
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                for i, table in enumerate(tables):
                    sheet_name = f'Table_{i+1}'
                    table.to_excel(writer, sheet_name=sheet_name, index=False)
        else:  # CSV
            output_file = f"{output_path}.csv"
            if len(tables) == 1:
                tables[0].to_csv(output_file, index=False)
            else:
                # Combinar todas las tablas
                combined = pd.concat(tables, ignore_index=True)
                combined.to_csv(output_file, index=False)
        
        print(f"[IMAGE_EXTRACTOR] Archivo guardado: {output_file}")
    except Exception as e:
        print(f"[IMAGE_EXTRACTOR] Error guardando archivo: {e}")
        raise
