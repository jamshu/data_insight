from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from api.routers.upload import get_session_processor
from services.data_processor import DataProcessor

router = APIRouter()

class SheetComparisonRequest(BaseModel):
    sheet1: str
    sheet2: str
    key_columns: List[str]
    comparison_columns: Optional[List[str]] = None

@router.get("/{session_id}/")
async def get_sheet_info(processor: DataProcessor = Depends(get_session_processor)):
    """Get information about all sheets in the Excel file"""
    try:
        sheet_info = processor.get_sheet_info()
        sheet_names = processor.get_sheet_names()
        
        # Add current active sheet info
        if processor.df is not None:
            sheet_info["active_sheet"] = sheet_names[0] if sheet_names else None
        
        return sheet_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/switch/")
async def switch_sheet(
    sheet_name: str,
    processor: DataProcessor = Depends(get_session_processor)
):
    """Switch to a different sheet for analysis"""
    try:
        success = processor.switch_sheet(sheet_name)
        if not success:
            raise HTTPException(status_code=404, detail=f"Sheet '{sheet_name}' not found")
        
        # Return basic info about the newly active sheet
        return {
            "success": True,
            "active_sheet": sheet_name,
            "info": processor.get_basic_info()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/compare/")
async def compare_sheets(
    request: SheetComparisonRequest,
    processor: DataProcessor = Depends(get_session_processor)
):
    """Compare two sheets based on key columns"""
    try:
        # Validate that this is an Excel file with multiple sheets
        if not processor.sheets:
            raise HTTPException(
                status_code=400, 
                detail="No multiple sheets available. This feature is only for Excel files with multiple sheets."
            )
        
        # Perform comparison
        result = processor.compare_sheets(
            sheet1_name=request.sheet1,
            sheet2_name=request.sheet2,
            key_columns=request.key_columns,
            comparison_columns=request.comparison_columns
        )
        
        # Check for errors in comparison
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/columns/")
async def get_common_columns(
    sheet1: str,
    sheet2: str,
    processor: DataProcessor = Depends(get_session_processor)
):
    """Get common columns between two sheets"""
    try:
        if sheet1 not in processor.sheets or sheet2 not in processor.sheets:
            raise HTTPException(status_code=404, detail="One or both sheets not found")
        
        df1 = processor.sheets[sheet1]
        df2 = processor.sheets[sheet2]
        
        common_columns = list(set(df1.columns) & set(df2.columns))
        
        return {
            "sheet1_columns": df1.columns.tolist(),
            "sheet2_columns": df2.columns.tolist(),
            "common_columns": common_columns
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
