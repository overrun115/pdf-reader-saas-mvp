import os
import sys
import argparse
import pandas as pd
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from pytesseract import Output
import cv2
from typing import List, Tuple, Optional

def preprocess_image(image_path: str) -> np.ndarray:
    """
    Preprocesa la imagen para mejorar la calidad del OCR.
    """
    print(f"Preprocesando imagen: {image_path}")
    
    # Cargar imagen con OpenCV
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen: {image_path}")
    
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aplicar filtro bilateral para reducir ruido preservando bordes
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Mejorar contraste usando CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # Aplicar filtro de enfoque
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    # Binarización adaptativa para mejorar texto
    binary = cv2.adaptiveThreshold(sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    # Operaciones morfológicas para limpiar la imagen
    kernel = np.ones((1,1), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    print("Preprocesamiento completado")
    return cleaned

def detect_table_structure(image: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """
    Detecta estructuras de tabla en la imagen usando detección de líneas.
    """
    print("Detectando estructura de tabla...")
    
    # Detectar líneas horizontales
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel)
    
    # Detectar líneas verticales
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel)
    
    # Combinar líneas para encontrar intersecciones
    table_structure = cv2.add(horizontal_lines, vertical_lines)
    
    # Encontrar contornos de celdas potenciales
    contours, _ = cv2.findContours(table_structure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    cells = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Filtrar regiones muy pequeñas o muy grandes
        if 20 < w < image.shape[1] * 0.8 and 10 < h < image.shape[0] * 0.8:
            cells.append((x, y, w, h))
    
    print(f"Detectadas {len(cells)} celdas potenciales")
    return cells

def extract_text_with_enhanced_ocr(image: np.ndarray, lang='eng+spa') -> str:
    """
    Extrae texto usando configuración optimizada de OCR.
    """
    # Configuración específica para tablas
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,:-/()$%'
    
    try:
        text = pytesseract.image_to_string(image, lang=lang, config=custom_config)
        return text.strip()
    except Exception as e:
        print(f"Error en OCR: {e}")
        # Fallback sin whitelist
        try:
            text = pytesseract.image_to_string(image, lang=lang, config=r'--oem 3 --psm 6')
            return text.strip()
        except:
            return ""

def extract_table_data_from_cells(image: np.ndarray, cells: List[Tuple[int, int, int, int]]) -> List[List[str]]:
    """
    Extrae datos de texto de cada celda detectada.
    """
    print("Extrayendo datos de celdas...")
    
    cell_data = []
    for i, (x, y, w, h) in enumerate(cells):
        # Extraer región de la celda
        cell_img = image[y:y+h, x:x+w]
        
        # Aplicar OCR a la celda
        cell_text = extract_text_with_enhanced_ocr(cell_img)
        
        if cell_text:
            cell_data.append({
                'text': cell_text,
                'x': x, 'y': y, 'w': w, 'h': h
            })
    
    # Organizar celdas en filas y columnas
    if not cell_data:
        return []
    
    # Agrupar por filas (similar coordenada Y)
    cell_data.sort(key=lambda c: (c['y'], c['x']))
    
    rows = []
    current_row = []
    current_y = cell_data[0]['y']
    y_tolerance = 20  # Tolerancia para considerar misma fila
    
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
    
    print(f"Organizadas {len(rows)} filas de datos")
    return rows

def process_text_to_table(text: str) -> List[List[str]]:
    """
    Procesa texto plano para extraer estructuras tabulares.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return []
    
    # Detectar separadores comunes
    potential_rows = []
    for line in lines:
        # Intentar diferentes separadores
        separators = ['\t', '|', ';', '  ', ',']
        best_split = None
        max_parts = 1
        
        for sep in separators:
            if sep in line:
                parts = [p.strip() for p in line.split(sep) if p.strip()]
                if len(parts) > max_parts:
                    max_parts = len(parts)
                    best_split = parts
        
        if best_split and len(best_split) >= 2:
            potential_rows.append(best_split)
        elif len(line.split()) >= 3:  # Al menos 3 palabras
            potential_rows.append(line.split())
    
    return potential_rows if len(potential_rows) >= 2 else []

def ocr_image_to_tables(image_path, output_path, format_type="excel"):
    """
    Extrae tablas de una imagen usando OCR mejorado y detección de estructura.
    """
    if not os.path.exists(image_path):
        print(f"Error: El archivo {image_path} no existe.")
        return False
    
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    try:
        # Preprocesar imagen
        processed_img = preprocess_image(image_path)
        
        # Método 1: Detección de estructura de tabla
        cells = detect_table_structure(processed_img)
        table_rows = []
        
        if cells:
            table_rows = extract_table_data_from_cells(processed_img, cells)
        
        # Método 2 (fallback): OCR completo y procesamiento de texto
        if not table_rows:
            print("Fallback: Procesando texto completo...")
            full_text = extract_text_with_enhanced_ocr(processed_img)
            if full_text:
                table_rows = process_text_to_table(full_text)
        
        # Método 3 (último fallback): OCR básico línea por línea
        if not table_rows:
            print("Último fallback: OCR básico...")
            img_pil = Image.fromarray(processed_img)
            tsv = pytesseract.image_to_data(img_pil, output_type=Output.DATAFRAME, lang='eng+spa')
            tsv = tsv[tsv['text'].notnull() & (tsv['text'].str.strip() != '')]
            
            line_data = []
            for line_num, line_df in tsv.groupby('line_num'):
                row = list(line_df['text'])
                if len(row) >= 2:  # Al menos 2 elementos
                    line_data.append(row)
            
            table_rows = line_data
        
        if not table_rows:
            print("No se pudieron extraer tablas de la imagen.")
            # Crear DataFrame vacío pero con estructura
            df = pd.DataFrame(columns=['Columna1'])
        else:
            # Normalizar filas para que tengan el mismo número de columnas
            max_cols = max(len(row) for row in table_rows)
            normalized_rows = []
            for row in table_rows:
                # Rellenar filas cortas con valores vacíos
                while len(row) < max_cols:
                    row.append('')
                normalized_rows.append(row[:max_cols])  # Truncar filas largas
            
            # Crear DataFrame
            columns = [f"Columna_{i+1}" for i in range(max_cols)]
            df = pd.DataFrame(normalized_rows, columns=columns)
            
            # Limpiar datos vacíos
            df = df.replace('', pd.NA).dropna(how='all').fillna('')
        
        # Guardar resultados
        base_path = os.path.splitext(output_path)[0]
        
        if format_type == "excel" or format_type == "both":
            excel_path = base_path + ".xlsx"
            df.to_excel(excel_path, index=False)
            print(f"Archivo Excel guardado en {excel_path}")
        
        if format_type == "csv" or format_type == "both":
            csv_path = base_path + ".csv"
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"Archivo CSV guardado en {csv_path}")
        
        print(f"Total de filas: {len(df)}, Total de columnas: {len(df.columns)}")
        return len(df) > 0
        
    except Exception as e:
        print(f"Error procesando imagen: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Extrae tablas de imágenes (JPG, PNG, etc.) usando OCR y las guarda en Excel/CSV.")
    parser.add_argument("image", help="Ruta a la imagen (JPG, PNG, etc.)")
    parser.add_argument("-o", "--output", default="ocr_tablas_img.xlsx", help="Archivo de salida (sin extensión)")
    parser.add_argument("-f", "--format", default="excel", choices=["excel", "csv", "both"], help="Formato de salida")
    args = parser.parse_args()
    ocr_image_to_tables(args.image, args.output, args.format)

if __name__ == "__main__":
    main()
