import os
import time
import zipfile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.database import FileStatus
from app.services.file_service import update_file_status, get_file_by_id
from shared.pdf_extractor import extract_tables_with_format
from shared.image_extractor import extract_tables_from_image
from .celery import celery_app as celery

@celery.task(bind=True, max_retries=3)
def process_pdf_task(self, file_id: int, user_id: int, output_format: str):
    """
    Background task to process PDF file and extract tables
    """
    
    db: Session = SessionLocal()
    
    try:
        print(f"[PDF_TASK] Worker Celery recibió tarea para file_id={file_id}, user_id={user_id}, output_format={output_format}")
        # Get file record
        file_record = get_file_by_id(db, file_id, user_id)
        if not file_record:
            print(f"[PDF_TASK][ERROR] File record not found: {file_id}")
            raise Exception(f"File record not found: {file_id}")
        if not os.path.exists(file_record.input_file_path):
            print(f"[PDF_TASK][ERROR] Input file not found: {file_record.input_file_path}")
            raise Exception(f"Input file not found: {file_record.input_file_path}")
        # Update status to processing
        update_file_status(db, file_id, FileStatus.PROCESSING)
        # Generate output file path
        upload_dir = settings.UPLOAD_DIR
        base_name = os.path.splitext(os.path.basename(file_record.original_filename))[0]
        output_base_path = os.path.join(upload_dir, f"{file_id}_{base_name}_tables")
        print(f"[PDF_TASK] Output base path: {output_base_path}")
        # Record start time
        start_time = time.time()
        # Process the file (PDF o imagen)
        try:
            if getattr(file_record, 'file_type', 'pdf') == 'image':
                success = extract_tables_from_image(
                    image_path=file_record.input_file_path,
                    output_path=output_base_path,
                    format_type=output_format
                )
            else:
                success = extract_tables_with_format(
                    pdf_path=file_record.input_file_path,
                    output_path=output_base_path,
                    format_type=output_format
                )
        except Exception as e:
            print(f"[PDF_TASK][ERROR] Exception en extracción: {e}")
            success = False
        print(f"[PDF_TASK] ¿Extracción exitosa?: {success}")
        # Calculate processing time
        processing_time = time.time() - start_time
        if success:
            # Determine final output file path
            final_output_path = _get_final_output_path(output_base_path, output_format)
            print(f"[PDF_TASK] Archivo final generado: {final_output_path}")
            print(f"[PDF_TASK] ¿Existe el archivo?: {os.path.exists(final_output_path)}")
            # Get table statistics
            tables_found, total_rows = _get_table_statistics(final_output_path, output_format)
            # Update file record with success
            update_file_status(
                db=db,
                file_id=file_id,
                status=FileStatus.COMPLETED,
                output_file_path=final_output_path,
                tables_found=tables_found,
                total_rows=total_rows,
                processing_time=processing_time
            )
            
            return {
                "success": True,
                "file_id": file_id,
                "processing_time": processing_time,
                "tables_found": tables_found,
                "total_rows": total_rows
            }
        
        else:
            # Update file record with failure
            update_file_status(
                db=db,
                file_id=file_id,
                status=FileStatus.FAILED,
                processing_time=processing_time,
                error_message="Failed to extract tables from PDF"
            )
            
            return {
                "success": False,
                "file_id": file_id,
                "error": "Failed to extract tables from PDF"
            }
    
    except Exception as exc:
        # Handle retries
        if self.request.retries < self.max_retries:
            # Retry after delay
            raise self.retry(countdown=60, exc=exc)
        
        # Final failure - update database
        processing_time = time.time() - start_time if 'start_time' in locals() else 0
        
        update_file_status(
            db=db,
            file_id=file_id,
            status=FileStatus.FAILED,
            processing_time=processing_time,
            error_message=str(exc)
        )
        
        return {
            "success": False,
            "file_id": file_id,
            "error": str(exc)
        }
    
    finally:
        db.close()

def _get_final_output_path(base_path: str, output_format: str) -> str:
    """Determine the final output file path based on format"""
    
    if output_format == "excel":
        return f"{base_path}.xlsx"
    elif output_format == "csv":
        return f"{base_path}.csv"
    elif output_format == "both":
        # Create a zip file containing both formats
        zip_path = f"{base_path}.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            excel_path = f"{base_path}.xlsx"
            csv_path = f"{base_path}.csv"
            
            if os.path.exists(excel_path):
                zipf.write(excel_path, f"{os.path.basename(base_path)}.xlsx")
            
            if os.path.exists(csv_path):
                zipf.write(csv_path, f"{os.path.basename(base_path)}.csv")
        
        # Clean up individual files
        for path in [excel_path, csv_path]:
            if os.path.exists(path):
                os.remove(path)
        
        return zip_path
    
    return f"{base_path}.xlsx"  # Default fallback

def _get_table_statistics(file_path: str, output_format: str) -> tuple[int, int]:
    """Get statistics about extracted tables"""
    
    try:
        if output_format == "both":
            # For zip files, try to extract Excel file and analyze
            import tempfile
            
            with zipfile.ZipFile(file_path, 'r') as zipf:
                for filename in zipf.namelist():
                    if filename.endswith('.xlsx'):
                        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
                            tmp.write(zipf.read(filename))
                            tmp_path = tmp.name
                        
                        try:
                            import pandas as pd
                            df = pd.read_excel(tmp_path)
                            return 1, len(df)  # Simplified: assume 1 table
                        finally:
                            os.unlink(tmp_path)
            
            return 0, 0
        
        elif output_format == "excel":
            import pandas as pd
            df = pd.read_excel(file_path)
            return 1, len(df)  # Simplified: assume 1 table
        
        elif output_format == "csv":
            import pandas as pd
            df = pd.read_csv(file_path)
            return 1, len(df)  # Simplified: assume 1 table
        
    except Exception as e:
        print(f"Error getting table statistics: {e}")
        return 0, 0
    
    return 0, 0

@celery.task
def cleanup_old_files_task():
    """Periodic task to clean up old files"""
    
    from app.services.file_service import cleanup_old_files
    
    db: Session = SessionLocal()
    
    try:
        deleted_count = cleanup_old_files(db, days_old=30)
        return f"Cleaned up {deleted_count} old files"
    
    except Exception as e:
        return f"Error during cleanup: {str(e)}"
    
    finally:
        db.close()

@celery.task
def reset_monthly_usage_task():
    """Monthly task to reset user processing counts"""
    
    from app.services.user_service import reset_monthly_usage
    
    db: Session = SessionLocal()
    
    try:
        users_updated = reset_monthly_usage(db)
        return f"Reset monthly usage for {users_updated} users"
    
    except Exception as e:
        return f"Error resetting monthly usage: {str(e)}"
    
    finally:
        db.close()

@celery.task
def send_processing_notification(user_email: str, file_name: str, success: bool):
    """Send email notification when processing is complete"""
    
    # TODO: Implement email sending logic
    # For now, just log the notification
    
    status = "completed successfully" if success else "failed"
    message = f"Processing of {file_name} has {status}"
    
    print(f"Email notification to {user_email}: {message}")
    
    return {"email": user_email, "message": message, "sent": False}

# Periodic tasks configuration is now handled in celery.py