"""
Model Loader Microservice
=========================

Handles loading, saving, and managing ML models with proper error handling
and metadata tracking. This is a focused microservice for model lifecycle management.
"""

import json
import logging
import pickle
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


@dataclass
class ModelMetadata:
    """Model metadata dataclass"""

    model_name: str
    model_type: str
    version: str
    created_at: datetime
    file_size_mb: float
    framework: str
    architecture: str | None = None
    input_shape: tuple | None = None
    output_shape: tuple | None = None
    parameters_count: int | None = None
    training_config: dict | None = None


class ModelLoader:
    """Microservice for loading and managing ML models"""

    def __init__(self, models_base_path: str = "models/"):
        self.models_base_path = Path(models_base_path)
        self.models_base_path.mkdir(parents=True, exist_ok=True)

        # Cache for loaded models
        self.model_cache = {}
        self.metadata_cache = {}

        logger.info(f"📦 ModelLoader initialized with base path: {self.models_base_path}")

    async def load_model(
        self,
        model_path: str,
        model_type: str,
        model_class: type | None = None,
        device: torch.device | None = None,
    ) -> Any:
        """Load a model from file with proper error handling

        Args:
            model_path: Path to model file (relative to base path)
            model_type: Type of model ("pytorch", "sklearn", "custom")
            model_class: Model class for PyTorch models
            device: Target device for PyTorch models

        Returns:
            Loaded model instance
        """
        try:
            full_path = self.models_base_path / model_path

            if not full_path.exists():
                raise FileNotFoundError(f"Model file not found: {full_path}")

            logger.info(f"📦 Loading {model_type} model from {model_path}")

            # Check cache first
            cache_key = f"{model_path}:{model_type}"
            if cache_key in self.model_cache:
                logger.info(f"✅ Model loaded from cache: {model_path}")
                return self.model_cache[cache_key]

            # Load based on model type
            if model_type == "pytorch":
                model = await self._load_pytorch_model(full_path, model_class, device)
            elif model_type == "sklearn":
                model = await self._load_sklearn_model(full_path)
            elif model_type == "custom":
                model = await self._load_custom_model(full_path)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")

            # Cache the loaded model
            self.model_cache[cache_key] = model

            logger.info(f"✅ Model loaded successfully: {model_path}")
            return model

        except Exception as e:
            logger.error(f"❌ Failed to load model {model_path}: {e}")
            raise

    async def save_model(
        self, model: Any, model_path: str, model_type: str, metadata: dict | None = None
    ) -> bool:
        """Save model to file with metadata

        Args:
            model: Model instance to save
            model_path: Path where to save (relative to base path)
            model_type: Type of model ("pytorch", "sklearn", "custom")
            metadata: Additional metadata to save

        Returns:
            True if successful, False otherwise
        """
        try:
            full_path = self.models_base_path / model_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"💾 Saving {model_type} model to {model_path}")

            # Save based on model type
            if model_type == "pytorch":
                success = await self._save_pytorch_model(model, full_path)
            elif model_type == "sklearn":
                success = await self._save_sklearn_model(model, full_path)
            elif model_type == "custom":
                success = await self._save_custom_model(model, full_path)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")

            if success:
                # Save metadata
                await self._save_model_metadata(full_path, model_type, model, metadata)

                # Update cache
                cache_key = f"{model_path}:{model_type}"
                self.model_cache[cache_key] = model

                logger.info(f"✅ Model saved successfully: {model_path}")

            return success

        except Exception as e:
            logger.error(f"❌ Failed to save model {model_path}: {e}")
            return False

    async def get_model_metadata(self, model_path: str) -> dict:
        """Get metadata for a saved model

        Args:
            model_path: Path to model file

        Returns:
            Model metadata dictionary
        """
        try:
            # Check cache first
            if model_path in self.metadata_cache:
                return self.metadata_cache[model_path]

            full_path = self.models_base_path / model_path
            metadata_path = full_path.with_suffix(full_path.suffix + ".meta.json")

            if not metadata_path.exists():
                logger.warning(f"Metadata file not found for {model_path}")
                return self._generate_basic_metadata(full_path)

            with open(metadata_path) as f:
                metadata = json.load(f)

            # Cache metadata
            self.metadata_cache[model_path] = metadata

            return metadata

        except Exception as e:
            logger.error(f"❌ Failed to load metadata for {model_path}: {e}")
            return {"error": str(e)}

    async def list_available_models(self, model_type: str | None = None) -> list[dict]:
        """List all available models with their metadata

        Args:
            model_type: Filter by model type (optional)

        Returns:
            List of model information dictionaries
        """
        try:
            models = []

            for model_file in self.models_base_path.rglob("*.pth"):  # PyTorch models
                if model_type and model_type != "pytorch":
                    continue

                relative_path = model_file.relative_to(self.models_base_path)
                metadata = await self.get_model_metadata(str(relative_path))

                models.append(
                    {
                        "path": str(relative_path),
                        "type": "pytorch",
                        "metadata": metadata,
                    }
                )

            for model_file in self.models_base_path.rglob("*.pkl"):  # Sklearn models
                if model_type and model_type != "sklearn":
                    continue

                relative_path = model_file.relative_to(self.models_base_path)
                metadata = await self.get_model_metadata(str(relative_path))

                models.append(
                    {
                        "path": str(relative_path),
                        "type": "sklearn",
                        "metadata": metadata,
                    }
                )

            logger.info(f"📋 Found {len(models)} available models")
            return models

        except Exception as e:
            logger.error(f"❌ Failed to list models: {e}")
            return []

    async def _load_pytorch_model(
        self,
        file_path: Path,
        model_class: type | None = None,
        device: torch.device | None = None,
    ) -> nn.Module:
        """Load PyTorch model"""
        if device is None:
            device = torch.device("cpu")

        if model_class:
            # Load with model class (preferred method)
            model = model_class()
            state_dict = torch.load(file_path, map_location=device)
            model.load_state_dict(state_dict)
            model.to(device)
            model.eval()
        else:
            # Load full model (fallback)
            model = torch.load(file_path, map_location=device)
            model.eval()

        return model

    async def _save_pytorch_model(self, model: nn.Module, file_path: Path) -> bool:
        """Save PyTorch model"""
        try:
            # Save only state dict (recommended)
            torch.save(model.state_dict(), file_path)
            return True
        except Exception as e:
            logger.error(f"PyTorch model save failed: {e}")
            return False

    async def _load_sklearn_model(self, file_path: Path) -> Any:
        """Load scikit-learn model"""
        with open(file_path, "rb") as f:
            return pickle.load(f)

    async def _save_sklearn_model(self, model: Any, file_path: Path) -> bool:
        """Save scikit-learn model"""
        try:
            with open(file_path, "wb") as f:
                pickle.dump(model, f)
            return True
        except Exception as e:
            logger.error(f"Sklearn model save failed: {e}")
            return False

    async def _load_custom_model(self, file_path: Path) -> Any:
        """Load custom model format"""
        # Implement based on your custom format
        with open(file_path, "rb") as f:
            return pickle.load(f)

    async def _save_custom_model(self, model: Any, file_path: Path) -> bool:
        """Save custom model format"""
        try:
            with open(file_path, "wb") as f:
                pickle.dump(model, f)
            return True
        except Exception as e:
            logger.error(f"Custom model save failed: {e}")
            return False

    async def _save_model_metadata(
        self,
        model_path: Path,
        model_type: str,
        model: Any,
        additional_metadata: dict | None = None,
    ) -> None:
        """Save model metadata to companion file"""
        try:
            metadata = {
                "model_name": model_path.stem,
                "model_type": model_type,
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "file_size_mb": round(model_path.stat().st_size / (1024 * 1024), 2),
                "framework": self._get_framework_name(model_type),
            }

            # Add model-specific metadata
            if model_type == "pytorch" and isinstance(model, nn.Module):
                metadata.update(
                    {
                        "parameters_count": sum(p.numel() for p in model.parameters()),
                        "architecture": type(model).__name__,
                    }
                )

            # Add additional metadata if provided
            if additional_metadata:
                metadata.update(additional_metadata)

            # Save to .meta.json file
            metadata_path = model_path.with_suffix(model_path.suffix + ".meta.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    def _get_framework_name(self, model_type: str) -> str:
        """Get framework name from model type"""
        framework_map = {
            "pytorch": "PyTorch",
            "sklearn": "scikit-learn",
            "custom": "Custom",
        }
        return framework_map.get(model_type, "Unknown")

    def _generate_basic_metadata(self, file_path: Path) -> dict:
        """Generate basic metadata when meta file doesn't exist"""
        try:
            stat = file_path.stat()
            return {
                "model_name": file_path.stem,
                "model_type": "unknown",
                "version": "unknown",
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
                "framework": "unknown",
            }
        except Exception:
            return {"error": "metadata_unavailable"}

    def clear_cache(self) -> dict:
        """Clear model cache"""
        cached_models = len(self.model_cache)
        cached_metadata = len(self.metadata_cache)

        self.model_cache.clear()
        self.metadata_cache.clear()

        return {
            "cache_cleared": True,
            "models_cleared": cached_models,
            "metadata_cleared": cached_metadata,
        }

    def get_service_health(self) -> dict:
        """Get service health status"""
        return {
            "service": "model_loader",
            "status": "healthy",
            "base_path": str(self.models_base_path),
            "base_path_exists": self.models_base_path.exists(),
            "cached_models": len(self.model_cache),
            "cached_metadata": len(self.metadata_cache),
        }
