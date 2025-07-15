from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import os
import uuid
import hashlib
import time
from datetime import datetime

from app.core.database import get_db
from app.api.dependencies import (
    get_current_active_user, 
    validate_file_upload, 
    require_processing_quota
)
from app.models.database import User, ProcessedFile, FileStatus, OutputFormat
from app.models.schemas import (
    FileUploadResponse, 
    FileProcessRequest, 
    ProcessedFileResponse,
    DashboardResponse,
    UserStats,
    RecentFile
)
from app.services.file_service import (
    save_uploaded_file,
    create_file_record,
    get_user_files,
    get_file_by_id,
    update_file_status,
    delete_file_record
)
# Restored PDF processing imports
# from app.tasks.pdf_tasks import process_pdf_task  # Still commented - may have other dependencies
import sys
import os
# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, backend_path)

try:
    from shared.pdf_extractor import get_table_preview, validate_pdf_file, extract_tables_with_format
    from shared.image_extractor import extract_tables_from_image
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback - create placeholder functions
    def get_table_preview(file_path):
        return {"tables_found": 0, "tables": [], "error": "PDF extractor not available"}
    
    def validate_pdf_file(file_path):
        return False, "PDF extractor not available"
    
    def extract_tables_with_format(file_path, output_format="excel"):
        return {"success": False, "error": "PDF extractor not available", "tables_found": 0}
    
    def extract_tables_from_image(file_path):
        return {"success": False, "error": "Image extractor not available", "tables_found": 0}
import imghdr

router = APIRouter()

class BulkDeleteRequest(BaseModel):
    file_ids: List[int]

def create_output_file(tables: List[dict], output_path: str, output_format: str):
    """Create output file from extracted tables"""
    import pandas as pd
    
    try:
        if output_format == "excel":
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for table in tables:
                    # Create DataFrame from table data
                    df = pd.DataFrame(table["data"], columns=table["headers"])
                    sheet_name = f"Table_{table['table_index'] + 1}"
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        elif output_format == "csv":
            # For CSV, combine all tables or just use the first one
            if len(tables) == 1:
                df = pd.DataFrame(tables[0]["data"], columns=tables[0]["headers"])
            else:
                # Combine all tables
                combined_data = []
                for table in tables:
                    df = pd.DataFrame(table["data"], columns=table["headers"])
                    df['source_table'] = f"Table_{table['table_index'] + 1}"
                    combined_data.append(df)
                df = pd.concat(combined_data, ignore_index=True)
            
            df.to_csv(output_path, index=False)
        
        print(f"Created output file: {output_path}")
        
    except Exception as e:
        print(f"Error creating output file: {e}")
        raise

def simple_process_pdf(file_id: int, user_id: int, output_format: str, db: Session):
    """Simple PDF processing function without Celery"""
    import time
    from datetime import datetime
    
    try:
        print(f"[SIMPLE_PROCESS] Starting processing for file_id={file_id}")
        
        # Get file record
        file_record = get_file_by_id(db, file_id, user_id)
        if not file_record:
            print(f"[SIMPLE_PROCESS][ERROR] File not found: {file_id}")
            return
            
        start_time = time.time()
        
        # Generate output path
        base_name = os.path.splitext(file_record.original_filename)[0]
        output_dir = os.path.join(os.path.dirname(file_record.input_file_path), "processed")
        os.makedirs(output_dir, exist_ok=True)
        
        if output_format == "excel":
            output_path = os.path.join(output_dir, f"{base_name}_tables.xlsx")
        elif output_format == "csv":
            output_path = os.path.join(output_dir, f"{base_name}_tables.csv")
        else:
            output_path = os.path.join(output_dir, f"{base_name}_tables.xlsx")
        
        # Process with optimized PDF extractor (limited rows for faster processing)
        print(f"[SIMPLE_PROCESS] Processing {file_record.original_filename} ({round(file_record.file_size/(1024*1024), 1)}MB)")
        result = extract_tables_with_format(file_record.input_file_path, output_format, max_rows_per_table=200)
        success = result.get("success", False)
        
        processing_time = time.time() - start_time
        
        if success:
            # Update file record as completed with real data
            file_record.status = FileStatus.COMPLETED
            file_record.output_file_path = result.get("output_path", output_path)
            file_record.tables_found = result.get("tables_found", 0)
            file_record.total_rows = result.get("total_rows", 0)
            file_record.processing_time = processing_time
            file_record.completed_at = datetime.utcnow()
            
            # No need to create output file since extract_tables_with_format already creates it
            
            print(f"[SIMPLE_PROCESS] Processing completed successfully for file_id={file_id}")
            print(f"[SIMPLE_PROCESS] Found {result.get('tables_found', 0)} tables with {result.get('total_rows', 0)} total rows")
        else:
            # Update file record as failed
            file_record.status = FileStatus.FAILED
            file_record.error_message = result.get("error", "Failed to extract tables from PDF")
            print(f"[SIMPLE_PROCESS] Processing failed for file_id={file_id}: {result.get('error', 'Unknown error')}")
        
        db.commit()
        
    except Exception as e:
        print(f"[SIMPLE_PROCESS][ERROR] Processing failed: {str(e)}")
        # Update file as failed
        try:
            file_record = get_file_by_id(db, file_id, user_id)
            if file_record:
                file_record.status = FileStatus.FAILED
                file_record.error_message = str(e)
                db.commit()
        except:
            pass

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(require_processing_quota),
    db: Session = Depends(get_db)
):
    """Upload a PDF or image file for processing"""
    
    # Validate file type
    file_content = await file.read()
    file_extension = os.path.splitext(file.filename)[1].lower()
    allowed_exts = ['.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    if file_extension not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_extension}"
        )
    # Detect type
    is_pdf = file_extension == '.pdf'
    is_image = file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    if not (is_pdf or is_image):
        raise HTTPException(status_code=400, detail="File must be PDF or image")
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    # Calculate file hash for deduplication
    file_hash = hashlib.md5(file_content).hexdigest()
    # Check if file already processed by this user
    existing_file = db.query(ProcessedFile).filter(
        ProcessedFile.user_id == current_user.id,
        ProcessedFile.file_hash == file_hash
    ).first()
    if existing_file:
        return FileUploadResponse(
            id=existing_file.id,
            original_filename=existing_file.original_filename,
            file_size=existing_file.file_size,
            status=existing_file.status,
            created_at=existing_file.created_at
        )
    # Save file to disk
    file_path = save_uploaded_file(file_content, unique_filename)
    # Validate content (PDF or image)
    if is_pdf:
        is_valid, error_msg = validate_pdf_file(file_path)
        if not is_valid:
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid PDF file: {error_msg}"
            )
    elif is_image:
        if not imghdr.what(file_path):
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
    # Create database record (add file_type)
    file_record = create_file_record(
        db=db,
        user_id=current_user.id,
        original_filename=file.filename,
        file_size=len(file_content),
        file_hash=file_hash,
        file_path=file_path,
        file_type='image' if is_image else 'pdf'
    )
    return FileUploadResponse(
        id=file_record.id,
        original_filename=file_record.original_filename,
        file_size=file_record.file_size,
        status=file_record.status,
        created_at=file_record.created_at
    )

