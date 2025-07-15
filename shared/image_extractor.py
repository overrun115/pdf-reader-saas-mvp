import os
import pandas as pd
from PIL import Image
import pytesseract
from pytesseract import Output

def extract_tables_from_image(image_path, output_path, format_type="excel"):
    """
    Extrae tablas de una imagen (JPG, PNG, etc.) usando OCR y guarda como Excel/CSV.
    """
    if not os.path.exists(image_path):
        print(f"Error: El archivo {image_path} no existe.")
        return False
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
