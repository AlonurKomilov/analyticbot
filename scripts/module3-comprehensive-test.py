#!/usr/bin/env python3
"""
AnalyticBot Phase 0.0 Module 3 - Comprehensive Test Suite
Advanced DevOps & Observability Testing

This script validates all Module 3 components:
- Enhanced monitoring stack (Grafana dashboards, Prometheus alerts)
- Kubernetes-native CI/CD pipeline functionality
- Backup & disaster recovery system
- Resource optimization and scaling
- Advanced alert management system
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import yaml

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class Module3TestSuite:
    """Comprehensive test suite for Phase 0.0 Module 3"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            "test_results": [],
            "start_time": datetime.now().isoformat(),
            "module": "Phase 0.0 Module 3 - Advanced DevOps & Observability",
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
        }

        # Test configuration
        self.monitoring_dir = self.project_root / "infrastructure" / "monitoring"
        self.grafana_dir = self.monitoring_dir / "grafana" / "dashboards" / "advanced"
        self.prometheus_rules = self.monitoring_dir / "prometheus" / "rules"
        self.workflows_dir = self.project_root / ".github" / "workflows"
        self.backup_script = self.project_root / "scripts" / "backup" / "backup-system.sh"

    def log_test(self, test_name: str, passed: bool, details: str = "", duration: float = 0):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
        }

        self.results["test_results"].append(result)
        self.results["total_tests"] += 1

        if passed:
            self.results["passed_tests"] += 1
            print(f"   ✅ {test_name}: {status}")
        else:
            self.results["failed_tests"] += 1
            print(f"   ❌ {test_name}: {status}")

        if details:
            print(f"      {details}")

    def test_grafana_dashboards(self) -> bool:
        """Test Grafana dashboard configurations"""
        print("\n📊 Testing Grafana dashboards...")

        try:
            dashboards = ["business-metrics.json", "infrastructure.json", "sla-slo.json"]

            all_passed = True

            for dashboard in dashboards:
                start_time = time.time()
                dashboard_path = self.grafana_dir / dashboard

                if not dashboard_path.exists():
                    self.log_test(
                        f"Grafana Dashboard - {dashboard}",
                        False,
                        f"Dashboard file not found: {dashboard_path}",
                    )
                    all_passed = False
                    continue

                try:
                    # Parse JSON
                    with open(dashboard_path) as f:
                        dashboard_data = json.load(f)

                    # Validate required fields
                    required_fields = ["title", "panels", "tags"]
                    missing_fields = [
                        field for field in required_fields if field not in dashboard_data
                    ]

                    if missing_fields:
                        self.log_test(
                            f"Grafana Dashboard - {dashboard}",
                            False,
                            f"Missing required fields: {missing_fields}",
                        )
                        all_passed = False
                        continue

                    # Validate panels
                    panels = dashboard_data.get("panels", [])
                    if len(panels) == 0:
                        self.log_test(
                            f"Grafana Dashboard - {dashboard}",
                            False,
                            "No panels found in dashboard",
                        )
                        all_passed = False
                        continue

                    # Check panel configuration
                    valid_panels = 0
                    for panel in panels:
                        if "targets" in panel and "title" in panel:
                            valid_panels += 1

                    panel_validity = valid_panels / len(panels) * 100

                    duration = time.time() - start_time
                    self.log_test(
                        f"Grafana Dashboard - {dashboard}",
                        True,
                        f"Valid dashboard with {len(panels)} panels ({panel_validity:.1f}% valid)",
                        duration,
                    )

                except json.JSONDecodeError as e:
                    self.log_test(
                        f"Grafana Dashboard - {dashboard}", False, f"Invalid JSON: {str(e)}"
                    )
                    all_passed = False
                except Exception as e:
                    self.log_test(
                        f"Grafana Dashboard - {dashboard}", False, f"Validation error: {str(e)}"
                    )
                    all_passed = False

            return all_passed

        except Exception as e:
            self.log_test("Grafana Dashboards Test", False, f"Error: {str(e)}")
            return False

    def test_prometheus_alerts(self) -> bool:
        """Test Prometheus alerting rules"""
        print("\n🚨 Testing Prometheus alerting rules...")

        try:
            alerts_file = self.prometheus_rules / "advanced-alerts.yml"

            if not alerts_file.exists():
                self.log_test("Prometheus Alerts", False, "Advanced alerts file not found")
                return False

            start_time = time.time()

            # Parse YAML
            with open(alerts_file) as f:
                alerts_data = yaml.safe_load(f)

            # Validate structure
            if "groups" not in alerts_data:
                self.log_test("Prometheus Alerts", False, "Missing 'groups' in alerts file")
                return False

            groups = alerts_data["groups"]
            total_rules = 0
            valid_rules = 0

            for group in groups:
                if "rules" not in group:
                    continue

                for rule in group["rules"]:
                    total_rules += 1

                    # Validate required fields
                    required_fields = ["alert", "expr", "labels", "annotations"]
                    if all(field in rule for field in required_fields):
                        valid_rules += 1

            rule_validity = valid_rules / total_rules * 100 if total_rules > 0 else 0

            duration = time.time() - start_time

            if rule_validity >= 90:
                self.log_test(
                    "Prometheus Alerts",
                    True,
                    f"{valid_rules}/{total_rules} rules valid ({rule_validity:.1f}%)",
                    duration,
                )
                return True
            else:
                self.log_test(
                    "Prometheus Alerts", False, f"Low rule validity: {rule_validity:.1f}%"
                )
                return False

        except Exception as e:
            self.log_test("Prometheus Alerts", False, f"Error: {str(e)}")
            return False

    def test_cicd_workflows(self) -> bool:
        """Test CI/CD workflow configurations"""
        print("\n🔄 Testing CI/CD workflows...")

        try:
            helm_workflow = self.workflows_dir / "helm-deploy.yml"

            if not helm_workflow.exists():
                self.log_test("CI/CD Workflows", False, "Helm deploy workflow not found")
                return False

            start_time = time.time()

            # Parse workflow YAML
            with open(helm_workflow) as f:
                workflow_data = yaml.safe_load(f)

            # Validate workflow structure
            required_keys = ["name", "jobs"]
            if "on" in workflow_data or True in workflow_data:  # 'on' might be parsed as True
                pass  # Trigger configuration exists
            else:
                required_keys.append("on")
            missing_keys = [key for key in required_keys if key not in workflow_data]

            if missing_keys:
                self.log_test("CI/CD Workflows", False, f"Missing workflow keys: {missing_keys}")
                return False

            # Validate jobs
            jobs = workflow_data.get("jobs", {})
            expected_jobs = ["helm-validation", "deploy-staging", "deploy-production"]

            job_score = 0
            for job_name in expected_jobs:
                if job_name in jobs:
                    job_score += 1
                    # Validate job has steps
                    if "steps" not in jobs[job_name]:
                        job_score -= 0.5

            job_validity = job_score / len(expected_jobs) * 100

            duration = time.time() - start_time

            if job_validity >= 80:
                self.log_test(
                    "CI/CD Workflows",
                    True,
                    f"Workflow validation: {job_validity:.1f}% complete",
                    duration,
                )
                return True
            else:
                self.log_test("CI/CD Workflows", False, f"Incomplete workflow: {job_validity:.1f}%")
                return False

        except Exception as e:
            self.log_test("CI/CD Workflows", False, f"Error: {str(e)}")
            return False

    def test_backup_system(self) -> bool:
        """Test backup system functionality"""
        print("\n💾 Testing backup system...")

        try:
            if not self.backup_script.exists():
                self.log_test("Backup System", False, "Backup script not found")
                return False

            start_time = time.time()

            # Test script syntax
            try:
                result = subprocess.run(
                    ["bash", "-n", str(self.backup_script)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode != 0:
                    self.log_test(
                        "Backup System", False, f"Syntax error in backup script: {result.stderr}"
                    )
                    return False

            except subprocess.TimeoutExpired:
                self.log_test("Backup System", False, "Backup script syntax check timeout")
                return False

            # Test script help function
            try:
                result = subprocess.run(
                    ["bash", str(self.backup_script), "help"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if "Usage:" not in result.stdout:
                    self.log_test("Backup System", False, "Help function not working")
                    return False

            except subprocess.TimeoutExpired:
                self.log_test("Backup System", False, "Backup script help timeout")
                return False

            # Test health check function
            try:
                result = subprocess.run(
                    ["bash", str(self.backup_script), "health"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env={
                        **os.environ,
                        "DB_HOST": "nonexistent",
                        "BACKUP_ROOT": str(tempfile.gettempdir()),
                    },
                )

                # Health check should run even if database is not available
                if "health check" not in result.stdout.lower():
                    self.log_test("Backup System", False, "Health check function not working")
                    return False

            except subprocess.TimeoutExpired:
                self.log_test("Backup System", False, "Backup health check timeout")
                return False

            duration = time.time() - start_time
            self.log_test(
                "Backup System",
                True,
                "Script syntax, help, and health check functions working",
                duration,
            )
            return True

        except Exception as e:
            self.log_test("Backup System", False, f"Error: {str(e)}")
            return False

    def test_monitoring_integration(self) -> bool:
        """Test monitoring stack integration"""
        print("\n📈 Testing monitoring integration...")

        try:
            start_time = time.time()

            # Check if monitoring components exist
            components = {
                "prometheus_config": self.monitoring_dir / "prometheus" / "prometheus.yml",
                "grafana_dashboards": self.grafana_dir,
                "alert_rules": self.prometheus_rules / "advanced-alerts.yml",
            }

            score = 0
            total_components = len(components)

            for component, path in components.items():
                if path.exists():
                    score += 1
                    print(f"      ✅ {component}: Found")
                else:
                    print(f"      ❌ {component}: Missing")

            # Check Helm monitoring integration
            helm_monitoring = (
                self.project_root / "infrastructure" / "helm" / "templates" / "monitoring.yaml"
            )
            if helm_monitoring.exists():
                score += 1
                total_components += 1
                print("      ✅ helm_monitoring: Found")
            else:
                print("      ❌ helm_monitoring: Missing")
                total_components += 1

            integration_score = score / total_components * 100
            duration = time.time() - start_time

            if integration_score >= 75:
                self.log_test(
                    "Monitoring Integration",
                    True,
                    f"Integration score: {integration_score:.1f}%",
                    duration,
                )
                return True
            else:
                self.log_test(
                    "Monitoring Integration",
                    False,
                    f"Low integration score: {integration_score:.1f}%",
                )
                return False

        except Exception as e:
            self.log_test("Monitoring Integration", False, f"Error: {str(e)}")
            return False

    def test_kubernetes_resources(self) -> bool:
        """Test Kubernetes resource configurations"""
        print("\n☸️ Testing Kubernetes resources...")

        try:
            start_time = time.time()

            # Check for advanced HPA configuration
            k8s_dir = self.project_root / "infrastructure" / "k8s"

            if not k8s_dir.exists():
                self.log_test("Kubernetes Resources", False, "K8s directory not found")
                return False

            # Look for HPA and resource optimization files
            resource_files = list(k8s_dir.rglob("*.yaml")) + list(k8s_dir.rglob("*.yml"))

            hpa_found = False
            monitoring_found = False

            for file_path in resource_files:
                try:
                    with open(file_path) as f:
                        content = f.read().lower()

                        if "horizontalpodautoscaler" in content or "kind: hpa" in content:
                            hpa_found = True

                        if "prometheus" in content or "grafana" in content:
                            monitoring_found = True

                except Exception:
                    continue

            # Check Helm templates for advanced configurations
            helm_templates = self.project_root / "infrastructure" / "helm" / "templates"
            if helm_templates.exists():
                template_files = list(helm_templates.rglob("*.yaml"))

                for file_path in template_files:
                    try:
                        with open(file_path) as f:
                            content = f.read().lower()

                            if "resources:" in content and (
                                "requests:" in content or "limits:" in content
                            ):
                                monitoring_found = True

                    except Exception:
                        continue

            score = 0
            if hpa_found:
                score += 1
            if monitoring_found:
                score += 1

            total_score = score / 2 * 100
            duration = time.time() - start_time

            if total_score >= 50:
                self.log_test(
                    "Kubernetes Resources",
                    True,
                    f"Resource optimization score: {total_score:.1f}%",
                    duration,
                )
                return True
            else:
                self.log_test(
                    "Kubernetes Resources",
                    False,
                    f"Limited resource optimization: {total_score:.1f}%",
                )
                return False

        except Exception as e:
            self.log_test("Kubernetes Resources", False, f"Error: {str(e)}")
            return False

    def test_module_integration(self) -> bool:
        """Test integration between Module 3 components and previous modules"""
        print("\n🔗 Testing module integration...")

        try:
            start_time = time.time()

            integration_score = 0
            total_checks = 4

            # Check Module 1 (Helm) integration
            helm_dir = self.project_root / "infrastructure" / "helm"
            if helm_dir.exists():
                # Check if monitoring is integrated into Helm charts
                values_files = list(helm_dir.glob("values*.yaml"))
                monitoring_in_helm = False

                for values_file in values_files:
                    try:
                        with open(values_file) as f:
                            content = f.read().lower()
                            if (
                                "prometheus" in content
                                or "grafana" in content
                                or "monitoring" in content
                            ):
                                monitoring_in_helm = True
                                break
                    except Exception:
                        continue

                if monitoring_in_helm:
                    integration_score += 1
                    print("      ✅ Module 1 Integration: Monitoring integrated into Helm")
                else:
                    print("      ❌ Module 1 Integration: No monitoring in Helm values")

            # Check Module 2 (Testing) integration
            module2_script = self.project_root / "scripts" / "module2_local_test.py"
            if module2_script.exists():
                integration_score += 1
                print("      ✅ Module 2 Integration: Test framework available")
            else:
                print("      ❌ Module 2 Integration: Test framework missing")

            # Check CI/CD integration with existing workflows
            existing_workflows = (
                list(self.workflows_dir.glob("*.yml")) if self.workflows_dir.exists() else []
            )
            if len(existing_workflows) > 1:  # Should have module 3 + existing workflows
                integration_score += 1
                print(f"      ✅ CI/CD Integration: {len(existing_workflows)} workflows found")
            else:
                print(f"      ❌ CI/CD Integration: Limited workflows ({len(existing_workflows)})")

            # Check backup integration with application structure
            if self.backup_script.exists():
                try:
                    with open(self.backup_script) as f:
                        backup_content = f.read()

                        if (
                            "infrastructure/helm" in backup_content
                            and "infrastructure/k8s" in backup_content
                        ):
                            integration_score += 1
                            print("      ✅ Backup Integration: Infrastructure backup included")
                        else:
                            print("      ❌ Backup Integration: Limited infrastructure backup")
                except Exception:
                    print("      ❌ Backup Integration: Could not validate")

            integration_percentage = integration_score / total_checks * 100
            duration = time.time() - start_time

            if integration_percentage >= 75:
                self.log_test(
                    "Module Integration",
                    True,
                    f"Integration score: {integration_percentage:.1f}%",
                    duration,
                )
                return True
            else:
                self.log_test(
                    "Module Integration",
                    False,
                    f"Low integration score: {integration_percentage:.1f}%",
                )
                return False

        except Exception as e:
            self.log_test("Module Integration", False, f"Error: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all Module 3 tests"""
        print("🚀 PHASE 0.0 MODULE 3 - COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print("🔧 Advanced DevOps & Observability Testing")
        print("=" * 60)

        # Run all test categories
        test_methods = [
            self.test_grafana_dashboards,
            self.test_prometheus_alerts,
            self.test_cicd_workflows,
            self.test_backup_system,
            self.test_monitoring_integration,
            self.test_kubernetes_resources,
            self.test_module_integration,
        ]

        start_time = time.time()

        for test_method in test_methods:
            try:
                await asyncio.sleep(0.1)  # Small delay for readability
                test_method()
            except Exception as e:
                self.log_test(
                    f"Test Method {test_method.__name__}", False, f"Unexpected error: {str(e)}"
                )

        # Calculate final results
        total_duration = time.time() - start_time
        self.results["end_time"] = datetime.now().isoformat()
        self.results["total_duration"] = total_duration
        self.results["success_rate"] = (
            (self.results["passed_tests"] / self.results["total_tests"] * 100)
            if self.results["total_tests"] > 0
            else 0
        )

        # Save results
        results_dir = self.project_root / "results"
        results_dir.mkdir(exist_ok=True)

        results_file = (
            results_dir / f"module3_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        # Print summary
        self.print_summary(results_file)

    def print_summary(self, results_file: Path):
        """Print test execution summary"""
        print("\n" + "=" * 60)
        print("🧪 MODULE 3 TEST SUMMARY")
        print("=" * 60)

        success_rate = self.results["success_rate"]

        print(f"✅ Tests Passed: {self.results['passed_tests']}")
        print(f"❌ Tests Failed: {self.results['failed_tests']}")
        print(f"📊 Total Tests: {self.results['total_tests']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")

        # Interpretation
        print("\n" + "=" * 60)
        if success_rate >= 90:
            print("🎉 EXCELLENT: Module 3 implementation is highly successful!")
            print("✅ Advanced DevOps & Observability ready for production")
        elif success_rate >= 75:
            print("🔥 GOOD: Module 3 implementation is solid with minor issues")
            print("🔧 Consider addressing failed tests before production")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Module 3 needs significant improvements")
            print("🛠️ Address failing tests before proceeding")
        else:
            print("🚨 CRITICAL: Module 3 implementation needs major work")
            print("❌ Not ready for production deployment")

        print("\n" + "=" * 60)
        print("🎯 NEXT STEPS:")

        if success_rate >= 90:
            print("✅ Module 3 validation complete - Ready for production!")
            print("🚀 Consider proceeding to Phase 1.0 or production deployment")
            print("📋 Implement any remaining monitoring configurations")
        elif success_rate >= 75:
            print("🔧 Address failed tests and re-run validation")
            print("📊 Review monitoring dashboard configurations")
            print("🔄 Verify CI/CD pipeline functionality")
        else:
            print("🛠️ Significant improvements needed:")
            print("   - Review all failed test details")
            print("   - Ensure all Module 3 components are properly implemented")
            print("   - Check integration with Modules 1 & 2")
            print("   - Validate monitoring stack configuration")

        print(f"\n📊 Results saved to: {results_file}")
        print("\n" + "=" * 60)


async def main():
    """Main test execution function"""
    test_suite = Module3TestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
