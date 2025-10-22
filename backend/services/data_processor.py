import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json
from datetime import datetime
import hashlib

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        # Handle NaN and Inf values
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, float):
        # Handle Python float NaN and Inf
        if pd.isna(obj) or np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

class DataProcessor:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.df: Optional[pd.DataFrame] = None
        self.sheets: Dict[str, pd.DataFrame] = {}  # For Excel files with multiple sheets
        self.file_hash = self._generate_file_hash()
        self._load_data()
    
    def _generate_file_hash(self) -> str:
        """Generate a unique hash for the file"""
        hasher = hashlib.md5()
        with open(self.file_path, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    
    def _load_data(self):
        """Load data from CSV or Excel file using Pandas"""
        file_ext = self.file_path.suffix.lower()
        
        try:
            if file_ext == '.csv':
                # Try to infer the separator
                self.df = pd.read_csv(self.file_path)
            elif file_ext in ['.xlsx', '.xls']:
                # Load all sheets from Excel file
                excel_file = pd.ExcelFile(self.file_path)
                sheet_names = excel_file.sheet_names
                
                if len(sheet_names) == 0:
                    # Empty Excel file - create empty dataframe
                    self.df = pd.DataFrame()
                elif len(sheet_names) == 1:
                    # Single sheet - load as main dataframe
                    self.df = pd.read_excel(self.file_path)
                else:
                    # Multiple sheets - load all into sheets dict
                    for sheet_name in sheet_names:
                        self.sheets[sheet_name] = pd.read_excel(self.file_path, sheet_name=sheet_name)
                    # Use first sheet as default dataframe
                    self.df = self.sheets[sheet_names[0]]
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")
    
    def get_basic_info(self) -> Dict[str, Any]:
        """Get basic information about the dataset"""
        if self.df is None:
            return {}
        
        # Handle empty dataframe
        if self.df.empty:
            return {
                "rows": 0,
                "columns": 0,
                "column_names": [],
                "dtypes": {},
                "memory_usage": "0.00 MB",
                "file_hash": self.file_hash,
                "is_empty": True
            }
        
        return {
            "rows": self.df.shape[0],
            "columns": self.df.shape[1],
            "column_names": self.df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in zip(self.df.columns, self.df.dtypes)},
            "memory_usage": f"{self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            "file_hash": self.file_hash,
            "is_empty": False
        }
    
    def get_column_stats(self) -> Dict[str, Any]:
        """Get detailed statistics for each column"""
        if self.df is None or self.df.empty:
            return {}
        
        stats = {}
        for col in self.df.columns:
            col_data = self.df[col]
            dtype = col_data.dtype
            
            col_stats = {
                "name": col,
                "dtype": str(dtype),
                "null_count": int(col_data.isnull().sum()),
                "null_percentage": (col_data.isnull().sum() / len(col_data) * 100) if len(col_data) > 0 else 0,
                "unique_count": int(col_data.nunique()),
                "unique_percentage": (col_data.nunique() / len(col_data) * 100) if len(col_data) > 0 else 0
            }
            
            # Numeric columns
            if np.issubdtype(dtype, np.number):
                # Calculate stats directly
                col_stats.update({
                    "mean": float(col_data.mean()) if not pd.isna(col_data.mean()) else None,
                    "std": float(col_data.std()) if not pd.isna(col_data.std()) else None,
                    "min": float(col_data.min()) if not pd.isna(col_data.min()) else None,
                    "25%": float(col_data.quantile(0.25)) if not pd.isna(col_data.quantile(0.25)) else None,
                    "50%": float(col_data.median()) if not pd.isna(col_data.median()) else None,
                    "75%": float(col_data.quantile(0.75)) if not pd.isna(col_data.quantile(0.75)) else None,
                    "max": float(col_data.max()) if not pd.isna(col_data.max()) else None,
                    "column_type": "numeric"
                })
            
            # Categorical/String columns
            elif dtype == object or pd.api.types.is_string_dtype(dtype):
                value_counts = col_data.value_counts().head(10)
                col_stats.update({
                    "top_values": [{"value": str(idx), "count": int(count)} 
                                  for idx, count in value_counts.items()],
                    "column_type": "categorical"
                })
            
            # Date columns
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                col_stats.update({
                    "min": str(col_data.min()),
                    "max": str(col_data.max()),
                    "column_type": "datetime"
                })
            
            # Boolean columns
            elif dtype == bool or pd.api.types.is_bool_dtype(dtype):
                value_counts = col_data.value_counts()
                col_stats.update({
                    "true_count": int(value_counts.get(True, 0)),
                    "false_count": int(value_counts.get(False, 0)),
                    "column_type": "boolean"
                })
            
            stats[col] = col_stats
        
        return stats
    
    def get_correlations(self) -> Dict[str, Any]:
        """Get correlation matrix for numeric columns"""
        if self.df is None or self.df.empty:
            return {}
        
        # Select only numeric columns
        numeric_df = self.df.select_dtypes(include=[np.number])
        numeric_cols = numeric_df.columns.tolist()
        
        if len(numeric_cols) < 2:
            return {"message": "Not enough numeric columns for correlation analysis"}
        
        # Calculate correlation matrix using Pandas
        corr_matrix = numeric_df.corr()
        
        # Convert to dictionary format
        correlations = {}
        for col1 in numeric_cols:
            correlations[col1] = {}
            for col2 in numeric_cols:
                corr_value = corr_matrix.loc[col1, col2]
                correlations[col1][col2] = float(corr_value) if not pd.isna(corr_value) else 0.0
        
        return {
            "matrix": correlations,
            "columns": numeric_cols
        }
    
    def get_data_sample(self, n: int = 100) -> List[Dict]:
        """Get a sample of the data"""
        if self.df is None or self.df.empty:
            return []
        
        sample = self.df.head(n)
        # Convert to dict and ensure all numpy types are converted
        sample_dict = sample.to_dict('records')
        return [convert_numpy_types(record) for record in sample_dict]
    
    def get_value_distribution(self, column: str, bins: int = 20) -> Dict[str, Any]:
        """Get distribution of values for a column"""
        if self.df is None or self.df.empty or column not in self.df.columns:
            return {}
        
        col_data = self.df[column]
        dtype = col_data.dtype
        
        # Numeric distribution
        if np.issubdtype(dtype, np.number):
            # Remove nulls
            clean_data = col_data.dropna()
            if len(clean_data) == 0:
                return {"error": "No non-null values"}
            
            min_val = float(clean_data.min())
            max_val = float(clean_data.max())
            
            # Create histogram using numpy
            hist_data = []
            if min_val != max_val:
                counts, bin_edges = np.histogram(clean_data, bins=bins)
                
                for i in range(len(bin_edges) - 1):
                    hist_data.append({
                        "range": f"{bin_edges[i]:.2f} - {bin_edges[i + 1]:.2f}",
                        "count": int(counts[i]),
                        "min": float(bin_edges[i]),
                        "max": float(bin_edges[i + 1])
                    })
            
            return {
                "type": "numeric",
                "histogram": hist_data,
                "min": min_val,
                "max": max_val,
                "mean": float(clean_data.mean()),
                "median": float(clean_data.median())
            }
        
        # Categorical distribution
        elif dtype == object or pd.api.types.is_string_dtype(dtype) or pd.api.types.is_categorical_dtype(dtype):
            value_counts = col_data.value_counts().head(50)
            return {
                "type": "categorical",
                "values": [{"value": str(idx), "count": int(count)} 
                          for idx, count in value_counts.items()]
            }
        
        # Date distribution
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            clean_data = col_data.dropna()
            return {
                "type": "datetime",
                "min": str(col_data.min()),
                "max": str(col_data.max()),
                "count": len(clean_data)
            }
        
        # Boolean distribution
        elif dtype == bool or pd.api.types.is_bool_dtype(dtype):
            value_counts = col_data.value_counts()
            return {
                "type": "boolean",
                "values": [{"value": str(idx), "count": int(count)} 
                          for idx, count in value_counts.items()]
            }
        
        return {"error": "Unsupported column type"}
    
    def detect_patterns(self) -> Dict[str, Any]:
        """Detect patterns and anomalies in the data"""
        if self.df is None or self.df.empty:
            return {}
        
        patterns = {
            "missing_data": {},
            "outliers": {},
            "data_quality": {}
        }
        
        # Missing data patterns
        for col in self.df.columns:
            null_count = int(self.df[col].isnull().sum())
            if null_count > 0:
                patterns["missing_data"][col] = {
                    "count": null_count,
                    "percentage": (null_count / len(self.df)) * 100
                }
        
        # Detect outliers in numeric columns using IQR method
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in numeric_cols:
            col_data = self.df[col].dropna()
            if len(col_data) > 0:
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                # Filter outliers using boolean mask
                outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
                if len(outliers) > 0:
                    patterns["outliers"][col] = {
                        "count": len(outliers),
                        "percentage": (len(outliers) / len(col_data)) * 100,
                        "lower_bound": float(lower_bound),
                        "upper_bound": float(upper_bound)
                    }
        
        # Data quality checks
        patterns["data_quality"]["duplicate_rows"] = int(self.df.duplicated().sum())
        patterns["data_quality"]["columns_with_single_value"] = [
            col for col in self.df.columns if self.df[col].nunique() == 1
        ]
        
        return patterns
    
    def compute_correlations(self) -> Dict[str, Any]:
        """Alias for get_correlations for compatibility"""
        return self.get_correlations()
    
    def detect_patterns_and_anomalies(self) -> Dict[str, Any]:
        """Alias for detect_patterns for compatibility"""
        return self.detect_patterns()
    
    def get_value_distributions(self) -> Dict[str, Any]:
        """Get distributions for all columns"""
        if self.df is None or self.df.empty:
            return {}
        distributions = {}
        for col in self.df.columns:
            distributions[col] = self.get_value_distribution(col)
        return distributions
    
    def export_processed_data(self, format: str = "csv") -> bytes:
        """Export processed data in various formats"""
        if self.df is None or self.df.empty:
            return b""
        
        if format == "csv":
            return self.df.to_csv(index=False).encode()
        elif format == "json":
            return self.df.to_json(orient='records').encode()
        elif format == "parquet":
            import io
            buffer = io.BytesIO()
            self.df.to_parquet(buffer, index=False)
            return buffer.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_sheet_names(self) -> List[str]:
        """Get list of sheet names if this is an Excel file with multiple sheets"""
        return list(self.sheets.keys())
    
    def get_sheet_info(self) -> Dict[str, Any]:
        """Get information about all sheets"""
        if not self.sheets:
            return {"has_multiple_sheets": False}
        
        sheet_info = {
            "has_multiple_sheets": True,
            "sheet_count": len(self.sheets),
            "sheets": {}
        }
        
        for sheet_name, df in self.sheets.items():
            sheet_info["sheets"][sheet_name] = {
                "rows": df.shape[0],
                "columns": df.shape[1],
                "column_names": df.columns.tolist(),
                "dtypes": {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}
            }
        
        return sheet_info
    
    def switch_sheet(self, sheet_name: str) -> bool:
        """Switch the active sheet for analysis"""
        if sheet_name in self.sheets:
            self.df = self.sheets[sheet_name]
            return True
        return False
    
    def compare_sheets(self, sheet1_name: str, sheet2_name: str, 
                      key_columns: List[str], 
                      comparison_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Compare two sheets based on key columns"""
        if sheet1_name not in self.sheets or sheet2_name not in self.sheets:
            return {"error": "One or both sheets not found"}
        
        df1 = self.sheets[sheet1_name]
        df2 = self.sheets[sheet2_name]
        
        # Validate key columns exist in both sheets
        for col in key_columns:
            if col not in df1.columns or col not in df2.columns:
                return {"error": f"Key column '{col}' not found in one or both sheets"}
        
        # If no comparison columns specified, use all common columns
        if comparison_columns is None:
            comparison_columns = list(set(df1.columns) & set(df2.columns))
        
        # Create key column for merging
        if len(key_columns) == 1:
            df1_key = df1[key_columns[0]].astype(str)
            df2_key = df2[key_columns[0]].astype(str)
        else:
            df1_key = df1[key_columns].astype(str).apply(lambda x: '_'.join(x), axis=1)
            df2_key = df2[key_columns].astype(str).apply(lambda x: '_'.join(x), axis=1)
        
        df1_with_key = df1.copy()
        df2_with_key = df2.copy()
        df1_with_key['_merge_key'] = df1_key
        df2_with_key['_merge_key'] = df2_key
        
        # Perform full outer merge
        merged = pd.merge(df1_with_key, df2_with_key, 
                         on='_merge_key', 
                         how='outer', 
                         suffixes=('_sheet1', '_sheet2'),
                         indicator=True)
        
        # Find matching, only in sheet1, and only in sheet2
        matching_rows = merged[merged['_merge'] == 'both'].copy()
        only_sheet1 = merged[merged['_merge'] == 'left_only'].copy()
        only_sheet2 = merged[merged['_merge'] == 'right_only'].copy()
        
        # Clean up merge artifacts
        matching_rows = matching_rows.drop(['_merge', '_merge_key'], axis=1)
        only_sheet1 = only_sheet1.drop(['_merge', '_merge_key'], axis=1)
        only_sheet2 = only_sheet2.drop(['_merge', '_merge_key'], axis=1)
        
        # For rows only in sheet1, keep only sheet1 columns
        sheet1_cols = [col for col in only_sheet1.columns if not col.endswith('_sheet2')]
        only_sheet1 = only_sheet1[sheet1_cols]
        only_sheet1.columns = [col.replace('_sheet1', '') if col.endswith('_sheet1') else col for col in only_sheet1.columns]
        
        # For rows only in sheet2, keep only sheet2 columns  
        sheet2_cols = [col for col in only_sheet2.columns if not col.endswith('_sheet1')]
        only_sheet2 = only_sheet2[sheet2_cols]
        only_sheet2.columns = [col.replace('_sheet2', '') if col.endswith('_sheet2') else col for col in only_sheet2.columns]
        
        # Find differences in matching rows
        differences = []
        if len(matching_rows) > 0:
            for col in comparison_columns:
                if col in df1.columns and col in df2.columns and col not in key_columns:
                    col1 = f"{col}_sheet1"
                    col2 = f"{col}_sheet2"
                    if col1 in matching_rows.columns and col2 in matching_rows.columns:
                        # Find rows where values differ
                        diff_mask = matching_rows[col1] != matching_rows[col2]
                        if diff_mask.any():
                            diff_rows = matching_rows[diff_mask]
                            for _, row in diff_rows.iterrows():
                                diff_record = {}
                                for k_col in key_columns:
                                    if f"{k_col}_sheet1" in row:
                                        diff_record[k_col] = row[f"{k_col}_sheet1"]
                                    elif k_col in row:
                                        diff_record[k_col] = row[k_col]
                                diff_record['column'] = col
                                diff_record['sheet1_value'] = row[col1]
                                diff_record['sheet2_value'] = row[col2]
                                differences.append(convert_numpy_types(diff_record))
        
        return {
            "summary": {
                "sheet1_name": sheet1_name,
                "sheet2_name": sheet2_name,
                "sheet1_rows": len(df1),
                "sheet2_rows": len(df2),
                "matching_rows": len(matching_rows),
                "only_in_sheet1": len(only_sheet1),
                "only_in_sheet2": len(only_sheet2),
                "key_columns": key_columns,
                "comparison_columns": comparison_columns
            },
            "matching_rows": convert_numpy_types(matching_rows.head(100).to_dict('records')),
            "only_in_sheet1": convert_numpy_types(only_sheet1.head(100).to_dict('records')),
            "only_in_sheet2": convert_numpy_types(only_sheet2.head(100).to_dict('records')),
            "differences": differences[:100]  # Limit to first 100 differences
        }
    
    def compare_sheets_full(self, sheet1_name: str, sheet2_name: str, 
                           key_columns: List[str], 
                           comparison_columns: Optional[List[str]] = None,
                           export_type: str = "all") -> Dict[str, Any]:
        """Compare two sheets and return full data for export (no limits)"""
        if sheet1_name not in self.sheets or sheet2_name not in self.sheets:
            return {"error": "One or both sheets not found"}
        
        df1 = self.sheets[sheet1_name]
        df2 = self.sheets[sheet2_name]
        
        # Validate key columns exist in both sheets
        for col in key_columns:
            if col not in df1.columns or col not in df2.columns:
                return {"error": f"Key column '{col}' not found in one or both sheets"}
        
        # If no comparison columns specified, use all common columns
        if comparison_columns is None:
            comparison_columns = list(set(df1.columns) & set(df2.columns))
        
        # Create key column for merging
        if len(key_columns) == 1:
            df1_key = df1[key_columns[0]].astype(str)
            df2_key = df2[key_columns[0]].astype(str)
        else:
            df1_key = df1[key_columns].astype(str).apply(lambda x: '_'.join(x), axis=1)
            df2_key = df2[key_columns].astype(str).apply(lambda x: '_'.join(x), axis=1)
        
        df1_with_key = df1.copy()
        df2_with_key = df2.copy()
        df1_with_key['_merge_key'] = df1_key
        df2_with_key['_merge_key'] = df2_key
        
        # Perform full outer merge
        merged = pd.merge(df1_with_key, df2_with_key, 
                         on='_merge_key', 
                         how='outer', 
                         suffixes=('_sheet1', '_sheet2'),
                         indicator=True)
        
        # Find matching, only in sheet1, and only in sheet2
        matching_rows = merged[merged['_merge'] == 'both'].copy()
        only_sheet1 = merged[merged['_merge'] == 'left_only'].copy()
        only_sheet2 = merged[merged['_merge'] == 'right_only'].copy()
        
        # Clean up merge artifacts
        matching_rows = matching_rows.drop(['_merge', '_merge_key'], axis=1)
        only_sheet1 = only_sheet1.drop(['_merge', '_merge_key'], axis=1)
        only_sheet2 = only_sheet2.drop(['_merge', '_merge_key'], axis=1)
        
        # For rows only in sheet1, keep only sheet1 columns
        sheet1_cols = [col for col in only_sheet1.columns if not col.endswith('_sheet2')]
        only_sheet1 = only_sheet1[sheet1_cols]
        only_sheet1.columns = [col.replace('_sheet1', '') if col.endswith('_sheet1') else col for col in only_sheet1.columns]
        
        # For rows only in sheet2, keep only sheet2 columns  
        sheet2_cols = [col for col in only_sheet2.columns if not col.endswith('_sheet1')]
        only_sheet2 = only_sheet2[sheet2_cols]
        only_sheet2.columns = [col.replace('_sheet2', '') if col.endswith('_sheet2') else col for col in only_sheet2.columns]
        
        # Return the requested data type without limits
        if export_type == "matching":
            return convert_numpy_types(matching_rows.to_dict('records'))
        elif export_type == "only1":
            return convert_numpy_types(only_sheet1.to_dict('records'))
        elif export_type == "only2":
            return convert_numpy_types(only_sheet2.to_dict('records'))
        else:  # "all"
            return {
                "matching_rows": convert_numpy_types(matching_rows.to_dict('records')),
                "only_in_sheet1": convert_numpy_types(only_sheet1.to_dict('records')),
                "only_in_sheet2": convert_numpy_types(only_sheet2.to_dict('records'))
            }
