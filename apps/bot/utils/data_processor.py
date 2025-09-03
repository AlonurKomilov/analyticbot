"""
🔄 Advanced Data Processing Engine - Module 4.1

Enterprise-grade data processing with multi-source ingestion,
real-time streaming, automated cleaning, and statistical analysis.
"""

import io
import json
import logging
import warnings
from typing import Any

import aiofiles
import numpy as np
import pandas as pd
import requests
from scipy import stats
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler
from sqlalchemy import create_engine

warnings.filterwarnings("ignore")

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
            "standard": StandardScaler(),
            "robust": RobustScaler(),
            "minmax": MinMaxScaler(),
        }
        self.imputers = {
            "mean": SimpleImputer(strategy="mean"),
            "median": SimpleImputer(strategy="median"),
            "knn": KNNImputer(n_neighbors=5),
        }
        self.processed_datasets = {}
        self.streaming_connections = {}

    async def ingest_data(self, source: str, source_type: str = "auto", **kwargs) -> pd.DataFrame:
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
            if source_type == "auto":
                source_type = self._detect_source_type(source)

            logger.info(f"Ingesting data from {source_type}: {source}")

            if source_type == "csv":
                return await self._ingest_csv(source, **kwargs)
            elif source_type == "json":
                return await self._ingest_json(source, **kwargs)
            elif source_type == "excel":
                return await self._ingest_excel(source, **kwargs)
            elif source_type == "sql":
                return await self._ingest_sql(source, **kwargs)
            elif source_type == "api":
                return await self._ingest_api(source, **kwargs)
            elif source_type == "stream":
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
            async with aiofiles.open(filepath) as file:
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
            if source.startswith("http"):
                # Fetch from URL
                response = requests.get(source, **kwargs)
                response.raise_for_status()
                data = response.json()
            else:
                # Read from file
                async with aiofiles.open(source) as file:
                    content = await file.read()
                    data = json.loads(content)

            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                if "data" in data:
                    df = pd.DataFrame(data["data"])
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
            headers = kwargs.get("headers", {})
            params = kwargs.get("params", {})

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
        handle_missing: str = "auto",
        remove_outliers: bool = True,
        outlier_method: str = "iqr",
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
        if strategy == "drop":
            return df.dropna()

        # Separate numeric and categorical columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns

        if strategy == "auto":
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
                mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown"
                df[col] = df[col].fillna(mode_val)

        elif strategy in ["mean", "median"]:
            for col in numeric_cols:
                fill_value = df[col].mean() if strategy == "mean" else df[col].median()
                df[col] = df[col].fillna(fill_value)

        elif strategy == "knn":
            if len(numeric_cols) > 0:
                imputer = KNNImputer(n_neighbors=5)
                df[numeric_cols] = imputer.fit_transform(df[numeric_cols])

        return df

    def _remove_outliers(self, df: pd.DataFrame, method: str) -> pd.DataFrame:
        """Remove outliers using various methods"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if method == "iqr":
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

        elif method == "zscore":
            for col in numeric_cols:
                z_scores = np.abs(stats.zscore(df[col].dropna()))
                df = df[z_scores < 3]  # Remove data points with |z-score| > 3

        elif method == "isolation":
            from sklearn.ensemble import IsolationForest

            if len(numeric_cols) > 0:
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outliers = iso_forest.fit_predict(df[numeric_cols].fillna(0))
                df = df[outliers == 1]

        return df

    def analyze_data_quality(self, df: pd.DataFrame) -> dict[str, Any]:
        """
        📊 Comprehensive Data Quality Analysis

        Returns:
            Dictionary with detailed data quality metrics
        """
        try:
            analysis = {
                "basic_info": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
                    "duplicate_rows": df.duplicated().sum(),
                },
                "column_analysis": {},
                "missing_data": {},
                "data_types": {},
                "statistical_summary": {},
                "correlations": {},
                "quality_score": 0,
            }

            # Column-wise analysis
            for col in df.columns:
                col_analysis = {
                    "type": str(df[col].dtype),
                    "missing_count": df[col].isna().sum(),
                    "missing_percentage": (df[col].isna().sum() / len(df)) * 100,
                    "unique_values": df[col].nunique(),
                    "unique_percentage": (df[col].nunique() / len(df)) * 100,
                }

                if df[col].dtype in ["int64", "float64"]:
                    col_analysis.update(
                        {
                            "mean": df[col].mean(),
                            "median": df[col].median(),
                            "std": df[col].std(),
                            "min": df[col].min(),
                            "max": df[col].max(),
                            "zeros_count": (df[col] == 0).sum(),
                            "outliers_count": self._count_outliers(df[col]),
                        }
                    )

                analysis["column_analysis"][col] = col_analysis

            # Missing data summary
            missing_data = df.isnull().sum()
            analysis["missing_data"] = {
                "total_missing": missing_data.sum(),
                "columns_with_missing": (missing_data > 0).sum(),
                "highest_missing_column": missing_data.idxmax() if missing_data.max() > 0 else None,
                "highest_missing_percentage": (missing_data.max() / len(df)) * 100,
            }

            # Data types summary
            type_counts = df.dtypes.value_counts()
            analysis["data_types"] = {str(dtype): count for dtype, count in type_counts.items()}

            # Statistical summary for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                analysis["statistical_summary"] = df[numeric_cols].describe().to_dict()

                # Correlation analysis
                correlation_matrix = df[numeric_cols].corr()
                high_correlations = []
                for i in range(len(correlation_matrix.columns)):
                    for j in range(i + 1, len(correlation_matrix.columns)):
                        corr_val = correlation_matrix.iloc[i, j]
                        if abs(corr_val) > 0.7:  # High correlation threshold
                            high_correlations.append(
                                {
                                    "column1": correlation_matrix.columns[i],
                                    "column2": correlation_matrix.columns[j],
                                    "correlation": corr_val,
                                }
                            )

                analysis["correlations"] = {
                    "high_correlations": high_correlations,
                    "correlation_matrix": correlation_matrix.to_dict(),
                }

            # Calculate overall quality score
            quality_score = self._calculate_quality_score(analysis)
            analysis["quality_score"] = quality_score

            logger.info(f"Data quality analysis complete. Quality score: {quality_score:.2f}/100")
            return analysis

        except Exception as e:
            logger.error(f"Data quality analysis failed: {str(e)}")
            raise

    def transform_data(
        self, df: pd.DataFrame, transformations: list[dict[str, Any]]
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
                transform_type = transform.get("type")
                columns = transform.get("columns", [])
                params = transform.get("params", {})

                if transform_type == "scale":
                    scaler_type = params.get("method", "standard")
                    if scaler_type in self.scalers:
                        scaler = self.scalers[scaler_type]
                        transformed_df[columns] = scaler.fit_transform(transformed_df[columns])

                elif transform_type == "log":
                    for col in columns:
                        transformed_df[f"{col}_log"] = np.log1p(transformed_df[col])

                elif transform_type == "category_encode":
                    encoding_method = params.get("method", "onehot")
                    if encoding_method == "onehot":
                        encoded = pd.get_dummies(transformed_df[columns], prefix=columns)
                        transformed_df = pd.concat(
                            [transformed_df.drop(columns, axis=1), encoded], axis=1
                        )
                    elif encoding_method == "label":
                        from sklearn.preprocessing import LabelEncoder

                        le = LabelEncoder()
                        for col in columns:
                            transformed_df[col] = le.fit_transform(transformed_df[col].astype(str))

                elif transform_type == "bin":
                    for col in columns:
                        bins = params.get("bins", 5)
                        transformed_df[f"{col}_binned"] = pd.cut(transformed_df[col], bins=bins)

                elif transform_type == "datetime":
                    for col in columns:
                        transformed_df[col] = pd.to_datetime(transformed_df[col])
                        if params.get("extract_features", False):
                            transformed_df[f"{col}_year"] = transformed_df[col].dt.year
                            transformed_df[f"{col}_month"] = transformed_df[col].dt.month
                            transformed_df[f"{col}_day"] = transformed_df[col].dt.day
                            transformed_df[f"{col}_dayofweek"] = transformed_df[col].dt.dayofweek

            logger.info(
                f"Data transformation complete: {len(transformations)} transformations applied"
            )
            return transformed_df

        except Exception as e:
            logger.error(f"Data transformation failed: {str(e)}")
            raise

    def _detect_source_type(self, source: str) -> str:
        """Auto-detect source type from file extension or URL pattern"""
        if source.startswith("http"):
            return "api"
        elif source.startswith("ws://") or source.startswith("wss://"):
            return "stream"
        elif source.endswith(".csv"):
            return "csv"
        elif source.endswith(".json"):
            return "json"
        elif source.endswith((".xlsx", ".xls")):
            return "excel"
        elif "SELECT" in source.upper():
            return "sql"
        else:
            return "csv"  # Default fallback

    def _auto_detect_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Auto-detect and convert column types"""
        for col in df.columns:
            # Try to convert to numeric
            if df[col].dtype == "object":
                # Try datetime first
                try:
                    df[col] = pd.to_datetime(df[col])
                    continue
                except Exception as e:
                    logger.debug(f"Failed to convert column {col} to datetime: {e}")
                    pass

                # Try numeric
                try:
                    df[col] = pd.to_numeric(df[col])
                    continue
                except Exception as e:
                    logger.debug(f"Failed to convert column {col} to numeric: {e}")
                    pass

        return df

    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic data validation and cleaning"""
        # Remove empty columns
        df = df.dropna(axis=1, how="all")

        # Remove empty rows
        df = df.dropna(axis=0, how="all")

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
        except Exception as e:
            logger.debug(f"Failed to count outliers: {e}")
            return 0

    def _calculate_quality_score(self, analysis: dict[str, Any]) -> float:
        """Calculate overall data quality score (0-100)"""
        score = 100.0

        # Penalize missing data
        missing_pct = analysis["missing_data"]["highest_missing_percentage"]
        score -= min(missing_pct * 0.5, 25)  # Max 25 point deduction

        # Penalize duplicates
        duplicate_pct = (
            analysis["basic_info"]["duplicate_rows"] / analysis["basic_info"]["total_rows"]
        ) * 100
        score -= min(duplicate_pct * 0.3, 15)  # Max 15 point deduction

        # Bonus for data variety
        if analysis["basic_info"]["total_columns"] > 5:
            score += min(analysis["basic_info"]["total_columns"] * 0.5, 10)

        return max(0, min(100, score))


# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    sample_data = {
        "id": range(1, 1001),
        "name": [f"User_{i}" for i in range(1, 1001)],
        "age": np.random.normal(35, 10, 1000),
        "salary": np.random.normal(50000, 15000, 1000),
        "department": np.random.choice(["IT", "Sales", "Marketing", "HR"], 1000),
        "join_date": pd.date_range("2020-01-01", periods=1000, freq="D"),
    }

    # Add some missing values and outliers
    sample_df = pd.DataFrame(sample_data)
    sample_df.loc[::50, "age"] = np.nan  # 2% missing
    sample_df.loc[::100, "salary"] = np.nan  # 1% missing
    sample_df.loc[5, "salary"] = 500000  # Outlier

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
