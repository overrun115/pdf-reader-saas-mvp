"""
Advanced OCR Service using PaddleOCR and docTR for enhanced text extraction
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
import fitz  # PyMuPDF
import numpy as np
from PIL import Image
import io
from pathlib import Path

# OCR engines
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    PaddleOCR = None

try:
    from doctr.models import ocr_predictor
    from doctr.io import DocumentFile
    DOCTR_AVAILABLE = True
except ImportError:
    DOCTR_AVAILABLE = False
    ocr_predictor = None
    DocumentFile = None

logger = logging.getLogger(__name__)

class AdvancedOCRService:
    """
    Advanced OCR service that combines PaddleOCR and docTR for maximum accuracy
    """
    
    def __init__(self):
        self.paddle_ocr = None
        self.doctr_predictor = None
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize OCR engines"""
        try:
            if PADDLE_AVAILABLE:
                logger.info("Initializing PaddleOCR...")
                try:
                    # Simple initialization to avoid compatibility issues
                    self.paddle_ocr = PaddleOCR(lang='en')
                    logger.info("PaddleOCR initialized successfully")
                except Exception as e:
                    logger.warning(f"PaddleOCR initialization failed: {e}")
                    self.paddle_ocr = None
            else:
                logger.warning("PaddleOCR not available")
                
            if DOCTR_AVAILABLE:
                logger.info("Initializing docTR...")
                try:
                    self.doctr_predictor = ocr_predictor(pretrained=True)
                    logger.info("docTR initialized successfully")
                except Exception as e:
                    logger.warning(f"docTR initialization failed: {e}")
                    self.doctr_predictor = None
            else:
                logger.warning("docTR not available")
                
        except Exception as e:
            logger.error(f"Failed to initialize OCR engines: {e}")
    
    def detect_if_scanned(self, pdf_path: str) -> bool:
        """
        Detect if PDF is scanned (image-based) vs native (text-based)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            True if PDF appears to be scanned, False if native
        """
        try:
            doc = fitz.open(pdf_path)
            
            # Sample first few pages for analysis
            sample_pages = min(3, len(doc))
            total_text_ratio = 0
            total_image_count = 0
            
            for page_num in range(sample_pages):
                page = doc[page_num]
                
                # Calculate text density
                text_length = len(page.get_text().strip())
                page_area = page.rect.width * page.rect.height
                text_ratio = text_length / page_area if page_area > 0 else 0
                
                # Count images
                image_count = len(page.get_images())
                
                total_text_ratio += text_ratio
                total_image_count += image_count
            
            doc.close()
            
            # Heuristics for scanned detection
            avg_text_ratio = total_text_ratio / sample_pages
            avg_image_count = total_image_count / sample_pages
            
            # If very low text density and high image count = likely scanned
            is_scanned = avg_text_ratio < 0.01 and avg_image_count > 0.5
            
            logger.info(f"Document analysis: text_ratio={avg_text_ratio:.4f}, "
                       f"images_per_page={avg_image_count:.1f}, scanned={is_scanned}")
            
            return is_scanned
            
        except Exception as e:
            logger.error(f"Error detecting document type: {e}")
            return False
    
    async def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF using appropriate method based on document type
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        is_scanned = self.detect_if_scanned(pdf_path)
        
        if is_scanned:
            logger.info("Processing as scanned document with OCR")
            return await self._extract_with_ocr(pdf_path)
        else:
            logger.info("Processing as native PDF with enhanced extraction")
            return await self._extract_native_enhanced(pdf_path)
    
    async def _extract_with_ocr(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from scanned PDF using OCR engines"""
        doc = fitz.open(pdf_path)
        all_pages = []
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Extract text with available OCR engines
                page_text = await self._ocr_image(img_data, page_num)
                
                all_pages.append({
                    "page_number": page_num + 1,
                    "text": page_text.get("text", ""),
                    "elements": page_text.get("elements", []),
                    "confidence": page_text.get("confidence", 0.0),
                    "method": "ocr"
                })
                
        finally:
            doc.close()
        
        # Combine all text
        combined_text = "\n\n".join([page["text"] for page in all_pages if page["text"]])
        
        return {
            "text": combined_text,
            "pages": all_pages,
            "total_pages": len(all_pages),
            "extraction_method": "advanced_ocr",
            "is_scanned": True
        }
    
    async def _extract_native_enhanced(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from native PDF with enhancements"""
        doc = fitz.open(pdf_path)
        all_pages = []
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Native text extraction
                text = page.get_text()
                
                # Get text with formatting info
                text_dict = page.get_text("dict")
                elements = self._parse_text_elements(text_dict)
                
                all_pages.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "elements": elements,
                    "confidence": 1.0,  # Native text has high confidence
                    "method": "native"
                })
                
        finally:
            doc.close()
        
        # Combine all text
        combined_text = "\n\n".join([page["text"] for page in all_pages if page["text"]])
        
        return {
            "text": combined_text,
            "pages": all_pages,
            "total_pages": len(all_pages),
            "extraction_method": "native_enhanced",
            "is_scanned": False
        }
    
    async def _ocr_image(self, img_data: bytes, page_num: int) -> Dict[str, Any]:
        """Perform OCR on image data using available engines"""
        results = {"text": "", "elements": [], "confidence": 0.0}
        
        # Try PaddleOCR first (faster)
        if self.paddle_ocr:
            try:
                paddle_result = await self._paddle_ocr_extract(img_data)
                if paddle_result["text"]:
                    results = paddle_result
                    logger.debug(f"PaddleOCR successful for page {page_num + 1}")
            except Exception as e:
                logger.warning(f"PaddleOCR failed for page {page_num + 1}: {e}")
        
        # Try docTR if PaddleOCR failed or not available
        if not results["text"] and self.doctr_predictor:
            try:
                doctr_result = await self._doctr_extract(img_data)
                if doctr_result["text"]:
                    results = doctr_result
                    logger.debug(f"docTR successful for page {page_num + 1}")
            except Exception as e:
                logger.warning(f"docTR failed for page {page_num + 1}: {e}")
        
        return results
    
    async def _paddle_ocr_extract(self, img_data: bytes) -> Dict[str, Any]:
        """Extract text using PaddleOCR"""
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(img_data))
        img_array = np.array(image)
        
        # Run OCR
        result = self.paddle_ocr.ocr(img_array, cls=True)
        
        # Parse results
        text_lines = []
        elements = []
        total_confidence = 0
        confidence_count = 0
        
        if result and result[0]:
            for line in result[0]:
                if len(line) >= 2:
                    bbox = line[0]  # Bounding box coordinates
                    text_info = line[1]  # (text, confidence)
                    
                    if len(text_info) >= 2:
                        text = text_info[0]
                        confidence = text_info[1]
                        
                        text_lines.append(text)
                        elements.append({
                            "text": text,
                            "bbox": bbox,
                            "confidence": confidence,
                            "engine": "paddleocr"
                        })
                        
                        total_confidence += confidence
                        confidence_count += 1
        
        avg_confidence = total_confidence / confidence_count if confidence_count > 0 else 0
        
        return {
            "text": "\n".join(text_lines),
            "elements": elements,
            "confidence": avg_confidence
        }
    
    async def _doctr_extract(self, img_data: bytes) -> Dict[str, Any]:
        """Extract text using docTR"""
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(img_data))
        
        # Run OCR
        result = self.doctr_predictor([np.array(image)])
        
        # Parse results
        text_lines = []
        elements = []
        
        if result and len(result.pages) > 0:
            page = result.pages[0]
            
            for block in page.blocks:
                for line in block.lines:
                    line_text = ""
                    line_confidence = 0
                    word_count = 0
                    
                    for word in line.words:
                        line_text += word.value + " "
                        line_confidence += word.confidence
                        word_count += 1
                    
                    if line_text.strip():
                        text_lines.append(line_text.strip())
                        avg_confidence = line_confidence / word_count if word_count > 0 else 0
                        
                        elements.append({
                            "text": line_text.strip(),
                            "bbox": line.geometry,
                            "confidence": avg_confidence,
                            "engine": "doctr"
                        })
        
        # Calculate overall confidence
        total_confidence = sum(elem["confidence"] for elem in elements)
        avg_confidence = total_confidence / len(elements) if elements else 0
        
        return {
            "text": "\n".join(text_lines),
            "elements": elements,
            "confidence": avg_confidence
        }
    
    def _parse_text_elements(self, text_dict: Dict) -> List[Dict[str, Any]]:
        """Parse PyMuPDF text dictionary into structured elements"""
        elements = []
        
        for block in text_dict.get("blocks", []):
            if "lines" in block:  # Text block
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        if span.get("text", "").strip():
                            elements.append({
                                "text": span["text"],
                                "bbox": span.get("bbox", [0, 0, 0, 0]),
                                "font": span.get("font", ""),
                                "size": span.get("size", 12),
                                "flags": span.get("flags", 0),
                                "confidence": 1.0,
                                "engine": "native"
                            })
        
        return elements
    
    def get_available_engines(self) -> Dict[str, bool]:
        """Get status of available OCR engines"""
        return {
            "paddleocr": PADDLE_AVAILABLE and self.paddle_ocr is not None,
            "doctr": DOCTR_AVAILABLE and self.doctr_predictor is not None
        }