from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any, Optional
import uuid
import traceback
from api.routers.upload import sessions

router = APIRouter()

@router.get("/{session_id}")
async def get_analysis(session_id: str = Path(...)):
    """Get comprehensive analysis for a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    processor = sessions[session_id]["processor"]
    
    try:
        # Get all analysis data
        print(f"Getting analysis for session: {session_id}")
        basic_info = processor.get_basic_info()
        print(f"Basic info: {basic_info}")
        
        column_stats_dict = processor.get_column_stats()
        print(f"Column stats retrieved")
        
        # Transform column_stats to array format expected by frontend
        column_stats = []
        for col_name, stats in column_stats_dict.items():
            stat_item = {
                "column": col_name,
                "dtype": stats.get("dtype", "unknown"),
                "missing": stats.get("null_count", 0),
                "unique": stats.get("unique_count", 0),
                "mean": stats.get("mean"),
                "mode": None  # We can add mode calculation if needed
            }
            # For categorical columns, get the most frequent value as mode
            if stats.get("column_type") == "categorical" and stats.get("top_values"):
                stat_item["mode"] = stats["top_values"][0]["value"] if stats["top_values"] else None
            column_stats.append(stat_item)
        
        correlations = processor.compute_correlations()
        print(f"Correlations retrieved")
        
        sample = processor.get_data_sample(n=100)
        print(f"Sample retrieved")
        
        patterns = processor.detect_patterns_and_anomalies()
        print(f"Patterns detected")
        
        distributions = processor.get_value_distributions()
        print(f"Distributions calculated")
        
        return {
            "session_id": session_id,
            "filename": basic_info.get("filename", "unknown.csv"),
            "rows": basic_info["rows"],
            "columns": basic_info["columns"],
            "file_size": basic_info.get("file_size_mb", 0),
            "column_stats": column_stats,
            "correlations": correlations,
            "sample": sample,
            "patterns": patterns,
            "distributions": distributions,
            "basic_info": basic_info
        }
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/{session_id}/custom")
async def custom_analysis(
    session_id: str,
    query: Dict[str, Any]
):
    """Perform custom analysis on the data"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    processor = sessions[session_id]["processor"]
    
    try:
        analysis_type = query.get("type", "basic")
        
        if analysis_type == "filter":
            # Filter data based on conditions
            filters = query.get("filters", [])
            
            # Support both single filter (backward compatibility) and multiple filters
            if not filters:
                # Check if it's a single filter (old format)
                column = query.get("column")
                operator = query.get("operator", "=")
                value = query.get("value")
                if column and value is not None:
                    filters = [{"column": column, "operator": operator, "value": value}]
            
            if filters:
                df = processor.df
                filtered = df.copy()
                
                for filter_item in filters:
                    column = filter_item.get("column")
                    operator = filter_item.get("operator", "=")
                    value = filter_item.get("value")
                    
                    if column and value is not None:
                        try:
                            # Handle text operators
                            if operator == "=":
                                # Convert both sides to string for text comparison
                                filtered = filtered[filtered[column].astype(str) == str(value)]
                            elif operator == "!=":
                                filtered = filtered[filtered[column].astype(str) != str(value)]
                            elif operator == "contains":
                                filtered = filtered[filtered[column].astype(str).str.contains(str(value), case=False, na=False)]
                            elif operator == "starts with":
                                filtered = filtered[filtered[column].astype(str).str.startswith(str(value), na=False)]
                            elif operator == "ends with":
                                filtered = filtered[filtered[column].astype(str).str.endswith(str(value), na=False)]
                            # Numeric operators
                            elif operator in [">", "<", ">=", "<="]:
                                # Try to convert to numeric if possible
                                try:
                                    numeric_value = float(value)
                                    if operator == ">":
                                        filtered = filtered[filtered[column] > numeric_value]
                                    elif operator == "<":
                                        filtered = filtered[filtered[column] < numeric_value]
                                    elif operator == ">=":
                                        filtered = filtered[filtered[column] >= numeric_value]
                                    elif operator == "<=":
                                        filtered = filtered[filtered[column] <= numeric_value]
                                except (ValueError, TypeError):
                                    # If conversion fails, skip this filter
                                    continue
                        except Exception as e:
                            print(f"Error applying filter on column {column}: {str(e)}")
                            continue
                
                # Always return a valid response, even if no matches
                return {
                    "rows_matched": len(filtered),
                    "percentage": (len(filtered) / len(df)) * 100 if len(df) > 0 else 0,
                    "sample": filtered.head(100).to_dict('records') if len(filtered) > 0 else []
                }
            else:
                # No filters provided, return empty result
                return {
                    "rows_matched": 0,
                    "percentage": 0,
                    "sample": []
                }
        
        elif analysis_type == "groupby":
            # Group by analysis
            group_column = query.get("group_column")
            agg_column = query.get("agg_column")
            agg_func = query.get("agg_func", "mean")
            
            if group_column:
                df = processor.df
                
                if agg_func == "mean" and agg_column:
                    result = df.groupby(group_column)[agg_column].mean().reset_index()
                elif agg_func == "sum" and agg_column:
                    result = df.groupby(group_column)[agg_column].sum().reset_index()
                elif agg_func == "count":
                    result = df.groupby(group_column).size().reset_index(name='count')
                elif agg_func == "max" and agg_column:
                    result = df.groupby(group_column)[agg_column].max().reset_index()
                elif agg_func == "min" and agg_column:
                    result = df.groupby(group_column)[agg_column].min().reset_index()
                else:
                    result = df.groupby(group_column)[agg_column].mean().reset_index()
                
                # Convert numpy types before returning
                from services.data_processor import convert_numpy_types
                return convert_numpy_types(result.to_dict('records'))
        
        return {"message": "Analysis completed"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom analysis failed: {str(e)}")
