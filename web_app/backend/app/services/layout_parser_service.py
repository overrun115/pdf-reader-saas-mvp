"""
Enhanced Layout Parser Service using LayoutParser for advanced document structure detection
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
import fitz  # PyMuPDF
import numpy as np
from PIL import Image
import io
from pathlib import Path

# LayoutParser imports
try:
    import layoutparser as lp
    LAYOUTPARSER_AVAILABLE = True
except ImportError:
    LAYOUTPARSER_AVAILABLE = False
    lp = None

# PDF to image conversion
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    convert_from_path = None

logger = logging.getLogger(__name__)

class LayoutParserService:
    """
    Enhanced layout analysis service using LayoutParser for document structure detection
    """
    
    def __init__(self):
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize LayoutParser model"""
        if not LAYOUTPARSER_AVAILABLE:
            logger.warning("LayoutParser not available")
            return
        
        try:
            logger.info("Checking LayoutParser capabilities...")
            
            # Check if detectron2 models are available
            if hasattr(lp, 'Detectron2LayoutModel'):
                logger.info("Initializing LayoutParser with Detectron2...")
                
                # Use PubLayNet model for general document layout
                config_path = 'lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config'
                model_path = 'lp://PubLayNet/faster_rcnn_R_50_FPN_3x/model'
                
                self.model = lp.Detectron2LayoutModel(
                    config_path=config_path,
                    model_path=model_path,
                    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.7],
                    label_map={
                        0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"
                    }
                )
                
                logger.info("LayoutParser with Detectron2 initialized successfully")
            else:
                logger.warning("Detectron2 not available, LayoutParser will use basic features")
                self.model = "basic"  # Indicate basic mode
            
        except Exception as e:
            logger.warning(f"LayoutParser model initialization failed: {e}")
            logger.info("Will use basic LayoutParser features without deep learning models")
            self.model = "basic"
    
    def is_available(self) -> bool:
        """Check if LayoutParser is available and initialized"""
        return LAYOUTPARSER_AVAILABLE and self.model is not None
    
    def has_advanced_model(self) -> bool:
        """Check if advanced AI model (Detectron2) is available"""
        return self.model is not None and self.model != "basic"
    
    async def analyze_document_layout(self, pdf_path: str) -> Dict[str, Any]:
        """
        Analyze document layout using LayoutParser
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing layout analysis results
        """
        if not self.is_available():
            logger.warning("LayoutParser not available, using fallback analysis")
            return await self._fallback_analysis(pdf_path)
        
        try:
            # Convert PDF to images
            images = await self._pdf_to_images(pdf_path)
            
            all_pages_layout = []
            
            for page_num, image in enumerate(images):
                try:
                    # Analyze layout for this page
                    page_layout = await self._analyze_page_layout(image, page_num + 1)
                    all_pages_layout.append(page_layout)
                    
                except Exception as e:
                    logger.warning(f"Layout analysis failed for page {page_num + 1}: {e}")
                    # Add empty layout for failed page
                    all_pages_layout.append({
                        "page_number": page_num + 1,
                        "elements": [],
                        "analysis_method": "failed"
                    })
            
            return {
                "pages": all_pages_layout,
                "total_pages": len(all_pages_layout),
                "analysis_method": "layoutparser",
                "model_info": {
                    "name": "PubLayNet",
                    "architecture": "faster_rcnn_R_50_FPN_3x"
                }
            }
            
        except Exception as e:
            logger.error(f"Document layout analysis failed: {e}")
            return await self._fallback_analysis(pdf_path)
    
    async def _pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """Convert PDF pages to images"""
        images = []
        
        if PDF2IMAGE_AVAILABLE:
            try:
                # Use pdf2image for better quality
                images = convert_from_path(pdf_path, dpi=150)
                logger.debug(f"Converted PDF to {len(images)} images using pdf2image")
                return images
            except Exception as e:
                logger.warning(f"pdf2image conversion failed: {e}")
        
        # Fallback to PyMuPDF
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert to higher resolution for better layout detection
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                image = Image.open(io.BytesIO(img_data))
                images.append(image)
            
            doc.close()
            logger.debug(f"Converted PDF to {len(images)} images using PyMuPDF")
            
        except Exception as e:
            logger.error(f"PDF to image conversion failed: {e}")
            raise
        
        return images
    
    async def _analyze_page_layout(self, image: Image.Image, page_num: int) -> Dict[str, Any]:
        """Analyze layout of a single page"""
        try:
            # Convert PIL image to numpy array
            img_array = np.array(image)
            
            # Detect layout elements
            layout = self.model.detect(img_array)
            
            # Parse detected elements
            elements = []
            for element in layout:
                element_info = {
                    "type": element.type,
                    "confidence": float(element.score),
                    "bbox": {
                        "x1": float(element.coordinates[0]),
                        "y1": float(element.coordinates[1]),
                        "x2": float(element.coordinates[2]),
                        "y2": float(element.coordinates[3])
                    },
                    "area": float(element.area)
                }
                
                # Calculate additional properties
                width = element_info["bbox"]["x2"] - element_info["bbox"]["x1"]
                height = element_info["bbox"]["y2"] - element_info["bbox"]["y1"]
                
                element_info.update({
                    "width": width,
                    "height": height,
                    "center_x": element_info["bbox"]["x1"] + width / 2,
                    "center_y": element_info["bbox"]["y1"] + height / 2
                })
                
                elements.append(element_info)
            
            # Sort elements by reading order (top to bottom, left to right)
            elements = self._sort_elements_by_reading_order(elements)
            
            # Detect columns and structure
            page_structure = self._analyze_page_structure(elements, image.size)
            
            return {
                "page_number": page_num,
                "elements": elements,
                "structure": page_structure,
                "image_size": {
                    "width": image.size[0],
                    "height": image.size[1]
                },
                "analysis_method": "layoutparser"
            }
            
        except Exception as e:
            logger.error(f"Page layout analysis failed: {e}")
            return {
                "page_number": page_num,
                "elements": [],
                "structure": {"columns": 1, "type": "unknown"},
                "analysis_method": "failed"
            }
    
    def _sort_elements_by_reading_order(self, elements: List[Dict]) -> List[Dict]:
        """Sort elements by natural reading order"""
        if not elements:
            return elements
        
        # Group elements by vertical position (rows)
        tolerance = 20  # pixels
        rows = []
        
        for element in elements:
            center_y = element["center_y"]
            
            # Find existing row or create new one
            placed = False
            for row in rows:
                if abs(row["avg_y"] - center_y) <= tolerance:
                    row["elements"].append(element)
                    row["avg_y"] = sum(e["center_y"] for e in row["elements"]) / len(row["elements"])
                    placed = True
                    break
            
            if not placed:
                rows.append({
                    "avg_y": center_y,
                    "elements": [element]
                })
        
        # Sort rows by Y position
        rows.sort(key=lambda r: r["avg_y"])
        
        # Sort elements within each row by X position
        sorted_elements = []
        for row in rows:
            row["elements"].sort(key=lambda e: e["center_x"])
            sorted_elements.extend(row["elements"])
        
        return sorted_elements
    
    def _analyze_page_structure(self, elements: List[Dict], image_size: Tuple[int, int]) -> Dict[str, Any]:
        """Analyze overall page structure"""
        if not elements:
            return {"columns": 1, "type": "empty"}
        
        # Detect number of columns
        text_elements = [e for e in elements if e["type"] in ["Text", "Title"]]
        
        if len(text_elements) < 2:
            return {"columns": 1, "type": "simple"}
        
        # Group elements by X position to detect columns
        x_positions = [e["center_x"] for e in text_elements]
        
        # Simple column detection using clustering
        if len(set(x_positions)) > 1:
            # Sort X positions and look for gaps
            x_sorted = sorted(x_positions)
            gaps = []
            
            for i in range(1, len(x_sorted)):
                gap = x_sorted[i] - x_sorted[i-1]
                if gap > image_size[0] * 0.1:  # Gap > 10% of page width
                    gaps.append(gap)
            
            columns = len(gaps) + 1 if gaps else 1
        else:
            columns = 1
        
        # Determine document type
        has_title = any(e["type"] == "Title" for e in elements)
        has_table = any(e["type"] == "Table" for e in elements)
        has_figure = any(e["type"] == "Figure" for e in elements)
        
        if has_table and has_figure:
            doc_type = "complex"
        elif has_title and columns > 1:
            doc_type = "article"
        elif has_table:
            doc_type = "tabular"
        elif has_figure:
            doc_type = "visual"
        else:
            doc_type = "text"
        
        return {
            "columns": columns,
            "type": doc_type,
            "has_title": has_title,
            "has_table": has_table,
            "has_figure": has_figure,
            "element_counts": {
                element_type: len([e for e in elements if e["type"] == element_type])
                for element_type in ["Text", "Title", "List", "Table", "Figure"]
            }
        }
    
    async def _fallback_analysis(self, pdf_path: str) -> Dict[str, Any]:
        """Fallback analysis when LayoutParser is not available"""
        logger.info("Using fallback layout analysis")
        
        try:
            doc = fitz.open(pdf_path)
            pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Basic structure analysis
                text_blocks = page.get_text("dict")
                elements = []
                
                for block in text_blocks.get("blocks", []):
                    if "lines" in block:  # Text block
                        bbox = block["bbox"]
                        element = {
                            "type": "Text",
                            "confidence": 0.8,
                            "bbox": {
                                "x1": bbox[0], "y1": bbox[1],
                                "x2": bbox[2], "y2": bbox[3]
                            },
                            "width": bbox[2] - bbox[0],
                            "height": bbox[3] - bbox[1],
                            "area": (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                        }
                        elements.append(element)
                
                pages.append({
                    "page_number": page_num + 1,
                    "elements": elements,
                    "structure": {"columns": 1, "type": "basic"},
                    "analysis_method": "fallback"
                })
            
            doc.close()
            
            return {
                "pages": pages,
                "total_pages": len(pages),
                "analysis_method": "fallback"
            }
            
        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
            return {
                "pages": [],
                "total_pages": 0,
                "analysis_method": "failed"
            }
    
    def get_supported_element_types(self) -> List[str]:
        """Get list of supported element types"""
        if self.is_available():
            return ["Text", "Title", "List", "Table", "Figure", "Form", "Header", "Footer", "Signature", "Logo"]
        else:
            return ["Text"]
    
    # NUEVAS FUNCIONALIDADES AVANZADAS - FASE 1.2
    
    async def detect_complex_tables(self, elements: List[Dict], image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detectar tablas complejas incluyendo tablas anidadas y multi-nivel
        """
        table_elements = [e for e in elements if e["type"] == "Table"]
        complex_tables = []
        
        for table in table_elements:
            # Analizar estructura interna de la tabla
            table_analysis = await self._analyze_table_structure(table, image)
            
            if table_analysis:
                complex_tables.append({
                    "bbox": table["bbox"],
                    "confidence": table["confidence"],
                    "structure": table_analysis,
                    "complexity": self._calculate_table_complexity(table_analysis),
                    "type": self._classify_table_type(table_analysis)
                })
        
        return complex_tables
    
    async def _analyze_table_structure(self, table_element: Dict, image: Image.Image) -> Optional[Dict[str, Any]]:
        """
        Analizar estructura interna de una tabla
        """
        try:
            # Extraer región de la tabla
            bbox = table_element["bbox"]
            table_region = image.crop((bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]))
            
            # Convertir a numpy array para análisis
            img_array = np.array(table_region)
            
            # Detectar líneas horizontales y verticales
            horizontal_lines = self._detect_horizontal_lines(img_array)
            vertical_lines = self._detect_vertical_lines(img_array)
            
            # Estimar estructura de celdas
            cells = self._estimate_table_cells(horizontal_lines, vertical_lines, table_region.size)
            
            return {
                "rows": len(horizontal_lines) - 1 if len(horizontal_lines) > 1 else 1,
                "columns": len(vertical_lines) - 1 if len(vertical_lines) > 1 else 1,
                "cells": cells,
                "has_header": self._detect_table_header(cells),
                "has_merged_cells": self._detect_merged_cells(cells),
                "grid_type": "complex" if len(cells) > 10 else "simple"
            }
            
        except Exception as e:
            logger.error(f"Table structure analysis failed: {e}")
            return None
    
    def _detect_horizontal_lines(self, img_array: np.ndarray) -> List[int]:
        """Detectar líneas horizontales en la imagen"""
        import cv2
        
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Crear kernel horizontal
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        
        # Detectar líneas horizontales
        horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        
        # Encontrar coordenadas Y de las líneas
        y_positions = []
        for y in range(horizontal_lines.shape[0]):
            if np.sum(horizontal_lines[y, :]) > horizontal_lines.shape[1] * 0.5 * 255:
                y_positions.append(y)
        
        # Agrupar líneas cercanas
        grouped_lines = []
        tolerance = 5
        
        for y in y_positions:
            if not grouped_lines or y - grouped_lines[-1] > tolerance:
                grouped_lines.append(y)
        
        return grouped_lines
    
    def _detect_vertical_lines(self, img_array: np.ndarray) -> List[int]:
        """Detectar líneas verticales en la imagen"""
        import cv2
        
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Crear kernel vertical
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        # Detectar líneas verticales
        vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        
        # Encontrar coordenadas X de las líneas
        x_positions = []
        for x in range(vertical_lines.shape[1]):
            if np.sum(vertical_lines[:, x]) > vertical_lines.shape[0] * 0.5 * 255:
                x_positions.append(x)
        
        # Agrupar líneas cercanas
        grouped_lines = []
        tolerance = 5
        
        for x in x_positions:
            if not grouped_lines or x - grouped_lines[-1] > tolerance:
                grouped_lines.append(x)
        
        return grouped_lines
    
    def _estimate_table_cells(self, h_lines: List[int], v_lines: List[int], image_size: Tuple[int, int]) -> List[Dict]:
        """Estimar celdas de la tabla basándose en líneas detectadas"""
        cells = []
        
        # Si no hay líneas suficientes, estimar basándose en el tamaño
        if len(h_lines) < 2:
            h_lines = [0, image_size[1]]
        if len(v_lines) < 2:
            v_lines = [0, image_size[0]]
        
        # Crear celdas basándose en intersecciones
        for i in range(len(h_lines) - 1):
            for j in range(len(v_lines) - 1):
                cell = {
                    "row": i,
                    "column": j,
                    "bbox": {
                        "x1": v_lines[j],
                        "y1": h_lines[i],
                        "x2": v_lines[j + 1],
                        "y2": h_lines[i + 1]
                    },
                    "width": v_lines[j + 1] - v_lines[j],
                    "height": h_lines[i + 1] - h_lines[i]
                }
                cells.append(cell)
        
        return cells
    
    def _detect_table_header(self, cells: List[Dict]) -> bool:
        """Detectar si la tabla tiene encabezado"""
        if not cells:
            return False
        
        # Asumir que la primera fila es encabezado si tiene formato diferente
        first_row_cells = [c for c in cells if c["row"] == 0]
        
        # Heurística simple: si la primera fila tiene celdas más altas
        if first_row_cells:
            avg_first_row_height = sum(c["height"] for c in first_row_cells) / len(first_row_cells)
            other_cells = [c for c in cells if c["row"] > 0]
            
            if other_cells:
                avg_other_height = sum(c["height"] for c in other_cells) / len(other_cells)
                return avg_first_row_height > avg_other_height * 1.2
        
        return False
    
    def _detect_merged_cells(self, cells: List[Dict]) -> bool:
        """Detectar si hay celdas fusionadas"""
        if len(cells) < 4:
            return False
        
        # Detectar patrones irregulares en el grid
        rows = set(c["row"] for c in cells)
        cols = set(c["column"] for c in cells)
        
        expected_cells = len(rows) * len(cols)
        actual_cells = len(cells)
        
        # Si hay menos celdas de las esperadas, probablemente hay fusiones
        return actual_cells < expected_cells * 0.9
    
    def _calculate_table_complexity(self, table_analysis: Dict) -> str:
        """Calcular nivel de complejidad de la tabla"""
        score = 0
        
        # Factores de complejidad
        if table_analysis["rows"] > 10:
            score += 2
        elif table_analysis["rows"] > 5:
            score += 1
        
        if table_analysis["columns"] > 5:
            score += 2
        elif table_analysis["columns"] > 3:
            score += 1
        
        if table_analysis["has_merged_cells"]:
            score += 2
        
        if table_analysis["has_header"]:
            score += 1
        
        if score >= 5:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"
    
    def _classify_table_type(self, table_analysis: Dict) -> str:
        """Clasificar tipo de tabla"""
        rows = table_analysis["rows"]
        cols = table_analysis["columns"]
        
        if rows > cols and cols <= 3:
            return "data_list"
        elif cols > rows and rows <= 3:
            return "comparison"
        elif rows > 10 and cols > 5:
            return "spreadsheet"
        elif table_analysis["has_header"]:
            return "structured_data"
        else:
            return "generic"
    
    async def detect_form_elements(self, elements: List[Dict], image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detectar elementos de formularios estructurados
        """
        form_elements = []
        
        # Buscar patrones típicos de formularios
        text_elements = [e for e in elements if e["type"] in ["Text", "Title"]]
        
        for element in text_elements:
            form_indicators = self._analyze_form_indicators(element, image)
            
            if form_indicators["is_form_element"]:
                form_elements.append({
                    "bbox": element["bbox"],
                    "confidence": element["confidence"],
                    "form_type": form_indicators["type"],
                    "field_name": form_indicators.get("field_name"),
                    "expected_input": form_indicators.get("expected_input"),
                    "is_required": form_indicators.get("is_required", False)
                })
        
        return form_elements
    
    def _analyze_form_indicators(self, element: Dict, image: Image.Image) -> Dict[str, Any]:
        """
        Analizar si un elemento es parte de un formulario
        """
        # Esta sería una implementación más sofisticada con ML
        # Por ahora, usaremos heurísticas básicas
        
        bbox = element["bbox"]
        width = bbox["x2"] - bbox["x1"]
        height = bbox["y2"] - bbox["y1"]
        
        # Heurísticas básicas para campos de formulario
        is_field_like = (
            width > height * 3 and  # Aspecto rectangular horizontal
            height < image.size[1] * 0.05 and  # No muy alto
            width > image.size[0] * 0.1  # Ancho mínimo
        )
        
        return {
            "is_form_element": is_field_like,
            "type": "text_field" if is_field_like else "unknown",
            "confidence": 0.7 if is_field_like else 0.1
        }
    
    async def detect_graphic_elements(self, elements: List[Dict], image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detectar elementos gráficos como firmas, sellos, logos
        """
        graphic_elements = []
        
        # Analizar elementos Figure para sub-clasificación
        figure_elements = [e for e in elements if e["type"] == "Figure"]
        
        for figure in figure_elements:
            graphic_type = await self._classify_graphic_element(figure, image)
            
            graphic_elements.append({
                "bbox": figure["bbox"],
                "confidence": figure["confidence"],
                "graphic_type": graphic_type["type"],
                "characteristics": graphic_type["characteristics"],
                "likely_purpose": graphic_type["purpose"]
            })
        
        return graphic_elements
    
    async def _classify_graphic_element(self, element: Dict, image: Image.Image) -> Dict[str, Any]:
        """
        Clasificar tipo de elemento gráfico
        """
        bbox = element["bbox"]
        width = bbox["x2"] - bbox["x1"]
        height = bbox["y2"] - bbox["y1"]
        aspect_ratio = width / height if height > 0 else 1
        
        # Heurísticas para clasificación
        characteristics = {
            "aspect_ratio": aspect_ratio,
            "size_relative": (width * height) / (image.size[0] * image.size[1]),
            "position": self._get_element_position(bbox, image.size)
        }
        
        # Clasificación básica
        if aspect_ratio > 2 and characteristics["size_relative"] < 0.1:
            return {
                "type": "signature",
                "characteristics": characteristics,
                "purpose": "authentication"
            }
        elif aspect_ratio < 1.5 and characteristics["size_relative"] < 0.05:
            return {
                "type": "seal_stamp",
                "characteristics": characteristics,
                "purpose": "verification"
            }
        elif characteristics["position"]["corner"] and characteristics["size_relative"] < 0.15:
            return {
                "type": "logo",
                "characteristics": characteristics,
                "purpose": "branding"
            }
        else:
            return {
                "type": "generic_figure",
                "characteristics": characteristics,
                "purpose": "illustration"
            }
    
    def _get_element_position(self, bbox: Dict, image_size: Tuple[int, int]) -> Dict[str, Any]:
        """
        Determinar posición relativa del elemento en la página
        """
        center_x = (bbox["x1"] + bbox["x2"]) / 2
        center_y = (bbox["y1"] + bbox["y2"]) / 2
        
        # Dividir página en cuadrantes
        h_third = image_size[0] / 3
        v_third = image_size[1] / 3
        
        position = {
            "horizontal": "left" if center_x < h_third else "center" if center_x < 2 * h_third else "right",
            "vertical": "top" if center_y < v_third else "middle" if center_y < 2 * v_third else "bottom",
            "corner": False
        }
        
        # Detectar si está en una esquina
        corner_threshold = 0.15
        position["corner"] = (
            (center_x < image_size[0] * corner_threshold or center_x > image_size[0] * (1 - corner_threshold)) and
            (center_y < image_size[1] * corner_threshold or center_y > image_size[1] * (1 - corner_threshold))
        )
        
        return position
    
    async def detect_multi_column_layout(self, elements: List[Dict], image_size: Tuple[int, int]) -> Dict[str, Any]:
        """
        Detectar y analizar layouts multi-columna avanzados
        """
        text_elements = [e for e in elements if e["type"] in ["Text", "Title"]]
        
        if len(text_elements) < 3:
            return {"columns": 1, "layout_type": "single", "column_boundaries": []}
        
        # Agrupar elementos por posición X
        x_positions = [(e["center_x"], e) for e in text_elements]
        x_positions.sort()
        
        # Detectar agrupaciones usando clustering
        columns = self._cluster_elements_by_x_position(x_positions, image_size[0])
        
        # Analizar características de cada columna
        column_analysis = []
        for i, column in enumerate(columns):
            analysis = self._analyze_column_characteristics(column, i, image_size)
            column_analysis.append(analysis)
        
        return {
            "columns": len(columns),
            "layout_type": self._determine_layout_type(len(columns), column_analysis),
            "column_boundaries": [col["boundaries"] for col in column_analysis],
            "column_analysis": column_analysis,
            "balance_score": self._calculate_layout_balance(column_analysis)
        }
    
    def _cluster_elements_by_x_position(self, x_positions: List[Tuple[float, Dict]], page_width: int) -> List[List[Dict]]:
        """
        Agrupar elementos por posición X para detectar columnas
        """
        if not x_positions:
            return []
        
        # Usar un algoritmo de clustering simple
        columns = []
        current_column = [x_positions[0][1]]
        threshold = page_width * 0.15  # 15% del ancho de la página
        
        for i in range(1, len(x_positions)):
            x_diff = x_positions[i][0] - x_positions[i-1][0]
            
            if x_diff > threshold:
                # Nueva columna
                columns.append(current_column)
                current_column = [x_positions[i][1]]
            else:
                # Misma columna
                current_column.append(x_positions[i][1])
        
        # Agregar la última columna
        if current_column:
            columns.append(current_column)
        
        return columns
    
    def _analyze_column_characteristics(self, column_elements: List[Dict], column_index: int, image_size: Tuple[int, int]) -> Dict[str, Any]:
        """
        Analizar características de una columna
        """
        if not column_elements:
            return {}
        
        # Calcular límites de la columna
        min_x = min(e["bbox"]["x1"] for e in column_elements)
        max_x = max(e["bbox"]["x2"] for e in column_elements)
        min_y = min(e["bbox"]["y1"] for e in column_elements)
        max_y = max(e["bbox"]["y2"] for e in column_elements)
        
        # Estadísticas de la columna
        width = max_x - min_x
        height = max_y - min_y
        element_count = len(column_elements)
        
        # Tipos de elementos en la columna
        element_types = {}
        for element in column_elements:
            elem_type = element.get("type", "unknown")
            element_types[elem_type] = element_types.get(elem_type, 0) + 1
        
        return {
            "index": column_index,
            "boundaries": {"x1": min_x, "y1": min_y, "x2": max_x, "y2": max_y},
            "width": width,
            "height": height,
            "width_percentage": (width / image_size[0]) * 100,
            "element_count": element_count,
            "element_types": element_types,
            "density": element_count / (width * height) if width * height > 0 else 0,
            "primary_type": max(element_types, key=element_types.get) if element_types else "unknown"
        }
    
    def _determine_layout_type(self, column_count: int, column_analysis: List[Dict]) -> str:
        """
        Determinar tipo de layout basado en el número y características de columnas
        """
        if column_count == 1:
            return "single_column"
        elif column_count == 2:
            if len(column_analysis) >= 2:
                width_diff = abs(column_analysis[0]["width"] - column_analysis[1]["width"])
                avg_width = (column_analysis[0]["width"] + column_analysis[1]["width"]) / 2
                if width_diff / avg_width < 0.2:  # Columnas similares
                    return "balanced_two_column"
                else:
                    return "unbalanced_two_column"
            return "two_column"
        elif column_count == 3:
            return "three_column"
        elif column_count > 3:
            return "multi_column_complex"
        else:
            return "unknown"
    
    def _calculate_layout_balance(self, column_analysis: List[Dict]) -> float:
        """
        Calcular puntuación de balance del layout (0-1)
        """
        if len(column_analysis) < 2:
            return 1.0
        
        # Comparar anchos de columnas
        widths = [col["width"] for col in column_analysis]
        width_variance = np.var(widths) if len(widths) > 1 else 0
        width_mean = np.mean(widths) if widths else 1
        
        # Comparar densidades
        densities = [col["density"] for col in column_analysis]
        density_variance = np.var(densities) if len(densities) > 1 else 0
        density_mean = np.mean(densities) if densities else 1
        
        # Calcular puntuación de balance (menor varianza = mejor balance)
        width_score = 1 - min(width_variance / (width_mean ** 2), 1) if width_mean > 0 else 0
        density_score = 1 - min(density_variance / (density_mean ** 2), 1) if density_mean > 0 else 0
        
        return (width_score + density_score) / 2
    
    async def enhanced_analyze_document_layout(self, pdf_path: str) -> Dict[str, Any]:
        """
        Análisis de layout mejorado con todas las nuevas funcionalidades
        """
        # Ejecutar análisis base
        base_analysis = await self.analyze_document_layout(pdf_path)
        
        if not base_analysis.get("pages"):
            return base_analysis
        
        # Mejorar análisis con nuevas funcionalidades
        enhanced_pages = []
        
        try:
            images = await self._pdf_to_images(pdf_path)
            
            for i, page_data in enumerate(base_analysis["pages"]):
                if i < len(images):
                    image = images[i]
                    elements = page_data.get("elements", [])
                    
                    # Análisis avanzados
                    complex_tables = await self.detect_complex_tables(elements, image)
                    form_elements = await self.detect_form_elements(elements, image)
                    graphic_elements = await self.detect_graphic_elements(elements, image)
                    multi_column_analysis = await self.detect_multi_column_layout(elements, image.size)
                    
                    # Combinar resultados
                    enhanced_page = page_data.copy()
                    enhanced_page.update({
                        "complex_tables": complex_tables,
                        "form_elements": form_elements,
                        "graphic_elements": graphic_elements,
                        "multi_column_layout": multi_column_analysis,
                        "enhanced_analysis": True
                    })
                    
                    enhanced_pages.append(enhanced_page)
                else:
                    enhanced_pages.append(page_data)
            
            # Actualizar resultado
            enhanced_analysis = base_analysis.copy()
            enhanced_analysis["pages"] = enhanced_pages
            enhanced_analysis["enhancement_level"] = "advanced"
            
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Enhanced layout analysis failed: {e}")
            # Retornar análisis base si falla la mejora
            base_analysis["enhancement_level"] = "basic"
            return base_analysis