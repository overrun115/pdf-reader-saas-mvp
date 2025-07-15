# Análisis de Exportación con Preservación de Layout

## Resumen Ejecutivo

Este documento analiza las mejores prácticas y herramientas para exportar contenido de PDFs a formatos editables (TXT, HTML, JSON, CSV, XLSX) manteniendo la disposición visual original tanto como sea posible.

## 1. Problemática Actual

### Desafíos en la Preservación de Layout:
- **Estructura de texto**: Los PDFs pueden tener texto en múltiples columnas, tablas complejas y elementos posicionados de manera absoluta
- **Espaciado y alineación**: Preservar espacios, tabulaciones y alineaciones originales
- **Elementos gráficos**: Mantener la relación entre texto e imágenes/gráficos
- **Jerarquía visual**: Conservar títulos, subtítulos, y estructura de párrafos

### Limitaciones de Formatos de Destino:
- **TXT**: Limitado a texto plano, sin formato visual
- **HTML**: Excelente para layout pero requiere CSS avanzado
- **JSON**: Estructurado pero no visual
- **CSV**: Solo para datos tabulares
- **XLSX**: Bueno para tablas pero limitado en layout complejo

## 2. Librerías y Herramientas Recomendadas

### 2.1 Librerías de Análisis de Layout Avanzado

#### **PDFplumber** (Python)
```python
import pdfplumber
import pandas as pd

def extract_with_layout(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extrae texto con coordenadas
            text_objects = page.chars
            
            # Extrae tablas con estructura
            tables = page.extract_tables()
            
            # Detecta columnas automáticamente
            columns = page.detect_columns()
            
            # Análisis de layout por regiones
            layout_analysis = page.analyze_layout()
```

**Ventajas**:
- Detección automática de columnas
- Preservación de coordenadas X,Y
- Extracción de tablas con estructura
- Análisis de espaciado y alineación

#### **PyMuPDF (fitz)** - Análisis de Bloques
```python
import fitz

def extract_layout_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    for page in doc:
        # Obtiene bloques de texto con coordenadas
        blocks = page.get_text("dict")
        
        # Analiza estructura jerárquica
        for block in blocks["blocks"]:
            if block["type"] == 0:  # Bloque de texto
                bbox = block["bbox"]
                lines = block["lines"]
                
                # Preserva espaciado y formato
                formatted_text = analyze_text_structure(lines)
```

**Ventajas**:
- Análisis de bloques estructurados
- Preservación de coordenadas exactas
- Detección de elementos gráficos
- Soporte para OCR integrado

#### **Camelot** - Especializado en Tablas
```python
import camelot

def extract_tables_with_layout(pdf_path):
    # Extrae tablas preservando formato
    tables = camelot.read_pdf(pdf_path, pages='all')
    
    for table in tables:
        # Preserva estructura original
        df = table.df
        
        # Mantiene información de celdas mergeadas
        merged_cells = table.cells
        
        # Preserva formato visual
        formatting = table.formatting
```

### 2.2 Librerías de Generación de Salida

#### **ReportLab** - Para HTML/PDF con Layout
```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

def generate_layout_preserved_html(content_blocks):
    html_parts = []
    
    for block in content_blocks:
        if block["type"] == "text":
            # Preserva espaciado usando CSS
            style = f"""
            <div style="
                position: relative;
                left: {block['x']}px;
                top: {block['y']}px;
                font-size: {block['font_size']}px;
                font-family: {block['font_family']};
                text-align: {block['alignment']};
            ">
                {block['text']}
            </div>
            """
            html_parts.append(style)
        elif block["type"] == "table":
            # Genera tabla HTML con estructura original
            table_html = generate_table_html(block)
            html_parts.append(table_html)
    
    return "\n".join(html_parts)
```