@router.get("/{file_id}/preview")
async def preview_file_tables(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a preview of tables in the uploaded PDF"""
    
    # Quick validation for performance
    if file_id > 1000:  # Reasonable upper bound
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File ID {file_id} is invalid"
        )
    
    # Get file record
    file_record = get_file_by_id(db, file_id, current_user.id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Get table preview based on file type
    if file_record.file_type == 'image':
        # For images, create a simple preview
        preview_data = {
            "tables_found": 1,
            "tables": [{
                "table_number": 1,
                "rows": 0,  # Use 0 instead of "unknown" to avoid type error
                "columns": ["Content"],
                "sample_data": [{"Content": "Image content will be processed during extraction"}]
            }]
        }
    else:
        # For PDFs, provide optimized preview based on processing status
        try:
            # Check if file exists
            if not os.path.exists(file_record.input_file_path):
                preview_data = {
                    "tables_found": 0,
                    "tables": [],
                    "error": f"File not found at {file_record.input_file_path}"
                }
            else:
                if file_record.status == FileStatus.COMPLETED and file_record.tables_found > 0:
                    # For completed files with tables, show metadata-based preview (fast)
                    preview_data = {
                        "tables_found": file_record.tables_found or 0,
                        "tables": [
                            {
                                "table_number": i + 1,
                                "rows": "Available",  # Don't count actual rows for speed
                                "columns": ["Data available - click 'Edit Tables' to view"],
                                "sample_data": [["Click 'Edit Tables' to view and modify table data"]]
                            }
                            for i in range(min(file_record.tables_found, 3))  # Show max 3 table previews
                        ],
                        "total_rows": file_record.total_rows or 0,
                        "processing_completed": True,
                        "preview_note": f"Found {file_record.tables_found} table{'s' if file_record.tables_found > 1 else ''} with {file_record.total_rows or 0} total rows. Click 'Edit Tables' for full access."
                    }
                elif file_record.status == FileStatus.COMPLETED:
                    # Completed but no tables found
                    preview_data = {
                        "tables_found": 0,
                        "tables": [],
                        "processing_completed": True,
                        "preview_note": "Processing completed. No tables were found in this PDF."
                    }
                else:
                    # For non-completed files, show basic PDF info (fast)
                    try:
                        import PyPDF2
                        with open(file_record.input_file_path, 'rb') as file:
                            reader = PyPDF2.PdfReader(file)
                            page_count = len(reader.pages)
                            
                            preview_data = {
                                "tables_found": 0,
                                "tables": [],
                                "page_count": page_count,
                                "file_size_mb": round(file_record.file_size / (1024*1024), 2),
                                "preview_note": f"PDF with {page_count} pages. Status: {file_record.status.value.title()}",
                                "status": file_record.status.value
                            }
                    except Exception as pdf_error:
                        print(f"PDF reading error: {pdf_error}")
                        # Minimal fallback
                        preview_data = {
                            "tables_found": 0,
                            "tables": [],
                            "file_size_mb": round(file_record.file_size / (1024*1024), 2),
                            "preview_note": f"File ready. Status: {file_record.status.value.title()}",
                            "status": file_record.status.value
                        }
        except Exception as e:
            # Fallback to basic preview
            print(f"Preview error: {e}")
            preview_data = {
                "tables_found": 0,
                "tables": [],
                "file_size_mb": round(file_record.file_size / (1024*1024), 2) if file_record.file_size else 0,
                "preview_note": "Basic preview available.",
                "error": f"Preview error: {str(e)}"
            }
    
    if preview_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not generate preview for this file"
        )
    
    # Add enhanced metadata
    enhanced_preview = {
        **preview_data,
        "file_info": {
            "id": file_record.id,
            "filename": file_record.original_filename,
            "size": file_record.file_size,
            "uploaded_at": file_record.created_at
        },
        "processing_suggestions": _generate_processing_suggestions(preview_data)
    }
    
    return enhanced_preview

@router.post("/{file_id}/process", response_model=dict)
async def process_file(
    file_id: int,
    process_request: FileProcessRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_processing_quota),
    db: Session = Depends(get_db)
):
    """Start processing a PDF file"""
    
    # Get file record
    file_record = get_file_by_id(db, file_id, current_user.id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if file_record.status != FileStatus.UPLOADED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File cannot be processed. Current status: {file_record.status}"
        )
    
    # Update file record with processing request
    file_record.output_format = OutputFormat(process_request.output_format)
    file_record.status = FileStatus.PROCESSING
    db.commit()
    
    # Start background processing with simple function instead of Celery
    background_tasks.add_task(
        simple_process_pdf,
        file_id=file_id,
        user_id=current_user.id,
        output_format=process_request.output_format,
        db=db
    )
    
    # Calculate estimated time based on file size (more accurate)
    file_size_mb = file_record.file_size / (1024 * 1024)
    if file_size_mb < 1:
        estimated_time = "30-60 seconds"
    elif file_size_mb < 5:
        estimated_time = "1-2 minutes"
    elif file_size_mb < 10:
        estimated_time = "2-3 minutes"
    else:
        estimated_time = "3-5 minutes"
    
    return {
        "message": "File processing started",
        "file_id": file_id,
        "status": "processing",
        "estimated_time": estimated_time,
        "file_size_mb": round(file_size_mb, 1)
    }

@router.get("/{file_id}/status", response_model=ProcessedFileResponse)
async def get_file_status(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get processing status of a file"""
    
    file_record = get_file_by_id(db, file_id, current_user.id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Generate download URL if file is completed
    download_url = None
    if file_record.status == FileStatus.COMPLETED and file_record.output_file_path:
        download_url = f"/api/files/{file_id}/download"
    
    return ProcessedFileResponse(
        id=file_record.id,
        original_filename=file_record.original_filename,
        file_size=file_record.file_size,
        status=file_record.status,
        output_format=file_record.output_format,
        tables_found=file_record.tables_found,
        total_rows=file_record.total_rows,
        processing_time=file_record.processing_time,
        error_message=file_record.error_message,
        created_at=file_record.created_at,
        completed_at=file_record.completed_at,
        download_url=download_url
    )


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download processed file - reflects current state of edited tables"""
    from fastapi.responses import FileResponse
    from app.models.database import EditableTableData
    import tempfile
    import pandas as pd
    import time
    
    file_record = get_file_by_id(db, file_id, current_user.id)
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if file_record.status != FileStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File processing not completed"
        )
    
    # Check if there are editable tables for this file
    editable_tables = db.query(EditableTableData).filter(
        EditableTableData.file_id == file_id
    ).all()
    
    output_file_path = file_record.output_file_path
    
    # If there are editable tables, regenerate the file with current data
    if editable_tables:
        try:
            export_format = "excel" if file_record.output_format == OutputFormat.EXCEL else "csv"
            file_extension = "xlsx" if export_format == "excel" else "csv"
            tmp_filename = f"download_{file_id}_{int(time.time())}.{file_extension}"
            tmp_file_path = os.path.join(tempfile.gettempdir(), tmp_filename)
            
            if export_format == "excel":
                if len(editable_tables) == 1:
                    # Single table
                    table = editable_tables[0]
                    table_data = table.edited_data
                    table_headers = table.headers
                    
                    if isinstance(table_data, str):
                        import json
                        table_data = json.loads(table_data)
                    if isinstance(table_headers, str):
                        import json
                        table_headers = json.loads(table_headers)
                    
                    df = pd.DataFrame(table_data, columns=table_headers)
                    df.to_excel(tmp_file_path, sheet_name='Data', index=False)
                else:
                    # Multiple tables - combine them
                    combined_data = []
                    for table in editable_tables:
                        table_data = table.edited_data
                        table_headers = table.headers
                        
                        if isinstance(table_data, str):
                            import json
                            table_data = json.loads(table_data)
                        if isinstance(table_headers, str):
                            import json
                            table_headers = json.loads(table_headers)
                        
                        df = pd.DataFrame(table_data, columns=table_headers)
                        df['source_table'] = table.table_name or f"Table_{table.table_index + 1}"
                        combined_data.append(df)
                    
                    combined_df = pd.concat(combined_data, ignore_index=True)
                    combined_df.to_excel(tmp_file_path, sheet_name='Data', index=False)
                    
            else:  # CSV
                if len(editable_tables) == 1:
                    # Single table
                    table = editable_tables[0]
                    table_data = table.edited_data
                    table_headers = table.headers
                    
                    if isinstance(table_data, str):
                        import json
                        table_data = json.loads(table_data)
                    if isinstance(table_headers, str):
                        import json
                        table_headers = json.loads(table_headers)
                    
                    df = pd.DataFrame(table_data, columns=table_headers)
                    df.to_csv(tmp_file_path, index=False)
                else:
                    # Multiple tables - combine them
                    combined_data = []
                    for table in editable_tables:
                        table_data = table.edited_data
                        table_headers = table.headers
                        
                        if isinstance(table_data, str):
                            import json
                            table_data = json.loads(table_data)
                        if isinstance(table_headers, str):
                            import json
                            table_headers = json.loads(table_headers)
                        
                        df = pd.DataFrame(table_data, columns=table_headers)
                        df['source_table'] = table.table_name or f"Table_{table.table_index + 1}"
                        combined_data.append(df)
                    
                    combined_df = pd.concat(combined_data, ignore_index=True)
                    combined_df.to_csv(tmp_file_path, index=False)
            
            output_file_path = tmp_file_path
            
        except Exception as e:
            # Fall back to original file if regeneration fails
            print(f"Warning: Failed to regenerate file with current table data: {e}")
            output_file_path = file_record.output_file_path
    
    # Verify the file exists
    if not output_file_path or not os.path.exists(output_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output file not found"
        )
    
    # Determine filename and media type
    base_name = os.path.splitext(file_record.original_filename)[0]
    if file_record.output_format == OutputFormat.EXCEL:
        filename = f"{base_name}_tables.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif file_record.output_format == OutputFormat.CSV:
        filename = f"{base_name}_tables.csv"
        media_type = "text/csv"
    else:
        filename = f"{base_name}_tables.zip"
        media_type = "application/zip"
    
    return FileResponse(
        path=output_file_path,
        filename=filename,
        media_type=media_type
    )

@router.get("/", response_model=List[ProcessedFileResponse])
async def list_files(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List user's processed files"""
    
    files = get_user_files(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status_filter=status_filter
    )
    
    result = []
    for file_record in files:
        download_url = None
        if file_record.status == FileStatus.COMPLETED and file_record.output_file_path:
            download_url = f"/api/files/{file_record.id}/download"
        
        result.append(ProcessedFileResponse(
            id=file_record.id,
            original_filename=file_record.original_filename,
            file_size=file_record.file_size,
            status=file_record.status,
            output_format=file_record.output_format,
            tables_found=file_record.tables_found,
            total_rows=file_record.total_rows,
            processing_time=file_record.processing_time,
            error_message=file_record.error_message,
            created_at=file_record.created_at,
            completed_at=file_record.completed_at,
            download_url=download_url
        ))
    
    return result

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a processed file"""
    
    print(f"[DELETE] Attempting to delete file {file_id} for user {current_user.id}")
    
    try:
        file_record = get_file_by_id(db, file_id, current_user.id)
        print(f"[DELETE] get_file_by_id returned: {file_record}")
        
        if not file_record:
            print(f"[DELETE] File {file_id} not found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_id} not found for user {current_user.id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DELETE] Exception in get_file_by_id: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    # Delete physical files
    if os.path.exists(file_record.input_file_path):
        os.remove(file_record.input_file_path)
    
    if file_record.output_file_path and os.path.exists(file_record.output_file_path):
        os.remove(file_record.output_file_path)
    
    # Delete database record
    delete_file_record(db, file_id)
    
    return {"message": "File deleted successfully"}

@router.post("/bulk-delete")
async def bulk_delete_files(
    request: BulkDeleteRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete multiple files at once"""
    
    if not request.file_ids:
        raise HTTPException(status_code=400, detail="No file IDs provided")
    
    if len(request.file_ids) > 50:  # Reasonable limit
        raise HTTPException(status_code=400, detail="Cannot delete more than 50 files at once")
    
    deleted_files = []
    failed_files = []
    
    for file_id in request.file_ids:
        try:
            # Verify file exists and belongs to user
            file_record = get_file_by_id(db, file_id, current_user.id)
            if not file_record:
                failed_files.append({"file_id": file_id, "error": "File not found"})
                continue
            
            # Delete physical files
            try:
                if os.path.exists(file_record.input_file_path):
                    os.remove(file_record.input_file_path)
                if file_record.output_file_path and os.path.exists(file_record.output_file_path):
                    os.remove(file_record.output_file_path)
            except Exception as e:
                # Don't fail the operation for disk errors, just log
                pass
            
            # Delete from database
            delete_file_record(db, file_id)
            deleted_files.append({
                "file_id": file_id,
                "filename": file_record.original_filename
            })
            
        except Exception as e:
            failed_files.append({
                "file_id": file_id, 
                "error": str(e)
            })
    
    return {
        "message": f"Bulk delete completed: {len(deleted_files)} files deleted, {len(failed_files)} failed",
        "deleted_files": deleted_files,
        "failed_files": failed_files,
        "total_deleted": len(deleted_files),
        "total_failed": len(failed_files)
    }

@router.get("/dashboard/stats", response_model=DashboardResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard statistics"""
    
    # Calculate tier limits
    tier_limits = {
        "free": 5,
        "basic": 50,
        "pro": 200,
        "enterprise": -1
    }
    
    user_limit = tier_limits.get(current_user.tier.value, 5)
    remaining = max(0, user_limit - current_user.files_processed_this_month) if user_limit != -1 else -1
    
    # Get recent files
    recent_files_query = db.query(ProcessedFile).filter(
        ProcessedFile.user_id == current_user.id
    ).order_by(ProcessedFile.created_at.desc()).limit(5)
    
    recent_files = []
    for file_record in recent_files_query:
        download_url = None
        if file_record.status == FileStatus.COMPLETED and file_record.output_file_path:
            download_url = f"/api/files/{file_record.id}/download"
        
        recent_files.append(RecentFile(
            id=file_record.id,
            original_filename=file_record.original_filename,
            status=file_record.status,
            tables_found=file_record.tables_found,
            created_at=file_record.created_at,
            download_url=download_url
        ))
    
    # Calculate files processed today
    from datetime import date
    today = date.today()
    files_today = db.query(ProcessedFile).filter(
        ProcessedFile.user_id == current_user.id,
        ProcessedFile.created_at >= today
    ).count()
    
    user_stats = UserStats(
        files_processed_today=files_today,
        files_processed_this_month=current_user.files_processed_this_month,
        total_files_processed=current_user.total_files_processed,
        tier=current_user.tier,
        tier_limit=user_limit,
        remaining_files=remaining
    )
    
    return DashboardResponse(
        user_stats=user_stats,
        recent_files=recent_files
    )

def _generate_processing_suggestions(preview_data: dict) -> dict:
    """Generate intelligent processing suggestions based on preview data"""
    
    suggestions = {
        "recommended_format": "excel",
        "complexity_score": "medium",
        "estimated_time": "2-5 minutes",
        "tips": []
    }
    
    if not preview_data.get("tables"):
        return suggestions
    
    total_tables = len(preview_data["tables"])
    total_rows = sum(table.get("rows", 0) if isinstance(table.get("rows", 0), int) else 0 for table in preview_data["tables"])
    
    # Analyze complexity
    if total_tables == 1 and total_rows < 100:
        suggestions["complexity_score"] = "low"
        suggestions["estimated_time"] = "30-60 seconds"
    elif total_tables > 5 or total_rows > 1000:
        suggestions["complexity_score"] = "high"
        suggestions["estimated_time"] = "5-10 minutes"
    
    # Format recommendations
    if total_tables > 1:
        suggestions["recommended_format"] = "excel"
        suggestions["tips"].append("Excel format recommended for multiple tables")
    
    # Add tips based on table structure
    for table in preview_data["tables"]:
        columns = table.get("columns", [])
        if any(col.isdigit() for col in columns):
            suggestions["tips"].append("Intelligent column mapping will be applied")
            break
    
    if total_rows > 500:
        suggestions["tips"].append("Large dataset detected - processing may take longer")
    
    return suggestions

# ==================== TABLE EDITOR ENDPOINTS ====================

@router.get("/{file_id}/tables", response_model=List[dict])
async def get_file_tables_for_editing(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tables from a processed file for editing"""
    from app.models.database import EditableTableData
    import json
    
    # Get the file and verify ownership with early validation
    print(f"[TABLES] Requesting tables for file_id={file_id}, user_id={current_user.id}")
    
    # Quick validation to avoid processing non-existent files
    if file_id > 1000:  # Reasonable upper bound for file IDs
        raise HTTPException(
            status_code=404,
            detail=f"File ID {file_id} is invalid"
        )
    
    file = get_file_by_id(db, file_id, current_user.id)
    if not file:
        print(f"[TABLES] File {file_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=404,
            detail="File not found or access denied"
        )
    
    if file.status != FileStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="File must be processed before editing tables"
        )
    
    # Check if we have editable tables already
    editable_tables = db.query(EditableTableData).filter(
        EditableTableData.file_id == file_id
    ).all()
    
    if editable_tables:
        # Return existing editable tables
        return [
            {
                "table_index": table.table_index,
                "table_name": table.table_name,
                "data": table.edited_data,
                "headers": table.headers,
                "rows_count": table.rows_count,
                "columns_count": table.columns_count,
                "has_changes": table.has_changes,
                "id": table.id
            }
            for table in editable_tables
        ]
    else:
        # Create editable tables from processed file
        try:
            print(f"[TABLES] Creating editable tables for file_id={file_id}")
            
            # Check if file actually has tables
            if file.tables_found == 0:
                print(f"[TABLES] File {file_id} has no tables, returning empty list")
                return []
            
            # Verify file exists on disk
            if not os.path.exists(file.input_file_path):
                print(f"[TABLES] File path does not exist: {file.input_file_path}")
                raise HTTPException(
                    status_code=404,
                    detail=f"File not found on disk: {file.input_file_path}"
                )
            
            # Get table data - use optimized approach
            print(f"[TABLES] Creating editable tables for file with {file.tables_found} table(s)")
            
            # Try to use cached data first, then extract if needed
            try:
                # Check for existing cache first (faster)
                cache_dir = os.path.join(os.path.dirname(file.input_file_path), '.preview_cache')
                if os.path.exists(cache_dir):
                    import glob
                    cache_files = glob.glob(os.path.join(cache_dir, f"preview_*.json"))
                    if cache_files:
                        # Use the most recent cache file
                        latest_cache = max(cache_files, key=os.path.getmtime)
                        try:
                            with open(latest_cache, 'r') as f:
                                import json
                                preview_data = json.load(f)
                                print(f"[TABLES] Using cached data from {os.path.basename(latest_cache)}")
                        except:
                            preview_data = None
                    else:
                        preview_data = None
                else:
                    preview_data = None
                
                # If no cache or cache failed, extract fresh data (but limit rows for performance)
                if not preview_data or not preview_data.get("tables"):
                    print(f"[TABLES] No cache available, extracting fresh data with limited rows")
                    preview_data = get_table_preview(file.input_file_path, max_rows=50)  # Reduced from 100
                    print(f"[TABLES] Fresh extraction: tables_found={preview_data.get('tables_found', 0)}")
                    
            except Exception as extract_error:
                print(f"[TABLES] Error in extraction process: {extract_error}")
                # Create fallback tables based on file metadata
                preview_data = {
                    "tables_found": file.tables_found,
                    "tables": [
                        {
                            "table_number": i + 1,
                            "columns": [f"Column {j+1}" for j in range(5)],  # 5 default columns
                            "sample_data": [
                                [f"Table {i+1} Data"] + [""] * 4,
                                [""] * 5,
                                [""] * 5
                            ]
                        }
                        for i in range(file.tables_found)
                    ]
                }
                print(f"[TABLES] Using fallback data structure with {file.tables_found} tables")
            
            if not preview_data or not preview_data.get("tables"):
                print(f"[TABLES] No table data found in preview")
                return []
            
            created_tables = []
            for i, table in enumerate(preview_data.get("tables", [])):
                print(f"[TABLES] Processing table {i+1}")
                
                # Convert sample data to proper format
                sample_data = table.get("sample_data", [])
                headers = table.get("columns", [])
                
                print(f"[TABLES] Table {i+1}: headers={len(headers)}, sample_data={len(sample_data)}")
                
                # Convert dict records to list of lists
                if sample_data and isinstance(sample_data[0], dict):
                    data = []
                    for row in sample_data:
                        data.append([str(row.get(col, "")) for col in headers])
                else:
                    data = [[str(cell) for cell in row] for row in sample_data]
                
                print(f"[TABLES] Table {i+1}: converted to {len(data)} rows")
                
                # Create editable table record
                editable_table = EditableTableData(
                    file_id=file_id,
                    table_index=i,
                    table_name=f"Table {i + 1}",
                    original_data=data,
                    edited_data=data,
                    headers=headers,
                    rows_count=len(data),
                    columns_count=len(headers) if headers else 0,
                    has_changes=False
                )
                
                try:
                    db.add(editable_table)
                    db.commit()
                    db.refresh(editable_table)
                    print(f"[TABLES] Successfully created editable table {i+1} with ID {editable_table.id}")
                except Exception as db_error:
                    print(f"[TABLES] Database error creating table {i+1}: {db_error}")
                    db.rollback()
                    raise
                
                created_tables.append({
                    "table_index": editable_table.table_index,
                    "table_name": editable_table.table_name,
                    "data": editable_table.edited_data,
                    "headers": editable_table.headers,
                    "rows_count": editable_table.rows_count,
                    "columns_count": editable_table.columns_count,
                    "has_changes": editable_table.has_changes,
                    "id": editable_table.id
                })
            
            print(f"[TABLES] Successfully created {len(created_tables)} editable tables")
            return created_tables
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions as-is
        except Exception as e:
            print(f"[TABLES] Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Error creating editable tables: {str(e)}"
            )

@router.put("/{file_id}/tables/{table_index}")
async def update_table_data(
    file_id: int,
    table_index: int,
    update_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update table data"""
    from app.models.database import EditableTableData
    
    # Verify file ownership
    file = get_file_by_id(db, file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found or access denied"
        )
    
    # Get the editable table
    editable_table = db.query(EditableTableData).filter(
        EditableTableData.file_id == file_id,
        EditableTableData.table_index == table_index
    ).first()
    
    if not editable_table:
        raise HTTPException(
            status_code=404,
            detail="Table not found"
        )
    
    # Update the table data
    if "data" in update_data:
        editable_table.edited_data = update_data["data"]
        editable_table.rows_count = len(update_data["data"])
        editable_table.has_changes = True
    
    if "headers" in update_data:
        editable_table.headers = update_data["headers"]
        editable_table.columns_count = len(update_data["headers"])
    
    if "table_name" in update_data:
        editable_table.table_name = update_data["table_name"]
    
    editable_table.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(editable_table)
    
    return {
        "message": "Table updated successfully",
        "table_id": editable_table.id,
        "has_changes": editable_table.has_changes
    }

@router.post("/{file_id}/tables/{table_index}/cell")
async def update_table_cell(
    file_id: int,
    table_index: int,
    cell_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a single cell in a table"""
    from app.models.database import EditableTableData
    
    # Verify file ownership
    file = get_file_by_id(db, file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found or access denied"
        )
    
    # Get the editable table
    editable_table = db.query(EditableTableData).filter(
        EditableTableData.file_id == file_id,
        EditableTableData.table_index == table_index
    ).first()
    
    if not editable_table:
        raise HTTPException(
            status_code=404,
            detail="Table not found"
        )
    
    # Extract cell update data
    row_index = cell_update.get("row_index")
    col_index = cell_update.get("col_index") 
    value = cell_update.get("value", "")
    
    # Update the cell
    try:
        # Get current data (SQLAlchemy JSON column should return as list directly)
        current_data = editable_table.edited_data
        
        # If it's somehow a string, parse it
        if isinstance(current_data, str):
            import json
            current_data = json.loads(current_data)
        
        # Ensure we have a mutable list
        current_data = list(current_data) if current_data else []
            
        if row_index < len(current_data) and col_index < len(current_data[row_index]):
            # Save current state as previous state for undo (deep copy for nested lists)
            import copy
            editable_table.previous_data = copy.deepcopy(current_data)
            
            # Update the cell
            current_data[row_index][col_index] = str(value)
            editable_table.edited_data = current_data
            editable_table.has_changes = True
            editable_table.updated_at = datetime.utcnow()
            
            # Mark the JSON fields as modified so SQLAlchemy knows to save them
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(editable_table, "edited_data")
            flag_modified(editable_table, "previous_data")
            
            # Flush and commit the changes immediately
            db.flush()
            db.commit()
            
            # Force a refresh of the object to clear any caching
            db.refresh(editable_table)
            
            return {
                "message": "Cell updated successfully",
                "row_index": row_index,
                "col_index": col_index,
                "value": value
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid cell coordinates"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating cell: {str(e)}"
        )

@router.post("/{file_id}/tables/{table_index}/row")
async def manage_table_row(
    file_id: int,
    table_index: int,
    operation_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add or delete rows in a table"""
    from app.models.database import EditableTableData
    
    # Verify file ownership
    file = get_file_by_id(db, file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found or access denied"
        )
    
    # Get the editable table
    editable_table = db.query(EditableTableData).filter(
        EditableTableData.file_id == file_id,
        EditableTableData.table_index == table_index
    ).first()
    
    if not editable_table:
        raise HTTPException(
            status_code=404,
            detail="Table not found"
        )
    
    operation = operation_data.get("operation")
    index = operation_data.get("index", 0)
    
    try:
        # Get current data (SQLAlchemy JSON column should return as list directly)
        current_data = editable_table.edited_data
        
        # If it's somehow a string, parse it
        if isinstance(current_data, str):
            import json
            current_data = json.loads(current_data)
        
        # Ensure we have a mutable list
        current_data = list(current_data) if current_data else []
        
        # Save current state as previous state for undo (deep copy for nested lists)
        import copy
        editable_table.previous_data = copy.deepcopy(current_data)
        
        if operation == "add_row":
            # Add empty row at specified index
            new_row = [""] * editable_table.columns_count
            if "data" in operation_data:
                new_row = operation_data["data"][:editable_table.columns_count]
            
            current_data.insert(index, new_row)
            
        elif operation == "delete_row":
            # Delete row at specified index
            if 0 <= index < len(current_data):
                current_data.pop(index)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid row index"
                )
        
        # Update the table with the modified data
        editable_table.edited_data = current_data
        editable_table.rows_count = len(current_data)
        editable_table.has_changes = True
        editable_table.updated_at = datetime.utcnow()
        
        # Mark the JSON fields as modified so SQLAlchemy knows to save them
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(editable_table, "edited_data")
        flag_modified(editable_table, "previous_data")
        
        # Flush and commit the changes immediately
        db.flush()
        db.commit()
        
        # Force a refresh of the object to clear any caching
        db.refresh(editable_table)
        
        return {
            "message": f"Row {operation} completed successfully",
            "operation": operation,
            "index": index,
            "new_row_count": len(current_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing row operation: {str(e)}"
        )

@router.post("/{file_id}/export-edited")
async def export_edited_tables(
    file_id: int,
    export_request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export tables with edited data"""
    from app.models.database import EditableTableData
    import tempfile
    import pandas as pd
    import time
    
    print(f"[EXPORT] Starting export for file_id={file_id}, user_id={current_user.id}")
    
    # Verify file ownership
    try:
        file = get_file_by_id(db, file_id, current_user.id)
        print(f"[EXPORT] get_file_by_id result: {file}")
        if not file:
            print(f"[EXPORT] File {file_id} not found for user {current_user.id}")
            raise HTTPException(
                status_code=404,
                detail="File not found or access denied"
            )
    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        print(f"[EXPORT] Error in get_file_by_id: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    
    # Get editable tables with fresh data
    try:
        print(f"[EXPORT] Querying editable tables for file_id={file_id}")
        editable_tables = db.query(EditableTableData).filter(
            EditableTableData.file_id == file_id
        ).all()
        print(f"[EXPORT] Found {len(editable_tables)} editable tables")
        
        # Force refresh of all table objects to get latest data
        for table in editable_tables:
            db.refresh(table)
            print(f"[EXPORT] Refreshed table {table.table_index}: {table.table_name}, rows: {table.rows_count}, changes: {table.has_changes}")
        
        if not editable_tables:
            print(f"[EXPORT] No editable tables found for file {file_id}")
            raise HTTPException(
                status_code=404,
                detail="No editable tables found for this file"
            )
    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        print(f"[EXPORT] Error querying editable tables: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error while querying tables: {str(e)}"
        )
    
    export_format = export_request.get("format", "excel")
    selected_tables = export_request.get("selected_tables", [])
    
    try:
        # Filter tables if specific tables are selected
        if selected_tables:
            tables_to_export = [
                table for table in editable_tables
                if table.table_index in selected_tables
            ]
        else:
            tables_to_export = editable_tables
        
        # Generate export file using a more reliable approach
        import os
        file_extension = "xlsx" if export_format == "excel" else export_format
        tmp_filename = f"export_{file_id}_{int(time.time())}.{file_extension}"
        tmp_file_path = os.path.join(tempfile.gettempdir(), tmp_filename)
        
        try:
            if export_format == "excel":
                # Create Excel file with consolidated data (same as CSV behavior)
                if len(tables_to_export) == 1:
                    # Single table case
                    table = tables_to_export[0]
                    
                    # Handle both list and JSON string formats
                    table_data = table.edited_data
                    table_headers = table.headers
                    
                    if isinstance(table_data, str):
                        import json
                        table_data = json.loads(table_data)
                    if isinstance(table_headers, str):
                        import json
                        table_headers = json.loads(table_headers)
                    
                    print(f"[EXPORT EXCEL] Single table: {table.table_name}, rows: {len(table_data)}")
                    
                    # Fix column mismatch by adjusting headers to match data
                    if table_data and len(table_data) > 0:
                        data_columns = len(table_data[0])
                        header_columns = len(table_headers)
                        
                        if data_columns != header_columns:
                            print(f"[EXPORT EXCEL] Column mismatch: {header_columns} headers vs {data_columns} data columns")
                            
                            if data_columns > header_columns:
                                # Add generic headers for extra columns
                                for i in range(header_columns, data_columns):
                                    table_headers.append(f"Column_{i+1}")
                                print(f"[EXPORT EXCEL] Added generic headers: {table_headers}")
                            elif data_columns < header_columns:
                                # Truncate headers to match data
                                table_headers = table_headers[:data_columns]
                                print(f"[EXPORT EXCEL] Truncated headers: {table_headers}")
                    
                    df = pd.DataFrame(table_data, columns=table_headers)
                    df.to_excel(tmp_file_path, sheet_name='Data', index=False)
                else:
                    # Multiple tables - combine them all (same as CSV)
                    combined_data = []
                    for table in tables_to_export:
                        # Handle both list and JSON string formats
                        table_data = table.edited_data
                        table_headers = table.headers
                        
                        if isinstance(table_data, str):
                            import json
                            table_data = json.loads(table_data)
                        if isinstance(table_headers, str):
                            import json
                            table_headers = json.loads(table_headers)
                        
                        print(f"[EXPORT EXCEL] Combining table: {table.table_name}, rows: {len(table_data)}")
                        
                        # Fix column mismatch by adjusting headers to match data
                        if table_data and len(table_data) > 0:
                            data_columns = len(table_data[0])
                            header_columns = len(table_headers)
                            
                            if data_columns != header_columns:
                                print(f"[EXPORT EXCEL] Column mismatch: {header_columns} headers vs {data_columns} data columns")
                                
                                if data_columns > header_columns:
                                    # Add generic headers for extra columns
                                    for i in range(header_columns, data_columns):
                                        table_headers.append(f"Column_{i+1}")
                                    print(f"[EXPORT EXCEL] Added generic headers: {table_headers}")
                                elif data_columns < header_columns:
                                    # Truncate headers to match data
                                    table_headers = table_headers[:data_columns]
                                    print(f"[EXPORT EXCEL] Truncated headers: {table_headers}")
                        
                        df = pd.DataFrame(table_data, columns=table_headers)
                        df['source_table'] = table.table_name or f"Table_{table.table_index + 1}"
                        combined_data.append(df)
                    
                    # Use robust concatenation that handles different table structures
                    if len(combined_data) == 1:
                        combined_df = combined_data[0]
                    else:
                        # For multiple tables with different structures, use concat with sort=False
                        combined_df = pd.concat(combined_data, ignore_index=True, sort=False)
                        # Fill NaN values with empty strings for better Excel output
                        combined_df = combined_df.fillna('')
                    
                    print(f"[EXPORT EXCEL] Combined Excel: {len(combined_df)} total rows, {len(combined_df.columns)} columns")
                    print(f"[EXPORT EXCEL] Final columns: {list(combined_df.columns)}")
                    combined_df.to_excel(tmp_file_path, sheet_name='Data', index=False)
                        
            elif export_format == "csv":
                # For CSV, combine all tables or export the first one
                if len(tables_to_export) == 1:
                    table = tables_to_export[0]
                    
                    # Handle both list and JSON string formats
                    table_data = table.edited_data
                    table_headers = table.headers
                    
                    if isinstance(table_data, str):
                        import json
                        table_data = json.loads(table_data)
                    if isinstance(table_headers, str):
                        import json
                        table_headers = json.loads(table_headers)
                    
                    print(f"[EXPORT CSV] Single table: {table.table_name}, rows: {len(table_data)}")
                    
                    # Fix column mismatch by adjusting headers to match data
                    if table_data and len(table_data) > 0:
                        data_columns = len(table_data[0])
                        header_columns = len(table_headers)
                        
                        if data_columns != header_columns:
                            print(f"[EXPORT CSV] Column mismatch: {header_columns} headers vs {data_columns} data columns")
                            
                            if data_columns > header_columns:
                                # Add generic headers for extra columns
                                for i in range(header_columns, data_columns):
                                    table_headers.append(f"Column_{i+1}")
                                print(f"[EXPORT CSV] Added generic headers: {table_headers}")
                            elif data_columns < header_columns:
                                # Truncate headers to match data
                                table_headers = table_headers[:data_columns]
                                print(f"[EXPORT CSV] Truncated headers: {table_headers}")
                    
                    df = pd.DataFrame(table_data, columns=table_headers)
                    df.to_csv(tmp_file_path, index=False)
                else:
                    # Combine all tables
                    combined_data = []
                    for table in tables_to_export:
                        # Handle both list and JSON string formats
                        table_data = table.edited_data
                        table_headers = table.headers
                        
                        if isinstance(table_data, str):
                            import json
                            table_data = json.loads(table_data)
                        if isinstance(table_headers, str):
                            import json
                            table_headers = json.loads(table_headers)
                        
                        print(f"[EXPORT CSV] Combining table: {table.table_name}, rows: {len(table_data)}")
                        print(f"[EXPORT CSV] Table headers: {table_headers}")
                        print(f"[EXPORT CSV] Table data preview: {table_data[:2] if table_data else 'None'}")
                        
                        try:
                            # Fix column mismatch by adjusting headers to match data
                            if table_data and len(table_data) > 0:
                                data_columns = len(table_data[0])
                                header_columns = len(table_headers)
                                
                                if data_columns != header_columns:
                                    print(f"[EXPORT CSV] Column mismatch: {header_columns} headers vs {data_columns} data columns")
                                    
                                    if data_columns > header_columns:
                                        # Add generic headers for extra columns
                                        for i in range(header_columns, data_columns):
                                            table_headers.append(f"Column_{i+1}")
                                        print(f"[EXPORT CSV] Added generic headers: {table_headers}")
                                    elif data_columns < header_columns:
                                        # Truncate headers to match data
                                        table_headers = table_headers[:data_columns]
                                        print(f"[EXPORT CSV] Truncated headers: {table_headers}")
                            
                            df = pd.DataFrame(table_data, columns=table_headers)
                            df['source_table'] = table.table_name or f"Table_{table.table_index + 1}"
                            combined_data.append(df)
                            print(f"[EXPORT CSV] Successfully created DataFrame for {table.table_name}")
                        except Exception as df_error:
                            print(f"[EXPORT CSV] Error creating DataFrame for {table.table_name}: {df_error}")
                            raise
                    
                    print(f"[EXPORT CSV] About to concatenate {len(combined_data)} DataFrames")
                    try:
                        # Instead of concatenating with mismatched structures, 
                        # let's use a more robust approach that preserves table structure
                        if len(combined_data) == 1:
                            combined_df = combined_data[0]
                        else:
                            # For multiple tables with different structures, use concat with sort=False
                            # to preserve original column order and fill missing values with empty strings
                            combined_df = pd.concat(combined_data, ignore_index=True, sort=False)
                            # Fill NaN values with empty strings for better CSV output
                            combined_df = combined_df.fillna('')
                        
                        print(f"[EXPORT CSV] Combined CSV: {len(combined_df)} total rows, {len(combined_df.columns)} columns")
                        print(f"[EXPORT CSV] Final columns: {list(combined_df.columns)}")
                    except Exception as concat_error:
                        print(f"[EXPORT CSV] Error concatenating DataFrames: {concat_error}")
                        raise
                    
                    print(f"[EXPORT CSV] About to save to: {tmp_file_path}")
                    try:
                        combined_df.to_csv(tmp_file_path, index=False)
                        print(f"[EXPORT CSV] Successfully saved CSV to {tmp_file_path}")
                    except Exception as save_error:
                        print(f"[EXPORT CSV] Error saving CSV: {save_error}")
                        raise
            
            # Return the file directly instead of just metadata
            from fastapi.responses import FileResponse
            
            # Determine filename and media type
            base_name = os.path.splitext(file.original_filename)[0]
            if export_format == "excel":
                filename = f"{base_name}_edited.xlsx"
                media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                filename = f"{base_name}_edited.csv"
                media_type = "text/csv"
            
            return FileResponse(
                path=tmp_file_path,
                filename=filename,
                media_type=media_type
            )
        except Exception as inner_e:
            # Clean up the temp file if there was an error
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
            raise inner_e
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting edited tables: {str(e)}"
        )

@router.post("/{file_id}/tables/{table_index}/reset")
async def reset_table_to_original(
    file_id: int,
    table_index: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reset table to its original state"""
    from app.models.database import EditableTableData
    
    # Verify file ownership
    file = get_file_by_id(db, file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found or access denied"
        )
    
    # Get the editable table
    editable_table = db.query(EditableTableData).filter(
        EditableTableData.file_id == file_id,
        EditableTableData.table_index == table_index
    ).first()
    
    if not editable_table:
        raise HTTPException(
            status_code=404,
            detail="Table not found"
        )
    
    try:
        # Reset edited data to original data
        editable_table.edited_data = editable_table.original_data
        editable_table.rows_count = len(editable_table.original_data) if editable_table.original_data else 0
        editable_table.has_changes = False
        editable_table.updated_at = datetime.utcnow()
        
        # Mark the JSON field as modified so SQLAlchemy knows to save it
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(editable_table, "edited_data")
        
        # Commit the changes
        db.commit()
        db.refresh(editable_table)
        
        return {
            "message": "Table reset to original state successfully",
            "table_index": table_index,
            "rows_count": editable_table.rows_count,
            "has_changes": editable_table.has_changes
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting table: {str(e)}"
        )

@router.post("/{file_id}/tables/{table_index}/undo")
async def undo_last_change(
    file_id: int,
    table_index: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Undo the last change made to the table"""
    from app.models.database import EditableTableData
    
    # Verify file ownership
    file = get_file_by_id(db, file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found or access denied"
        )
    
    # Get the editable table
    editable_table = db.query(EditableTableData).filter(
        EditableTableData.file_id == file_id,
        EditableTableData.table_index == table_index
    ).first()
    
    if not editable_table:
        raise HTTPException(
            status_code=404,
            detail="Table not found"
        )
    
    print(f"[UNDO] Table {table_index}: previous_data exists = {editable_table.previous_data is not None}")
    if editable_table.previous_data:
        print(f"[UNDO] Previous data length: {len(editable_table.previous_data)}")
        print(f"[UNDO] Current data length: {len(editable_table.edited_data)}")
    
    if not editable_table.previous_data:
        print(f"[UNDO] No previous data available for table {table_index}")
        raise HTTPException(
            status_code=400,
            detail="No previous state available for undo"
        )
    
    try:
        # Save current state before undoing (in case user wants to redo)
        current_state = editable_table.edited_data
        
        # Restore previous state
        editable_table.edited_data = editable_table.previous_data
        editable_table.rows_count = len(editable_table.previous_data) if editable_table.previous_data else 0
        
        # Check if we're back to original state
        if (editable_table.edited_data == editable_table.original_data):
            editable_table.has_changes = False
        else:
            editable_table.has_changes = True
            
        editable_table.updated_at = datetime.utcnow()
        
        # Clear previous data since we used it
        editable_table.previous_data = None
        
        # Mark the JSON fields as modified so SQLAlchemy knows to save them
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(editable_table, "edited_data")
        flag_modified(editable_table, "previous_data")
        
        # Commit the changes
        db.commit()
        db.refresh(editable_table)
        
        return {
            "message": "Last change undone successfully",
            "table_index": table_index,
            "rows_count": editable_table.rows_count,
            "has_changes": editable_table.has_changes
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error undoing last change: {str(e)}"
        )

@router.post("/{file_id}/tables/{table_index}/columns/bulk-delete")
async def bulk_delete_columns(
    file_id: int,
    table_index: int,
    delete_request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete multiple columns from a table"""
    from app.models.database import EditableTableData
    
    # Verify file ownership
    file = get_file_by_id(db, file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=404,
            detail="File not found or access denied"
        )
    
    # Get the editable table
    editable_table = db.query(EditableTableData).filter(
        EditableTableData.file_id == file_id,
        EditableTableData.table_index == table_index
    ).first()
    
    if not editable_table:
        raise HTTPException(
            status_code=404,
            detail="Table not found"
        )
    
    column_indices = delete_request.get("column_indices", [])
    if not column_indices:
        raise HTTPException(
            status_code=400,
            detail="No column indices provided"
        )
    
    try:
        # Get current data
        current_data = editable_table.edited_data
        current_headers = editable_table.headers
        
        if isinstance(current_data, str):
            import json
            current_data = json.loads(current_data)
        if isinstance(current_headers, str):
            import json
            current_headers = json.loads(current_headers)
        
        # Ensure we have mutable lists
        current_data = [list(row) for row in current_data] if current_data else []
        current_headers = list(current_headers) if current_headers else []
        
        # Save current state as previous state for undo (deep copy for nested lists)
        import copy
        editable_table.previous_data = copy.deepcopy(current_data)
        
        # Validate column indices
        max_col_index = len(current_headers) - 1
        valid_indices = [idx for idx in column_indices if 0 <= idx <= max_col_index]
        
        if not valid_indices:
            raise HTTPException(
                status_code=400,
                detail="No valid column indices provided"
            )
        
        # Sort indices in descending order to delete from right to left
        valid_indices.sort(reverse=True)
        
        # Delete headers
        for col_idx in valid_indices:
            if col_idx < len(current_headers):
                current_headers.pop(col_idx)
        
        # Delete data columns
        for row in current_data:
            for col_idx in valid_indices:
                if col_idx < len(row):
                    row.pop(col_idx)
        
        # Update the table
        editable_table.edited_data = current_data
        editable_table.headers = current_headers
        editable_table.columns_count = len(current_headers)
        editable_table.has_changes = True
        editable_table.updated_at = datetime.utcnow()
        
        # Mark the JSON fields as modified so SQLAlchemy knows to save them
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(editable_table, "edited_data")
        flag_modified(editable_table, "headers")
        flag_modified(editable_table, "previous_data")
        
        # Commit the changes
        db.commit()
        db.refresh(editable_table)
        
        return {
            "message": f"{len(valid_indices)} columns deleted successfully",
            "columns_deleted": len(valid_indices),
            "new_column_count": len(current_headers)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting columns: {str(e)}"
        )