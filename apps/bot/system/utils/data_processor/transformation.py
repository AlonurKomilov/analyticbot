"""
Data transformation module.

This module provides data transformation capabilities including
scaling, encoding, binning, and feature engineering.
"""

from typing import Any

from .base import SCALERS, logger, np, pd


class DataTransformationMixin:
    """
    Mixin class providing data transformation capabilities.

    Features:
    - Feature scaling (standard, robust, minmax)
    - Logarithmic transformations
    - Category encoding (one-hot, label)
    - Binning
    - DateTime feature extraction
    """

    def __init__(self):
        """Initialize transformation components"""
        self.scalers = SCALERS

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


__all__ = ["DataTransformationMixin"]
