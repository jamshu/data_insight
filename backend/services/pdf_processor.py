import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json
from datetime import datetime
import hashlib
import io
import logging

# PDF processing libraries
try:
    import pdfplumber
    import PyPDF2
    import tabula
    PDF_LIBRARIES_AVAILABLE = True
    CAMELOT_AVAILABLE = False
    try:
        import camelot
        CAMELOT_AVAILABLE = True
    except ImportError:
        logging.warning("Camelot not available, will use alternative methods")
except ImportError as e:
    PDF_LIBRARIES_AVAILABLE = False
    CAMELOT_AVAILABLE = False
    logging.warning(f"PDF processing libraries not available: {e}")

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

class PDFProcessor:
    def __init__(self, file_path: str):
        if not PDF_LIBRARIES_AVAILABLE:
            raise ImportError("PDF processing libraries are not installed. Please install PyPDF2, pdfplumber, tabula-py, and camelot-py[cv]")
        
        self.file_path = Path(file_path)
        self.df: Optional[pd.DataFrame] = None
        self.tables: List[pd.DataFrame] = []  # For multiple tables in PDF
        self.file_hash = self._generate_file_hash()
        self.extraction_method = None
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
        """Extract tables from PDF using multiple methods"""
        try:
            # Method 1: Try pdfplumber first (good for text-based tables)
            tables = self._extract_with_pdfplumber()
            if tables:
                self.extraction_method = "pdfplumber"
                self.tables = tables
                self.df = tables[0] if tables else pd.DataFrame()
                return
            
            # Method 2: Try tabula-py (good for complex tables)
            tables = self._extract_with_tabula()
            if tables:
                self.extraction_method = "tabula"
                self.tables = tables
                self.df = tables[0] if tables else pd.DataFrame()
                return
            
            # Method 3: Try camelot (good for structured tables)
            tables = self._extract_with_camelot()
            if tables:
                self.extraction_method = "camelot"
                self.tables = tables
                self.df = tables[0] if tables else pd.DataFrame()
                return
            
            # If no tables found, create empty dataframe
            self.df = pd.DataFrame()
            self.extraction_method = "none"
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def _extract_with_pdfplumber(self) -> List[pd.DataFrame]:
        """Extract tables using pdfplumber"""
        tables = []
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table_num, table in enumerate(page_tables):
                            if table and len(table) > 1:  # Ensure table has data
                                # Convert to DataFrame
                                df = pd.DataFrame(table[1:], columns=table[0])
                                # Clean the data
                                df = self._clean_dataframe(df)
                                if not df.empty:
                                    tables.append(df)
        except Exception as e:
            logging.warning(f"pdfplumber extraction failed: {e}")
        return tables
    
    def _extract_with_tabula(self) -> List[pd.DataFrame]:
        """Extract tables using tabula-py"""
        tables = []
        try:
            # Try different extraction methods
            for method in ['lattice', 'stream']:
                try:
                    extracted_tables = tabula.read_pdf(
                        str(self.file_path), 
                        pages='all', 
                        multiple_tables=True,
                        lattice=method == 'lattice',
                        stream=method == 'stream'
                    )
                    if extracted_tables:
                        for table in extracted_tables:
                            if not table.empty:
                                cleaned_df = self._clean_dataframe(table)
                                if not cleaned_df.empty:
                                    tables.append(cleaned_df)
                        if tables:
                            break
                except Exception as e:
                    logging.warning(f"tabula {method} extraction failed: {e}")
                    continue
        except Exception as e:
            logging.warning(f"tabula extraction failed: {e}")
        return tables
    
    def _extract_with_camelot(self) -> List[pd.DataFrame]:
        """Extract tables using camelot"""
        tables = []
        if not CAMELOT_AVAILABLE:
            return tables
            
        try:
            # Try both lattice and stream methods
            for method in ['lattice', 'stream']:
                try:
                    camelot_tables = camelot.read_pdf(str(self.file_path), pages='all', flavor=method)
                    if camelot_tables:
                        for table in camelot_tables:
                            if not table.df.empty:
                                cleaned_df = self._clean_dataframe(table.df)
                                if not cleaned_df.empty:
                                    tables.append(cleaned_df)
                        if tables:
                            break
                except Exception as e:
                    logging.warning(f"camelot {method} extraction failed: {e}")
                    continue
        except Exception as e:
            logging.warning(f"camelot extraction failed: {e}")
        return tables
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the extracted dataframe"""
        if df.empty:
            return df
        
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Clean column names
        if not df.empty:
            df.columns = [str(col).strip() for col in df.columns]
            
            # Remove rows that are all NaN or empty strings
            df = df.dropna(how='all')
            
            # Clean string values
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip()
                    # Replace empty strings with NaN
                    df[col] = df[col].replace('', np.nan)
        
        return df
    
    def get_basic_info(self) -> Dict[str, Any]:
        """Get basic information about the extracted data"""
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
                "is_empty": True,
                "extraction_method": self.extraction_method,
                "table_count": len(self.tables)
            }
        
        return {
            "rows": self.df.shape[0],
            "columns": self.df.shape[1],
            "column_names": self.df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in zip(self.df.columns, self.df.dtypes)},
            "memory_usage": f"{self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            "file_hash": self.file_hash,
            "is_empty": False,
            "extraction_method": self.extraction_method,
            "table_count": len(self.tables)
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
    
    def compute_correlations(self) -> Dict[str, Any]:
        """Alias for get_correlations for compatibility with DataProcessor"""
        return self.get_correlations()
    
    def get_data_sample(self, n: int = 100) -> List[Dict]:
        """Get a sample of the data"""
        if self.df is None or self.df.empty:
            return []
        
        sample = self.df.head(n)
        # Convert to dict and ensure all numpy types are converted
        sample_dict = sample.to_dict('records')
        return [convert_numpy_types(record) for record in sample_dict]
    
    def get_all_tables(self) -> List[Dict[str, Any]]:
        """Get all extracted tables"""
        if not self.tables:
            return []
        
        tables_data = []
        for i, table in enumerate(self.tables):
            tables_data.append({
                "table_index": i,
                "rows": table.shape[0],
                "columns": table.shape[1],
                "column_names": table.columns.tolist(),
                "sample_data": convert_numpy_types(table.head(5).to_dict('records'))
            })
        
        return tables_data
    
    def export_to_excel(self, output_path: str = None) -> str:
        """Export extracted tables to Excel file"""
        if not self.tables:
            raise ValueError("No tables to export")
        
        if output_path is None:
            output_path = str(self.file_path.parent / f"{self.file_path.stem}_extracted.xlsx")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for i, table in enumerate(self.tables):
                sheet_name = f"Table_{i+1}" if len(self.tables) > 1 else "Data"
                table.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return output_path
    
    def export_to_csv(self, output_path: str = None) -> str:
        """Export main table to CSV file"""
        if self.df is None or self.df.empty:
            raise ValueError("No data to export")
        
        if output_path is None:
            output_path = str(self.file_path.parent / f"{self.file_path.stem}_extracted.csv")
        
        self.df.to_csv(output_path, index=False)
        return output_path
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get summary of the extraction process"""
        return {
            "extraction_method": self.extraction_method,
            "table_count": len(self.tables),
            "main_table_rows": self.df.shape[0] if self.df is not None else 0,
            "main_table_columns": self.df.shape[1] if self.df is not None else 0,
            "file_hash": self.file_hash,
            "extraction_successful": len(self.tables) > 0
        }
    
    def detect_patterns_and_anomalies(self) -> Dict[str, Any]:
        """Detect patterns and anomalies in the data - alias for detect_patterns"""
        return self.detect_patterns()
    
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
    
    def get_value_distributions(self) -> Dict[str, Any]:
        """Get distributions for all columns"""
        if self.df is None or self.df.empty:
            return {}
        distributions = {}
        for col in self.df.columns:
            distributions[col] = self.get_value_distribution(col)
        return distributions
    
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