#### **XlsxWriter** - Para Excel con Formato Avanzado
```python
import xlsxwriter

def create_layout_preserved_xlsx(content_blocks, filename):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    
    # Define formatos basados en el PDF original
    formats = {
        'header': workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'bg_color': '#D3D3D3'
        }),
        'body': workbook.add_format({
            'font_size': 11,
            'text_wrap': True
        })
    }
    
    row = 0
    for block in content_blocks:
        if block["type"] == "text":
            # Preserva formato de texto
            worksheet.write(row, 0, block["text"], formats['body'])
        elif block["type"] == "table":
            # Escribe tabla con formato original
            row = write_table_with_format(worksheet, block, row, formats)
        row += 1
    
    workbook.close()
```

## 3. Estrategias de Preservación de Layout

### 3.1 Análisis de Estructura Jerárquica

#### Detección de Elementos:
```python
def analyze_document_structure(pdf_path):
    structure = {
        "headers": [],
        "paragraphs": [],
        "tables": [],
        "lists": [],
        "images": [],
        "columns": []
    }
    
    # Análisis por coordenadas y formato
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Detecta títulos por tamaño de fuente
            chars = page.chars
            headers = detect_headers_by_font_size(chars)
            
            # Detecta columnas por distribución espacial
            columns = detect_columns_by_spacing(chars)
            
            # Detecta listas por indentación
            lists = detect_lists_by_indentation(chars)
            
            # Detecta tablas por alineación
            tables = detect_tables_by_alignment(chars)
    
    return structure
```

### 3.2 Preservación de Espaciado

#### Para Texto Plano (TXT):
```python
def preserve_spacing_in_text(text_blocks):
    lines = []
    
    for block in text_blocks:
        # Calcula espaciado relativo
        indent = calculate_indent(block['x'], block['page_width'])
        
        # Preserva espaciado vertical
        vertical_spacing = calculate_vertical_spacing(block['y'], previous_y)
        
        # Genera línea con espaciado
        line = " " * indent + block['text']
        lines.append(line)
        
        # Añade espaciado vertical
        if vertical_spacing > threshold:
            lines.extend([""] * (vertical_spacing // line_height))
    
    return "\n".join(lines)
```

#### Para HTML con CSS:
```python
def generate_css_layout(content_blocks):
    css = """
    <style>
    .pdf-container {
        position: relative;
        width: 100%;
        font-family: Arial, sans-serif;
    }
    
    .text-block {
        position: absolute;
        white-space: pre-wrap;
    }
    
    .table-block {
        position: absolute;
        border-collapse: collapse;
    }
    
    .column-layout {
        columns: 2;
        column-gap: 20px;
    }
    </style>
    """
    
    html_blocks = []
    for block in content_blocks:
        style = f"""
        <div class="text-block" style="
            left: {block['x']}px;
            top: {block['y']}px;
            width: {block['width']}px;
            font-size: {block['font_size']}px;
        ">
            {block['text']}
        </div>
        """
        html_blocks.append(style)
    
    return css + '<div class="pdf-container">' + "\n".join(html_blocks) + '</div>'
```

### 3.3 Manejo de Columnas

#### Detección Automática:
```python
def detect_and_preserve_columns(page_content):
    # Analiza distribución horizontal del texto
    x_positions = [char['x0'] for char in page_content['chars']]
    
    # Detecta columnas por clustering
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=2)  # Asume 2 columnas
    clusters = kmeans.fit_predict(np.array(x_positions).reshape(-1, 1))
    
    # Organiza contenido por columnas
    columns = {}
    for i, char in enumerate(page_content['chars']):
        col = clusters[i]
        if col not in columns:
            columns[col] = []
        columns[col].append(char)
    
    return columns
```

## 4. Implementación Específica para el Proyecto

### 4.1 Mejoras Propuestas para `document_ai_service.py`

