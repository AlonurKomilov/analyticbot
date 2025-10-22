"""
Data quality analysis module.

This module provides comprehensive data quality analysis including
column analysis, missing data detection, correlation analysis,
and overall quality scoring.
"""

from typing import Any

from .base import logger, np, pd


class DataQualityMixin:
    """
    Mixin class providing data quality analysis capabilities.
    
    Features:
    - Basic dataset metrics
    - Column-wise analysis
    - Missing data analysis
    - Statistical summaries
    - Correlation analysis
    - Overall quality scoring
    """

    def analyze_data_quality(self, df: pd.DataFrame) -> dict[str, Any]:
        """
        📊 Comprehensive Data Quality Analysis

        Returns:
            Dictionary with detailed data quality metrics
        """
        try:
            analysis: dict[str, Any] = {
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
                            "outliers_count": count_outliers(df[col]),
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
                        try:
                            # Handle different types of correlation values
                            # Type cast to Any to handle numpy/pandas scalar types properly
                            from typing import Any as AnyType

                            corr_val_any: AnyType = corr_val

                            if hasattr(corr_val_any, "item") and callable(corr_val_any.item):
                                # For pandas/numpy scalars with .item() method
                                # .item() returns a scalar that needs to be converted
                                item_result = corr_val_any.item()
                                if isinstance(item_result, (int, float)):
                                    corr_val_float = float(item_result)
                                else:
                                    # Skip non-numeric scalar results
                                    continue
                            elif isinstance(corr_val, (int, float)):
                                # For regular numeric types
                                corr_val_float = float(corr_val)
                            else:
                                # Skip non-numeric values
                                continue

                            if abs(corr_val_float) > 0.7:  # High correlation threshold
                                high_correlations.append(
                                    {
                                        "column1": correlation_matrix.columns[i],
                                        "column2": correlation_matrix.columns[j],
                                        "correlation": corr_val_float,
                                    }
                                )
                        except (ValueError, TypeError):
                            # Skip non-numeric correlation values
                            continue

                analysis["correlations"] = {
                    "high_correlations": high_correlations,
                    "correlation_matrix": correlation_matrix.to_dict(),
                }

            # Calculate overall quality score
            quality_score = calculate_quality_score(analysis)
            analysis["quality_score"] = quality_score

            logger.info(f"Data quality analysis complete. Quality score: {quality_score:.2f}/100")
            return analysis

        except Exception as e:
            logger.error(f"Data quality analysis failed: {str(e)}")
            raise


# Utility functions

def count_outliers(series: pd.Series) -> int:
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


def calculate_quality_score(analysis: dict[str, Any]) -> float:
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


__all__ = ["DataQualityMixin", "count_outliers", "calculate_quality_score"]
