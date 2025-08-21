"""
🔄 Advanced Data Processing Engine - Module 4.1

Enterprise-grade data processing with multi-source ingestion,
real-time streaming, automated cleaning, and statistical analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable
import asyncio
import aiofiles
import json
import io
from datetime import datetime, timedelta
import logging
from pathlib import Path
import sqlite3
import psycopg2
from sqlalchemy import create_engine
import requests
import websockets
from scipy import stats
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.impute import SimpleImputer, KNNImputer
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AdvancedDataProcessor:
    """
    🔄 Advanced Data Processing Engine
    
    Comprehensive data processing capabilities:
    - Multi-format data ingestion (CSV, JSON, Excel, Parquet, SQL)
    - Real-time data streaming via WebSocket
    - Automated data cleaning and validation
    - Statistical analysis and outlier detection
    - Data transformation and feature engineering
    """
    
    def __init__(self):
        self.scalers = {
            'standard': StandardScaler(),
            'robust': RobustScaler(),
            'minmax': MinMaxScaler()
        }
        self.imputers = {
            'mean': SimpleImputer(strategy='mean'),
            'median': SimpleImputer(strategy='median'),
            'knn': KNNImputer(n_neighbors=5)
        }
        self.processed_datasets = {}
        self.streaming_connections = {}
        
    async def ingest_data(
        self, 
        source: str, 
        source_type: str = 'auto',
        **kwargs
    ) -> pd.DataFrame:
        """
        🔽 Multi-source Data Ingestion
        
        Args:
            source: Data source (file path, URL, SQL query, etc.)
            source_type: Source type (csv, json, excel, sql, api, stream)
            **kwargs: Additional parameters for specific source types
            
        Returns:
            DataFrame with ingested data
        """
        try:
            # Auto-detect source type if not specified
            if source_type == 'auto':
                source_type = self._detect_source_type(source)
            
            logger.info(f"Ingesting data from {source_type}: {source}")
            
            if source_type == 'csv':
                return await self._ingest_csv(source, **kwargs)
            elif source_type == 'json':
                return await self._ingest_json(source, **kwargs)
            elif source_type == 'excel':
                return await self._ingest_excel(source, **kwargs)
            elif source_type == 'sql':
                return await self._ingest_sql(source, **kwargs)
            elif source_type == 'api':
                return await self._ingest_api(source, **kwargs)
            elif source_type == 'stream':
                return await self._setup_streaming(source, **kwargs)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
                
        except Exception as e:
            logger.error(f"Data ingestion failed: {str(e)}")
            raise
    
    async def _ingest_csv(self, filepath: str, **kwargs) -> pd.DataFrame:
        """Ingest CSV data with async file reading"""
        try:
            # Read CSV asynchronously
            async with aiofiles.open(filepath, 'r') as file:
                content = await file.read()
            
            # Parse CSV
            df = pd.read_csv(io.StringIO(content), **kwargs)
            
            # Auto-detect column types
            df = self._auto_detect_types(df)
            
            logger.info(f"CSV ingestion successful: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"CSV ingestion failed: {str(e)}")
            raise
    
    async def _ingest_json(self, source: str, **kwargs) -> pd.DataFrame:
        """Ingest JSON data from file or URL"""
        try:
            if source.startswith('http'):
                # Fetch from URL
                response = requests.get(source, **kwargs)
                response.raise_for_status()
                data = response.json()
            else:
                # Read from file
                async with aiofiles.open(source, 'r') as file:
                    content = await file.read()
                    data = json.loads(content)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                if 'data' in data:
                    df = pd.DataFrame(data['data'])
                else:
                    df = pd.DataFrame([data])
            else:
                raise ValueError("Invalid JSON structure")
            
            df = self._auto_detect_types(df)
            
            logger.info(f"JSON ingestion successful: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"JSON ingestion failed: {str(e)}")
            raise
    
    async def _ingest_excel(self, filepath: str, **kwargs) -> pd.DataFrame:
        """Ingest Excel data"""
        try:
            df = pd.read_excel(filepath, **kwargs)
            df = self._auto_detect_types(df)
            
            logger.info(f"Excel ingestion successful: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Excel ingestion failed: {str(e)}")
            raise
    
    async def _ingest_sql(self, query: str, connection_string: str, **kwargs) -> pd.DataFrame:
        """Ingest data from SQL database"""
        try:
            engine = create_engine(connection_string)
            df = pd.read_sql(query, engine, **kwargs)
            df = self._auto_detect_types(df)
            
            logger.info(f"SQL ingestion successful: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"SQL ingestion failed: {str(e)}")
            raise
    
    async def _ingest_api(self, url: str, **kwargs) -> pd.DataFrame:
        """Ingest data from REST API"""
        try:
            headers = kwargs.get('headers', {})
            params = kwargs.get('params', {})
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data)
            df = self._auto_detect_types(df)
            
            logger.info(f"API ingestion successful: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"API ingestion failed: {str(e)}")
            raise
    
    def clean_data(
        self, 
        df: pd.DataFrame, 
        remove_duplicates: bool = True,
        handle_missing: str = 'auto',
        remove_outliers: bool = True,
        outlier_method: str = 'iqr'
    ) -> pd.DataFrame:
        """
        🧹 Comprehensive Data Cleaning
        
        Args:
            df: Input DataFrame
            remove_duplicates: Remove duplicate rows
            handle_missing: Missing value strategy ('auto', 'drop', 'mean', 'median', 'knn')
            remove_outliers: Remove statistical outliers
            outlier_method: Outlier detection method ('iqr', 'zscore', 'isolation')
            
        Returns:
            Cleaned DataFrame
        """
        try:
            logger.info(f"Starting data cleaning: {len(df)} rows")
            cleaned_df = df.copy()
            
            # Remove duplicates
            if remove_duplicates:
                before_count = len(cleaned_df)
                cleaned_df = cleaned_df.drop_duplicates()
                duplicates_removed = before_count - len(cleaned_df)
                if duplicates_removed > 0:
                    logger.info(f"Removed {duplicates_removed} duplicate rows")
            
            # Handle missing values
            cleaned_df = self._handle_missing_values(cleaned_df, handle_missing)
            
            # Remove outliers
            if remove_outliers:
                cleaned_df = self._remove_outliers(cleaned_df, outlier_method)
            
            # Data validation
            cleaned_df = self._validate_data(cleaned_df)
            
            logger.info(f"Data cleaning complete: {len(cleaned_df)} rows remaining")
            return cleaned_df
            
        except Exception as e:
            logger.error(f"Data cleaning failed: {str(e)}")
            raise
    
    def _handle_missing_values(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """Handle missing values with various strategies"""
        if strategy == 'drop':
            return df.dropna()
        
        # Separate numeric and categorical columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns
        
        if strategy == 'auto':
            # Automatically choose best strategy per column
            for col in numeric_cols:
                missing_pct = df[col].isna().sum() / len(df)
                if missing_pct < 0.05:  # Less than 5% missing
                    df[col] = df[col].fillna(df[col].median())
                elif missing_pct < 0.3:  # Less than 30% missing
                    imputer = KNNImputer(n_neighbors=5)
                    df[col] = imputer.fit_transform(df[[col]]).flatten()
                else:
                    df[col] = df[col].fillna(df[col].median())
            
            # Fill categorical missing values with mode
            for col in categorical_cols:
                mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else 'Unknown'
                df[col] = df[col].fillna(mode_val)
        
        elif strategy in ['mean', 'median']:
            for col in numeric_cols:
                fill_value = df[col].mean() if strategy == 'mean' else df[col].median()
                df[col] = df[col].fillna(fill_value)
        
        elif strategy == 'knn':
            if len(numeric_cols) > 0:
                imputer = KNNImputer(n_neighbors=5)
                df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        
        return df
    
    def _remove_outliers(self, df: pd.DataFrame, method: str) -> pd.DataFrame:
        """Remove outliers using various methods"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if method == 'iqr':
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        
        elif method == 'zscore':
            for col in numeric_cols:
                z_scores = np.abs(stats.zscore(df[col].dropna()))
                df = df[z_scores < 3]  # Remove data points with |z-score| > 3
        
        elif method == 'isolation':
            from sklearn.ensemble import IsolationForest
            
            if len(numeric_cols) > 0:
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outliers = iso_forest.fit_predict(df[numeric_cols].fillna(0))
                df = df[outliers == 1]
        
        return df
    
    def analyze_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        📊 Comprehensive Data Quality Analysis
        
        Returns:
            Dictionary with detailed data quality metrics
        """
        try:
            analysis = {
                'basic_info': {
                    'total_rows': len(df),
                    'total_columns': len(df.columns),
                    'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
                    'duplicate_rows': df.duplicated().sum()
                },
                'column_analysis': {},
                'missing_data': {},
                'data_types': {},
                'statistical_summary': {},
                'correlations': {},
                'quality_score': 0
            }
            
            # Column-wise analysis
            for col in df.columns:
                col_analysis = {
                    'type': str(df[col].dtype),
                    'missing_count': df[col].isna().sum(),
                    'missing_percentage': (df[col].isna().sum() / len(df)) * 100,
                    'unique_values': df[col].nunique(),
                    'unique_percentage': (df[col].nunique() / len(df)) * 100
                }
                
                if df[col].dtype in ['int64', 'float64']:
                    col_analysis.update({
                        'mean': df[col].mean(),
                        'median': df[col].median(),
                        'std': df[col].std(),
                        'min': df[col].min(),
                        'max': df[col].max(),
                        'zeros_count': (df[col] == 0).sum(),
                        'outliers_count': self._count_outliers(df[col])
                    })
                
                analysis['column_analysis'][col] = col_analysis
            
            # Missing data summary
            missing_data = df.isnull().sum()
            analysis['missing_data'] = {
                'total_missing': missing_data.sum(),
                'columns_with_missing': (missing_data > 0).sum(),
                'highest_missing_column': missing_data.idxmax() if missing_data.max() > 0 else None,
                'highest_missing_percentage': (missing_data.max() / len(df)) * 100
            }
            
            # Data types summary
            type_counts = df.dtypes.value_counts()
            analysis['data_types'] = {str(dtype): count for dtype, count in type_counts.items()}
            
            # Statistical summary for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                analysis['statistical_summary'] = df[numeric_cols].describe().to_dict()
                
                # Correlation analysis
                correlation_matrix = df[numeric_cols].corr()
                high_correlations = []
                for i in range(len(correlation_matrix.columns)):
                    for j in range(i+1, len(correlation_matrix.columns)):
                        corr_val = correlation_matrix.iloc[i, j]
                        if abs(corr_val) > 0.7:  # High correlation threshold
                            high_correlations.append({
                                'column1': correlation_matrix.columns[i],
                                'column2': correlation_matrix.columns[j],
                                'correlation': corr_val
                            })
                
                analysis['correlations'] = {
                    'high_correlations': high_correlations,
                    'correlation_matrix': correlation_matrix.to_dict()
                }
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(analysis)
            analysis['quality_score'] = quality_score
            
            logger.info(f"Data quality analysis complete. Quality score: {quality_score:.2f}/100")
            return analysis
            
        except Exception as e:
            logger.error(f"Data quality analysis failed: {str(e)}")
            raise
    
    def transform_data(
        self, 
        df: pd.DataFrame, 
        transformations: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        🔄 Apply Data Transformations
        
        Args:
            df: Input DataFrame
            transformations: List of transformation dictionaries
            
        Returns:
            Transformed DataFrame
        """
        try:
            transformed_df = df.copy()
            
            for transform in transformations:
                transform_type = transform.get('type')
                columns = transform.get('columns', [])
                params = transform.get('params', {})
                
                if transform_type == 'scale':
                    scaler_type = params.get('method', 'standard')
                    if scaler_type in self.scalers:
                        scaler = self.scalers[scaler_type]
                        transformed_df[columns] = scaler.fit_transform(transformed_df[columns])
                
                elif transform_type == 'log':
                    for col in columns:
                        transformed_df[f'{col}_log'] = np.log1p(transformed_df[col])
                
                elif transform_type == 'category_encode':
                    encoding_method = params.get('method', 'onehot')
                    if encoding_method == 'onehot':
                        encoded = pd.get_dummies(transformed_df[columns], prefix=columns)
                        transformed_df = pd.concat([transformed_df.drop(columns, axis=1), encoded], axis=1)
                    elif encoding_method == 'label':
                        from sklearn.preprocessing import LabelEncoder
                        le = LabelEncoder()
                        for col in columns:
                            transformed_df[col] = le.fit_transform(transformed_df[col].astype(str))
                
                elif transform_type == 'bin':
                    for col in columns:
                        bins = params.get('bins', 5)
                        transformed_df[f'{col}_binned'] = pd.cut(transformed_df[col], bins=bins)
                
                elif transform_type == 'datetime':
                    for col in columns:
                        transformed_df[col] = pd.to_datetime(transformed_df[col])
                        if params.get('extract_features', False):
                            transformed_df[f'{col}_year'] = transformed_df[col].dt.year
                            transformed_df[f'{col}_month'] = transformed_df[col].dt.month
                            transformed_df[f'{col}_day'] = transformed_df[col].dt.day
                            transformed_df[f'{col}_dayofweek'] = transformed_df[col].dt.dayofweek
            
            logger.info(f"Data transformation complete: {len(transformations)} transformations applied")
            return transformed_df
            
        except Exception as e:
            logger.error(f"Data transformation failed: {str(e)}")
            raise
    
    def _detect_source_type(self, source: str) -> str:
        """Auto-detect source type from file extension or URL pattern"""
        if source.startswith('http'):
            return 'api'
        elif source.startswith('ws://') or source.startswith('wss://'):
            return 'stream'
        elif source.endswith('.csv'):
            return 'csv'
        elif source.endswith('.json'):
            return 'json'
        elif source.endswith(('.xlsx', '.xls')):
            return 'excel'
        elif 'SELECT' in source.upper():
            return 'sql'
        else:
            return 'csv'  # Default fallback
    
    def _auto_detect_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Auto-detect and convert column types"""
        for col in df.columns:
            # Try to convert to numeric
            if df[col].dtype == 'object':
                # Try datetime first
                try:
                    df[col] = pd.to_datetime(df[col])
                    continue
                except:
                    pass
                
                # Try numeric
                try:
                    df[col] = pd.to_numeric(df[col])
                    continue
                except:
                    pass
        
        return df
    
    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic data validation and cleaning"""
        # Remove empty columns
        df = df.dropna(axis=1, how='all')
        
        # Remove empty rows
        df = df.dropna(axis=0, how='all')
        
        return df
    
    def _count_outliers(self, series: pd.Series) -> int:
        """Count outliers using IQR method"""
        try:
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return len(series[(series < lower_bound) | (series > upper_bound)])
        except:
            return 0
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall data quality score (0-100)"""
        score = 100.0
        
        # Penalize missing data
        missing_pct = analysis['missing_data']['highest_missing_percentage']
        score -= min(missing_pct * 0.5, 25)  # Max 25 point deduction
        
        # Penalize duplicates
        duplicate_pct = (analysis['basic_info']['duplicate_rows'] / 
                        analysis['basic_info']['total_rows']) * 100
        score -= min(duplicate_pct * 0.3, 15)  # Max 15 point deduction
        
        # Bonus for data variety
        if analysis['basic_info']['total_columns'] > 5:
            score += min(analysis['basic_info']['total_columns'] * 0.5, 10)
        
        return max(0, min(100, score))

# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    sample_data = {
        'id': range(1, 1001),
        'name': [f'User_{i}' for i in range(1, 1001)],
        'age': np.random.normal(35, 10, 1000),
        'salary': np.random.normal(50000, 15000, 1000),
        'department': np.random.choice(['IT', 'Sales', 'Marketing', 'HR'], 1000),
        'join_date': pd.date_range('2020-01-01', periods=1000, freq='D')
    }
    
    # Add some missing values and outliers
    sample_df = pd.DataFrame(sample_data)
    sample_df.loc[::50, 'age'] = np.nan  # 2% missing
    sample_df.loc[::100, 'salary'] = np.nan  # 1% missing
    sample_df.loc[5, 'salary'] = 500000  # Outlier
    
    # Test the processor
    processor = AdvancedDataProcessor()
    
    print("🔄 Testing Advanced Data Processor...")
    
    # Test data cleaning
    cleaned_data = processor.clean_data(sample_df)
    print(f"Original data: {len(sample_df)} rows")
    print(f"Cleaned data: {len(cleaned_data)} rows")
    
    # Test quality analysis
    quality_report = processor.analyze_data_quality(sample_df)
    print(f"Data Quality Score: {quality_report['quality_score']:.2f}/100")
    
    print("✅ Advanced Data Processor test complete!")
"""
🔧 Advanced Data Processing Utility - Bot Utils