#### Análisis de Layout Mejorado:
```python
async def _analyze_layout_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
    """Analiza la estructura del layout para preservar formato."""
    structure = {
        "columns": [],
        "headers": [],
        "tables": [],
        "text_blocks": [],
        "spatial_relationships": []
    }
    
    elements = content.get("elements", [])
    
    # Agrupa elementos por página
    pages = {}
    for element in elements:
        page_num = element.get("page", 1)
        if page_num not in pages:
            pages[page_num] = []
        pages[page_num].append(element)
    
    # Analiza cada página
    for page_num, page_elements in pages.items():
        page_structure = self._analyze_page_layout(page_elements)
        structure["pages"] = structure.get("pages", {})
        structure["pages"][page_num] = page_structure
    
    return structure

def _analyze_page_layout(self, elements: List[Dict]) -> Dict[str, Any]:
    """Analiza el layout de una página específica."""
    # Detecta columnas por posición X
    x_positions = [elem.get("bbox", {}).get("x0", 0) for elem in elements if elem.get("bbox")]
    
    # Detecta headers por tamaño de fuente
    headers = [elem for elem in elements if elem.get("font_size", 10) > 12]
    
    # Detecta tablas por alineación
    tables = self._detect_tables_by_alignment(elements)
    
    return {
        "columns": self._detect_columns(x_positions),
        "headers": headers,
        "tables": tables,
        "text_blocks": [elem for elem in elements if elem not in headers]
    }
```

#### Exportación HTML Mejorada:
```python
async def _export_to_html_with_layout(self, content: Dict[str, Any], file_path: Path) -> None:
    """Exporta a HTML preservando el layout original."""
    
    # Analiza estructura
    layout = await self._analyze_layout_structure(content)
    
    # CSS para preservar layout
    css = """
    <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .page { page-break-after: always; position: relative; min-height: 800px; }
    .text-block { margin-bottom: 10px; }
    .header { font-weight: bold; font-size: 1.2em; margin: 20px 0 10px 0; }
    .column-left { float: left; width: 48%; }
    .column-right { float: right; width: 48%; }
    .table-container { margin: 20px 0; overflow-x: auto; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; font-weight: bold; }
    .clearfix::after { content: ""; display: table; clear: both; }
    </style>
    """
    
    # Genera HTML con estructura preservada
    html_content = [css, "<body>"]
    
    for page_num, page_data in layout.get("pages", {}).items():
        html_content.append(f'<div class="page">')
        html_content.append(f'<h2>Page {page_num}</h2>')
        
        # Maneja columnas
        if len(page_data.get("columns", [])) > 1:
            html_content.append('<div class="clearfix">')
            html_content.append('<div class="column-left">')
            # Contenido columna izquierda
            html_content.append('</div>')
            html_content.append('<div class="column-right">')
            # Contenido columna derecha
            html_content.append('</div>')
            html_content.append('</div>')
        
        # Añade tablas
        for table in page_data.get("tables", []):
            html_content.append(self._generate_table_html(table))
        
        html_content.append('</div>')
    
    html_content.append("</body></html>")
    
    # Escribe archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))
```

#### Exportación XLSX Mejorada:
```python
async def _export_to_xlsx_with_layout(self, content: Dict[str, Any], file_path: Path) -> None:
    """Exporta a XLSX preservando estructura y formato."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
        from openpyxl.utils import get_column_letter
        
        wb = Workbook()
        wb.remove(wb.active)
        
        # Analiza estructura
        layout = await self._analyze_layout_structure(content)
        
        # Crea hoja por página
        for page_num, page_data in layout.get("pages", {}).items():
            ws = wb.create_sheet(title=f"Page_{page_num}")
            
            # Aplica formato basado en estructura
            self._apply_layout_to_sheet(ws, page_data)
        
        # Crea hoja de resumen con tablas
        if layout.get("tables"):
            summary_ws = wb.create_sheet(title="All_Tables", index=0)
            self._write_all_tables_to_sheet(summary_ws, layout["tables"])
        
        wb.save(str(file_path))
        
    except Exception as e:
        logger.error(f"Error in XLSX export with layout: {str(e)}")
        # Fallback a método básico
        await self._export_to_xlsx(content, file_path)
```

### 4.2 Herramientas de Terceros Recomendadas

#### **Docling** (Ya implementado)
- Excelente para extracción inicial
- Buena detección de estructura
- Soporte para OCR

