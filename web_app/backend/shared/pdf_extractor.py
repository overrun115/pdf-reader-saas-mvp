import sys
import os
import pandas as pd
from typing import List, Set, Tuple, Optional
from docling.document_converter import DocumentConverter
import hashlib
import json
import time

def extract_tables_with_format(pdf_path: str, output_format: str = "excel") -> dict:
    """
    Extract tables from PDF and return structured data.
    
    Args:
        pdf_path: Path to the PDF file
        output_format: 'excel', 'csv', or 'both'
    
    Returns:
        dict: Result with success, tables_found, total_rows, and tables data
    """
    try:
        # Verify that the PDF file exists
        if not os.path.exists(pdf_path):
            print(f"Error: File {pdf_path} does not exist.")
            return {"success": False, "error": "File not found", "tables_found": 0}
            
        # Create output file path
        output_dir = os.path.join(os.path.dirname(pdf_path), "processed")
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        if output_format == "excel":
            output_path = os.path.join(output_dir, f"{base_name}.xlsx")
        elif output_format == "csv":
            output_path = os.path.join(output_dir, f"{base_name}.csv")
        else:
            output_path = os.path.join(output_dir, f"{base_name}.xlsx")
        
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        doc = result.document
        tables = getattr(doc, 'tables', [])
        
        if not tables:
            print("No tables found in the PDF.")
            return {"success": False, "error": "No tables found", "tables_found": 0}
            
        print(f"Found {len(tables)} tables in the PDF.")
        
        # Extract all tables and normalize columns
        all_dfs = []
        reference_columns = None
        table_data = []
        
        for idx, table in enumerate(tables):
            try:
                df = table.export_to_dataframe()
                if df.empty:
                    print(f"Table {idx + 1} is empty, skipping.")
                    continue
                    
                # Clean column names (remove extra spaces)
                df.columns = [str(col).strip() for col in df.columns]
                
                # If it's the first table with descriptive names, use as reference
                if reference_columns is None and not all(col.isdigit() for col in df.columns):
                    reference_columns = list(df.columns)
                    print(f"Table {idx + 1} (reference): {len(df)} rows, columns: {reference_columns}")
                    all_dfs.append((idx, df))
                    continue
                
                # If columns are numbers, map to reference columns
                if reference_columns and all(col.isdigit() for col in df.columns):
                    # Create mapping based on order and number of columns
                    if len(df.columns) == len(reference_columns):
                        column_mapping = dict(zip(df.columns, reference_columns))
                        df = df.rename(columns=column_mapping)
                        print(f"Table {idx + 1} (mapped): {len(df)} rows, columns mapped from {list(column_mapping.keys())} to {reference_columns}")
                    else:
                        print(f"Table {idx + 1}: Cannot map - different number of columns ({len(df.columns)} vs {len(reference_columns)})")
                        print(f"Current columns: {list(df.columns)}")
                else:
                    print(f"Table {idx + 1}: {len(df)} rows, columns: {list(df.columns)}")
                
                all_dfs.append((idx, df))
                
            except Exception as e:
                print(f"Error processing table {idx + 1}: {e}")
                continue
        
        if not all_dfs:
            print("No valid tables could be processed.")
            return {"success": False, "error": "No valid tables found", "tables_found": 0}
            
        # Get all unique columns after mapping
        all_columns: Set[str] = set()
        for idx, df in all_dfs:
            all_columns.update(df.columns)
        
        # Use reference columns if available, otherwise use all unique ones
        if reference_columns:
            unified_columns = reference_columns
            print(f"Using reference columns: {unified_columns}")
        else:
            unified_columns = sorted(list(all_columns))
            print(f"Unified columns: {unified_columns}")
        
        # Normalize all tables to have the same columns
        normalized_dfs = []
        for idx, df in all_dfs:
            # Create DataFrame with all columns, filling missing with NaN
            normalized_df = df.reindex(columns=unified_columns, fill_value=None)
            normalized_dfs.append(normalized_df)
            
            # Add table data for response
            table_data.append({
                "table_index": idx,
                "headers": list(unified_columns),
                "data": normalized_df.values.tolist()
            })
        
        # Concatenate all normalized tables
        df_final = pd.concat(normalized_dfs, ignore_index=True, sort=False)
        
        # Save in specified format
        save_success = save_dataframe(df_final, output_path, output_format)
        
        if save_success:
            return {
                "success": True,
                "tables_found": len(tables),
                "total_rows": len(df_final),
                "tables": table_data,
                "output_path": output_path
            }
        else:
            return {"success": False, "error": "Failed to save output file", "tables_found": len(tables)}
        
    except FileNotFoundError:
        print(f"Error: Could not find file {pdf_path}")
        return {"success": False, "error": "File not found", "tables_found": 0}
    except PermissionError:
        print(f"Error: No permissions to read {pdf_path}")
        return {"success": False, "error": "Permission denied", "tables_found": 0}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"success": False, "error": str(e), "tables_found": 0}

