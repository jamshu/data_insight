from fastapi import APIRouter, File, UploadFile, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from typing import Dict
from services.data_processor import DataProcessor
from services.pdf_processor import PDFProcessor
import uuid
import os
from datetime import datetime
import shutil

router = APIRouter()

# In-memory session storage (in production, use Redis or a database)
sessions: Dict[str, dict] = {}

def get_session_processor(request: Request, session_id: str = None):
    """Dependency to get session processor"""
    if session_id and session_id in sessions:
        return sessions[session_id]["processor"]
    return None

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """Upload a CSV, Excel, or PDF file for analysis"""
    
    # Validate file extension
    allowed_extensions = {'.csv', '.xlsx', '.xls', '.pdf'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Please upload CSV, Excel, or PDF files."
        )
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Save uploaded file
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{session_id}_{file.filename}")
    
    try:
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the file based on type
        if file_ext == '.pdf':
            processor = PDFProcessor(file_path)
            basic_info = processor.get_basic_info()
            file_type = "pdf"
        else:
            processor = DataProcessor(file_path)
            basic_info = processor.get_basic_info()
            file_type = "data"
        
        # Store session
        sessions[session_id] = {
            "processor": processor,
            "filename": file.filename,
            "file_path": file_path,
            "timestamp": datetime.now(),
            "basic_info": basic_info,
            "file_type": file_type
        }
        
        # Clean up old sessions (keep only last 10)
        if len(sessions) > 10:
            oldest_session = min(sessions.keys(), key=lambda k: sessions[k]["timestamp"])
            old_file = sessions[oldest_session]["file_path"]
            if os.path.exists(old_file):
                os.remove(old_file)
            del sessions[oldest_session]
        
        return JSONResponse(
            status_code=200,
            content={
                "session_id": session_id,
                "filename": file.filename,
                "message": "File uploaded and processed successfully",
                "basic_info": basic_info
            }
        )
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get information about an upload session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "filename": session["filename"],
        "uploaded_at": session["timestamp"].isoformat(),
        "basic_info": session["basic_info"]
    }

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete an upload session and its associated file"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Remove file
    file_path = sessions[session_id]["file_path"]
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Remove session
    del sessions[session_id]
    
    return {"message": "Session deleted successfully"}

@router.post("/pdf-to-excel/{session_id}")
async def convert_pdf_to_excel(session_id: str):
    """Convert uploaded PDF to Excel format"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session.get("file_type") != "pdf":
        raise HTTPException(status_code=400, detail="Session is not a PDF file")
    
    try:
        processor = session["processor"]
        
        # Export to Excel
        excel_path = processor.export_to_excel()
        
        # Also export to CSV for compatibility
        csv_path = processor.export_to_csv()
        
        # Get extraction summary
        extraction_summary = processor.get_extraction_summary()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "PDF converted to Excel successfully",
                "excel_file": excel_path,
                "csv_file": csv_path,
                "extraction_summary": extraction_summary,
                "tables_found": len(processor.tables),
                "main_table_info": {
                    "rows": processor.df.shape[0] if processor.df is not None else 0,
                    "columns": processor.df.shape[1] if processor.df is not None else 0
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF conversion failed: {str(e)}")

@router.get("/pdf-tables/{session_id}")
async def get_pdf_tables(session_id: str):
    """Get all tables extracted from PDF"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session.get("file_type") != "pdf":
        raise HTTPException(status_code=400, detail="Session is not a PDF file")
    
    try:
        processor = session["processor"]
        tables_data = processor.get_all_tables()
        
        return {
            "session_id": session_id,
            "tables": tables_data,
            "total_tables": len(tables_data),
            "extraction_method": processor.extraction_method
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get PDF tables: {str(e)}")
