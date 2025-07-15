import sys
import argparse
from docling.document_converter import DocumentConverter
import os
import pandas as pd
from typing import List, Set
import re
import itertools


def extract_tables_from_pdf(pdf_path, output_path):
    try:
        # Verificar que el archivo PDF existe
        if not os.path.exists(pdf_path):
            print(f"Error: El archivo {pdf_path} no existe.")
            return False
            
        # Crea el directorio de salida si no existe
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        doc = result.document
        tables = getattr(doc, 'tables', [])
        
        if not tables:
            print("No se encontraron tablas en el PDF.")
            return False
            
        print(f"Se encontraron {len(tables)} tablas en el PDF.")
        
        # Extraer todas las tablas y normalizar columnas
        all_dfs = []
        reference_columns = None
        
        for idx, table in enumerate(tables):
            try:
                df = table.export_to_dataframe()
                if df.empty:
                    print(f"Tabla {idx + 1} está vacía, se omite.")
                    continue
                    
                # Limpiar nombres de columnas (eliminar espacios extra)
                df.columns = [str(col).strip() for col in df.columns]
                
                # Si es la primera tabla con nombres descriptivos, usarla como referencia
                if reference_columns is None and not all(col.isdigit() for col in df.columns):
                    reference_columns = list(df.columns)
                    print(f"Tabla {idx + 1} (referencia): {len(df)} filas, columnas: {reference_columns}")
                    all_dfs.append((idx, df))
                    continue
                
                # Si las columnas son números, mapear a las columnas de referencia
                if reference_columns and all(col.isdigit() for col in df.columns):
                    # Crear mapeo basado en el orden y número de columnas
                    if len(df.columns) == len(reference_columns):
                        column_mapping = dict(zip(df.columns, reference_columns))
                        df = df.rename(columns=column_mapping)
                        print(f"Tabla {idx + 1} (mapeada): {len(df)} filas, columnas mapeadas de {list(column_mapping.keys())} a {reference_columns}")
                    else:
                        print(f"Tabla {idx + 1}: No se puede mapear - diferentes números de columnas ({len(df.columns)} vs {len(reference_columns)})")
                        print(f"Columnas actuales: {list(df.columns)}")
                else:
                    print(f"Tabla {idx + 1}: {len(df)} filas, columnas: {list(df.columns)}")
                
                all_dfs.append((idx, df))
                
            except Exception as e:
                print(f"Error procesando tabla {idx + 1}: {e}")
                continue
        
        if not all_dfs:
            print("No se pudieron procesar tablas válidas.")
            return False
            
        # Obtener todas las columnas únicas después del mapeo
        all_columns: Set[str] = set()
        for idx, df in all_dfs:
            all_columns.update(df.columns)
        
        # Usar columnas de referencia si están disponibles, sino usar todas las únicas
        if reference_columns:
            unified_columns = reference_columns
            print(f"Usando columnas de referencia: {unified_columns}")
        else:
            unified_columns = sorted(list(all_columns))
            print(f"Columnas unificadas: {unified_columns}")
        
        # Normalizar todas las tablas para que tengan las mismas columnas
        normalized_dfs = []
        for idx, df in all_dfs:
            # Crear DataFrame con todas las columnas, rellenando con NaN las faltantes
            normalized_df = df.reindex(columns=unified_columns, fill_value=None)
            normalized_dfs.append(normalized_df)
        
        # Concatenar todas las tablas normalizadas
        df_final = pd.concat(normalized_dfs, ignore_index=True, sort=False)
        
        # Post-procesar para dividir filas fusionadas (producto cartesiano)
        df_final = split_rows_with_multiple_values(df_final)
        
        # Guardar en el formato especificado
        return save_dataframe(df_final, output_path)
        
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {pdf_path}")
        return False
    except PermissionError:
        print(f"Error: Sin permisos para leer {pdf_path} o escribir en {output_path}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False


def save_dataframe(df, output_path, format_type="excel"):
    """
    Guardar DataFrame en el formato especificado.
    format_type: 'excel', 'csv', o 'both'
    """
    try:
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
        return True
        
    except Exception as e:
        print(f"Error al guardar archivo: {e}")
        return False


def extract_tables_with_format(pdf_path, output_path, format_type="excel"):
    """Versión extendida que acepta tipo de formato"""
    try:
        # Verificar que el archivo PDF existe
        if not os.path.exists(pdf_path):
            print(f"Error: El archivo {pdf_path} no existe.")
            return False
            
        # Crea el directorio de salida si no existe
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        doc = result.document
        tables = getattr(doc, 'tables', [])
        
        if not tables:
            print("No se encontraron tablas en el PDF.")
            return False
            
        print(f"Se encontraron {len(tables)} tablas en el PDF.")
        
        # Extraer todas las tablas y normalizar columnas
        all_dfs = []
        reference_columns = None
        
        for idx, table in enumerate(tables):
            try:
                df = table.export_to_dataframe()
                if df.empty:
                    print(f"Tabla {idx + 1} está vacía, se omite.")
                    continue
                    
                # Limpiar nombres de columnas (eliminar espacios extra)
                df.columns = [str(col).strip() for col in df.columns]
                
                # Si es la primera tabla con nombres descriptivos, usarla como referencia
                if reference_columns is None and not all(col.isdigit() for col in df.columns):
                    reference_columns = list(df.columns)
                    print(f"Tabla {idx + 1} (referencia): {len(df)} filas, columnas: {reference_columns}")
                    all_dfs.append((idx, df))
                    continue
                
                # Si las columnas son números, mapear a las columnas de referencia
                if reference_columns and all(col.isdigit() for col in df.columns):
                    # Crear mapeo basado en el orden y número de columnas
                    if len(df.columns) == len(reference_columns):
                        column_mapping = dict(zip(df.columns, reference_columns))
                        df = df.rename(columns=column_mapping)
                        print(f"Tabla {idx + 1} (mapeada): {len(df)} filas, columnas mapeadas de {list(column_mapping.keys())} a {reference_columns}")
                    else:
                        print(f"Tabla {idx + 1}: No se puede mapear - diferentes números de columnas ({len(df.columns)} vs {len(reference_columns)})")
                        print(f"Columnas actuales: {list(df.columns)}")
                else:
                    print(f"Tabla {idx + 1}: {len(df)} filas, columnas: {list(df.columns)}")
                
                all_dfs.append((idx, df))
                
            except Exception as e:
                print(f"Error procesando tabla {idx + 1}: {e}")
                continue
        
        if not all_dfs:
            print("No se pudieron procesar tablas válidas.")
            return False
            
        # Obtener todas las columnas únicas después del mapeo
        all_columns: Set[str] = set()
        for idx, df in all_dfs:
            all_columns.update(df.columns)
        
        # Usar columnas de referencia si están disponibles, sino usar todas las únicas
        if reference_columns:
            unified_columns = reference_columns
            print(f"Usando columnas de referencia: {unified_columns}")
        else:
            unified_columns = sorted(list(all_columns))
            print(f"Columnas unificadas: {unified_columns}")
        
        # Normalizar todas las tablas para que tengan las mismas columnas
        normalized_dfs = []
        for idx, df in all_dfs:
            # Crear DataFrame con todas las columnas, rellenando con NaN las faltantes
            normalized_df = df.reindex(columns=unified_columns, fill_value=None)
            normalized_dfs.append(normalized_df)
        
        # Concatenar todas las tablas normalizadas
        df_final = pd.concat(normalized_dfs, ignore_index=True, sort=False)
        
        # Post-procesar para dividir filas fusionadas (producto cartesiano)
        df_final = split_rows_with_multiple_values(df_final)
        
        # Guardar en el formato especificado
        return save_dataframe(df_final, output_path, format_type)
        
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {pdf_path}")
        return False
    except PermissionError:
        print(f"Error: Sin permisos para leer {pdf_path} o escribir en {output_path}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False


def split_rows_with_multiple_values(df, delimiters=None):
    """
    Divide filas donde una o más celdas contienen múltiples valores separados por delimitadores.
    Genera todas las combinaciones posibles (producto cartesiano) de los valores detectados.
    """
    if delimiters is None:
        delimiters = [r'\s{2,}', r'\t', r'\s\|\s', r'\|', r',', r';', r'\s']  # dobles espacios, tab, pipe, coma, punto y coma, espacio simple
    pattern = re.compile('|'.join(delimiters))
    new_rows = []
    for _, row in df.iterrows():
        split_cells = []
        for val in row:
            if isinstance(val, str):
                parts = [p for p in pattern.split(val) if p.strip() != '']
                split_cells.append(parts if parts else [None])
            else:
                split_cells.append([val])
        # Generar todas las combinaciones posibles
        for combination in itertools.product(*split_cells):
            new_rows.append(combination)
    return pd.DataFrame(new_rows, columns=df.columns)


def process_multiple_pdfs(pdf_files, output_dir="."):
    """Procesa múltiples archivos PDF y genera un Excel por cada uno."""
    os.makedirs(output_dir, exist_ok=True)
    results = []
    
    for pdf_file in pdf_files:
        if not os.path.exists(pdf_file):
            print(f"Error: El archivo {pdf_file} no existe.")
            continue
            
        # Generar nombre de salida basado en el nombre del PDF
        pdf_name = os.path.splitext(os.path.basename(pdf_file))[0]
        output_file = os.path.join(output_dir, f"{pdf_name}_tablas.xlsx")
        
        print(f"\n=== Procesando {pdf_file} ===")
        success = extract_tables_from_pdf(pdf_file, output_file)
        results.append((pdf_file, output_file, success))
        
    # Resumen de resultados
    print(f"\n=== Resumen ===")
    for pdf_file, output_file, success in results:
        status = "✓ Exitoso" if success else "✗ Falló"
        print(f"{status}: {os.path.basename(pdf_file)} → {os.path.basename(output_file)}")
    
    return all(success for _, _, success in results)


def main():
    parser = argparse.ArgumentParser(description="Extrae tablas de uno o más PDFs usando Docling y las guarda en archivos Excel.")
    parser.add_argument("pdfs", nargs="+", help="Ruta a uno o más archivos PDF")
    parser.add_argument("-o", "--output-dir", default=".", help="Directorio de salida para los archivos Excel (default: directorio actual)")
    args = parser.parse_args()
    
    if len(args.pdfs) == 1:
        # Modo compatible con versión anterior (un solo PDF)
        pdf_name = os.path.splitext(os.path.basename(args.pdfs[0]))[0]
        output_file = os.path.join(args.output_dir, f"{pdf_name}_tablas.xlsx")
        success = extract_tables_from_pdf(args.pdfs[0], output_file)
    else:
        # Modo múltiples PDFs
        success = process_multiple_pdfs(args.pdfs, args.output_dir)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
