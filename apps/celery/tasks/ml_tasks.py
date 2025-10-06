"""
Machine Learning and Deep Learning Celery Tasks

This module contains CPU-intensive ML/DL operations that should NOT run in the async event loop.
All tasks here are synchronous and executed by Celery workers in the 'ml_processing' queue.

Purpose:
- Prevent event loop blocking from scikit-learn, TensorFlow operations
- Enable parallel processing of multiple ML training jobs
- Provide async-safe interface for DL services

Queue: ml_processing (dedicated worker pool recommended)
Priority: HIGH - These tasks can take 30-60 seconds
"""

import logging
from typing import Any

from celery import Task

from apps.celery.celery_app import celery_app

logger = logging.getLogger(__name__)


class MLTask(Task):
    """Base task for ML operations with error handling and logging."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log task failure for monitoring."""
        logger.error(
            f"ML Task {self.name} failed: {exc}",
            extra={"task_id": task_id, "args": args, "kwargs": kwargs, "error": str(exc)},
        )

    def on_success(self, retval, task_id, args, kwargs):
        """Log task success for monitoring."""
        logger.info(
            f"ML Task {self.name} completed successfully",
            extra={"task_id": task_id, "args": args, "kwargs": kwargs},
        )


@celery_app.task(
    name="apps.celery.tasks.ml_tasks.train_growth_model",
    base=MLTask,
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def train_growth_model(
    self, channel_id: int, training_data: dict[str, Any], config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Train growth forecasting model for a channel.

    This task performs CPU-intensive scikit-learn operations:
    - StandardScaler.fit() on feature data
    - PolynomialFeatures.fit_transform()
    - Model training and validation

    Args:
        channel_id: Telegram channel ID
        training_data: Historical metrics and features
        config: Optional training configuration

    Returns:
        Dict with trained model artifacts and metrics

    Raises:
        Exception: Re-raised after retry attempts exhausted
    """
    try:
        logger.info(f"Starting growth model training for channel {channel_id}")

        # Import here to avoid loading heavy libraries at startup
        from core.services.deep_learning.growth.growth_forecaster_service import (
            GrowthForecasterService,
        )
        from core.services.deep_learning.infrastructure.gpu_config import GPUConfigService
        from core.services.deep_learning.infrastructure.model_loader import ModelLoader

        # Initialize required services
        gpu_config = GPUConfigService()
        model_loader = ModelLoader()

        # Initialize forecaster service
        forecaster = GrowthForecasterService(gpu_config=gpu_config, model_loader=model_loader)

        # Update progress
        self.update_state(state="PROGRESS", meta={"progress": 30, "status": "Processing data"})

        # Convert training_data to DataFrame
        import pandas as pd

        if isinstance(training_data, dict) and "data" in training_data:
            df = pd.DataFrame(training_data["data"])
        elif isinstance(training_data, dict):
            df = pd.DataFrame([training_data])
        elif isinstance(training_data, list):
            df = pd.DataFrame(training_data)
        else:
            df = training_data  # Assume it's already a DataFrame

        # Get forecast configuration
        forecast_horizon = config.get("forecast_horizon", 7) if config else 7
        include_uncertainty = config.get("include_uncertainty", True) if config else True

        self.update_state(state="PROGRESS", meta={"progress": 60, "status": "Making predictions"})

        # Perform CPU-intensive prediction (BLOCKING - OK in Celery worker)
        # This uses the new predict_growth_sync method
        result = forecaster.predict_growth_sync(
            data=df,
            forecast_horizon=forecast_horizon,
            include_uncertainty=include_uncertainty,
            return_attention=False,
        )

        self.update_state(state="PROGRESS", meta={"progress": 90, "status": "Finalizing results"})

        logger.info(
            f"Growth model training completed for channel {channel_id}",
            extra={"forecast_horizon": forecast_horizon, "confidence": result.get("confidence", 0)},
        )

        return {
            "status": "success",
            "channel_id": channel_id,
            "forecast_horizon": forecast_horizon,
            "predictions": result.get("predictions", []),
            "confidence": result.get("confidence", 0.0),
            "uncertainty": result.get("uncertainty"),
            "timestamp": result.get("timestamp"),
            "metrics": result.get("metrics", {}),
        }

    except Exception as exc:
        logger.error(f"Growth model training failed for channel {channel_id}: {exc}", exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=exc)


@celery_app.task(
    name="apps.celery.tasks.ml_tasks.process_content_analysis",
    base=MLTask,
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def process_content_analysis(
    self, post_id: int, content_data: dict[str, Any], analysis_type: str = "sentiment"
) -> dict[str, Any]:
    """
    Perform CPU-intensive content analysis (NLP, sentiment, topic modeling).

    This task handles:
    - Text vectorization (TF-IDF, word embeddings)
    - Sentiment analysis with ML models
    - Topic extraction
    - Content classification

    Args:
        post_id: Post identifier
        content_data: Post content and metadata
        analysis_type: Type of analysis (sentiment/topic/classification)

    Returns:
        Dict with analysis results and confidence scores
    """
    try:
        logger.info(
            f"Starting content analysis for post {post_id}", extra={"analysis_type": analysis_type}
        )

        # TODO: ContentAnalyzer service not yet implemented
        # from core.services.deep_learning.content.content_analyzer import ContentAnalyzer

        logger.warning(
            f"Content analysis requested for post {post_id} but service not implemented yet"
        )

        # Return placeholder result
        return {
            "status": "not_implemented",
            "post_id": post_id,
            "analysis_type": analysis_type,
            "message": "Content analysis service not yet implemented",
            "content_length": len(content_data.get("text", "")),
        }

    except Exception as exc:
        logger.error(f"Content analysis failed for post {post_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(
    name="apps.celery.tasks.ml_tasks.generate_predictions",
    base=MLTask,
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def generate_predictions(
    self, channel_id: int, prediction_type: str, input_data: dict[str, Any], horizon: int = 30
) -> dict[str, Any]:
    """
    Generate ML predictions for various metrics.

    This task handles:
    - Growth forecasting (subscriber trends)
    - Engagement predictions (views, reactions)
    - Optimal posting time recommendations
    - Content performance predictions

    Args:
        channel_id: Channel identifier
        prediction_type: Type of prediction (growth/engagement/timing/content)
        input_data: Historical data and features
        horizon: Prediction horizon in days

    Returns:
        Dict with predictions, confidence intervals, and feature importance
    """
    try:
        logger.info(
            f"Generating predictions for channel {channel_id}",
            extra={"type": prediction_type, "horizon": horizon},
        )

        # Import prediction services

        # TODO: PredictiveOrchestratorService requires many dependencies and only has async methods
        # orchestrator = PredictiveOrchestratorService()

        logger.warning(
            f"Prediction task called for channel {channel_id} but sync method not implemented. "
            "Use async prediction endpoints instead."
        )

        return {
            "status": "not_implemented",
            "channel_id": channel_id,
            "prediction_type": prediction_type,
            "message": "Sync prediction not available. Use async prediction endpoints.",
            "horizon": horizon,
        }

    except Exception as exc:
        logger.error(f"Prediction generation failed for channel {channel_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(name="apps.celery.tasks.ml_tasks.batch_train_models", base=MLTask, bind=True)
def batch_train_models(
    self, channel_ids: list[int], training_config: dict[str, Any]
) -> dict[str, Any]:
    """
    Train models for multiple channels in batch.

    This is a coordinator task that spawns individual training tasks.
    Useful for scheduled retraining of all active channels.

    Args:
        channel_ids: List of channel IDs to train
        training_config: Shared training configuration

    Returns:
        Dict with task IDs and status for each channel
    """
    try:
        logger.info(f"Starting batch model training for {len(channel_ids)} channels")

        task_results = {}

        # Spawn individual training tasks
        for channel_id in channel_ids:
            task = train_growth_model.delay(  # type: ignore[attr-defined]
                channel_id=channel_id,
                training_data={},  # Fetched inside task
                config=training_config,
            )
            task_results[channel_id] = {"task_id": task.id, "status": "queued"}

        logger.info(
            f"Batch training spawned {len(task_results)} tasks",
            extra={"channel_count": len(channel_ids)},
        )

        return {"status": "success", "total_channels": len(channel_ids), "tasks": task_results}

    except Exception as exc:
        logger.error(f"Batch training coordination failed: {exc}", exc_info=True)
        raise


# Helper function for async code to submit ML tasks
def submit_ml_task_async(task_name: str, *args, **kwargs) -> str:
    """
    Submit ML task from async code and return task ID.

    Usage in async services:
        task_id = submit_ml_task_async(
            "train_growth_model",
            channel_id=123,
            training_data=data
        )
        return {"task_id": task_id, "status": "processing"}

    Args:
        task_name: Name of ML task to execute
        *args: Positional arguments for task
        **kwargs: Keyword arguments for task

    Returns:
        Celery task ID for status checking
    """
    task_map = {
        "train_growth_model": train_growth_model,
        "process_content_analysis": process_content_analysis,
        "generate_predictions": generate_predictions,
        "batch_train_models": batch_train_models,
    }

    if task_name not in task_map:
        raise ValueError(f"Unknown ML task: {task_name}")

    task = task_map[task_name].delay(*args, **kwargs)
    return task.id
