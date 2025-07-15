import os
import sys
import argparse
import pandas as pd
from docling.document_converter import DocumentConverter

def docling_ocr_pdf_to_tables(pdf_path, output_path, format_type="excel"):
    """
    Extrae tablas de un PDF (digital o escaneado) usando Docling (con OCR si es necesario) y guarda como Excel/CSV.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: El archivo {pdf_path} no existe.")
        return False
    # Si output_path es un archivo (sin carpeta), no usar dirname
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc = result.document
    tables = getattr(doc, 'tables', [])
    if not tables:
        print("No se encontraron tablas en el PDF.")
        return False
    print(f"Se encontraron {len(tables)} tablas en el PDF.")
    all_dfs = []
    for idx, table in enumerate(tables):
        try:
            df = table.export_to_dataframe()
            if df is None or df.empty:
                print(f"Tabla {idx + 1} está vacía, se omite.")
                continue
            df.columns = [str(col).strip() for col in df.columns]
            print(f"Tabla {idx + 1}: {len(df)} filas, columnas: {list(df.columns)}")
            all_dfs.append(df)
        except Exception as e:
            print(f"Error procesando tabla {idx + 1}: {e}")
            continue
    if not all_dfs:
        print("No se pudieron procesar tablas válidas.")
        return False
    df_final = pd.concat(all_dfs, ignore_index=True, sort=False)
    base_path = os.path.splitext(output_path)[0]
    if format_type == "excel" or format_type == "both":
        excel_path = base_path + ".xlsx"
        df_final.to_excel(excel_path, index=False)
        print(f"Archivo Excel guardado en {excel_path}")
    if format_type == "csv" or format_type == "both":
        csv_path = base_path + ".csv"
        df_final.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"Archivo CSV guardado en {csv_path}")
    print(f"Total de filas: {len(df_final)}, Total de columnas: {len(df_final.columns)}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Extrae tablas de PDFs (digitales o escaneados) usando Docling (OCR automático) y las guarda en Excel/CSV.")
    parser.add_argument("pdf", help="Ruta al archivo PDF")
    parser.add_argument("-o", "--output", default="docling_ocr_tablas.xlsx", help="Archivo de salida (sin extensión)")
    parser.add_argument("-f", "--format", default="excel", choices=["excel", "csv", "both"], help="Formato de salida")
    args = parser.parse_args()
    docling_ocr_pdf_to_tables(args.pdf, args.output, args.format)

if __name__ == "__main__":
    main()
