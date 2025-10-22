"""
Data cleaning module.

This module handles data cleaning operations including duplicate removal,
missing value handling, outlier detection and removal, and data validation.
"""

from sklearn.ensemble import IsolationForest

from .base import IMPUTERS, logger, np, pd, stats


class DataCleaningMixin:
    """
    Mixin class providing data cleaning capabilities.
    
    Features:
    - Duplicate removal
    - Missing value handling (multiple strategies)
    - Outlier detection and removal (IQR, Z-score, Isolation Forest)
    - Data validation
    """

    def __init__(self):
        """Initialize cleaning components"""
        self.imputers = IMPUTERS

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
            cleaned_df = validate_data(cleaned_df)

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
                    from sklearn.impute import KNNImputer

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
                from sklearn.impute import KNNImputer

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
                try:
                    column_data = df[col].dropna()
                    if len(column_data) > 0:
                        z_scores = np.abs(stats.zscore(column_data.values))
                        # Create boolean mask for the original dataframe
                        valid_indices = column_data.index[z_scores < 3]
                        df = df.loc[df.index.isin(valid_indices)]
                except Exception as e:
                    logger.warning(f"Z-score outlier removal failed for column {col}: {e}")
                    continue

        elif method == "isolation":
            if len(numeric_cols) > 0:
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outliers = iso_forest.fit_predict(df[numeric_cols].fillna(0))
                df = df[outliers == 1]

        return df


# Utility functions

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Basic data validation and cleaning"""
    # Remove empty columns
    df = df.dropna(axis=1, how="all")

    # Remove empty rows
    df = df.dropna(axis=0, how="all")

    return df


__all__ = ["DataCleaningMixin", "validate_data"]
