import fitz  # PyMuPDF
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
from typing import List, Dict, Any
from PIL import Image
import numpy as np
import io
import tempfile
import os

class DoctrLayoutOCR:
    def __init__(self, model_name: str = 'db_resnet50', reco_name: str = 'crnn_vgg16_bn'):
        # Puedes cambiar los modelos por otros soportados por doctr
        self.model = ocr_predictor(det_arch=model_name, reco_arch=reco_name, pretrained=True)

    def pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """Renderiza cada página del PDF a una imagen PIL"""
        doc = fitz.open(pdf_path)
        images = []
        try:
            for page in doc:
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                images.append(img)
        finally:
            doc.close()
        return images

    def analyze_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extrae texto y layout de cada página usando DocTR (procesa todas las páginas en lote)"""
        images = self.pdf_to_images(pdf_path)
        temp_files = []
        try:
            # Guardar cada imagen como PNG temporal y recolectar rutas
            for idx, img in enumerate(images):
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                img.save(tmp, format='PNG')
                tmp.close()
                temp_files.append(tmp.name)
            doc = DocumentFile.from_images(temp_files)
            out = self.model(doc)
            results = []
            for idx, page in enumerate(out.pages):
                # Manejo robusto de la exportación de texto
                page_export = page.export()
                if isinstance(page_export, dict):
                    text = page_export.get('value') or page_export.get('text') or str(page_export)
                else:
                    text = str(page_export)
                page_result = {
                    'page_number': idx + 1,
                    'blocks': page.blocks,
                    'text': text,
                }
                results.append(page_result)
            return results
        finally:
            # Limpiar archivos temporales
            for f in temp_files:
                try:
                    os.remove(f)
                except Exception:
                    pass
