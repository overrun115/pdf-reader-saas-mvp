#!/usr/bin/env python3
"""
Advanced OCR and NLP Service - Múltiples engines de OCR con post-procesamiento inteligente
Parte de la expansión de inteligencia documental
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import fitz  # PyMuPDF

# OCR Engines
import pytesseract
import easyocr
# from paddleocr import PaddleOCR  # Temporarily disabled for Docker compatibility

# NLP Libraries
import spacy
import nltk
from langdetect import detect, DetectorFactory
from textblob import TextBlob
import re

# Machine Learning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

DetectorFactory.seed = 0  # For consistent language detection

@dataclass
class OCRResult:
    """Resultado de OCR con metadatos de confianza"""
    text: str
    confidence: float
    engine: str
    language: str
    bbox: Optional[Tuple[int, int, int, int]] = None
    word_confidences: Optional[List[float]] = None

@dataclass
class TextElement:
    """Elemento de texto procesado con análisis NLP"""
    text: str
    bbox: Tuple[int, int, int, int]
    confidence: float
    element_type: str  # 'paragraph', 'title', 'table_cell', 'list_item'
    language: str
    entities: List[Dict[str, Any]]
    corrected_text: Optional[str] = None

class AdvancedOCRNLPService:
    """
    Servicio avanzado de OCR con múltiples engines y post-procesamiento NLP
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize OCR Engines
        self._init_ocr_engines()
        
        # Initialize NLP Models
        self._init_nlp_models()
        
        # Configuration
        self.min_confidence_threshold = 0.6
        self.ensemble_weights = {
            'tesseract': 0.3,
            'easyocr': 0.4,
            'paddleocr': 0.3
        }
        
    def _init_ocr_engines(self):
        """Inicializar engines de OCR"""
        try:
            # EasyOCR - Soporta múltiples idiomas
            self.easyocr_reader = easyocr.Reader(['en', 'es', 'fr', 'de', 'it', 'pt'])
            self.logger.info("EasyOCR initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize EasyOCR: {e}")
            self.easyocr_reader = None
            
        try:
            # PaddleOCR - Excelente para layouts complejos (temporarily disabled)
            # self.paddleocr_reader = PaddleOCR(
            #     use_angle_cls=True,
            #     lang='en',
            #     show_log=False
            # )
            self.paddleocr_reader = None
            self.logger.info("PaddleOCR temporarily disabled for Docker compatibility")
        except Exception as e:
            self.logger.error(f"Failed to initialize OCR engines: {e}")
            self.paddleocr_reader = None
    
    def _init_nlp_models(self):
        """Inicializar modelos NLP"""
        try:
            # Load spaCy model for NER and text processing
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.logger.warning("spaCy en_core_web_sm model not found. Installing...")
                os.system("python -m spacy download en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
                
            self.logger.info("spaCy model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize NLP models: {e}")
            self.nlp = None
    
    async def extract_text_with_multiple_engines(
        self,
        image: np.ndarray,
        use_ensemble: bool = True
    ) -> List[OCRResult]:
        """
        Extrae texto usando múltiples engines de OCR
        """
        results = []
        
        # Tesseract OCR
        tesseract_result = await self._run_tesseract_ocr(image)
        if tesseract_result:
            results.append(tesseract_result)
            
        # EasyOCR
        if self.easyocr_reader:
            easyocr_result = await self._run_easyocr(image)
            if easyocr_result:
                results.append(easyocr_result)
                
        # PaddleOCR
        if self.paddleocr_reader:
            paddleocr_result = await self._run_paddleocr(image)
            if paddleocr_result:
                results.append(paddleocr_result)
        
        if use_ensemble and len(results) > 1:
            # Crear resultado ensemble
            ensemble_result = self._create_ensemble_result(results)
            results.append(ensemble_result)
            
        return results
    
    async def _run_tesseract_ocr(self, image: np.ndarray) -> Optional[OCRResult]:
        """Ejecutar Tesseract OCR"""
        try:
            # Configuración optimizada para Tesseract
            config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ .,;:!?()-'
            
            # Extraer texto con confianzas
            data = pytesseract.image_to_data(
                image, 
                output_type=pytesseract.Output.DICT,
                config=config
            )
            
            # Combinar texto y calcular confianza promedio
            words = []
            confidences = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:
                    words.append(data['text'][i])
                    confidences.append(int(data['conf'][i]))
            
            if not words:
                return None
                
            text = ' '.join(words)
            avg_confidence = sum(confidences) / len(confidences) / 100.0
            
            # Detectar idioma
            try:
                language = detect(text) if len(text) > 10 else 'en'
            except:
                language = 'en'
            
            return OCRResult(
                text=text,
                confidence=avg_confidence,
                engine='tesseract',
                language=language,
                word_confidences=[c/100.0 for c in confidences]
            )
            
        except Exception as e:
            self.logger.error(f"Tesseract OCR failed: {e}")
            return None
    
    async def _run_easyocr(self, image: np.ndarray) -> Optional[OCRResult]:
        """Ejecutar EasyOCR"""
        try:
            results = self.easyocr_reader.readtext(image)
            
            if not results:
                return None
            
            # Combinar todos los textos detectados
            texts = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                if confidence > 0.1:  # Filtrar resultados de muy baja confianza
                    texts.append(text)
                    confidences.append(confidence)
            
            if not texts:
                return None
                
            combined_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences)
            
            # Detectar idioma
            try:
                language = detect(combined_text) if len(combined_text) > 10 else 'en'
            except:
                language = 'en'
            
            return OCRResult(
                text=combined_text,
                confidence=avg_confidence,
                engine='easyocr',
                language=language,
                word_confidences=confidences
            )
            
        except Exception as e:
            self.logger.error(f"EasyOCR failed: {e}")
            return None
    
    async def _run_paddleocr(self, image: np.ndarray) -> Optional[OCRResult]:
        """Ejecutar PaddleOCR (temporarily disabled)"""
        if self.paddleocr_reader is None:
            return None
        try:
            results = self.paddleocr_reader.ocr(image, cls=True)
            
            if not results or not results[0]:
                return None
            
            # Extraer texto y confianzas
            texts = []
            confidences = []
            
            for line in results[0]:
                if line:
                    bbox, (text, confidence) = line
                    if confidence > 0.1:
                        texts.append(text)
                        confidences.append(confidence)
            
            if not texts:
                return None
                
            combined_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences)
            
            # Detectar idioma
            try:
                language = detect(combined_text) if len(combined_text) > 10 else 'en'
            except:
                language = 'en'
            
            return OCRResult(
                text=combined_text,
                confidence=avg_confidence,
                engine='paddleocr',
                language=language,
                word_confidences=confidences
            )
            
        except Exception as e:
            self.logger.error(f"PaddleOCR failed: {e}")
            return None
    
    def _create_ensemble_result(self, results: List[OCRResult]) -> OCRResult:
        """
        Crear resultado ensemble combinando múltiples engines OCR
        """
        if not results:
            return None
            
        # Calcular pesos basados en confianza y configuración
        weighted_texts = []
        total_weight = 0
        
        for result in results:
            engine_weight = self.ensemble_weights.get(result.engine, 0.33)
            confidence_weight = result.confidence
            final_weight = engine_weight * confidence_weight
            
            weighted_texts.append((result.text, final_weight))
            total_weight += final_weight
        
        # Seleccionar el texto con mayor peso o combinar inteligentemente
        if weighted_texts:
            # Por ahora, seleccionar el de mayor peso
            best_text = max(weighted_texts, key=lambda x: x[1])[0]
            
            # Calcular confianza ensemble
            avg_confidence = sum(r.confidence for r in results) / len(results)
            
            # Detectar idioma del mejor resultado
            try:
                language = detect(best_text) if len(best_text) > 10 else 'en'
            except:
                language = 'en'
            
            return OCRResult(
                text=best_text,
                confidence=avg_confidence,
                engine='ensemble',
                language=language
            )
        
        return results[0]  # Fallback al primer resultado
    
    async def post_process_with_nlp(self, ocr_result: OCRResult) -> OCRResult:
        """
        Post-procesamiento NLP para mejorar la calidad del texto extraído
        """
        if not self.nlp or not ocr_result.text:
            return ocr_result
        
        try:
            # Corrección básica de texto
            corrected_text = self._correct_common_ocr_errors(ocr_result.text)
            
            # Análisis con spaCy
            doc = self.nlp(corrected_text)
            
            # Extraer entidades nombradas
            entities = []
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 0.8  # spaCy no proporciona confianza directa
                })
            
            # Crear resultado mejorado
            improved_result = OCRResult(
                text=corrected_text,
                confidence=min(ocr_result.confidence * 1.1, 1.0),  # Mejora ligera por corrección
                engine=f"{ocr_result.engine}_nlp",
                language=ocr_result.language,
                bbox=ocr_result.bbox,
                word_confidences=ocr_result.word_confidences
            )
            
            return improved_result
            
        except Exception as e:
            self.logger.error(f"NLP post-processing failed: {e}")
            return ocr_result
    
    def _correct_common_ocr_errors(self, text: str) -> str:
        """
        Corregir errores comunes de OCR
        """
        corrections = {
            # Números comúnmente mal reconocidos
            r'\b0\b': 'O',  # Cero por O
            r'\b1\b': 'I',  # Uno por I (en contexto)
            r'\b5\b': 'S',  # Cinco por S (en contexto)
            
            # Caracteres especiales
            r'([a-z])1([a-z])': r'\1l\2',  # 1 por l en medio de palabras
            r'([a-z])0([a-z])': r'\1o\2',  # 0 por o en medio de palabras
            
            # Espacios extra
            r'\s+': ' ',  # Múltiples espacios por uno
            r'([a-z])\s+([a-z])': r'\1\2',  # Espacios dentro de palabras
            
            # Puntuación
            r'\s+([.,;:!?])': r'\1',  # Espacios antes de puntuación
        }
        
        corrected = text
        for pattern, replacement in corrections.items():
            corrected = re.sub(pattern, replacement, corrected)
        
        return corrected.strip()
    
    async def analyze_text_elements(
        self,
        ocr_results: List[OCRResult],
        image_shape: Tuple[int, int]
    ) -> List[TextElement]:
        """
        Analizar elementos de texto para clasificación automática
        """
        elements = []
        
        for ocr_result in ocr_results:
            if not ocr_result.text.strip():
                continue
                
            # Clasificar tipo de elemento basado en características
            element_type = self._classify_text_element(ocr_result.text)
            
            # Extraer entidades si tenemos NLP disponible
            entities = []
            if self.nlp:
                try:
                    doc = self.nlp(ocr_result.text)
                    entities = [
                        {
                            'text': ent.text,
                            'label': ent.label_,
                            'start': ent.start_char,
                            'end': ent.end_char
                        }
                        for ent in doc.ents
                    ]
                except:
                    pass
            
            element = TextElement(
                text=ocr_result.text,
                bbox=ocr_result.bbox or (0, 0, image_shape[1], image_shape[0]),
                confidence=ocr_result.confidence,
                element_type=element_type,
                language=ocr_result.language,
                entities=entities,
                corrected_text=None
            )
            
            elements.append(element)
        
        return elements
    
    def _classify_text_element(self, text: str) -> str:
        """
        Clasificar tipo de elemento de texto
        """
        text_clean = text.strip()
        
        # Títulos (texto en mayúsculas, corto)
        if text_clean.isupper() and len(text_clean) < 100:
            return 'title'
        
        # Listas (comienzan con números o viñetas)
        if re.match(r'^\s*[-•*]\s+', text_clean) or re.match(r'^\s*\d+\.\s+', text_clean):
            return 'list_item'
        
        # Celdas de tabla (texto corto, posiblemente números)
        if len(text_clean) < 50 and (text_clean.replace('.', '').replace(',', '').isdigit() or '$' in text_clean):
            return 'table_cell'
        
        # Por defecto, párrafo
        return 'paragraph'
    
    async def process_pdf_page(
        self,
        pdf_path: str,
        page_num: int,
        enhance_quality: bool = True
    ) -> Dict[str, Any]:
        """
        Procesar una página de PDF con OCR avanzado y análisis NLP
        """
        try:
            # Abrir PDF y extraer página como imagen
            doc = fitz.open(pdf_path)
            page = doc[page_num]
            
            # Convertir a imagen con alta resolución
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom para mejor calidad
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Cargar imagen con OpenCV
            img_array = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if enhance_quality:
                image = self._enhance_image_quality(image)
            
            # Ejecutar OCR con múltiples engines
            ocr_results = await self.extract_text_with_multiple_engines(image)
            
            # Post-procesamiento NLP
            improved_results = []
            for result in ocr_results:
                improved_result = await self.post_process_with_nlp(result)
                improved_results.append(improved_result)
            
            # Analizar elementos de texto
            text_elements = await self.analyze_text_elements(
                improved_results,
                image.shape[:2]
            )
            
            doc.close()
            
            return {
                'page_number': page_num,
                'ocr_results': [
                    {
                        'text': r.text,
                        'confidence': r.confidence,
                        'engine': r.engine,
                        'language': r.language,
                        'bbox': r.bbox
                    }
                    for r in improved_results
                ],
                'text_elements': [
                    {
                        'text': elem.text,
                        'bbox': elem.bbox,
                        'confidence': elem.confidence,
                        'type': elem.element_type,
                        'language': elem.language,
                        'entities': elem.entities
                    }
                    for elem in text_elements
                ],
                'processing_info': {
                    'engines_used': [r.engine for r in improved_results],
                    'avg_confidence': sum(r.confidence for r in improved_results) / len(improved_results) if improved_results else 0,
                    'total_elements': len(text_elements)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error processing PDF page {page_num}: {e}")
            return {
                'page_number': page_num,
                'error': str(e),
                'ocr_results': [],
                'text_elements': [],
                'processing_info': {
                    'engines_used': [],
                    'avg_confidence': 0,
                    'total_elements': 0
                }
            }
    
    def _enhance_image_quality(self, image: np.ndarray) -> np.ndarray:
        """
        Mejorar calidad de imagen para mejor OCR
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Reducir ruido
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Mejorar contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Binarización adaptativa
        binary = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Convertir de vuelta a BGR para compatibilidad
        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del servicio de OCR
        """
        return {
            'available_engines': {
                'tesseract': True,
                'easyocr': self.easyocr_reader is not None,
                'paddleocr': self.paddleocr_reader is not None
            },
            'nlp_available': self.nlp is not None,
            'supported_languages': ['en', 'es', 'fr', 'de', 'it', 'pt'],
            'min_confidence_threshold': self.min_confidence_threshold,
            'ensemble_weights': self.ensemble_weights
        }