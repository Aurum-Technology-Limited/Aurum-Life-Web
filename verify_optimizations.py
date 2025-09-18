#!/usr/bin/env python3
"""
Verification script for performance optimizations
Checks that all optimizations have been properly implemented
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class OptimizationVerifier:
    def __init__(self):
        self.results = {
            "frontend": {},
            "backend": {},
            "summary": {
                "total_checks": 0,
                "passed": 0,
                "failed": 0
            }
        }
        
    def check_frontend_optimizations(self):
        """Verify frontend bundle optimizations"""
        print("🔍 Checking Frontend Optimizations...")
        
        # Check 1: Lazy loading implementation
        app_js_path = Path("/workspace/frontend/src/App.js")
        if app_js_path.exists():
            content = app_js_path.read_text()
            lazy_imports = content.count("lazy(() => import")
            
            if lazy_imports > 10:
                self.record_check("Frontend: Lazy loading", True, f"Found {lazy_imports} lazy imports")
            else:
                self.record_check("Frontend: Lazy loading", False, f"Only {lazy_imports} lazy imports found")
        
        # Check 2: LazyChart component exists
        lazy_chart_path = Path("/workspace/frontend/src/components/ui/LazyChart.jsx")
        if lazy_chart_path.exists():
            self.record_check("Frontend: LazyChart component", True, "Component created")
        else:
            self.record_check("Frontend: LazyChart component", False, "Component not found")
        
        # Check 3: Webpack optimization config
        craco_path = Path("/workspace/frontend/craco.config.js")
        if craco_path.exists():
            content = craco_path.read_text()
            has_terser = "TerserPlugin" in content
            has_compression = "CompressionPlugin" in content
            has_split_chunks = "splitChunks" in content
            
            if all([has_terser, has_compression, has_split_chunks]):
                self.record_check("Frontend: Webpack optimization", True, "All optimizations configured")
            else:
                missing = []
                if not has_terser: missing.append("TerserPlugin")
                if not has_compression: missing.append("CompressionPlugin")
                if not has_split_chunks: missing.append("splitChunks")
                self.record_check("Frontend: Webpack optimization", False, f"Missing: {', '.join(missing)}")
        
        # Check 4: Package.json has optimization dependencies
        package_json_path = Path("/workspace/frontend/package.json")
        if package_json_path.exists():
            with open(package_json_path) as f:
                package_data = json.load(f)
            
            dev_deps = package_data.get("devDependencies", {})
            has_terser = "terser-webpack-plugin" in dev_deps
            has_compression = "compression-webpack-plugin" in dev_deps
            
            if has_terser and has_compression:
                self.record_check("Frontend: Optimization dependencies", True, "All dependencies added")
            else:
                self.record_check("Frontend: Optimization dependencies", False, "Missing webpack plugins")
        
        # Check 5: Chart components updated
        files_to_check = [
            "/workspace/frontend/src/components/ui/DonutChart.jsx",
            "/workspace/frontend/src/components/AnalyticsDashboard.jsx"
        ]
        
        updated_count = 0
        for file_path in files_to_check:
            if Path(file_path).exists():
                content = Path(file_path).read_text()
                if "LazyChart" in content or "LazyDoughnut" in content or "LazyBar" in content:
                    updated_count += 1
        
        if updated_count >= 2:
            self.record_check("Frontend: Chart components updated", True, f"{updated_count} components updated")
        else:
            self.record_check("Frontend: Chart components updated", False, f"Only {updated_count} components updated")
    
    def check_backend_optimizations(self):
        """Verify backend caching implementation"""
        print("\n🔍 Checking Backend Optimizations...")
        
        # Check 1: Cache service import
        server_path = Path("/workspace/backend/server.py")
        if server_path.exists():
            content = server_path.read_text()
            
            # Check cache service import
            if "from cache_service import cache_service" in content:
                self.record_check("Backend: Cache service import", True, "Import found")
            else:
                self.record_check("Backend: Cache service import", False, "Import missing")
            
            # Check 2: Caching decorator implementation
            if "def cache_user_endpoint" in content:
                self.record_check("Backend: Caching decorator", True, "Decorator implemented")
            else:
                self.record_check("Backend: Caching decorator", False, "Decorator not found")
            
            # Check 3: Cached endpoints
            cached_endpoints = []
            endpoints = ["/pillars", "/areas", "/projects", "/tasks", "/journal", "/alignment/dashboard"]
            
            for endpoint in endpoints:
                # Check if endpoint has caching decorator
                if f'@api_router.get("{endpoint}")' in content:
                    # Find the line and check if it has caching
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if f'@api_router.get("{endpoint}")' in line:
                            # Check previous lines for cache decorator
                            for j in range(max(0, i-3), i):
                                if "@cache_user_endpoint" in lines[j]:
                                    cached_endpoints.append(endpoint)
                                    break
            
            if len(cached_endpoints) >= 5:
                self.record_check("Backend: Cached endpoints", True, f"{len(cached_endpoints)} endpoints cached")
            else:
                self.record_check("Backend: Cached endpoints", False, f"Only {len(cached_endpoints)} endpoints cached")
            
            # Check 4: Cache service exists
            cache_service_path = Path("/workspace/backend/cache_service.py")
            if cache_service_path.exists():
                self.record_check("Backend: Cache service file", True, "Service file exists")
            else:
                self.record_check("Backend: Cache service file", False, "Service file missing")
    
    def record_check(self, name, passed, details):
        """Record check result"""
        self.results["summary"]["total_checks"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
            print(f"✅ {name}: {details}")
        else:
            self.results["summary"]["failed"] += 1
            print(f"❌ {name}: {details}")
        
        category = "frontend" if name.startswith("Frontend") else "backend"
        self.results[category][name] = {
            "passed": passed,
            "details": details
        }
    
    def generate_report(self):
        """Generate final report"""
        print("\n" + "="*60)
        print("📊 OPTIMIZATION VERIFICATION REPORT")
        print("="*60)
        
        print(f"\nTotal Checks: {self.results['summary']['total_checks']}")
        print(f"✅ Passed: {self.results['summary']['passed']}")
        print(f"❌ Failed: {self.results['summary']['failed']}")
        
        success_rate = (self.results['summary']['passed'] / self.results['summary']['total_checks']) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 All optimizations successfully implemented!")
        elif success_rate >= 80:
            print("\n✨ Most optimizations implemented successfully!")
        else:
            print("\n⚠️  Some optimizations need attention")
        
        # Save detailed report
        report_path = Path("/workspace/optimization_verification_report.json")
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_path}")
        
        # Installation instructions
        print("\n📦 INSTALLATION INSTRUCTIONS:")
        print("="*60)
        print("\nFrontend:")
        print("1. cd frontend")
        print("2. yarn install  # Install new dependencies")
        print("3. yarn build    # Build optimized production bundle")
        print("\nBackend:")
        print("1. cd backend")
        print("2. Ensure Redis is running (optional, falls back to memory)")
        print("3. python server.py  # Start server with caching enabled")
        
        print("\n🚀 TESTING THE OPTIMIZATIONS:")
        print("="*60)
        print("\n1. Start the backend server")
        print("2. Run the performance audit: python performance_audit.py")
        print("3. Compare bundle sizes before/after")
        print("4. Test API response times (should be faster on second request)")
        
        return success_rate

def main():
    verifier = OptimizationVerifier()
    
    print("🚀 Verifying Performance Optimizations...")
    print("="*60)
    
    verifier.check_frontend_optimizations()
    verifier.check_backend_optimizations()
    
    success_rate = verifier.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate == 100 else 1)

if __name__ == "__main__":
    main()