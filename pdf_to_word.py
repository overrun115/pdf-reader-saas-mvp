import sys
from pdf2docx import Converter
import os

def pdf_to_word(pdf_path, docx_path=None):
    if not os.path.exists(pdf_path):
        print(f"Archivo no encontrado: {pdf_path}")
        return
    if docx_path is None:
        docx_path = os.path.splitext(pdf_path)[0] + '.docx'
    print(f"Convirtiendo {pdf_path} a {docx_path} ...")
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()
    print(f"Conversión completada: {docx_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python pdf_to_word.py <archivo.pdf> [salida.docx]")
        sys.exit(1)
    pdf_path = sys.argv[1]
    docx_path = sys.argv[2] if len(sys.argv) > 2 else None
    pdf_to_word(pdf_path, docx_path)