Enterprise-grade data processing engine with multi-format ingestion,
cleaning, validation, and statistical analysis capabilities.

This utility provides comprehensive data processing capabilities for the AnalyticBot,
including data loading, cleaning, validation, transformation, and quality analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import asyncio
import aiofiles
import json
import warnings
from datetime import datetime, timedelta
from pathlib import Path
import os
warnings.filterwarnings('ignore')

# Statistical libraries
from scipy import stats
from scipy.stats import zscore
import scipy.stats as stats

# Data processing libraries
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.decomposition import PCA

# Database connectivity (if needed)
try:
    import psycopg2
    import sqlite3
    from sqlalchemy import create_engine
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Additional data formats
try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

try:
    import xmltodict
    XML_AVAILABLE = True
except ImportError:
    XML_AVAILABLE = False

logger = logging.getLogger(__name__)

class AdvancedDataProcessor:
    """
    🔧 Advanced Data Processing Engine for AnalyticBot
    
    Comprehensive data processing capabilities:
    - Multi-format data ingestion (CSV, JSON, Excel, Parquet, SQL)
    - Advanced data cleaning and validation
    - Statistical analysis and outlier detection
    - Data transformation and feature engineering
    - Data quality assessment and reporting
    - Integration with bot analytics pipeline
    """
    
    def __init__(self):
        self.loaded_data = {}
        self.processing_history = {}
        self.data_quality_reports = {}
        self.scalers = {}
        self.encoders = {}
        
        # Processing configuration
        self.config = {
            'outlier_threshold': 3.0,  # Z-score threshold
            'missing_threshold': 0.5,  # Column drop threshold for missing values
            'correlation_threshold': 0.9,  # High correlation threshold
            'variance_threshold': 0.01  # Low variance threshold
        }
    
    async def load_data(self, source: Union[str, Dict], 
                       data_type: str = 'auto',
                       **kwargs) -> Dict[str, Any]:
        """
        📥 Universal data loader with format auto-detection
        """
        try:
            df = None
            metadata = {}
            
            if isinstance(source, str):
                # File-based loading
                file_path = Path(source)
                
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {source}")
                
                # Auto-detect format if not specified
                if data_type == 'auto':
                    data_type = self._detect_file_format(file_path)
                
                if data_type == 'csv':
                    df = pd.read_csv(source, **kwargs)
                elif data_type == 'json':
                    df = pd.read_json(source, **kwargs)
                elif data_type == 'excel' and EXCEL_AVAILABLE:
                    df = pd.read_excel(source, **kwargs)
                elif data_type == 'parquet':
                    df = pd.read_parquet(source, **kwargs)
                elif data_type == 'pickle':
                    df = pd.read_pickle(source)
                else:
                    raise ValueError(f"Unsupported file format: {data_type}")
                
                metadata['source'] = str(file_path)
                metadata['file_size'] = file_path.stat().st_size
                
            elif isinstance(source, dict):
                # Dictionary or API response
                if 'sql' in source and DATABASE_AVAILABLE:
                    # SQL query loading
                    engine = create_engine(source['connection_string'])
                    df = pd.read_sql(source['query'], engine)
                    metadata['source'] = 'database'
                elif 'data' in source:
                    # Direct data loading
                    df = pd.DataFrame(source['data'])
                    metadata['source'] = 'dict'
                else:
                    raise ValueError("Invalid source dictionary format")
            
            if df is None:
                raise ValueError("Failed to load data")
            
            # Generate data ID
            data_id = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Basic metadata
            metadata.update({
                'rows': len(df),
                'columns': len(df.columns),
                'data_types': df.dtypes.to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'load_timestamp': datetime.now().isoformat()
            })
            
            # Store loaded data
            self.loaded_data[data_id] = df
            
            # Perform initial analysis
            initial_analysis = await self._initial_data_analysis(df)
            
            return {
                'data_id': data_id,
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'metadata': metadata,
                'analysis': initial_analysis
            }
            
        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            return {'error': str(e)}
    
    async def clean_data(self, data_id: str, 
                        cleaning_options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        🧹 Comprehensive data cleaning pipeline
        """
        try:
            if data_id not in self.loaded_data:
                raise ValueError(f"Data ID {data_id} not found")
            
            df = self.loaded_data[data_id].copy()
            original_shape = df.shape
            cleaning_report = {'steps': []}
            
            # Default cleaning options
            if cleaning_options is None:
                cleaning_options = {
                    'remove_duplicates': True,
                    'handle_missing': 'auto',
                    'remove_outliers': True,
                    'standardize_columns': True,
                    'fix_data_types': True
                }
            
            # Step 1: Remove duplicates
            if cleaning_options.get('remove_duplicates', False):
                before_count = len(df)
                df = df.drop_duplicates()
                after_count = len(df)
                
                if before_count != after_count:
                    cleaning_report['steps'].append({
                        'step': 'remove_duplicates',
                        'removed': before_count - after_count,
                        'remaining': after_count
                    })
            
            # Step 2: Fix data types
            if cleaning_options.get('fix_data_types', False):
                type_fixes = []
                for col in df.columns:
                    if df[col].dtype == 'object':
                        # Try to convert to numeric
                        try:
                            pd.to_numeric(df[col], errors='raise')
                            df[col] = pd.to_numeric(df[col])
                            type_fixes.append(f"{col}: object -> numeric")
                        except (ValueError, TypeError):
                            # Try to convert to datetime
                            try:
                                pd.to_datetime(df[col], errors='raise')
                                df[col] = pd.to_datetime(df[col])
                                type_fixes.append(f"{col}: object -> datetime")
                            except (ValueError, TypeError):
                                pass  # Keep as object
                
                if type_fixes:
                    cleaning_report['steps'].append({
                        'step': 'fix_data_types',
                        'fixes': type_fixes
                    })
            
            # Step 3: Handle missing values
            if cleaning_options.get('handle_missing') != 'skip':
                missing_info = df.isnull().sum()
                missing_cols = missing_info[missing_info > 0]
                
                if len(missing_cols) > 0:
                    missing_strategy = cleaning_options.get('handle_missing', 'auto')
                    
                    if missing_strategy == 'auto':
                        # Smart missing value handling
                        for col in missing_cols.index:
                            missing_pct = missing_cols[col] / len(df)
                            
                            if missing_pct > self.config['missing_threshold']:
                                # Drop column if too many missing values
                                df = df.drop(col, axis=1)
                                cleaning_report['steps'].append({
                                    'step': 'drop_column',
                                    'column': col,
                                    'reason': f'Missing {missing_pct:.1%} of values'
                                })
                            else:
                                # Impute based on data type
                                if df[col].dtype in ['int64', 'float64']:
                                    df[col].fillna(df[col].median(), inplace=True)
                                    strategy = 'median'
                                else:
                                    df[col].fillna(df[col].mode().iloc[0], inplace=True)
                                    strategy = 'mode'
                                
                                cleaning_report['steps'].append({
                                    'step': 'impute_missing',
                                    'column': col,
                                    'strategy': strategy,
                                    'count': int(missing_cols[col])
                                })
                    
                    elif missing_strategy == 'drop':
                        df = df.dropna()
                        cleaning_report['steps'].append({
                            'step': 'drop_rows_with_missing',
                            'rows_removed': original_shape[0] - len(df)
                        })
            
            # Step 4: Remove outliers
            if cleaning_options.get('remove_outliers', False):
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                outlier_info = []
                
                for col in numeric_cols:
                    z_scores = np.abs(zscore(df[col]))
                    outlier_mask = z_scores > self.config['outlier_threshold']
                    outlier_count = outlier_mask.sum()
                    
                    if outlier_count > 0:
                        df = df[~outlier_mask]
                        outlier_info.append({
                            'column': col,
                            'outliers_removed': int(outlier_count)
                        })
                
                if outlier_info:
                    cleaning_report['steps'].append({
                        'step': 'remove_outliers',
                        'details': outlier_info,
                        'threshold': self.config['outlier_threshold']
                    })
            
            # Step 5: Standardize column names
            if cleaning_options.get('standardize_columns', False):
                original_columns = df.columns.tolist()
                # Convert to lowercase and replace spaces with underscores
                df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('[^a-zA-Z0-9_]', '', regex=True)
                
                if original_columns != df.columns.tolist():
                    cleaning_report['steps'].append({
                        'step': 'standardize_column_names',
                        'changes': dict(zip(original_columns, df.columns.tolist()))
                    })
            
            # Update stored data
            cleaned_data_id = f"{data_id}_cleaned"
            self.loaded_data[cleaned_data_id] = df
            
            # Store cleaning history
            self.processing_history[cleaned_data_id] = {
                'original_data_id': data_id,
                'operation': 'clean',
                'timestamp': datetime.now().isoformat(),
                'report': cleaning_report
            }
            
            return {
                'cleaned_data_id': cleaned_data_id,
                'original_shape': original_shape,
                'final_shape': df.shape,
                'cleaning_report': cleaning_report,
                'improvement': {
                    'rows_changed': original_shape[0] - df.shape[0],
                    'columns_changed': original_shape[1] - df.shape[1]
                }
            }
            
        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            return {'error': str(e)}
    
    async def analyze_data_quality(self, data_id: str) -> Dict[str, Any]:
        """
        📊 Comprehensive data quality analysis
        """
        try:
            if data_id not in self.loaded_data:
                raise ValueError(f"Data ID {data_id} not found")
            
            df = self.loaded_data[data_id]
            
            # Basic statistics
            quality_report = {
                'basic_info': {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
                    'duplicated_rows': df.duplicated().sum()
                }
            }
            
            # Missing values analysis
            missing_analysis = {}
            missing_counts = df.isnull().sum()
            
            for col in df.columns:
                missing_count = missing_counts[col]
                missing_analysis[col] = {
                    'missing_count': int(missing_count),
                    'missing_percentage': float(missing_count / len(df) * 100),
                    'data_type': str(df[col].dtype)
                }
            
            quality_report['missing_values'] = missing_analysis
            
            # Data type analysis
            type_analysis = {}
            for dtype in df.dtypes.value_counts().index:
                cols_of_type = df.select_dtypes(include=[dtype]).columns.tolist()
                type_analysis[str(dtype)] = {
                    'count': len(cols_of_type),
                    'columns': cols_of_type
                }
            
            quality_report['data_types'] = type_analysis
            
            # Numeric columns analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                numeric_analysis = {}
                
                for col in numeric_cols:
                    col_data = df[col]
                    
                    # Basic statistics
                    stats_dict = {
                        'mean': float(col_data.mean()),
                        'median': float(col_data.median()),
                        'std': float(col_data.std()),
                        'min': float(col_data.min()),
                        'max': float(col_data.max()),
                        'q25': float(col_data.quantile(0.25)),
                        'q75': float(col_data.quantile(0.75))
                    }
                    
                    # Outlier detection
                    z_scores = np.abs(zscore(col_data.dropna()))
                    outliers = (z_scores > self.config['outlier_threshold']).sum()
                    
                    # Distribution analysis
                    skewness = float(col_data.skew())
                    kurtosis = float(col_data.kurtosis())
                    
                    numeric_analysis[col] = {
                        **stats_dict,
                        'outliers': int(outliers),
                        'outlier_percentage': float(outliers / len(col_data) * 100),
                        'skewness': skewness,
                        'kurtosis': kurtosis,
                        'normality_test_p_value': float(stats.shapiro(col_data.dropna().sample(min(5000, len(col_data.dropna()))))[1]) if len(col_data.dropna()) > 0 else None
                    }
                
                quality_report['numeric_analysis'] = numeric_analysis
            
            # Categorical columns analysis
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                categorical_analysis = {}
                
                for col in categorical_cols:
                    col_data = df[col]
                    value_counts = col_data.value_counts()
                    
                    categorical_analysis[col] = {
                        'unique_values': int(col_data.nunique()),
                        'most_common': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                        'most_common_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                        'most_common_percentage': float(value_counts.iloc[0] / len(col_data) * 100) if len(value_counts) > 0 else 0,
                        'cardinality': int(col_data.nunique()),
                        'mode': str(col_data.mode().iloc[0]) if len(col_data.mode()) > 0 else None
                    }
                
                quality_report['categorical_analysis'] = categorical_analysis
            
            # Correlation analysis (for numeric columns)
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                
                # Find highly correlated pairs
                high_corr_pairs = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > self.config['correlation_threshold']:
                            high_corr_pairs.append({
                                'column1': corr_matrix.columns[i],
                                'column2': corr_matrix.columns[j],
                                'correlation': float(corr_val)
                            })
                
                quality_report['correlation_analysis'] = {
                    'correlation_matrix': corr_matrix.to_dict(),
                    'high_correlations': high_corr_pairs
                }
            
            # Data completeness score
            completeness_scores = {}
            for col in df.columns:
                completeness = (1 - df[col].isnull().sum() / len(df)) * 100
                completeness_scores[col] = float(completeness)
            
            overall_completeness = sum(completeness_scores.values()) / len(completeness_scores)
            
            quality_report['data_completeness'] = {
                'overall_score': float(overall_completeness),
                'column_scores': completeness_scores
            }
            
            # Quality score calculation
            quality_score = self._calculate_quality_score(quality_report)
            quality_report['overall_quality_score'] = quality_score
            
            # Store quality report
            self.data_quality_reports[data_id] = quality_report
            
            return quality_report
            
        except Exception as e:
            logger.error(f"Data quality analysis failed: {e}")
            return {'error': str(e)}
    
    async def transform_data(self, data_id: str, 
                           transformations: List[Dict]) -> Dict[str, Any]:
        """
        🔄 Apply data transformations
        """
        try:
            if data_id not in self.loaded_data:
                raise ValueError(f"Data ID {data_id} not found")
            
            df = self.loaded_data[data_id].copy()
            transformation_log = []
            
            for transform in transformations:
                transform_type = transform.get('type')
                
                if transform_type == 'scale':
                    # Scaling transformation
                    columns = transform.get('columns', df.select_dtypes(include=[np.number]).columns)
                    method = transform.get('method', 'standard')
                    
                    if method == 'standard':
                        scaler = StandardScaler()
                    elif method == 'minmax':
                        scaler = MinMaxScaler()
                    elif method == 'robust':
                        scaler = RobustScaler()
                    else:
                        raise ValueError(f"Unknown scaling method: {method}")
                    
                    df[columns] = scaler.fit_transform(df[columns])
                    self.scalers[f"{data_id}_{method}"] = scaler
                    
                    transformation_log.append({
                        'type': 'scale',
                        'method': method,
                        'columns': list(columns)
                    })
                
                elif transform_type == 'encode':
                    # Encoding transformation
                    columns = transform.get('columns', df.select_dtypes(include=['object']).columns)
                    method = transform.get('method', 'label')
                    
                    for col in columns:
                        if method == 'label':
                            encoder = LabelEncoder()
                            df[col] = encoder.fit_transform(df[col].astype(str))
                            self.encoders[f"{data_id}_{col}_label"] = encoder
                        elif method == 'onehot':
                            # One-hot encoding
                            encoded = pd.get_dummies(df[col], prefix=col)
                            df = pd.concat([df.drop(col, axis=1), encoded], axis=1)
                    
                    transformation_log.append({
                        'type': 'encode',
                        'method': method,
                        'columns': list(columns)
                    })
                
                elif transform_type == 'feature_selection':
                    # Feature selection
                    target = transform.get('target')
                    k_features = transform.get('k', 10)
                    
                    if target and target in df.columns:
                        X = df.drop(target, axis=1)
                        y = df[target]
                        
                        # Select appropriate scorer
                        if y.dtype in ['int64', 'float64'] and y.nunique() > 20:
                            scorer = f_regression
                        else:
                            scorer = f_classif
                        
                        selector = SelectKBest(score_func=scorer, k=k_features)
                        X_selected = selector.fit_transform(X, y)
                        
                        # Get selected feature names
                        selected_features = X.columns[selector.get_support()].tolist()
                        df = pd.concat([pd.DataFrame(X_selected, columns=selected_features), df[[target]]], axis=1)
                        
                        transformation_log.append({
                            'type': 'feature_selection',
                            'selected_features': selected_features,
                            'original_features': len(X.columns),
                            'selected_count': k_features
                        })
                
                elif transform_type == 'pca':
                    # Principal Component Analysis
                    n_components = transform.get('n_components', 2)
                    columns = transform.get('columns', df.select_dtypes(include=[np.number]).columns)
                    
                    pca = PCA(n_components=n_components)
                    pca_result = pca.fit_transform(df[columns])
                    
                    # Create PCA columns
                    pca_columns = [f'PC{i+1}' for i in range(n_components)]
                    pca_df = pd.DataFrame(pca_result, columns=pca_columns)
                    
                    # Replace original columns with PCA components
                    df = pd.concat([df.drop(columns, axis=1), pca_df], axis=1)
                    
                    transformation_log.append({
                        'type': 'pca',
                        'n_components': n_components,
                        'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
                        'cumulative_variance': np.cumsum(pca.explained_variance_ratio_).tolist()
                    })
            
            # Create new data ID for transformed data
            transformed_data_id = f"{data_id}_transformed"
            self.loaded_data[transformed_data_id] = df
            
            # Store transformation history
            self.processing_history[transformed_data_id] = {
                'original_data_id': data_id,
                'operation': 'transform',
                'timestamp': datetime.now().isoformat(),
                'transformations': transformation_log
            }
            
            return {
                'transformed_data_id': transformed_data_id,
                'shape': df.shape,
                'transformations_applied': len(transformation_log),
                'transformation_log': transformation_log
            }
            
        except Exception as e:
            logger.error(f"Data transformation failed: {e}")
            return {'error': str(e)}
    
    def _detect_file_format(self, file_path: Path) -> str:
        """Auto-detect file format based on extension"""
        suffix = file_path.suffix.lower()
        
        format_map = {
            '.csv': 'csv',
            '.json': 'json',
            '.xlsx': 'excel',
            '.xls': 'excel',
            '.parquet': 'parquet',
            '.pkl': 'pickle',
            '.pickle': 'pickle'
        }
        
        return format_map.get(suffix, 'csv')  # Default to CSV
    
    async def _initial_data_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform initial analysis of loaded data"""
        try:
            analysis = {
                'basic_stats': {
                    'total_cells': df.size,
                    'missing_cells': df.isnull().sum().sum(),
                    'missing_percentage': float(df.isnull().sum().sum() / df.size * 100),
                    'duplicated_rows': int(df.duplicated().sum())
                },
                'column_info': {}
            }
            
            for col in df.columns:
                col_info = {
                    'dtype': str(df[col].dtype),
                    'non_null_count': int(df[col].notna().sum()),
                    'null_count': int(df[col].isnull().sum()),
                    'unique_values': int(df[col].nunique())
                }
                
                if df[col].dtype in ['int64', 'float64']:
                    col_info.update({
                        'mean': float(df[col].mean()) if df[col].notna().sum() > 0 else None,
                        'std': float(df[col].std()) if df[col].notna().sum() > 0 else None,
                        'min': float(df[col].min()) if df[col].notna().sum() > 0 else None,
                        'max': float(df[col].max()) if df[col].notna().sum() > 0 else None
                    })
                
                analysis['column_info'][col] = col_info
            
            return analysis
            
        except Exception:
            return {'error': 'Initial analysis failed'}
    
    def _calculate_quality_score(self, quality_report: Dict) -> float:
        """Calculate overall data quality score (0-100)"""
        try:
            score_components = []
            
            # Completeness score (40% weight)
            completeness = quality_report.get('data_completeness', {}).get('overall_score', 0)
            score_components.append(completeness * 0.4)
            
            # Consistency score (30% weight) - based on data types and outliers
            consistency_score = 100
            if 'numeric_analysis' in quality_report:
                for col_stats in quality_report['numeric_analysis'].values():
                    outlier_pct = col_stats.get('outlier_percentage', 0)
                    consistency_score -= outlier_pct * 0.5  # Penalize outliers
            
            consistency_score = max(0, consistency_score)
            score_components.append(consistency_score * 0.3)
            
            # Validity score (20% weight) - based on data type appropriateness
            validity_score = 100
            # This is a simplified calculation - could be enhanced with more validation rules
            score_components.append(validity_score * 0.2)
            
            # Uniqueness score (10% weight) - based on duplicate records
            duplicate_pct = quality_report.get('basic_info', {}).get('duplicated_rows', 0) / quality_report.get('basic_info', {}).get('rows', 1) * 100
            uniqueness_score = max(0, 100 - duplicate_pct)
            score_components.append(uniqueness_score * 0.1)
            
            total_score = sum(score_components)
            return float(min(100, max(0, total_score)))
            
        except Exception:
            return 0.0
    
    def get_data_info(self, data_id: str) -> Dict[str, Any]:
        """Get information about stored data"""
        if data_id not in self.loaded_data:
            return {'error': f'Data ID {data_id} not found'}
        
        df = self.loaded_data[data_id]
        
        return {
            'data_id': data_id,
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'head': df.head().to_dict(),
            'processing_history': self.processing_history.get(data_id, {})
        }
    
    def list_loaded_data(self) -> Dict[str, Dict]:
        """List all loaded datasets"""
        return {
            data_id: {
                'shape': df.shape,
                'columns': len(df.columns),
                'memory_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
            }
            for data_id, df in self.loaded_data.items()
        }
    
    async def export_data(self, data_id: str, output_path: str, 
                         format: str = 'csv', **kwargs) -> Dict[str, Any]:
        """Export processed data to file"""
        try:
            if data_id not in self.loaded_data:
                raise ValueError(f"Data ID {data_id} not found")
            
            df = self.loaded_data[data_id]
            output_file = Path(output_path)
            
            # Create directory if it doesn't exist
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format == 'csv':
                df.to_csv(output_path, index=False, **kwargs)
            elif format == 'json':
                df.to_json(output_path, **kwargs)
            elif format == 'excel' and EXCEL_AVAILABLE:
                df.to_excel(output_path, index=False, **kwargs)
            elif format == 'parquet':
                df.to_parquet(output_path, **kwargs)
            elif format == 'pickle':
                df.to_pickle(output_path)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            return {
                'success': True,
                'output_path': str(output_file),
                'format': format,
                'rows': len(df),
                'file_size': output_file.stat().st_size if output_file.exists() else 0
            }
            
        except Exception as e:
            logger.error(f"Data export failed: {e}")
            return {'error': str(e)}
    
    async def health_check(self):
        """Health check for the data processor"""
        return {
            'status': 'healthy',
            'loaded_datasets': len(self.loaded_data),
            'total_memory_usage_mb': sum(df.memory_usage(deep=True).sum() for df in self.loaded_data.values()) / 1024 / 1024,
            'dependencies': {
                'database': DATABASE_AVAILABLE,
                'excel': EXCEL_AVAILABLE,
                'xml': XML_AVAILABLE
            }
        }

# Convenience function for easy integration with bot utils
async def create_data_processor():
    """Factory function to create and initialize data processor"""
    return AdvancedDataProcessor()

# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    np.random.seed(42)
    
    # Create sample dataset with various issues
    sample_data = {
        'id': range(1, 1001),
        'name': [f'User_{i}' if i % 50 != 0 else None for i in range(1, 1001)],  # Some missing values
        'age': [np.random.randint(18, 80) if i % 100 != 0 else None for i in range(1000)],  # Some missing values
        'salary': np.random.normal(50000, 15000, 1000),
        'department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing'], 1000),
        'score': np.random.normal(75, 10, 1000)
    }
    
    # Add some outliers
    sample_data['salary'][::100] = np.random.uniform(200000, 300000, 10)  # Salary outliers
    sample_data['score'][::150] = np.random.uniform(0, 30, 7)  # Score outliers
    
    # Add some duplicates
    for i in range(5):
        sample_data['id'].append(sample_data['id'][i])
        sample_data['name'].append(sample_data['name'][i])
        sample_data['age'].append(sample_data['age'][i])
        sample_data['salary'] = np.append(sample_data['salary'], sample_data['salary'][i])
        sample_data['department'] = np.append(sample_data['department'], sample_data['department'][i])
        sample_data['score'] = np.append(sample_data['score'], sample_data['score'][i])
    
    df = pd.DataFrame(sample_data)
    
    # Save to CSV for testing
    df.to_csv('/tmp/test_data.csv', index=False)
    
    # Test the processor
    processor = AdvancedDataProcessor()
    
    print("🔧 Testing Advanced Data Processor...")
    
    async def test_processor():
        # Test data loading
        load_result = await processor.load_data('/tmp/test_data.csv')
        print(f"Loaded data: {load_result['shape']} shape")
        
        data_id = load_result['data_id']
        
        # Test data quality analysis
        quality_result = await processor.analyze_data_quality(data_id)
        print(f"Data quality score: {quality_result['overall_quality_score']:.1f}/100")
        print(f"Missing values: {quality_result['basic_info']['missing_cells']} cells")
        print(f"Duplicated rows: {quality_result['basic_info']['duplicated_rows']}")
        
        # Test data cleaning
        clean_result = await processor.clean_data(data_id)
        print(f"After cleaning: {clean_result['final_shape']} shape")
        print(f"Cleaning steps: {len(clean_result['cleaning_report']['steps'])}")
        
        # Test data transformation
        transformations = [
            {'type': 'scale', 'method': 'standard', 'columns': ['age', 'salary', 'score']},
            {'type': 'encode', 'method': 'label', 'columns': ['department']}
        ]
        
        transform_result = await processor.transform_data(clean_result['cleaned_data_id'], transformations)
        print(f"Applied {transform_result['transformations_applied']} transformations")
        
        # Test export
        export_result = await processor.export_data(
            transform_result['transformed_data_id'], 
            '/tmp/processed_data.csv'
        )
        print(f"Exported to: {export_result['output_path']}")
    
    asyncio.run(test_processor())
    
    print("✅ Advanced Data Processor test complete!")
