#!/usr/bin/env python3
"""
Phase 0.0 Module 2 - Local Testing Without Docker
Simplified testing approach for environments without Docker
"""

import asyncio
import subprocess
import sys
import os
import time
import json
import sqlite3
from pathlib import Path
from datetime import datetime

class Module2LocalTester:
    def __init__(self):
        self.project_root = Path("/workspaces/analyticbot")
        self.api_port = 8001
        self.api_url = f"http://localhost:{self.api_port}"
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
        
        # Setup test database
        self.db_path = self.project_root / "test_analyticbot.db"
        self.redis_available = False
        
    def log_test(self, test_name, passed, message="", duration=0):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        print(f"{'✅' if passed else '❌'} {test_name}: {status}")
        if message:
            print(f"   {message}")
        
        self.results["tests"].append({
            "name": test_name,
            "status": status,
            "message": message,
            "duration": duration
        })
        
        if passed:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1
        self.results["summary"]["total"] += 1
    
    def setup_test_environment(self):
        """Setup test environment without Docker"""
        print("🔧 Setting up local test environment...")
        
        # Create test database
        try:
            if self.db_path.exists():
                self.db_path.unlink()
            
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
            
            self.log_test("Test Database Setup", True, f"SQLite database created at {self.db_path}")
            return True
            
        except Exception as e:
            self.log_test("Test Database Setup", False, f"Error: {str(e)}")
            return False
    
    def test_python_environment(self):
        """Test Python environment and dependencies"""
        print("\n🐍 Testing Python environment...")
        
        # Test Python version
        python_version = sys.version
        self.log_test("Python Version", True, f"Python {python_version.split()[0]}")
        
        # Test key dependencies
        dependencies = [
            "fastapi", "uvicorn", "sqlalchemy", "asyncpg", 
            "redis", "aiogram", "aiohttp", "pydantic"
        ]
        
        failed_imports = []
        for dep in dependencies:
            try:
                __import__(dep)
                print(f"   ✅ {dep}")
            except ImportError:
                failed_imports.append(dep)
                print(f"   ❌ {dep} - Not available")
        
        success = len(failed_imports) == 0
        message = f"All dependencies available" if success else f"Missing: {', '.join(failed_imports)}"
        self.log_test("Dependencies Check", success, message)
        return success
    
    def test_application_structure(self):
        """Test application file structure"""
        print("\n📁 Testing application structure...")
        
        required_files = [
            "main.py", "bot/__init__.py", "bot/database/db.py",
            "bot/handlers/__init__.py", "requirements.txt", "Dockerfile"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"   ✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"   ❌ {file_path} - Missing")
        
        success = len(missing_files) == 0
        message = f"All files present" if success else f"Missing: {', '.join(missing_files)}"
        self.log_test("Application Structure", success, message)
        return success
    
    async def test_fastapi_import(self):
        """Test FastAPI application import"""
        print("\n🚀 Testing FastAPI application...")
        
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(str(self.project_root))
            
            # Set test environment variables
            test_env = {
                **os.environ,
                "DATABASE_URL": f"sqlite:///{self.db_path}",
                "REDIS_URL": "redis://localhost:6379/0",  # Will fail gracefully
                "ENVIRONMENT": "testing",
                "DEBUG": "true",
                "BOT_TOKEN": "test_token",
                "JWT_SECRET_KEY": "test_secret_key"
            }
            
            # Try to import the main application
            import sys
            sys.path.insert(0, str(self.project_root))
            
            try:
                from apis.main_api import app
                self.log_test("FastAPI Import", True, "Application imported successfully")
                return True
            except ImportError as e:
                self.log_test("FastAPI Import", False, f"Import error: {str(e)}")
                return False
            
        except Exception as e:
            self.log_test("FastAPI Import", False, f"Error: {str(e)}")
            return False
        finally:
            os.chdir(original_cwd)
    
    async def test_basic_functionality(self):
        """Test basic application functionality without full server"""
        print("\n⚙️ Testing basic functionality...")
        
        try:
            # Test database model imports
            from bot.models.twa import User  # Correct import path for Pydantic User model
            self.log_test("Database Models", True, "Models imported successfully")
            
            # Test configuration
            from bot.config import settings
            self.log_test("Configuration", True, "Settings loaded successfully")
            
            # Test utility functions
            from bot.utils.language_manager import LanguageManager
            self.log_test("Language Manager", True, "Language utilities working")
            
            return True
            
        except Exception as e:
            self.log_test("Basic Functionality", False, f"Error: {str(e)}")
            return False
    
    def test_helm_charts_validation(self):
        """Validate Helm charts from Module 1"""
        print("\n⚙️ Testing Helm charts validation...")
        
        try:
            helm_dir = self.project_root / "infrastructure" / "helm"
            
            # Check Helm files exist
            helm_files = [
                "Chart.yaml", "values.yaml", "values-production.yaml",
                "templates/api-deployment.yaml", "templates/bot-deployment.yaml"
            ]
            
            all_present = True
            for file_name in helm_files:
                file_path = helm_dir / file_name
                if not file_path.exists():
                    all_present = False
                    break
            
            if all_present:
                # Run the structure validation script
                validation_script = helm_dir / "validate_structure.py"
                if validation_script.exists():
                    os.chdir(str(helm_dir))
                    result = subprocess.run(
                        [sys.executable, "validate_structure.py"],
                        capture_output=True, text=True, timeout=30
                    )
                    os.chdir(str(self.project_root))
                    
                    success = result.returncode == 0
                    message = "Helm validation passed" if success else f"Validation failed: {result.stderr[:200]}"
                    self.log_test("Helm Charts Validation", success, message)
                    return success
                else:
                    self.log_test("Helm Charts Validation", False, "Validation script not found")
                    return False
            else:
                self.log_test("Helm Charts Validation", False, "Required Helm files missing")
                return False
                
        except Exception as e:
            self.log_test("Helm Charts Validation", False, f"Error: {str(e)}")
            return False
    
    def save_results(self):
        """Save test results"""
        results_dir = self.project_root / "results"
        results_dir.mkdir(exist_ok=True)
        
        filename = f"module2_local_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📊 Results saved to: {filepath}")
        return filepath
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🧪 MODULE 2 LOCAL TEST SUMMARY")
        print("="*60)
        
        summary = self.results["summary"]
        total = summary["total"]
        passed = summary["passed"]
        failed = summary["failed"]
        
        print(f"✅ Tests Passed: {passed}")
        print(f"❌ Tests Failed: {failed}")
        print(f"📊 Total Tests: {total}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("\n🎉 EXCELLENT: Module 2 local validation highly successful!")
                print("✅ Ready for Kubernetes/Docker deployment when available")
            elif success_rate >= 75:
                print("\n✅ GOOD: Module 2 local validation working well")
                print("ℹ️ Minor issues detected, but foundation is solid")
            elif success_rate >= 50:
                print("\n⚠️ FAIR: Module 2 local validation has some issues")
                print("🔧 Recommend addressing failures before deployment")
            else:
                print("\n❌ POOR: Module 2 local validation needs attention")
                print("🚨 Critical issues detected, requires fixes")
        
        return passed >= total * 0.75  # 75% pass rate required
    
    async def run_all_tests(self):
        """Run all local tests"""
        print("🚀 PHASE 0.0 MODULE 2 - LOCAL TESTING SUITE")
        print("="*60)
        print("ℹ️ Docker not available - Running local validation tests")
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment")
            return False
        
        # Environment tests
        print("\n🔍 Testing environment...")
        self.test_python_environment()
        self.test_application_structure()
        
        # Application tests
        await self.test_fastapi_import()
        await self.test_basic_functionality()
        
        # Infrastructure tests
        self.test_helm_charts_validation()
        
        # Save and summarize
        self.save_results()
        return self.print_summary()

async def main():
    """Main test runner"""
    tester = Module2LocalTester()
    
    try:
        success = await tester.run_all_tests()
        
        print("\n" + "="*60)
        print("🎯 NEXT STEPS:")
        if success:
            print("✅ Local validation passed - Application structure is solid")
            print("🚀 Ready for Docker/Kubernetes deployment when available")
            print("📋 Consider running: kubectl apply -f infrastructure/k8s/")
        else:
            print("🔧 Address validation failures before proceeding")
            print("📋 Review results and fix identified issues")
        
        print("\n🔧 ALTERNATIVE DEPLOYMENT OPTIONS:")
        print("1. Fix Docker daemon and retry Docker Compose deployment")
        print("2. Use existing Kubernetes configs: kubectl apply -f infrastructure/k8s/")
        print("3. Use direct Python execution for development testing")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        tester.save_results()
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        tester.save_results()
        sys.exit(3)

if __name__ == "__main__":
    asyncio.run(main())