def save_dataframe(df: pd.DataFrame, output_path: str, format_type: str = "excel") -> bool:
    """
    Save DataFrame in specified format.
    
    Args:
        df: DataFrame to save
        output_path: Base path for output file
        format_type: 'excel', 'csv', or 'both'
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        base_path = os.path.splitext(output_path)[0]
        saved_files = []
        
        if format_type == "excel" or format_type == "both":
            excel_path = base_path + ".xlsx"
            df.to_excel(excel_path, index=False)
            saved_files.append(excel_path)
            print(f"Excel file saved at {excel_path}")
        
        if format_type == "csv" or format_type == "both":
            csv_path = base_path + ".csv"
            df.to_csv(csv_path, index=False, encoding='utf-8')
            saved_files.append(csv_path)
            print(f"CSV file saved at {csv_path}")
        
        print(f"Total rows: {len(df)}, Total columns: {len(df.columns)}")
        return True
        
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

def get_table_preview(pdf_path: str, max_rows: int = 10) -> Optional[dict]:
    """
    Get a preview of tables in the PDF without saving files.
    Uses caching to avoid reprocessing the same file.
    
    Args:
        pdf_path: Path to the PDF file
        max_rows: Maximum rows to return per table
    
    Returns:
        dict: Preview data with table information
    """
    try:
        if not os.path.exists(pdf_path):
            return None
        
        # Create cache directory
        cache_dir = os.path.join(os.path.dirname(pdf_path), '.preview_cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Generate cache key based on file path and modification time
        file_stat = os.stat(pdf_path)
        cache_key = hashlib.md5(f"{pdf_path}_{file_stat.st_mtime}_{max_rows}".encode()).hexdigest()
        cache_file = os.path.join(cache_dir, f"preview_{cache_key}.json")
        
        # Check if cache exists and is recent (less than 1 hour old)
        if os.path.exists(cache_file):
            cache_age = time.time() - os.path.getmtime(cache_file)
            if cache_age < 3600:  # 1 hour cache
                try:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                        print(f"Using cached preview for {os.path.basename(pdf_path)}")
                        return cached_data
                except:
                    pass  # If cache read fails, continue with normal processing
        
        print(f"Generating new preview for {os.path.basename(pdf_path)}")
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        doc = result.document
        tables = getattr(doc, 'tables', [])
        
        if not tables:
            preview_data = {"tables_found": 0, "tables": []}
        else:
            preview_data = {
                "tables_found": len(tables),
                "tables": []
            }
            
            for idx, table in enumerate(tables):
                try:
                    df = table.export_to_dataframe()
                    if df.empty:
                        continue
                    
                    # Clean column names
                    df.columns = [str(col).strip() for col in df.columns]
                    
                    # Get preview data
                    table_preview = {
                        "table_number": idx + 1,
                        "rows": len(df),
                        "columns": list(df.columns),
                        "sample_data": df.head(max_rows).to_dict('records') if not df.empty else []
                    }
                    
                    preview_data["tables"].append(table_preview)
                    
                except Exception as e:
                    print(f"Error previewing table {idx + 1}: {e}")
                    continue
        
        # Save to cache
        try:
            with open(cache_file, 'w') as f:
                json.dump(preview_data, f)
        except Exception as e:
            print(f"Failed to save preview cache: {e}")
        
        return preview_data
        
    except Exception as e:
        print(f"Error creating preview: {e}")
        return None

def validate_pdf_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate if a file is a proper PDF and can be processed.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        if not file_path.lower().endswith('.pdf'):
            return False, "File is not a PDF"
        
        # Try to open with DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(file_path)
        
        if not result or not result.document:
            return False, "Could not read PDF content"
        
        return True, "Valid PDF file"
        
    except Exception as e:
        return False, f"PDF validation error: {str(e)}"