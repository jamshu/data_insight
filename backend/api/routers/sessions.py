from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from api.routers.upload import sessions

router = APIRouter()

@router.get("/")
async def list_sessions():
    """List all active sessions"""
    session_list = []
    
    for session_id, session_data in sessions.items():
        processor = session_data["processor"]
        basic_info = processor.get_basic_info()
        
        session_list.append({
            "session_id": session_id,
            "filename": session_data["filename"],
            "rows": basic_info["rows"],
            "columns": basic_info["columns"],
            "uploaded_at": session_data["timestamp"].isoformat(),
            "active": True,
            "file_size_mb": basic_info.get("file_size_mb", 0)
        })
    
    # Sort by upload time, most recent first
    session_list.sort(key=lambda x: x["uploaded_at"], reverse=True)
    
    return {"sessions": session_list, "total": len(session_list)}

@router.get("/{session_id}")
async def get_session(session_id: str):
    """Get details for a specific session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    processor = session_data["processor"]
    basic_info = processor.get_basic_info()
    
    return {
        "session_id": session_id,
        "filename": session_data["filename"],
        "uploaded_at": session_data["timestamp"].isoformat(),
        "basic_info": basic_info,
        "status": "active"
    }

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a specific session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    return {"message": f"Session {session_id} deleted successfully"}

@router.delete("/clear")
async def clear_all_sessions():
    """Clear all sessions"""
    count = len(sessions)
    sessions.clear()
    return {"message": f"Cleared {count} sessions"}
