import os
import sys
import argparse
import pandas as pd
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output


def ocr_pdf_to_tables(pdf_path, output_path, format_type="excel"):
    """
    Extrae tablas de un PDF escaneado usando OCR y guarda como Excel/CSV.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: El archivo {pdf_path} no existe.")
        return False
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    # Convertir PDF a imágenes
    images = convert_from_path(pdf_path)
    all_rows = []
    for i, img in enumerate(images):
        print(f"Procesando página {i+1}...")
        # OCR con pytesseract en modo TSV
        tsv = pytesseract.image_to_data(img, output_type=Output.DATAFRAME, lang='eng')
        # Filtrar solo líneas con texto
        tsv = tsv[tsv['text'].notnull() & (tsv['text'].str.strip() != '')]
        # Agrupar por línea
        for line_num, line_df in tsv.groupby('line_num'):
            row = list(line_df['text'])
            all_rows.append(row)
    # Convertir a DataFrame (rellenar filas cortas)
    max_cols = max(len(row) for row in all_rows) if all_rows else 0
    df = pd.DataFrame([row + [None]*(max_cols-len(row)) for row in all_rows], columns=[f"col{i+1}" for i in range(max_cols)])
    # Guardar
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


def ocr_image_to_tables(image_path, output_path, format_type="excel"):
    """
    Extrae tablas de una imagen (JPG, PNG, etc.) usando OCR y guarda como Excel/CSV.
    """
    if not os.path.exists(image_path):
        print(f"Error: El archivo {image_path} no existe.")
        return False
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    img = Image.open(image_path)
    tsv = pytesseract.image_to_data(img, output_type=Output.DATAFRAME, lang='eng')
    tsv = tsv[tsv['text'].notnull() & (tsv['text'].str.strip() != '')]
    all_rows = []
    for line_num, line_df in tsv.groupby('line_num'):
        row = list(line_df['text'])
        all_rows.append(row)
    max_cols = max(len(row) for row in all_rows) if all_rows else 0
    df = pd.DataFrame([row + [None]*(max_cols-len(row)) for row in all_rows], columns=[f"col{i+1}" for i in range(max_cols)])
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


def main():
    parser = argparse.ArgumentParser(description="Extrae tablas de PDFs escaneados o imágenes usando OCR y las guarda en Excel/CSV.")
    parser.add_argument("file", help="Ruta al archivo PDF o imagen (JPG, PNG, etc.)")
    parser.add_argument("-o", "--output", default="ocr_tablas.xlsx", help="Archivo de salida (sin extensión)")
    parser.add_argument("-f", "--format", default="excel", choices=["excel", "csv", "both"], help="Formato de salida")
    args = parser.parse_args()
    ext = os.path.splitext(args.file)[1].lower()
    if ext in [".pdf"]:
        ocr_pdf_to_tables(args.file, args.output, args.format)
    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
        ocr_image_to_tables(args.file, args.output, args.format)
    else:
        print("Formato de archivo no soportado. Usa PDF o imagen (JPG, PNG, BMP, TIFF).")

if __name__ == "__main__":
    main()
