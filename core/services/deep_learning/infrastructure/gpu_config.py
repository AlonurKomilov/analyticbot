"""
GPU Configuration Microservice
=============================

Handles GPU detection, configuration, and optimization for deep learning models.
This is a focused microservice with single responsibility: GPU management.
"""

import torch
import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    """Device information dataclass"""
    device_type: str
    device_name: str
    memory_total: Optional[int] = None
    memory_available: Optional[int] = None
    compute_capability: Optional[str] = None
    cuda_available: bool = False
    mps_available: bool = False


class GPUConfigService:
    """Microservice for GPU configuration and hardware optimization"""
    
    def __init__(self):
        self.device = self._detect_optimal_device()
        self.device_info = self._get_device_info()
        self.memory_limit = self._calculate_memory_limit()
        
        logger.info(f"🔧 GPUConfigService initialized on {self.device}")
        logger.info(f"📊 Device info: {self.device_info.device_name}")
    
    def _detect_optimal_device(self) -> torch.device:
        """Detect the best available device for computation"""
        if torch.cuda.is_available():
            # Use CUDA if available
            device = torch.device("cuda")
            logger.info("🚀 CUDA GPU detected and selected")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            # Use Apple Silicon MPS if available
            device = torch.device("mps")
            logger.info("🍎 Apple MPS detected and selected")
        else:
            # Fallback to CPU
            device = torch.device("cpu")
            logger.info("💻 Using CPU (no GPU acceleration available)")
        
        return device
    
    def _get_device_info(self) -> DeviceInfo:
        """Get detailed device information"""
        if self.device.type == "cuda":
            gpu_props = torch.cuda.get_device_properties(0)
            return DeviceInfo(
                device_type="cuda",
                device_name=gpu_props.name,
                memory_total=gpu_props.total_memory,
                memory_available=torch.cuda.get_device_properties(0).total_memory,
                compute_capability=f"{gpu_props.major}.{gpu_props.minor}",
                cuda_available=True,
                mps_available=False
            )
        elif self.device.type == "mps":
            return DeviceInfo(
                device_type="mps",
                device_name="Apple Silicon GPU",
                cuda_available=False,
                mps_available=True
            )
        else:
            import platform
            return DeviceInfo(
                device_type="cpu",
                device_name=f"CPU ({platform.processor()})",
                cuda_available=False,
                mps_available=False
            )
    
    def _calculate_memory_limit(self) -> Optional[int]:
        """Calculate optimal memory limit for models"""
        if self.device.type == "cuda":
            total_memory = torch.cuda.get_device_properties(0).total_memory
            # Use 80% of available GPU memory
            return int(total_memory * 0.8)
        # No specific limit for CPU/MPS
        return None
    
    def get_optimal_batch_size(self, model_size_mb: float = 100) -> int:
        """Calculate optimal batch size based on available memory
        
        Args:
            model_size_mb: Estimated model size in MB
            
        Returns:
            Recommended batch size
        """
        if self.device.type == "cuda" and self.memory_limit:
            # Calculate based on GPU memory
            available_memory_mb = self.memory_limit / (1024 * 1024)
            # Reserve memory for model and leave buffer for gradients
            available_for_batch = available_memory_mb - (model_size_mb * 3)  # 3x for model + gradients + activations
            
            # Rough estimate: each sample takes ~1MB for typical analytics data
            sample_memory_mb = 1.0
            optimal_batch_size = max(1, int(available_for_batch / sample_memory_mb))
            
            # Clamp to reasonable range
            return min(max(optimal_batch_size, 1), 128)
        
        elif self.device.type == "mps":
            # Apple Silicon - moderate batch sizes work well
            return 32
        else:
            # CPU - smaller batches
            return 16
    
    def get_device_info(self) -> Dict:
        """Get device information as dictionary"""
        info = {
            "device": str(self.device),
            "device_type": self.device_info.device_type,
            "device_name": self.device_info.device_name,
            "cuda_available": self.device_info.cuda_available,
            "mps_available": self.device_info.mps_available,
        }
        
        if self.device_info.memory_total:
            info["memory_total_gb"] = round(self.device_info.memory_total / (1024**3), 2)
        
        if self.device_info.compute_capability:
            info["compute_capability"] = self.device_info.compute_capability
        
        return info
    
    def is_gpu_available(self) -> bool:
        """Check if any GPU acceleration is available"""
        return self.device.type in ["cuda", "mps"]
    
    def optimize_for_inference(self) -> Dict:
        """Configure PyTorch for optimal inference performance"""
        optimizations = []
        
        # Set number of threads for CPU
        if self.device.type == "cpu":
            torch.set_num_threads(4)  # Optimal for most analytics workloads
            optimizations.append("set_cpu_threads=4")
        
        # Enable cuDNN benchmarking for consistent input sizes
        if self.device.type == "cuda":
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False  # Slight performance gain
            optimizations.append("cudnn_benchmark=True")
        
        # Disable gradient computation for inference
        torch.set_grad_enabled(False)
        optimizations.append("gradients_disabled")
        
        logger.info(f"🔧 Applied optimizations: {', '.join(optimizations)}")
        
        return {
            "optimizations_applied": optimizations,
            "device": str(self.device),
            "inference_ready": True
        }
    
    def get_recommended_settings(self, task_type: str = "inference") -> Dict:
        """Get recommended settings for different task types
        
        Args:
            task_type: "inference", "training", or "batch_processing"
            
        Returns:
            Dictionary with recommended settings
        """
        base_settings = {
            "device": str(self.device),
            "batch_size": self.get_optimal_batch_size(),
        }
        
        if task_type == "inference":
            base_settings.update({
                "gradient_computation": False,
                "deterministic": False,  # Faster inference
                "benchmark_mode": True if self.device.type == "cuda" else False
            })
        elif task_type == "training":
            base_settings.update({
                "gradient_computation": True,
                "deterministic": True,   # Reproducible training
                "benchmark_mode": False,
                "mixed_precision": True if self.device.type == "cuda" else False
            })
        elif task_type == "batch_processing":
            base_settings.update({
                "batch_size": min(self.get_optimal_batch_size() * 2, 256),  # Larger batches
                "gradient_computation": False,
                "benchmark_mode": True if self.device.type == "cuda" else False
            })
        
        return base_settings
    
    def clear_cache(self) -> Dict:
        """Clear GPU cache if available"""
        if self.device.type == "cuda":
            torch.cuda.empty_cache()
            return {"cache_cleared": True, "device": "cuda"}
        
        return {"cache_cleared": False, "reason": "no_gpu_cache_available"}
    
    def get_service_health(self) -> Dict:
        """Get service health status"""
        try:
            # Test device availability
            test_tensor = torch.tensor([1.0], device=self.device)
            device_working = True
        except Exception as e:
            device_working = False
            logger.error(f"Device test failed: {e}")
        
        return {
            "service": "gpu_config",
            "status": "healthy" if device_working else "unhealthy",
            "device_working": device_working,
            "device_info": self.get_device_info(),
            "memory_limit_mb": self.memory_limit / (1024*1024) if self.memory_limit else None
        }