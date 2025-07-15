from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import redis
import json
from pathlib import Path

from app.core.database import get_db
from app.services.file_service import process_pdf_file
from app.models.schemas import (
    FileProcessResult, 
    TrialFileUploadResponse, 
    TrialDownloadRequest, 
    TrialDownloadResponse, 
    TrialSessionInfo
)
from app.core.config import settings

router = APIRouter()

# Redis connection for session management
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

# Trial limitations
TRIAL_FILE_LIMIT = 3
TRIAL_SESSION_DURATION = 3600  # 1 hour in seconds
MAX_FILE_SIZE_TRIAL = 10 * 1024 * 1024  # 10MB for trial users

def generate_session_id() -> str:
    """Generate a unique session ID for trial users."""
    return str(uuid.uuid4())

def get_or_create_session(request: Request) -> str:
    """Get existing session ID from headers or create a new one."""
    session_id = request.headers.get("x-session-id")
    if not session_id:
        session_id = generate_session_id()
    
    # Check if session exists and is valid
    session_key = f"trial_session:{session_id}"
    session_data = redis_client.get(session_key)
    
    if not session_data:
        # Create new session
        session_info = {
            "created_at": datetime.now().isoformat(),
            "files_uploaded": 0,
            "email": None,
            "file_ids": []
        }
        redis_client.setex(session_key, TRIAL_SESSION_DURATION, json.dumps(session_info))
    
    return session_id

def get_session_info(session_id: str) -> Dict[str, Any]:
    """Get session information from Redis."""
    session_key = f"trial_session:{session_id}"
    session_data = redis_client.get(session_key)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    return json.loads(session_data)

def update_session_info(session_id: str, updates: Dict[str, Any]) -> None:
    """Update session information in Redis."""
    session_key = f"trial_session:{session_id}"
    session_info = get_session_info(session_id)
    session_info.update(updates)
    redis_client.setex(session_key, TRIAL_SESSION_DURATION, json.dumps(session_info))

@router.post("/trial/upload", response_model=TrialFileUploadResponse)
async def trial_upload(
    file: UploadFile = File(...),
    request: Request = None
) -> TrialFileUploadResponse:
    """Upload a file for trial processing (no registration required)."""
    
    session_id = get_or_create_session(request)
    session_info = get_session_info(session_id)
    
    # Check trial limits
    if session_info["files_uploaded"] >= TRIAL_FILE_LIMIT:
        raise HTTPException(
            status_code=429, 
            detail=f"Trial limit reached. You can upload up to {TRIAL_FILE_LIMIT} files per session."
        )
    
    # Check file size
    if file.size > MAX_FILE_SIZE_TRIAL:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Trial users can upload files up to {MAX_FILE_SIZE_TRIAL // (1024*1024)}MB."
        )
    
    # Check file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed for trial")
    
    # Generate trial file ID
    trial_file_id = str(uuid.uuid4())
    
    # Create temporary directory for trial files
    trial_dir = Path(tempfile.gettempdir()) / "pdf_extractor_trial" / session_id
    trial_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded file
    file_path = trial_dir / f"{trial_file_id}_{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store file info in Redis
        file_info = {
            "id": trial_file_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "uploaded_at": datetime.now().isoformat(),
            "status": "uploaded",
            "size": file.size
        }
        
        file_key = f"trial_file:{trial_file_id}"
        redis_client.setex(file_key, TRIAL_SESSION_DURATION, json.dumps(file_info))
        
        # Update session info
        session_info["files_uploaded"] += 1
        session_info["file_ids"].append(trial_file_id)
        update_session_info(session_id, session_info)
        
        return TrialFileUploadResponse(
            session_id=session_id,
            file_id=trial_file_id,
            filename=file.filename,
            message=f"File uploaded successfully. {TRIAL_FILE_LIMIT - session_info['files_uploaded']} uploads remaining.",
            remaining_uploads=TRIAL_FILE_LIMIT - session_info["files_uploaded"]
        )
        
    except Exception as e:
        # Clean up on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.post("/trial/{file_id}/process")
