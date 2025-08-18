# Prometheus metrics task - append to tasks.py

@resilient_task(name="bot.tasks.update_prometheus_metrics", bind=True)
def update_prometheus_metrics(self):  # type: ignore[override]
    """Periodic task to update Prometheus metrics"""
    async def _run() -> str:
        context = ErrorContext().add("task", "update_prometheus_metrics")
        
        try:
            from bot.services.prometheus_service import collect_system_metrics
            
            logger.info("Collecting Prometheus metrics")
            
            # Collect system and application metrics
            await collect_system_metrics()
            
            logger.info("Prometheus metrics collection completed")
            
            return "metrics-updated"
            
        except Exception as e:
            ErrorHandler.log_error(e, context)
            return "metrics-failed"
        finally:
            await cleanup_resources()

    return asyncio.run(_run())
