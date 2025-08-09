from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import StreamingResponse
import io
import json
from typing import Optional
from api.routers.upload import sessions
import pandas as pd

router = APIRouter()

@router.get("/{session_id}")
async def export_data(
    session_id: str,
    format: str = "csv"
):
    """Export processed data in various formats"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    processor = sessions[session_id]["processor"]
    
    try:
        df = processor.df
        
        if format.lower() == "csv":
            # Export as CSV
            csv_string = df.to_csv(index=False)
            output = io.BytesIO(csv_string.encode())
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=export_{session_id}.csv"
                }
            )
        
        elif format.lower() == "json":
            # Export as JSON
            from services.data_processor import convert_numpy_types
            data = df.to_dict('records')
            json_str = json.dumps(convert_numpy_types(data), indent=2)
            output = io.BytesIO(json_str.encode())
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=export_{session_id}.json"
                }
            )
        
        elif format.lower() in ["excel", "xlsx"]:
            # Export as Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=export_{session_id}.xlsx"
                }
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/{session_id}/filtered")
async def export_filtered_data(
    session_id: str,
    filter_config: dict,
    format: str = "csv"
):
    """Export filtered data based on conditions"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    processor = sessions[session_id]["processor"]
    
    try:
        df = processor.df.copy()  # Work with a copy to avoid modifying original
        
        # Apply filters
        for filter_item in filter_config.get("filters", []):
            column = filter_item.get("column")
            operator = filter_item.get("operator")
            value = filter_item.get("value")
            
            if column and operator and value is not None:
                if operator == "=":
                    df = df[df[column] == value]
                elif operator == ">":
                    df = df[df[column] > value]
                elif operator == "<":
                    df = df[df[column] < value]
                elif operator == "contains":
                    df = df[df[column].astype(str).str.contains(str(value), na=False)]
        
        # Export filtered data
        if format.lower() == "csv":
            csv_string = df.to_csv(index=False)
            output = io.BytesIO(csv_string.encode())
            output.seek(0)
            
            return StreamingResponse(
                output,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=filtered_{session_id}.csv"
                }
            )
        
        # Add other formats as needed
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filtered export failed: {str(e)}")