async def trial_process(
    file_id: str,
    request: Request = None
) -> FileProcessResult:
    """Process a trial file and extract tables (limited preview)."""
    
    session_id = request.headers.get("x-session-id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    # Get file info
    file_key = f"trial_file:{file_id}"
    file_data = redis_client.get(file_key)
    
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    file_info = json.loads(file_data)
    file_path = Path(file_info["file_path"])
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    try:
        # Update status to processing
        file_info["status"] = "processing"
        redis_client.setex(file_key, TRIAL_SESSION_DURATION, json.dumps(file_info))
        
        # Process the PDF file
        result = await process_pdf_file(str(file_path), file_info["filename"])
        
        # Limit results for trial users (only first 2 tables, first 10 rows each)
        if result.tables:
            limited_tables = []
            for i, table in enumerate(result.tables[:2]):  # Only first 2 tables
                # Convert TableData object to dict for manipulation
                table_dict = table.model_dump() if hasattr(table, 'model_dump') else dict(table)
                table_data = table_dict.get("data", [])
                
                limited_table = {
                    **table_dict,
                    "data": table_data[:10] if len(table_data) > 10 else table_data  # Only first 10 rows
                }
                if len(table_data) > 10:
                    limited_table["trial_message"] = f"Showing first 10 rows of {len(table_data)} total rows. Register to see all data."
                limited_tables.append(limited_table)
            
            result.tables = limited_tables
            
            if len(result.tables) > 2:
                result.trial_message = f"Showing 2 of {len(result.tables)} tables found. Register to access all tables."
        
        # Update file status
        file_info["status"] = "completed"
        file_info["processed_at"] = datetime.now().isoformat()
        file_info["result"] = result.model_dump()
        redis_client.setex(file_key, TRIAL_SESSION_DURATION, json.dumps(file_info))
        
        # Add trial limitations to result
        result.is_trial = True
        result.trial_limitations = {
            "max_tables": 2,
            "max_rows_per_table": 10,
            "download_requires_email": True
        }
        
        return result
        
    except Exception as e:
        # Update status to error
        file_info["status"] = "error"
        file_info["error"] = str(e)
        redis_client.setex(file_key, TRIAL_SESSION_DURATION, json.dumps(file_info))
        
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@router.get("/trial/{file_id}/status")
async def trial_file_status(
    file_id: str,
    request: Request = None
) -> Dict[str, Any]:
    """Get the status of a trial file."""
    
    session_id = request.headers.get("x-session-id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    file_key = f"trial_file:{file_id}"
    file_data = redis_client.get(file_key)
    
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    file_info = json.loads(file_data)
    
    return {
        "id": file_info["id"],
        "filename": file_info["filename"],
        "status": file_info["status"],
        "uploaded_at": file_info["uploaded_at"],
        "processed_at": file_info.get("processed_at"),
        "error": file_info.get("error")
    }

@router.post("/trial/{file_id}/request-download", response_model=TrialDownloadResponse)
async def trial_request_download(
    file_id: str,
    download_request: TrialDownloadRequest,
    request: Request = None
) -> TrialDownloadResponse:
    """Request download link for trial file (requires email)."""
    
    session_id = request.headers.get("x-session-id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    # Basic email validation
    email = download_request.email
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email address required")
    
    # Get file info
    file_key = f"trial_file:{file_id}"
    file_data = redis_client.get(file_key)
    
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    file_info = json.loads(file_data)
    
    if file_info["status"] != "completed":
        raise HTTPException(status_code=400, detail="File not ready for download")
    
    # Update session with email
    session_info = get_session_info(session_id)
    session_info["email"] = email
    update_session_info(session_id, session_info)
    
    # Generate download token
    download_token = str(uuid.uuid4())
    download_key = f"trial_download:{download_token}"
    
    download_info = {
        "file_id": file_id,
        "email": email,
        "session_id": session_id,
        "format": download_request.format,
        "selected_tables": download_request.selected_tables,
        "created_at": datetime.now().isoformat()
    }
    
    # Download token expires in 1 hour
    redis_client.setex(download_key, 3600, json.dumps(download_info))
    
    return TrialDownloadResponse(
        message="Download link generated successfully",
        download_token=download_token,
        expires_in="1 hour"
    )

@router.get("/trial/download/{download_token}")
async def trial_download(download_token: str):
    """Download processed trial file using download token."""
    
    download_key = f"trial_download:{download_token}"
    download_data = redis_client.get(download_key)
    
    if not download_data:
        raise HTTPException(status_code=404, detail="Download link expired or invalid")
    
    download_info = json.loads(download_data)
    file_id = download_info["file_id"]
    format_type = download_info.get("format", "excel")
    selected_table_indices = download_info.get("selected_tables")
    
    # Get file info
    file_key = f"trial_file:{file_id}"
    file_data = redis_client.get(file_key)
    
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    file_info = json.loads(file_data)
    
    if "result" not in file_info:
        raise HTTPException(status_code=400, detail="File not processed yet")
    
    # Create file for download based on format
    result = FileProcessResult(**file_info["result"])
    
    if not result.tables:
        raise HTTPException(status_code=400, detail="No tables found in file")
    
    # Filter tables based on selection if provided
    if selected_table_indices is not None and len(selected_table_indices) > 0:
        # Validate indices and filter tables
        valid_indices = [i for i in selected_table_indices if 0 <= i < len(result.tables)]
        if not valid_indices:
            raise HTTPException(status_code=400, detail="No valid tables selected")
        result.tables = [result.tables[i] for i in valid_indices]
    elif selected_table_indices is not None and len(selected_table_indices) == 0:
        raise HTTPException(status_code=400, detail="No tables selected for download")
    
    # Generate output file
    output_dir = Path(tempfile.gettempdir()) / "trial_downloads"
    output_dir.mkdir(exist_ok=True)
    
    try:
        if format_type == "excel":
            output_filename = f"trial_{file_id}_tables.xlsx"
            output_path = output_dir / output_filename
            
            # Create Excel file with trial limitations
            import pandas as pd
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for i, table in enumerate(result.tables):
                    df = pd.DataFrame(table.data)
                    sheet_name = f"Table_{i+1}"
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
        elif format_type == "csv":
            output_filename = f"trial_{file_id}_tables.csv"
            output_path = output_dir / output_filename
            
            # Create CSV file (combine all tables)
            import pandas as pd
            
            all_data = []
            for i, table in enumerate(result.tables):
                table_df = pd.DataFrame(table.data)
                table_df['Table_Source'] = f"Table_{i+1}"
                all_data.append(table_df)
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                combined_df.to_csv(output_path, index=False)
            
            media_type = 'text/csv'
            
        elif format_type == "word":
            output_filename = f"trial_{file_id}_tables.docx"
            output_path = output_dir / output_filename
            
            # Create Word document with tables
            from app.services.file_service import create_word_document
            
            # Convert tables to format expected by create_word_document
            tables_data = []
            for table in result.tables:
                tables_data.append({
                    'data': table.data
                })
            
            create_word_document(tables_data, file_info["filename"], str(output_path))
            media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
        # Mark download token as used
        redis_client.delete(download_key)
        
        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type=media_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download: {str(e)}")

@router.get("/trial/session/{session_id}", response_model=TrialSessionInfo)
async def trial_session_info(session_id: str) -> TrialSessionInfo:
    """Get trial session information."""
    
    try:
        session_info = get_session_info(session_id)
        
        # Get file information for all files in session
        files = []
        for file_id in session_info.get("file_ids", []):
            file_key = f"trial_file:{file_id}"
            file_data = redis_client.get(file_key)
            if file_data:
                file_info = json.loads(file_data)
                files.append({
                    "id": file_info["id"],
                    "filename": file_info["filename"],
                    "status": file_info["status"],
                    "uploaded_at": file_info["uploaded_at"]
                })
        
        return TrialSessionInfo(
            session_id=session_id,
            created_at=session_info["created_at"],
            files_uploaded=session_info["files_uploaded"],
            remaining_uploads=TRIAL_FILE_LIMIT - session_info["files_uploaded"],
            email=session_info.get("email"),
            files=files
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session info: {str(e)}")