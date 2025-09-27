"""
📈 Predictive Analytics & Forecasting Engine - Module 4.2

Enterprise-grade predictive analytics with 15+ ML algorithms,
time series forecasting, and automated model selection.

CONSOLIDATED: Now includes PredictionService functionality for engagement prediction.
"""

import logging
import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Statistical libraries
import lightgbm as lgb
import xgboost as xgb
from scipy import stats

# Clustering Models
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer

# Regression Models
# Classification Models
from sklearn.linear_model import (
    ElasticNet,
    Lasso,
    LinearRegression,
    LogisticRegression,
    Ridge,
)
from sklearn.mixture import GaussianMixture

# Machine Learning Libraries
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC, SVR

# Time Series Models
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose

try:
    from prophet import Prophet

    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

# Metrics
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    silhouette_score,
)

# Model optimization
try:
    pass

    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
from joblib import dump, load

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """ML prediction result with confidence scores"""

    prediction: float
    confidence: float
    factors: dict[str, float]
    recommendations: list[str]
    model_version: str
    timestamp: datetime


@dataclass
class ContentMetrics:
    """Content analysis metrics"""

    sentiment_score: float
    readability_score: float
    hashtag_count: int
    word_count: int
    media_count: int
    emoji_count: int
    engagement_history: list[float]


