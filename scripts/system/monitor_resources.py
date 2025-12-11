#!/usr/bin/env python3
"""
Resource Monitor for AnalyticBot

Monitors system resources and sends alerts when thresholds are exceeded.
Can be run as a cron job or systemd service.
"""

import logging
import sys
from datetime import datetime

import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("/tmp/analyticbot_monitor.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Thresholds
MEMORY_WARNING_PERCENT = 75
MEMORY_CRITICAL_PERCENT = 85
CPU_WARNING_PERCENT = 80
CPU_CRITICAL_PERCENT = 90
DISK_WARNING_PERCENT = 80
DISK_CRITICAL_PERCENT = 90
MAX_PROCESS_AGE_HOURS = 24


class ResourceMonitor:
    """Monitor system resources and detect issues"""

    def __init__(self):
        self.alerts: list[str] = []

    def check_memory(self) -> dict:
        """Check memory usage"""
        mem = psutil.virtual_memory()

        status = "healthy"
        if mem.percent >= MEMORY_CRITICAL_PERCENT:
            status = "critical"
            self.alerts.append(
                f"🔴 CRITICAL: Memory usage at {mem.percent}% (>= {MEMORY_CRITICAL_PERCENT}%)"
            )
        elif mem.percent >= MEMORY_WARNING_PERCENT:
            status = "warning"
            self.alerts.append(
                f"🟡 WARNING: Memory usage at {mem.percent}% (>= {MEMORY_WARNING_PERCENT}%)"
            )

        return {
            "status": status,
            "percent": mem.percent,
            "used_gb": mem.used / (1024**3),
            "available_gb": mem.available / (1024**3),
            "total_gb": mem.total / (1024**3),
        }

    def check_cpu(self) -> dict:
        """Check CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=1)

        status = "healthy"
        if cpu_percent >= CPU_CRITICAL_PERCENT:
            status = "critical"
            self.alerts.append(
                f"🔴 CRITICAL: CPU usage at {cpu_percent}% (>= {CPU_CRITICAL_PERCENT}%)"
            )
        elif cpu_percent >= CPU_WARNING_PERCENT:
            status = "warning"
            self.alerts.append(
                f"🟡 WARNING: CPU usage at {cpu_percent}% (>= {CPU_WARNING_PERCENT}%)"
            )

        return {"status": status, "percent": cpu_percent, "cores": psutil.cpu_count()}

    def check_disk(self) -> dict:
        """Check disk usage"""
        disk = psutil.disk_usage("/")

        status = "healthy"
        if disk.percent >= DISK_CRITICAL_PERCENT:
            status = "critical"
            self.alerts.append(
                f"🔴 CRITICAL: Disk usage at {disk.percent}% (>= {DISK_CRITICAL_PERCENT}%)"
            )
        elif disk.percent >= DISK_WARNING_PERCENT:
            status = "warning"
            self.alerts.append(
                f"🟡 WARNING: Disk usage at {disk.percent}% (>= {DISK_WARNING_PERCENT}%)"
            )

        return {
            "status": status,
            "percent": disk.percent,
            "used_gb": disk.used / (1024**3),
            "free_gb": disk.free / (1024**3),
            "total_gb": disk.total / (1024**3),
        }

    def check_orphaned_processes(self) -> list[dict]:
        """Find potentially orphaned processes"""
        orphaned = []
        current_time = datetime.now()

        for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time", "memory_info"]):
            try:
                # Check for Python multiprocessing workers
                cmdline = " ".join(proc.info["cmdline"] or [])
                if "multiprocessing" not in cmdline:
                    continue

                # Check process age
                create_time = datetime.fromtimestamp(proc.info["create_time"])
                age_hours = (current_time - create_time).total_seconds() / 3600

                if age_hours > MAX_PROCESS_AGE_HOURS:
                    memory_mb = proc.info["memory_info"].rss / (1024**2)
                    orphaned.append(
                        {
                            "pid": proc.info["pid"],
                            "name": proc.info["name"],
                            "age_hours": round(age_hours, 1),
                            "memory_mb": round(memory_mb, 1),
                            "cmdline": cmdline[:100],
                        }
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if orphaned:
            total_memory = sum(p["memory_mb"] for p in orphaned)
            self.alerts.append(
                f"⚠️  Found {len(orphaned)} orphaned processes (total {round(total_memory, 1)} MB)"
            )

        return orphaned

    def check_high_memory_processes(self) -> list[dict]:
        """Find processes using excessive memory"""
        high_memory = []

        for proc in psutil.process_iter(["pid", "name", "memory_info", "cmdline"]):
            try:
                memory_mb = proc.info["memory_info"].rss / (1024**2)

                # Flag processes using > 500 MB
                if memory_mb > 500:
                    cmdline = " ".join(proc.info["cmdline"] or [])
                    high_memory.append(
                        {
                            "pid": proc.info["pid"],
                            "name": proc.info["name"],
                            "memory_mb": round(memory_mb, 1),
                            "cmdline": cmdline[:100],
                        }
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by memory usage
        high_memory.sort(key=lambda x: x["memory_mb"], reverse=True)

        if high_memory:
            self.alerts.append(f"📊 {len(high_memory)} processes using > 500 MB")

        return high_memory[:10]  # Top 10

    def generate_report(self) -> dict:
        """Generate full resource monitoring report"""
        logger.info("=" * 60)
        logger.info("AnalyticBot Resource Monitor Report")
        logger.info("=" * 60)

        # Check all resources
        memory = self.check_memory()
        cpu = self.check_cpu()
        disk = self.check_disk()
        orphaned = self.check_orphaned_processes()
        high_memory = self.check_high_memory_processes()

        # Log results
        logger.info(
            f"\n📊 Memory: {memory['percent']:.1f}% used "
            f"({memory['used_gb']:.1f}/{memory['total_gb']:.1f} GB)"
        )
        logger.info(f"💻 CPU: {cpu['percent']:.1f}% used ({cpu['cores']} cores)")
        logger.info(
            f"💾 Disk: {disk['percent']:.1f}% used "
            f"({disk['used_gb']:.1f}/{disk['total_gb']:.1f} GB)"
        )

        if orphaned:
            logger.info(f"\n⚠️  Orphaned Processes ({len(orphaned)}):")
            for proc in orphaned[:5]:
                logger.info(
                    f"  PID {proc['pid']}: {proc['age_hours']}h old, {proc['memory_mb']} MB"
                )

        if high_memory:
            logger.info("\n📈 High Memory Processes:")
            for proc in high_memory[:5]:
                logger.info(f"  PID {proc['pid']}: {proc['memory_mb']} MB - {proc['name']}")

        # Log alerts
        if self.alerts:
            logger.info(f"\n🚨 Alerts ({len(self.alerts)}):")
            for alert in self.alerts:
                logger.info(f"  {alert}")
        else:
            logger.info("\n✅ All systems healthy")

        logger.info("=" * 60)

        return {
            "timestamp": datetime.now().isoformat(),
            "memory": memory,
            "cpu": cpu,
            "disk": disk,
            "orphaned_processes": orphaned,
            "high_memory_processes": high_memory,
            "alerts": self.alerts,
        }


def main():
    """Run resource monitoring"""
    monitor = ResourceMonitor()
    report = monitor.generate_report()

    # Exit with error code if there are critical alerts
    has_critical = any("CRITICAL" in alert for alert in report["alerts"])
    sys.exit(1 if has_critical else 0)


if __name__ == "__main__":
    main()
