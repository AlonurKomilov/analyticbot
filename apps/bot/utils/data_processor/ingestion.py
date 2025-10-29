"""
Data ingestion module.

This module handles multi-source data ingestion including CSV, JSON, Excel,
SQL databases, REST APIs, and streaming sources.
"""

from .base import aiofiles, create_engine, io, json, logger, pd, requests


class DataIngestionMixin:
    """
    Mixin class providing data ingestion capabilities.

    Supports ingestion from:
    - CSV files
    - JSON files and URLs
    - Excel files
    - SQL databases
    - REST APIs
    - Streaming sources (placeholder)
    """

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
                source_type = detect_source_type(source)

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

    async def _setup_streaming(self, source: str, **kwargs) -> pd.DataFrame:
        """Setup streaming data source (placeholder implementation)"""
        logger.info(f"Setting up streaming from: {source}")
        # For now, return empty DataFrame - can be implemented later
        return pd.DataFrame()

    async def _ingest_csv(self, filepath: str, **kwargs) -> pd.DataFrame:
        """Ingest CSV data with async file reading"""
        try:
            # Read CSV asynchronously
            async with aiofiles.open(filepath) as file:
                content = await file.read()

            # Parse CSV
            df = pd.read_csv(io.StringIO(content), **kwargs)

            # Auto-detect column types
            df = auto_detect_types(df)

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

            df = auto_detect_types(df)

            logger.info(f"JSON ingestion successful: {len(df)} rows, {len(df.columns)} columns")
            return df

        except Exception as e:
            logger.error(f"JSON ingestion failed: {str(e)}")
            raise

    async def _ingest_excel(self, filepath: str, **kwargs) -> pd.DataFrame:
        """Ingest Excel data"""
        try:
            df = pd.read_excel(filepath, **kwargs)
            df = auto_detect_types(df)

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
            df = auto_detect_types(df)

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
            df = auto_detect_types(df)

            logger.info(f"API ingestion successful: {len(df)} rows, {len(df.columns)} columns")
            return df

        except Exception as e:
            logger.error(f"API ingestion failed: {str(e)}")
            raise


# Utility functions


def detect_source_type(source: str) -> str:
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


def auto_detect_types(df: pd.DataFrame) -> pd.DataFrame:
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

            # Try numeric
            try:
                df[col] = pd.to_numeric(df[col])
                continue
            except Exception as e:
                logger.debug(f"Failed to convert column {col} to numeric: {e}")

    return df


__all__ = ["DataIngestionMixin", "detect_source_type", "auto_detect_types"]
