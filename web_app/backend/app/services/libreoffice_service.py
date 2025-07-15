"""
LibreOffice Headless Service for Document Conversion
Provides high-quality document format conversion using LibreOffice
"""

import logging
import subprocess
import tempfile
import os
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class LibreOfficeService:
    """Service for LibreOffice headless conversions"""
    
    def __init__(self):
        self.libreoffice_path = self._find_libreoffice_executable()
        self.available = self.libreoffice_path is not None
        self.temp_dir = Path(tempfile.gettempdir()) / "libreoffice_conversions"
        self.temp_dir.mkdir(exist_ok=True)
        
        if self.available:
            logger.info(f"LibreOffice found at: {self.libreoffice_path}")
        else:
            logger.warning("LibreOffice not found - office conversions unavailable")
    
    def _find_libreoffice_executable(self) -> Optional[str]:
        """Find LibreOffice executable on system"""
        
        # Common LibreOffice paths on different systems
        possible_paths = [
            # Linux
            '/usr/bin/libreoffice',
            '/usr/local/bin/libreoffice',
            '/snap/bin/libreoffice',
            '/opt/libreoffice*/program/soffice',
            
            # macOS
            '/Applications/LibreOffice.app/Contents/MacOS/soffice',
            '/opt/homebrew/bin/libreoffice',
            
            # Windows (if running in WSL or similar)
            '/mnt/c/Program Files/LibreOffice/program/soffice.exe',
            '/mnt/c/Program Files (x86)/LibreOffice/program/soffice.exe',
        ]
        
        # Try finding in PATH first
        try:
            result = subprocess.run(['which', 'libreoffice'], 
                                 capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try soffice command
        try:
            result = subprocess.run(['which', 'soffice'], 
                                 capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check common installation paths
        for path in possible_paths:
            if '*' in path:
                # Handle wildcard paths
                import glob
                matches = glob.glob(path)
                if matches:
                    potential_path = matches[0]
                    if os.path.isfile(potential_path) and os.access(potential_path, os.X_OK):
                        return potential_path
            else:
                if os.path.isfile(path) and os.access(path, os.X_OK):
                    return path
        
        return None
    
    async def convert_document(self, input_path: str, output_format: str, 
                             output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert document using LibreOffice headless mode
        
        Args:
            input_path: Path to input document
            output_format: Target format (pdf, docx, odt, html, etc.)
            output_path: Optional specific output path
            
        Returns:
            Dictionary with conversion results
        """
        
        if not self.available:
            raise Exception("LibreOffice not available for conversion")
        
        if not os.path.exists(input_path):
            raise Exception(f"Input file not found: {input_path}")
        
        try:
            # Create temporary output directory
            temp_output_dir = self.temp_dir / f"conversion_{os.getpid()}"
            temp_output_dir.mkdir(exist_ok=True)
            
            # Build LibreOffice command
            cmd = [
                self.libreoffice_path,
                '--headless',
                '--convert-to', output_format,
                '--outdir', str(temp_output_dir),
                input_path
            ]
            
            logger.info(f"Running LibreOffice conversion: {' '.join(cmd)}")
            
            # Execute conversion
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)  # 5 minute timeout
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown LibreOffice error"
                raise Exception(f"LibreOffice conversion failed: {error_msg}")
            
            # Find the converted file
            input_name = Path(input_path).stem
            expected_output = temp_output_dir / f"{input_name}.{output_format}"
            
            if not expected_output.exists():
                # Try to find any file with the correct extension
                output_files = list(temp_output_dir.glob(f"*.{output_format}"))
                if output_files:
                    expected_output = output_files[0]
                else:
                    raise Exception(f"Converted file not found in {temp_output_dir}")
            
            # Move to final location
            if output_path:
                final_output = Path(output_path)
                final_output.parent.mkdir(parents=True, exist_ok=True)
                expected_output.rename(final_output)
                final_path = str(final_output)
            else:
                final_path = str(expected_output)
            
            file_size = os.path.getsize(final_path)
            
            # Cleanup temporary directory
            try:
                import shutil
                shutil.rmtree(temp_output_dir)
            except:
                pass  # Ignore cleanup errors
            
            logger.info(f"LibreOffice conversion completed: {file_size} bytes")
            
            return {
                'success': True,
                'output_path': final_path,
                'file_size': file_size,
                'format': output_format,
                'method': 'libreoffice_headless',
                'stdout': stdout.decode() if stdout else '',
                'stderr': stderr.decode() if stderr else ''
            }
            
        except asyncio.TimeoutError:
            logger.error("LibreOffice conversion timed out")
            return {
                'success': False,
                'error': 'Conversion timed out after 5 minutes',
                'method': 'libreoffice_headless'
            }
            
        except Exception as e:
            logger.error(f"LibreOffice conversion failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'libreoffice_headless'
            }
    
    async def pdf_to_docx(self, pdf_path: str, docx_path: str) -> Dict[str, Any]:
        """Convert PDF to DOCX using LibreOffice"""
        return await self.convert_document(pdf_path, 'docx', docx_path)
    
    async def pdf_to_odt(self, pdf_path: str, odt_path: str) -> Dict[str, Any]:
        """Convert PDF to ODT using LibreOffice"""
        return await self.convert_document(pdf_path, 'odt', odt_path)
    
    async def html_to_docx(self, html_path: str, docx_path: str) -> Dict[str, Any]:
        """Convert HTML to DOCX using LibreOffice"""
        return await self.convert_document(html_path, 'docx', docx_path)
    
    async def odt_to_docx(self, odt_path: str, docx_path: str) -> Dict[str, Any]:
        """Convert ODT to DOCX using LibreOffice"""
        return await self.convert_document(odt_path, 'docx', docx_path)
    
    async def enhance_docx_with_html(self, html_content: str, output_path: str) -> Dict[str, Any]:
        """
        Create high-quality DOCX from HTML content using LibreOffice
        This can preserve complex layouts better than direct conversion
        """
        
        if not self.available:
            raise Exception("LibreOffice not available for HTML to DOCX conversion")
        
        try:
            # Create temporary HTML file
            temp_html = self.temp_dir / f"temp_{os.getpid()}.html"
            
            # Enhanced HTML with better styling for LibreOffice conversion
            enhanced_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Document</title>
                <style>
                    body {{
                        font-family: 'Times New Roman', serif;
                        font-size: 12pt;
                        line-height: 1.15;
                        margin: 1in;
                        color: black;
                    }}
                    h1 {{ font-size: 16pt; font-weight: bold; margin: 12pt 0 6pt 0; }}
                    h2 {{ font-size: 14pt; font-weight: bold; margin: 10pt 0 5pt 0; }}
                    h3 {{ font-size: 12pt; font-weight: bold; margin: 8pt 0 4pt 0; }}
                    p {{ margin: 6pt 0; text-align: justify; }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 12pt 0;
                    }}
                    th, td {{
                        border: 1pt solid black;
                        padding: 6pt;
                        text-align: left;
                        vertical-align: top;
                    }}
                    th {{
                        background-color: #f0f0f0;
                        font-weight: bold;
                    }}
                    .page-break {{
                        page-break-before: always;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(enhanced_html)
            
            # Convert HTML to DOCX
            result = await self.html_to_docx(str(temp_html), output_path)
            
            # Cleanup
            temp_html.unlink(missing_ok=True)
            
            if result.get('success'):
                result['method'] = 'libreoffice_html_enhanced'
                result['features'] = {
                    'layout_preservation': 'high',
                    'table_support': True,
                    'image_support': True,
                    'style_preservation': True
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced HTML to DOCX conversion failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'libreoffice_html_enhanced'
            }
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported input and output formats"""
        return {
            'input': ['pdf', 'html', 'odt', 'doc', 'docx', 'rtf', 'txt'],
            'output': ['docx', 'odt', 'pdf', 'html', 'rtf', 'txt']
        }
    
    def is_available(self) -> bool:
        """Check if LibreOffice is available"""
        return self.available
    
    async def test_conversion(self) -> Dict[str, Any]:
        """Test LibreOffice installation with a simple conversion"""
        
        if not self.available:
            return {
                'success': False,
                'error': 'LibreOffice not available'
            }
        
        try:
            # Create a simple test document
            test_html = self.temp_dir / "test.html"
            with open(test_html, 'w', encoding='utf-8') as f:
                f.write("""
                <!DOCTYPE html>
                <html>
                <head><title>Test</title></head>
                <body><h1>LibreOffice Test</h1><p>This is a test conversion.</p></body>
                </html>
                """)
            
            # Test conversion
            test_output = self.temp_dir / "test.docx"
            result = await self.html_to_docx(str(test_html), str(test_output))
            
            # Cleanup
            test_html.unlink(missing_ok=True)
            test_output.unlink(missing_ok=True)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }