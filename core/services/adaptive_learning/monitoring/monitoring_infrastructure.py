"""
Monitoring Infrastructure for Adaptive Learning
===============================================

Provides infrastructure services for monitoring model performance,
storing metrics, and managing monitoring resources.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
from pathlib import Path

from ..protocols.monitoring_protocols import (
    MonitoringInfrastructureProtocol,
    PerformanceMetric,
    PerformanceAlert,
    PerformanceMetricType,
    AlertSeverity
)

logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """Configuration for monitoring infrastructure"""
    storage_path: str = "monitoring_data/"
    retention_days: int = 30
    alert_check_interval: int = 60  # seconds
    batch_size: int = 100
    enable_real_time_alerts: bool = True
    enable_metric_aggregation: bool = True


class MonitoringInfrastructureService:
    """
    Infrastructure service for monitoring capabilities.
    
    Provides storage, configuration, and resource management
    for model performance monitoring.
    """
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.storage_path = Path(self.config.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # In-memory caches
        self.metrics_cache: Dict[str, List[PerformanceMetric]] = {}
        self.alerts_cache: Dict[str, List[PerformanceAlert]] = {}
        self.thresholds_cache: Dict[str, Dict[PerformanceMetricType, Tuple[float, AlertSeverity]]] = {}
        
        # Monitoring state
        self.is_initialized = False
        self.monitoring_tasks: List[asyncio.Task] = []
        
        logger.info("📊 Monitoring Infrastructure Service initialized")
    
    async def initialize_monitoring(self, config: Dict[str, Any]) -> bool:
        """Initialize monitoring infrastructure"""
        try:
            # Update configuration
            if 'storage_path' in config:
                self.config.storage_path = config['storage_path']
                self.storage_path = Path(self.config.storage_path)
                self.storage_path.mkdir(parents=True, exist_ok=True)
            
            if 'retention_days' in config:
                self.config.retention_days = config['retention_days']
            
            if 'alert_check_interval' in config:
                self.config.alert_check_interval = config['alert_check_interval']
            
            # Load existing data
            await self._load_existing_data()
            
            # Start background tasks
            if self.config.enable_real_time_alerts:
                alert_task = asyncio.create_task(self._alert_monitoring_loop())
                self.monitoring_tasks.append(alert_task)
            
            # Start cleanup task
            cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.monitoring_tasks.append(cleanup_task)
            
            self.is_initialized = True
            logger.info("✅ Monitoring infrastructure initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize monitoring infrastructure: {e}")
            return False
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get status of monitoring infrastructure"""
        return {
            'service': 'monitoring_infrastructure',
            'status': 'healthy' if self.is_initialized else 'initializing',
            'is_initialized': self.is_initialized,
            'storage_path': str(self.storage_path),
            'retention_days': self.config.retention_days,
            'cached_models': len(self.metrics_cache),
            'total_metrics': sum(len(metrics) for metrics in self.metrics_cache.values()),
            'total_alerts': sum(len(alerts) for alerts in self.alerts_cache.values()),
            'active_tasks': len([task for task in self.monitoring_tasks if not task.done()]),
            'config': asdict(self.config)
        }
    
    async def cleanup_old_metrics(self, retention_days: int) -> int:
        """Clean up old metrics beyond retention period"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            cleaned_count = 0
            
            # Clean metrics cache
            for model_id in list(self.metrics_cache.keys()):
                original_count = len(self.metrics_cache[model_id])
                self.metrics_cache[model_id] = [
                    metric for metric in self.metrics_cache[model_id]
                    if metric.timestamp > cutoff_date
                ]
                cleaned_count += original_count - len(self.metrics_cache[model_id])
                
                # Remove empty entries
                if not self.metrics_cache[model_id]:
                    del self.metrics_cache[model_id]
            
            # Clean alerts cache
            for model_id in list(self.alerts_cache.keys()):
                original_count = len(self.alerts_cache[model_id])
                self.alerts_cache[model_id] = [
                    alert for alert in self.alerts_cache[model_id]
                    if alert.timestamp > cutoff_date
                ]
                cleaned_count += original_count - len(self.alerts_cache[model_id])
                
                # Remove empty entries
                if not self.alerts_cache[model_id]:
                    del self.alerts_cache[model_id]
            
            # Clean storage files
            storage_cleaned = await self._cleanup_storage_files(cutoff_date)
            cleaned_count += storage_cleaned
            
            logger.info(f"🧹 Cleaned up {cleaned_count} old monitoring records")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old metrics: {e}")
            return 0
    
    async def store_metric(self, metric: PerformanceMetric) -> bool:
        """Store a performance metric"""
        try:
            # Add to cache
            if metric.model_id not in self.metrics_cache:
                self.metrics_cache[metric.model_id] = []
            
            self.metrics_cache[metric.model_id].append(metric)
            
            # Persist to storage
            await self._persist_metric(metric)
            
            # Check for alerts
            if self.config.enable_real_time_alerts:
                await self._check_metric_for_alerts(metric)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store metric: {e}")
            return False
    
    async def store_alert(self, alert: PerformanceAlert) -> bool:
        """Store a performance alert"""
        try:
            # Add to cache
            if alert.model_id not in self.alerts_cache:
                self.alerts_cache[alert.model_id] = []
            
            self.alerts_cache[alert.model_id].append(alert)
            
            # Persist to storage
            await self._persist_alert(alert)
            
            logger.warning(f"🚨 Performance alert generated: {alert.message}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store alert: {e}")
            return False
    
    async def get_metrics(
        self,
        model_id: str,
        metric_types: Optional[List[PerformanceMetricType]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[PerformanceMetric]:
        """Retrieve performance metrics"""
        try:
            if model_id not in self.metrics_cache:
                return []
            
            metrics = self.metrics_cache[model_id]
            
            # Filter by metric types
            if metric_types:
                metrics = [m for m in metrics if m.metric_type in metric_types]
            
            # Filter by time range
            if time_range:
                start_time, end_time = time_range
                metrics = [
                    m for m in metrics
                    if start_time <= m.timestamp <= end_time
                ]
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to get metrics: {e}")
            return []
    
    async def set_alert_threshold(
        self,
        model_id: str,
        metric_type: PerformanceMetricType,
        threshold_value: float,
        severity: AlertSeverity
    ) -> bool:
        """Set alert threshold for a metric"""
        try:
            if model_id not in self.thresholds_cache:
                self.thresholds_cache[model_id] = {}
            
            self.thresholds_cache[model_id][metric_type] = (threshold_value, severity)
            
            # Persist threshold configuration
            await self._persist_threshold_config(model_id)
            
            logger.info(f"📊 Set alert threshold for {model_id}/{metric_type.value}: {threshold_value} ({severity.value})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to set alert threshold: {e}")
            return False
    
    async def _load_existing_data(self) -> None:
        """Load existing monitoring data from storage"""
        try:
            # Load metrics
            metrics_dir = self.storage_path / "metrics"
            if metrics_dir.exists():
                for model_dir in metrics_dir.iterdir():
                    if model_dir.is_dir():
                        model_id = model_dir.name
                        self.metrics_cache[model_id] = []
                        
                        for metric_file in model_dir.glob("*.json"):
                            try:
                                with open(metric_file, 'r') as f:
                                    metric_data = json.load(f)
                                    # Convert to PerformanceMetric object
                                    # This is a simplified version - full implementation would handle serialization
                                    pass
                            except Exception as e:
                                logger.warning(f"Failed to load metric file {metric_file}: {e}")
            
            # Load thresholds
            thresholds_file = self.storage_path / "thresholds.json"
            if thresholds_file.exists():
                with open(thresholds_file, 'r') as f:
                    thresholds_data = json.load(f)
                    # Load threshold configurations
                    # This is a simplified version
                    pass
            
            logger.info("📂 Loaded existing monitoring data")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load existing data: {e}")
    
    async def _persist_metric(self, metric: PerformanceMetric) -> None:
        """Persist metric to storage"""
        try:
            metrics_dir = self.storage_path / "metrics" / metric.model_id
            metrics_dir.mkdir(parents=True, exist_ok=True)
            
            # Create filename with timestamp
            filename = f"metric_{metric.timestamp.strftime('%Y%m%d_%H%M%S_%f')}.json"
            metric_file = metrics_dir / filename
            
            # Serialize metric (simplified)
            metric_data = {
                'metric_type': metric.metric_type.value,
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat(),
                'model_id': metric.model_id,
                'service_name': metric.service_name,
                'metadata': metric.metadata
            }
            
            with open(metric_file, 'w') as f:
                json.dump(metric_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Failed to persist metric: {e}")
    
    async def _persist_alert(self, alert: PerformanceAlert) -> None:
        """Persist alert to storage"""
        try:
            alerts_dir = self.storage_path / "alerts" / alert.model_id
            alerts_dir.mkdir(parents=True, exist_ok=True)
            
            # Create filename with timestamp
            filename = f"alert_{alert.timestamp.strftime('%Y%m%d_%H%M%S_%f')}.json"
            alert_file = alerts_dir / filename
            
            # Serialize alert (simplified)
            alert_data = {
                'alert_id': alert.alert_id,
                'severity': alert.severity.value,
                'metric_type': alert.metric_type.value,
                'current_value': alert.current_value,
                'threshold_value': alert.threshold_value,
                'model_id': alert.model_id,
                'service_name': alert.service_name,
                'timestamp': alert.timestamp.isoformat(),
                'message': alert.message,
                'resolved': alert.resolved
            }
            
            with open(alert_file, 'w') as f:
                json.dump(alert_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Failed to persist alert: {e}")
    
    async def _persist_threshold_config(self, model_id: str) -> None:
        """Persist threshold configuration"""
        try:
            thresholds_file = self.storage_path / "thresholds.json"
            
            # Load existing thresholds
            all_thresholds = {}
            if thresholds_file.exists():
                with open(thresholds_file, 'r') as f:
                    all_thresholds = json.load(f)
            
            # Update with current thresholds
            if model_id in self.thresholds_cache:
                all_thresholds[model_id] = {
                    metric_type.value: {'threshold': threshold, 'severity': severity.value}
                    for metric_type, (threshold, severity) in self.thresholds_cache[model_id].items()
                }
            
            # Save updated thresholds
            with open(thresholds_file, 'w') as f:
                json.dump(all_thresholds, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Failed to persist threshold config: {e}")
    
    async def _check_metric_for_alerts(self, metric: PerformanceMetric) -> None:
        """Check if metric triggers any alerts"""
        try:
            if metric.model_id not in self.thresholds_cache:
                return
            
            thresholds = self.thresholds_cache[metric.model_id]
            if metric.metric_type not in thresholds:
                return
            
            threshold_value, severity = thresholds[metric.metric_type]
            
            # Check if threshold is exceeded (simplified logic)
            threshold_exceeded = False
            if metric.metric_type in [PerformanceMetricType.ERROR_RATE, PerformanceMetricType.LATENCY]:
                # Higher values are worse
                threshold_exceeded = metric.value > threshold_value
            else:
                # Lower values are worse (accuracy, precision, etc.)
                threshold_exceeded = metric.value < threshold_value
            
            if threshold_exceeded:
                # Generate alert
                alert = PerformanceAlert(
                    alert_id=f"alert_{metric.model_id}_{metric.metric_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    severity=severity,
                    metric_type=metric.metric_type,
                    current_value=metric.value,
                    threshold_value=threshold_value,
                    model_id=metric.model_id,
                    service_name=metric.service_name,
                    timestamp=datetime.utcnow(),
                    message=f"{metric.metric_type.value} threshold exceeded: {metric.value} vs {threshold_value}"
                )
                
                await self.store_alert(alert)
                
        except Exception as e:
            logger.error(f"❌ Failed to check metric for alerts: {e}")
    
    async def _alert_monitoring_loop(self) -> None:
        """Background task for alert monitoring"""
        while True:
            try:
                await asyncio.sleep(self.config.alert_check_interval)
                
                # Perform periodic alert checks
                # This could include checking for patterns, trends, etc.
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in alert monitoring loop: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Background task for periodic cleanup"""
        while True:
            try:
                # Run cleanup every 24 hours
                await asyncio.sleep(24 * 3600)
                await self.cleanup_old_metrics(self.config.retention_days)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in cleanup loop: {e}")
    
    async def _cleanup_storage_files(self, cutoff_date: datetime) -> int:
        """Clean up old storage files"""
        try:
            cleaned_count = 0
            
            # Clean metric files
            metrics_dir = self.storage_path / "metrics"
            if metrics_dir.exists():
                for model_dir in metrics_dir.iterdir():
                    if model_dir.is_dir():
                        for metric_file in model_dir.glob("*.json"):
                            try:
                                # Extract timestamp from filename
                                timestamp_str = metric_file.stem.split('_', 1)[1]
                                file_timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S_%f')
                                
                                if file_timestamp < cutoff_date:
                                    metric_file.unlink()
                                    cleaned_count += 1
                            except Exception:
                                # Skip files with invalid timestamps
                                pass
            
            # Clean alert files
            alerts_dir = self.storage_path / "alerts"
            if alerts_dir.exists():
                for model_dir in alerts_dir.iterdir():
                    if model_dir.is_dir():
                        for alert_file in model_dir.glob("*.json"):
                            try:
                                # Extract timestamp from filename
                                timestamp_str = alert_file.stem.split('_', 1)[1]
                                file_timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S_%f')
                                
                                if file_timestamp < cutoff_date:
                                    alert_file.unlink()
                                    cleaned_count += 1
                            except Exception:
                                # Skip files with invalid timestamps
                                pass
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup storage files: {e}")
            return 0
    
    async def shutdown(self) -> None:
        """Shutdown monitoring infrastructure"""
        try:
            # Cancel all background tasks
            for task in self.monitoring_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self.monitoring_tasks.clear()
            self.is_initialized = False
            
            logger.info("🛑 Monitoring infrastructure shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            'service': 'monitoring_infrastructure',
            'status': 'healthy' if self.is_initialized else 'initializing',
            'is_initialized': self.is_initialized,
            'storage_path': str(self.storage_path),
            'cached_models': len(self.metrics_cache),
            'active_tasks': len([task for task in self.monitoring_tasks if not task.done()])
        }