#### **Adobe PDF Services API**
```python
# Para casos que requieren máxima precisión
from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation

def extract_with_adobe_api(pdf_path):
    # Configuración de credenciales
    credentials = Credentials.service_account_credentials_builder()
    
    # Operación de extracción
    extract_pdf_operation = ExtractPDFOperation.create_new()
    extract_pdf_operation.set_input(pdf_path)
    
    # Opciones de extracción
    extract_pdf_options = ExtractPDFOptions.builder()
    extract_pdf_options.add_elements_to_extract([
        ExtractElementType.TEXT,
        ExtractElementType.TABLES,
        ExtractElementType.IMAGES
    ])
    
    # Incluye información de formato
    extract_pdf_options.add_elements_to_extract_renditions([
        ExtractRenditionsElementType.TABLES,
        ExtractRenditionsElementType.FIGURES
    ])
    
    result = extract_pdf_operation.execute(credentials)
    return result
```

#### **Tabulizer** (Para tablas complejas)
```python
import tabula

def extract_complex_tables(pdf_path):
    # Extrae tablas con estructura compleja
    tables = tabula.read_pdf(
        pdf_path,
        pages='all',
        multiple_tables=True,
        guess=True,
        stream=True,  # Para tablas sin líneas
        area=[50, 50, 750, 550]  # Área específica
    )
    
    return tables
```

## 5. Recomendaciones de Implementación

### 5.1 Prioridades por Formato

#### **HTML** (Prioridad Alta):
- Implementar CSS absolute positioning
- Usar coordenadas exactas del PDF
- Mantener estructura de columnas
- Preservar jerarquía de títulos

#### **XLSX** (Prioridad Media):
- Crear hojas por página
- Preservar estructura de tablas
- Usar formato condicional para destacar headers
- Implementar auto-ajuste de columnas

#### **TXT** (Prioridad Baja):
- Usar espaciado basado en coordenadas
- Mantener estructura de párrafos
- Preservar alineación básica

### 5.2 Casos de Uso Específicos

#### **Documentos Multi-Columna**:
```python
def handle_multi_column_layout(elements):
    # Detecta columnas por clustering de posiciones X
    columns = detect_columns_by_clustering(elements)
    
    # Ordena contenido por columna y luego por Y
    for col_elements in columns:
        col_elements.sort(key=lambda x: x.get('y', 0))
    
    # Genera salida respetando orden de lectura
    return merge_columns_reading_order(columns)
```

#### **Documentos con Tablas Complejas**:
```python
def handle_complex_tables(table_elements):
    # Detecta celdas mergeadas
    merged_cells = detect_merged_cells(table_elements)
    
    # Preserva estructura de headers
    headers = detect_table_headers(table_elements)
    
    # Genera estructura preservando formato
    return reconstruct_table_structure(table_elements, merged_cells, headers)
```

### 5.3 Métricas de Calidad

#### **Precisión de Layout**:
- Medición de distancia entre posiciones originales y exportadas
- Preservación de alineación relativa
- Mantenimiento de proporções

#### **Legibilidad**:
- Preservación de estructura jerárquica
- Mantenimiento de orden de lectura
- Claridad en separación de secciones

#### **Usabilidad**:
- Facilidad de edición en formato destino
- Compatibilidad con herramientas estándar
- Tamaño de archivo razonable

## 6. Conclusiones y Próximos Pasos

### 6.1 Implementación Inmediata
1. **Mejorar análisis de layout** en `document_ai_service.py`
2. **Implementar coordenadas absolutas** para HTML
3. **Añadir detección de columnas** automática
4. **Mejorar formato XLSX** con estilos

### 6.2 Implementación Futura
1. **Integrar Adobe PDF Services** para casos complejos
2. **Implementar ML para detección** de estructura
3. **Añadir soporte para gráficos** y diagramas
4. **Crear templates personalizables** por tipo de documento

### 6.3 Herramientas Adicionales
- **PDFplumber** para análisis detallado
- **Camelot** para tablas complejas
- **ReportLab** para generación de salida
- **OpenCV** para análisis de imágenes

El objetivo es lograr exports que sean tanto **visualmente similares** al PDF original como **completamente editables** en el formato destino.