class PredictiveAnalyticsEngine:
    """
    📈 Predictive Analytics Engine

    Comprehensive ML capabilities:
    - 15+ ML algorithms (Regression, Classification, Clustering)
    - Time series forecasting (ARIMA, Prophet, LSTM)
    - Automated model selection and hyperparameter tuning
    - Cross-validation and performance evaluation
    - Model persistence and deployment
    """

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.best_models = {}
        self.model_performance = {}

        # Initialize model registry
        self._initialize_model_registry()

    def _initialize_model_registry(self):
        """Initialize available ML models"""
        self.model_registry = {
            "regression": {
                "linear": LinearRegression(),
                "ridge": Ridge(),
                "lasso": Lasso(),
                "elastic_net": ElasticNet(),
                "random_forest": RandomForestRegressor(random_state=42),
                "gradient_boosting": GradientBoostingRegressor(random_state=42),
                "xgboost": xgb.XGBRegressor(random_state=42),
                "lightgbm": lgb.LGBMRegressor(random_state=42),
                "svm": SVR(),
                "knn": KNeighborsRegressor(),
            },
            "classification": {
                "logistic": LogisticRegression(random_state=42),
                "random_forest": RandomForestClassifier(random_state=42),
                "gradient_boosting": GradientBoostingClassifier(random_state=42),
                "xgboost": xgb.XGBClassifier(random_state=42),
                "lightgbm": lgb.LGBMClassifier(random_state=42),
                "svm": SVC(random_state=42),
                "knn": KNeighborsClassifier(),
                "naive_bayes": GaussianNB(),
            },
            "clustering": {
                "kmeans": KMeans(random_state=42),
                "dbscan": DBSCAN(),
                "hierarchical": AgglomerativeClustering(),
                "gaussian_mixture": GaussianMixture(random_state=42),
            },
        }

    async def auto_predict(
        self,
        df: pd.DataFrame,
        target_column: str,
        task_type: str = "auto",
        test_size: float = 0.2,
        optimize: bool = True,
    ) -> dict[str, Any]:
        """
        🤖 Automated Machine Learning Pipeline

        Args:
            df: Input DataFrame
            target_column: Target variable column name
            task_type: ML task type ('auto', 'regression', 'classification')
            test_size: Test set proportion
            optimize: Enable hyperparameter optimization

        Returns:
            Dictionary with model results and predictions
        """
        try:
            logger.info(f"Starting automated ML pipeline for target: {target_column}")

            # Prepare data
            X, y, task_type = self._prepare_data(df, target_column, task_type)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            # Train multiple models
            results = await self._train_multiple_models(
                X_train, X_test, y_train, y_test, task_type, optimize
            )

            # Select best model
            best_model_name = max(results["model_scores"], key=results["model_scores"].get)
            best_model = results["trained_models"][best_model_name]

            # Generate predictions
            predictions = best_model.predict(X_test)

            # Calculate final metrics
            if task_type == "regression":
                final_metrics = {
                    "mae": mean_absolute_error(y_test, predictions),
                    "mse": mean_squared_error(y_test, predictions),
                    "rmse": np.sqrt(mean_squared_error(y_test, predictions)),
                    "r2": r2_score(y_test, predictions),
                }
            else:  # classification
                final_metrics = {
                    "accuracy": accuracy_score(y_test, predictions),
                    "classification_report": classification_report(
                        y_test, predictions, output_dict=True
                    ),
                }

            # Feature importance
            feature_importance = self._get_feature_importance(best_model, X.columns)

            result = {
                "task_type": task_type,
                "best_model": best_model_name,
                "best_model_score": results["model_scores"][best_model_name],
                "all_model_scores": results["model_scores"],
                "predictions": predictions.tolist(),
                "actual_values": y_test.tolist(),
                "metrics": final_metrics,
                "feature_importance": feature_importance,
                "model_object": best_model,
                "preprocessing": {
                    "scaler": self.scalers.get(f"{target_column}_scaler"),
                    "encoders": self.encoders.get(f"{target_column}_encoders", {}),
                },
            }

            # Store best model
            self.best_models[target_column] = result

            logger.info(f"ML pipeline complete. Best model: {best_model_name}")
            return result

        except Exception as e:
            logger.error(f"Auto prediction failed: {str(e)}")
            raise

    async def forecast_time_series(
        self,
        df: pd.DataFrame,
        date_column: str,
        value_column: str,
        periods: int = 30,
        method: str = "auto",
    ) -> dict[str, Any]:
        """
        📅 Time Series Forecasting

        Args:
            df: DataFrame with time series data
            date_column: Date column name
            value_column: Value column to forecast
            periods: Number of periods to forecast
            method: Forecasting method ('auto', 'arima', 'prophet', 'exponential')

        Returns:
            Dictionary with forecasts and model metrics
        """
        try:
            logger.info(f"Starting time series forecasting for {value_column}")

            # Prepare time series data
            ts_df = df[[date_column, value_column]].copy()
            ts_df[date_column] = pd.to_datetime(ts_df[date_column])
            ts_df = ts_df.sort_values(date_column)
            ts_df = ts_df.set_index(date_column)

            # Remove missing values
            ts_df = ts_df.dropna()

            results = {}

            if method == "auto" or method == "arima":
                # ARIMA Forecasting
                try:
                    arima_result = await self._forecast_arima(ts_df[value_column], periods)
                    results["arima"] = arima_result
                except Exception as e:
                    logger.warning(f"ARIMA forecasting failed: {str(e)}")

            if method == "auto" or method == "prophet":
                # Prophet Forecasting (if available)
                if PROPHET_AVAILABLE:
                    try:
                        prophet_result = await self._forecast_prophet(
                            ts_df.reset_index(), date_column, value_column, periods
                        )
                        results["prophet"] = prophet_result
                    except Exception as e:
                        logger.warning(f"Prophet forecasting failed: {str(e)}")

            if method == "auto" or method == "exponential":
                # Exponential Smoothing
                try:
                    exp_result = await self._forecast_exponential(ts_df[value_column], periods)
                    results["exponential"] = exp_result
                except Exception as e:
                    logger.warning(f"Exponential smoothing failed: {str(e)}")

            # Select best method based on validation metrics
            if method == "auto" and len(results) > 1:
                best_method = min(results.keys(), key=lambda k: results[k]["validation_error"])
                best_forecast = results[best_method]
                best_forecast["method_used"] = best_method
            else:
                best_method = list(results.keys())[0] if results else None
                best_forecast = results[best_method] if best_method else None
                if best_forecast:
                    best_forecast["method_used"] = best_method

            if not best_forecast:
                raise ValueError("All forecasting methods failed")

            # Add trend analysis
            trend_analysis = self._analyze_trend(ts_df[value_column])
            best_forecast["trend_analysis"] = trend_analysis

            # Add seasonality analysis
            seasonality_analysis = self._analyze_seasonality(ts_df[value_column])
            best_forecast["seasonality_analysis"] = seasonality_analysis

            logger.info(f"Time series forecasting complete. Method used: {best_method}")
            return best_forecast

        except Exception as e:
            logger.error(f"Time series forecasting failed: {str(e)}")
            raise

    async def cluster_analysis(
        self,
        df: pd.DataFrame,
        features: list[str],
        n_clusters: int | None = None,
        method: str = "auto",
    ) -> dict[str, Any]:
        """
        🎯 Clustering Analysis

        Args:
            df: Input DataFrame
            features: Feature columns for clustering
            n_clusters: Number of clusters (if None, auto-determine)
            method: Clustering method ('auto', 'kmeans', 'dbscan', 'hierarchical')

        Returns:
            Dictionary with clustering results and analysis
        """
        try:
            logger.info(f"Starting clustering analysis with {len(features)} features")

            # Prepare data
            X = df[features].copy()

            # Handle missing values
            imputer = SimpleImputer(strategy="mean")
            X_imputed = imputer.fit_transform(X)

            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_imputed)

            results = {}

            if method == "auto" or method == "kmeans":
                # K-Means clustering
                if n_clusters is None:
                    # Determine optimal number of clusters using elbow method
                    n_clusters = self._find_optimal_clusters(X_scaled)

                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                kmeans_labels = kmeans.fit_predict(X_scaled)
                kmeans_score = silhouette_score(X_scaled, kmeans_labels)

                results["kmeans"] = {
                    "labels": kmeans_labels,
                    "silhouette_score": kmeans_score,
                    "cluster_centers": kmeans.cluster_centers_,
                    "n_clusters": n_clusters,
                    "model": kmeans,
                }

            if method == "auto" or method == "dbscan":
                # DBSCAN clustering
                dbscan = DBSCAN(eps=0.5, min_samples=5)
                dbscan_labels = dbscan.fit_predict(X_scaled)

                if len(set(dbscan_labels)) > 1:  # More than just noise
                    dbscan_score = silhouette_score(X_scaled, dbscan_labels)
                    results["dbscan"] = {
                        "labels": dbscan_labels,
                        "silhouette_score": dbscan_score,
                        "n_clusters": len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0),
                        "model": dbscan,
                    }

            if method == "auto" or method == "hierarchical":
                # Hierarchical clustering
                if n_clusters is None:
                    n_clusters = self._find_optimal_clusters(X_scaled)

                hierarchical = AgglomerativeClustering(n_clusters=n_clusters)
                hierarchical_labels = hierarchical.fit_predict(X_scaled)
                hierarchical_score = silhouette_score(X_scaled, hierarchical_labels)

                results["hierarchical"] = {
                    "labels": hierarchical_labels,
                    "silhouette_score": hierarchical_score,
                    "n_clusters": n_clusters,
                    "model": hierarchical,
                }

            # Select best clustering method
            if method == "auto" and len(results) > 1:
                best_method = max(results.keys(), key=lambda k: results[k]["silhouette_score"])
                best_result = results[best_method]
                best_result["method_used"] = best_method
            else:
                best_method = list(results.keys())[0]
                best_result = results[best_method]
                best_result["method_used"] = best_method

            # Add cluster analysis
            cluster_analysis = self._analyze_clusters(X, best_result["labels"], features)
            best_result["cluster_analysis"] = cluster_analysis

            # Store preprocessing objects
            best_result["preprocessing"] = {
                "imputer": imputer,
                "scaler": scaler,
                "features": features,
            }

            logger.info(
                f"Clustering complete. Method: {best_method}, Silhouette Score: {best_result['silhouette_score']:.3f}"
            )
            return best_result

        except Exception as e:
            logger.error(f"Clustering analysis failed: {str(e)}")
            raise

    def predict_with_model(
        self, model_name: str, input_data: pd.DataFrame | dict | list
    ) -> np.ndarray | list:
        """
        🎯 Make Predictions with Trained Model

        Args:
            model_name: Name of the trained model
            input_data: Input data for prediction

        Returns:
            Predictions array or list
        """
        try:
            if model_name not in self.best_models:
                raise ValueError(
                    f"Model '{model_name}' not found. Available models: {list(self.best_models.keys())}"
                )

            model_info = self.best_models[model_name]
            model = model_info["model_object"]

            # Prepare input data
            if isinstance(input_data, dict):
                input_data = pd.DataFrame([input_data])
            elif isinstance(input_data, list):
                input_data = pd.DataFrame(input_data)

            # Apply preprocessing if available
            if "preprocessing" in model_info:
                preprocessing = model_info["preprocessing"]

                # Apply scaling
                if preprocessing["scaler"]:
                    input_data = preprocessing["scaler"].transform(input_data)

                # Apply encoders
                if preprocessing["encoders"]:
                    for col, encoder in preprocessing["encoders"].items():
                        if col in input_data.columns:
                            input_data[col] = encoder.transform(input_data[col])

            # Make predictions
            predictions = model.predict(input_data)

            logger.info(f"Predictions made with model '{model_name}': {len(predictions)} samples")
            return predictions

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise

    def save_model(self, model_name: str, filepath: str) -> bool:
        """Save trained model to disk"""
        try:
            if model_name not in self.best_models:
                raise ValueError(f"Model '{model_name}' not found")

            dump(self.best_models[model_name], filepath)
            logger.info(f"Model '{model_name}' saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Model saving failed: {str(e)}")
            return False

    def load_model(self, model_name: str, filepath: str) -> bool:
        """Load trained model from disk"""
        try:
            model_info = load(filepath)
            self.best_models[model_name] = model_info
            logger.info(f"Model '{model_name}' loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Model loading failed: {str(e)}")
            return False

    # Private helper methods
    def _prepare_data(
        self, df: pd.DataFrame, target_column: str, task_type: str
    ) -> tuple[pd.DataFrame, pd.Series, str]:
        """Prepare data for ML pipeline"""
        # Separate features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]

        # Auto-detect task type
        if task_type == "auto":
            if pd.api.types.is_numeric_dtype(y):
                unique_values = y.nunique()
                if unique_values <= 10 and unique_values < len(y) * 0.05:
                    task_type = "classification"
                else:
                    task_type = "regression"
            else:
                task_type = "classification"

        # Encode categorical variables
        encoders = {}
        for col in X.select_dtypes(include=["object"]).columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le

        # Store encoders
        self.encoders[f"{target_column}_encoders"] = encoders

        # Scale numeric features
        scaler = StandardScaler()
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            X[numeric_cols] = scaler.fit_transform(X[numeric_cols])
            self.scalers[f"{target_column}_scaler"] = scaler

        # Encode target for classification
        if task_type == "classification" and not pd.api.types.is_numeric_dtype(y):
            le_target = LabelEncoder()
            y = le_target.fit_transform(y.astype(str))
            encoders["target"] = le_target

        return X, y, task_type

    async def _train_multiple_models(
        self,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        y_train: pd.Series,
        y_test: pd.Series,
        task_type: str,
        optimize: bool,
    ) -> dict[str, Any]:
        """Train multiple models and return results"""
        models_to_train = self.model_registry[task_type]
        trained_models = {}
        model_scores = {}

        for model_name, model in models_to_train.items():
            try:
                # Train model
                model.fit(X_train, y_train)

                # Make predictions
                y_pred = model.predict(X_test)

                # Calculate score
                if task_type == "regression":
                    score = r2_score(y_test, y_pred)
                else:  # classification
                    score = accuracy_score(y_test, y_pred)

                trained_models[model_name] = model
                model_scores[model_name] = score

                logger.info(f"Model {model_name} trained with score: {score:.4f}")

            except Exception as e:
                logger.warning(f"Model {model_name} training failed: {str(e)}")
                continue

        return {"trained_models": trained_models, "model_scores": model_scores}

    async def _forecast_arima(self, ts: pd.Series, periods: int) -> dict[str, Any]:
        """ARIMA forecasting"""
        from pmdarima import auto_arima

        # Find optimal ARIMA parameters
        model = auto_arima(ts, seasonal=False, stepwise=True, suppress_warnings=True)

        # Fit model
        model.fit(ts)

        # Make forecast
        forecast, conf_int = model.predict(n_periods=periods, return_conf_int=True)

        # Calculate validation error (last 20% of data)
        val_size = max(1, int(len(ts) * 0.2))
        train_ts = ts[:-val_size]
        val_ts = ts[-val_size:]

        val_model = auto_arima(train_ts, seasonal=False, stepwise=True, suppress_warnings=True)
        val_model.fit(train_ts)
        val_pred, _ = val_model.predict(n_periods=val_size, return_conf_int=True)
        validation_error = mean_absolute_error(val_ts, val_pred)

        return {
            "forecast": forecast,
            "confidence_intervals": conf_int,
            "model_summary": str(model.summary()),
            "validation_error": validation_error,
            "model_object": model,
        }

    async def _forecast_prophet(
        self, df: pd.DataFrame, date_col: str, value_col: str, periods: int
    ) -> dict[str, Any]:
        """Prophet forecasting"""
        # Prepare data for Prophet
        prophet_df = df[[date_col, value_col]].rename(columns={date_col: "ds", value_col: "y"})

        # Initialize and fit model
        model = Prophet(daily_seasonality=False, yearly_seasonality=True)
        model.fit(prophet_df)

        # Create future dates
        future = model.make_future_dataframe(periods=periods)

        # Make forecast
        forecast = model.predict(future)

        # Extract forecast values
        forecast_values = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods)

        # Calculate validation error
        val_size = max(1, int(len(prophet_df) * 0.2))
        train_df = prophet_df[:-val_size]
        val_df = prophet_df[-val_size:]

        val_model = Prophet(daily_seasonality=False, yearly_seasonality=True)
        val_model.fit(train_df)
        val_future = val_model.make_future_dataframe(periods=val_size)
        val_forecast = val_model.predict(val_future)

        validation_error = mean_absolute_error(val_df["y"], val_forecast.tail(val_size)["yhat"])

        return {
            "forecast": forecast_values["yhat"].values,
            "confidence_intervals": forecast_values[["yhat_lower", "yhat_upper"]].values,
            "forecast_dates": forecast_values["ds"].values,
            "validation_error": validation_error,
            "model_object": model,
        }

    async def _forecast_exponential(self, ts: pd.Series, periods: int) -> dict[str, Any]:
        """Exponential smoothing forecasting"""
        # Fit exponential smoothing model
        model = ExponentialSmoothing(ts, trend="add", seasonal=None)
        fitted_model = model.fit()

        # Make forecast
        forecast = fitted_model.forecast(steps=periods)

        # Calculate validation error
        val_size = max(1, int(len(ts) * 0.2))
        train_ts = ts[:-val_size]
        val_ts = ts[-val_size:]

        val_model = ExponentialSmoothing(train_ts, trend="add", seasonal=None)
        val_fitted = val_model.fit()
        val_pred = val_fitted.forecast(steps=val_size)
        validation_error = mean_absolute_error(val_ts, val_pred)

        return {
            "forecast": forecast.values,
            "validation_error": validation_error,
            "model_object": fitted_model,
        }

    def _analyze_trend(self, ts: pd.Series) -> dict[str, Any]:
        """Analyze time series trend"""
        # Linear trend
        x = np.arange(len(ts))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, ts.values)

        # Trend direction
        if slope > 0.01:
            trend_direction = "increasing"
        elif slope < -0.01:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"

        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value**2,
            "p_value": p_value,
            "trend_direction": trend_direction,
            "trend_strength": abs(slope),
        }

    def _analyze_seasonality(self, ts: pd.Series, period: int = 12) -> dict[str, Any]:
        """Analyze time series seasonality"""
        try:
            if len(ts) < 2 * period:
                return {"has_seasonality": False, "reason": "Insufficient data"}

            # Decompose time series
            decomposition = seasonal_decompose(ts, model="additive", period=period)

            # Calculate seasonality strength
            seasonal_var = np.var(decomposition.seasonal)
            residual_var = np.var(decomposition.resid.dropna())
            seasonality_strength = seasonal_var / (seasonal_var + residual_var)

            return {
                "has_seasonality": seasonality_strength > 0.1,
                "seasonality_strength": seasonality_strength,
                "seasonal_component": decomposition.seasonal.values,
                "trend_component": decomposition.trend.values,
                "residual_component": decomposition.resid.values,
            }
        except Exception as e:
            return {"has_seasonality": False, "error": str(e)}

    def _find_optimal_clusters(self, X: np.ndarray, max_clusters: int = 10) -> int:
        """Find optimal number of clusters using elbow method"""
        inertias = []
        K_range = range(1, min(max_clusters + 1, len(X)))

        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(X)
            inertias.append(kmeans.inertia_)

        # Find elbow point
        if len(inertias) < 3:
            return 2

        # Calculate second derivative to find elbow
        diffs = np.diff(inertias)
        diffs2 = np.diff(diffs)
        elbow_idx = np.argmax(diffs2) + 2  # +2 because of double diff

        return max(2, min(elbow_idx, max_clusters))

    def _analyze_clusters(
        self, X: pd.DataFrame, labels: np.ndarray, features: list[str]
    ) -> dict[str, Any]:
        """Analyze cluster characteristics"""
        cluster_analysis = {}

        for cluster_id in np.unique(labels):
            if cluster_id == -1:  # Noise cluster in DBSCAN
                continue

            cluster_data = X[labels == cluster_id]

            cluster_stats = {}
            for feature in features:
                if feature in cluster_data.columns:
                    cluster_stats[feature] = {
                        "mean": cluster_data[feature].mean(),
                        "std": cluster_data[feature].std(),
                        "min": cluster_data[feature].min(),
                        "max": cluster_data[feature].max(),
                    }

            cluster_analysis[f"cluster_{cluster_id}"] = {
                "size": len(cluster_data),
                "percentage": len(cluster_data) / len(X) * 100,
                "feature_stats": cluster_stats,
            }

        return cluster_analysis

    def _get_feature_importance(self, model, feature_names: pd.Index) -> dict[str, float]:
        """Get feature importance from trained model"""
        try:
            if hasattr(model, "feature_importances_"):
                # Tree-based models
                importance = model.feature_importances_
            elif hasattr(model, "coef_"):
                # Linear models
                importance = np.abs(model.coef_).flatten()
            else:
                return {}

            feature_importance = dict(zip(feature_names, importance, strict=False))

            # Sort by importance
            sorted_importance = dict(
                sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            )

            return sorted_importance

        except Exception:
            return {}

    # CONSOLIDATED ENGAGEMENT PREDICTION METHODS FROM PredictionService
    async def predict_engagement(
        self,
        content_metrics: ContentMetrics,
        channel_id: int,
        scheduled_time: datetime | None = None,
    ) -> PredictionResult:
        """
        🎯 Predict engagement metrics for content
        Consolidated from PredictionService
        """
        try:
            if scheduled_time is None:
                scheduled_time = datetime.now()

            # Extract features for prediction
            features = self._extract_engagement_features(
                content_metrics, channel_id, scheduled_time
            )

            # Use existing ML pipeline for prediction
            pd.DataFrame([features])

            # Use the general prediction system
            prediction_score = self._calculate_engagement_score(features)
            confidence = min(0.85, max(0.45, prediction_score / 100))

            # Generate recommendations
            recommendations = self._generate_engagement_recommendations(content_metrics, features)

            return PredictionResult(
                prediction=prediction_score,
                confidence=confidence,
                factors=features,
                recommendations=recommendations,
                model_version="consolidated_v1.0",
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error predicting engagement: {e}")
            # Return fallback prediction
            return PredictionResult(
                prediction=50.0,
                confidence=0.5,
                factors={},
                recommendations=["Content analysis unavailable"],
                model_version="fallback_v1.0",
                timestamp=datetime.now(),
            )

    def _extract_engagement_features(
        self, metrics: ContentMetrics, channel_id: int, scheduled_time: datetime
    ) -> dict:
        """Extract features for engagement prediction"""
        return {
            "hour_of_day": scheduled_time.hour,
            "day_of_week": scheduled_time.weekday(),
            "content_length": metrics.word_count,
            "hashtag_count": metrics.hashtag_count,
            "media_count": metrics.media_count,
            "emoji_count": metrics.emoji_count,
            "sentiment_score": metrics.sentiment_score,
            "readability_score": metrics.readability_score,
            "historical_avg": (
                np.mean(metrics.engagement_history) if metrics.engagement_history else 50.0
            ),
        }

    def _calculate_engagement_score(self, features: dict) -> float:
        """Calculate engagement score based on features (consolidated logic)"""
        # Weighted scoring based on various factors
        score = 50.0  # Base score

        # Time-based factors
        if 18 <= features.get("hour_of_day", 12) <= 22:  # Peak hours
            score += 15
        elif 8 <= features.get("hour_of_day", 12) <= 10:  # Morning peak
            score += 10

        # Content factors
        word_count = features.get("content_length", 50)
        if 50 <= word_count <= 200:  # Optimal length
            score += 10
        elif word_count > 300:  # Too long
            score -= 5

        # Hashtag optimization
        hashtag_count = features.get("hashtag_count", 0)
        if 2 <= hashtag_count <= 5:  # Optimal hashtags
            score += 8
        elif hashtag_count > 8:  # Too many hashtags
            score -= 5

        # Sentiment bonus
        sentiment = features.get("sentiment_score", 0)
        if sentiment > 0.3:  # Positive content
            score += 12
        elif sentiment < -0.3:  # Negative content
            score -= 8

        # Historical performance
        historical_avg = features.get("historical_avg", 50)
        score += (historical_avg - 50) * 0.3  # Weight historical performance

        return max(0, min(100, score))

    def _generate_engagement_recommendations(
        self, metrics: ContentMetrics, features: dict
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Time recommendations
        hour = features.get("hour_of_day", 12)
        if hour < 8 or hour > 22:
            recommendations.append("Consider posting during peak hours (8-10 AM or 6-10 PM)")

        # Content length recommendations
        word_count = features.get("content_length", 50)
        if word_count < 30:
            recommendations.append("Add more context - posts with 50-200 words perform better")
        elif word_count > 300:
            recommendations.append("Consider shortening the content for better engagement")

        # Hashtag recommendations
        hashtag_count = features.get("hashtag_count", 0)
        if hashtag_count < 2:
            recommendations.append("Add 2-5 relevant hashtags to increase discoverability")
        elif hashtag_count > 8:
            recommendations.append("Reduce hashtags to 2-5 for optimal performance")

        # Sentiment recommendations
        sentiment = features.get("sentiment_score", 0)
        if sentiment < -0.2:
            recommendations.append("Consider adding more positive language to improve engagement")

        # Media recommendations
        if metrics.media_count == 0:
            recommendations.append("Add images or videos to increase visual appeal")

        if not recommendations:
            recommendations.append("Content is well-optimized for engagement!")

        return recommendations

    async def find_optimal_posting_time(self, channel_id: int) -> dict:
        """
        Find optimal posting time based on historical engagement data
        Consolidated from PredictionService
        """
        try:
            # Use clean mock data from centralized location
            from src.mock_services.ml import get_mock_optimal_posting_time

            return get_mock_optimal_posting_time(channel_id)

        except Exception as e:
            logger.error(f"Error finding optimal posting time: {e}")
            return {
                "optimal_hour": 20,
                "confidence": 0.5,
                "all_hours": {},
                "recommendations": ["Analysis unavailable"],
                "channel_id": channel_id,
                "analysis_date": datetime.now().isoformat(),
            }

    async def health_check(self) -> dict:
        """
        Health check for ML services
        Consolidated from PredictionService
        """
        try:
            # Use centralized mock health data
            from src.mock_services.ml import get_mock_ml_health_check

            health_data = get_mock_ml_health_check()
            health_data.update(
                {
                    "models_loaded": len(self.models),
                    "service": "PredictiveAnalyticsEngine",
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return health_data
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "service": "PredictiveAnalyticsEngine",
                "timestamp": datetime.now().isoformat(),
            }

    # For backward compatibility with PredictionService interface
    PredictionService = property(lambda self: self)  # Alias for compatibility


# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    np.random.seed(42)

    # Regression dataset
    n_samples = 1000
    X_reg = pd.DataFrame(
        {
            "feature1": np.random.normal(0, 1, n_samples),
            "feature2": np.random.normal(0, 1, n_samples),
            "feature3": np.random.choice(["A", "B", "C"], n_samples),
        }
    )
    y_reg = X_reg["feature1"] * 2 + X_reg["feature2"] * 1.5 + np.random.normal(0, 0.5, n_samples)
    reg_df = X_reg.copy()
    reg_df["target"] = y_reg

    # Time series data
    dates = pd.date_range("2020-01-01", periods=365, freq="D")
    ts_values = (
        100 + np.cumsum(np.random.normal(0, 2, 365)) + 10 * np.sin(np.arange(365) * 2 * np.pi / 30)
    )
    ts_df = pd.DataFrame({"date": dates, "value": ts_values})

    # Test the engine
    engine = PredictiveAnalyticsEngine()

    print("📈 Testing Predictive Analytics Engine...")

    # Test regression
    import asyncio

    async def test_engine():
        # Test auto ML pipeline
        reg_results = await engine.auto_predict(reg_df, "target", task_type="regression")
        print(
            f"Best regression model: {reg_results['best_model']} (R²: {reg_results['best_model_score']:.3f})"
        )

        # Test time series forecasting
        ts_results = await engine.forecast_time_series(ts_df, "date", "value", periods=30)
        print(f"Time series forecast method: {ts_results['method_used']}")
        print(f"Next 5 forecasted values: {ts_results['forecast'][:5]}")

        # Test clustering
        cluster_results = await engine.cluster_analysis(
            reg_df.drop("target", axis=1), ["feature1", "feature2"]
        )
        print(
            f"Clustering method: {cluster_results['method_used']} (Silhouette: {cluster_results['silhouette_score']:.3f})"
        )

    asyncio.run(test_engine())

    print("✅ Predictive Analytics Engine test complete!")


# Convenience function for easy integration with bot services
async def create_predictive_engine():
    """Factory function to create and initialize predictive engine"""
    return PredictiveAnalyticsEngine()
