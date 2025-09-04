#!/usr/bin/env python3
"""
Comprehensive Performance Audit Tool for Aurum Life Application
Analyzes frontend bundle size, API response times, database queries, and security
"""

import json
import time
import requests
import asyncio
import subprocess
import os
from datetime import datetime
from typing import Dict, List, Any
import psutil
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings("ignore")

class PerformanceAuditor:
    def __init__(self):
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "frontend": {},
            "backend": {},
            "database": {},
            "security": {},
            "recommendations": []
        }
        self.api_base_url = "http://localhost:8000/api"
        
    async def run_full_audit(self):
        """Run comprehensive performance audit"""
        print("🚀 Starting Aurum Life Performance Audit...")
        
        # Frontend analysis
        print("\n📦 Analyzing Frontend Performance...")
        await self.analyze_frontend()
        
        # Backend analysis
        print("\n⚡ Analyzing Backend Performance...")
        await self.analyze_backend()
        
        # Database analysis
        print("\n🗄️ Analyzing Database Performance...")
        await self.analyze_database()
        
        # Security check
        print("\n🔒 Running Security Checks...")
        await self.analyze_security()
        
        # Generate recommendations
        print("\n💡 Generating Recommendations...")
        self.generate_recommendations()
        
        # Save results
        self.save_results()
        
        return self.results
    
    async def analyze_frontend(self):
        """Analyze frontend performance metrics"""
        frontend_metrics = {
            "bundle_analysis": {},
            "dependencies": {},
            "optimization_opportunities": []
        }
        
        # Check if frontend is built
        build_path = "/workspace/frontend/build"
        if os.path.exists(build_path):
            # Analyze bundle size
            bundle_sizes = {}
            for root, dirs, files in os.walk(build_path):
                for file in files:
                    if file.endswith('.js') or file.endswith('.css'):
                        file_path = os.path.join(root, file)
                        size_kb = os.path.getsize(file_path) / 1024
                        bundle_sizes[file] = round(size_kb, 2)
            
            # Sort by size
            sorted_bundles = sorted(bundle_sizes.items(), key=lambda x: x[1], reverse=True)
            frontend_metrics["bundle_analysis"]["files"] = dict(sorted_bundles[:10])
            frontend_metrics["bundle_analysis"]["total_size_kb"] = sum(bundle_sizes.values())
            
            # Check for large bundles
            large_bundles = [f for f, size in bundle_sizes.items() if size > 500]
            if large_bundles:
                frontend_metrics["optimization_opportunities"].append({
                    "issue": "Large bundle sizes detected",
                    "files": large_bundles,
                    "recommendation": "Consider code splitting and lazy loading"
                })
        
        # Analyze package.json dependencies
        package_json_path = "/workspace/frontend/package.json"
        if os.path.exists(package_json_path):
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            deps = package_data.get("dependencies", {})
            
            # Check for optimization opportunities
            heavy_deps = ["moment", "lodash", "@mui/material", "antd"]
            for dep in heavy_deps:
                if dep in deps:
                    frontend_metrics["optimization_opportunities"].append({
                        "issue": f"Heavy dependency: {dep}",
                        "recommendation": f"Consider lighter alternatives or tree-shaking for {dep}"
                    })
            
            # React version check
            react_version = deps.get("react", "").replace("^", "")
            frontend_metrics["dependencies"]["react"] = react_version
            
            # Check for multiple UI libraries
            ui_libs = [d for d in deps if any(ui in d for ui in ["@radix-ui", "@mui", "antd", "bootstrap"])]
            if len(ui_libs) > 5:
                frontend_metrics["optimization_opportunities"].append({
                    "issue": "Multiple UI component libraries detected",
                    "count": len(ui_libs),
                    "libraries": ui_libs[:10],
                    "recommendation": "Consider consolidating UI libraries to reduce bundle size"
                })
        
        self.results["frontend"] = frontend_metrics
    
    async def analyze_backend(self):
        """Analyze backend API performance"""
        backend_metrics = {
            "api_response_times": {},
            "endpoint_analysis": [],
            "performance_issues": []
        }
        
        # Test common endpoints
        test_endpoints = [
            ("GET", "/health", None),
            ("GET", "/pillars", None),
            ("GET", "/areas", None),
            ("GET", "/projects", None),
            ("GET", "/tasks", None),
            ("GET", "/stats/overview", None),
        ]
        
        # Check if server is running
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                # Run performance tests
                for method, endpoint, data in test_endpoints:
                    try:
                        start_time = time.time()
                        
                        if method == "GET":
                            resp = requests.get(f"{self.api_base_url}{endpoint}", timeout=10)
                        else:
                            resp = requests.post(f"{self.api_base_url}{endpoint}", json=data, timeout=10)
                        
                        response_time = (time.time() - start_time) * 1000  # ms
                        
                        backend_metrics["api_response_times"][endpoint] = {
                            "response_time_ms": round(response_time, 2),
                            "status_code": resp.status_code,
                            "size_bytes": len(resp.content)
                        }
                        
                        # Flag slow endpoints
                        if response_time > 500:
                            backend_metrics["performance_issues"].append({
                                "endpoint": endpoint,
                                "response_time_ms": response_time,
                                "issue": "Slow response time",
                                "recommendation": "Implement caching or optimize database queries"
                            })
                        
                    except Exception as e:
                        backend_metrics["api_response_times"][endpoint] = {
                            "error": str(e),
                            "status": "failed"
                        }
        except:
            backend_metrics["status"] = "Backend server not running"
        
        # Check for N+1 query patterns
        server_file = "/workspace/backend/server.py"
        if os.path.exists(server_file):
            with open(server_file, 'r') as f:
                content = f.read()
                
            # Simple pattern detection
            if "for " in content and "await " in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "for " in line and i + 1 < len(lines) and "await " in lines[i + 1]:
                        backend_metrics["performance_issues"].append({
                            "issue": "Potential N+1 query pattern detected",
                            "location": f"Line {i+1}",
                            "recommendation": "Use bulk queries or eager loading"
                        })
        
        self.results["backend"] = backend_metrics
    
    async def analyze_database(self):
        """Analyze database performance and schema"""
        db_metrics = {
            "schema_analysis": {},
            "index_opportunities": [],
            "query_patterns": []
        }
        
        # Analyze SQL schema files
        schema_files = [
            "/workspace/supabase_schema.sql",
            "/workspace/create_alignment_scores_table.sql",
            "/workspace/create_daily_reflections_table.sql"
        ]
        
        missing_indexes = []
        for schema_file in schema_files:
            if os.path.exists(schema_file):
                with open(schema_file, 'r') as f:
                    content = f.read().lower()
                
                # Check for tables without indexes
                if "create table" in content:
                    tables = content.split("create table")
                    for table in tables[1:]:
                        table_name = table.split('(')[0].strip()
                        if "create index" not in table and table_name:
                            missing_indexes.append(table_name)
        
        if missing_indexes:
            db_metrics["index_opportunities"].append({
                "issue": "Tables potentially missing indexes",
                "tables": missing_indexes[:5],
                "recommendation": "Add indexes on frequently queried columns (user_id, created_at, etc.)"
            })
        
        # Check for complex queries
        backend_files = ["/workspace/backend/supabase_services.py", "/workspace/backend/services.py"]
        for file_path in backend_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Look for complex query patterns
                if content.count("JOIN") > 10:
                    db_metrics["query_patterns"].append({
                        "file": os.path.basename(file_path),
                        "issue": "Multiple JOIN operations detected",
                        "recommendation": "Consider query optimization or materialized views"
                    })
        
        self.results["database"] = db_metrics
    
    async def analyze_security(self):
        """Analyze security configuration"""
        security_metrics = {
            "vulnerabilities": [],
            "best_practices": [],
            "cors_config": {}
        }
        
        # Check CORS configuration
        server_file = "/workspace/backend/server.py"
        if os.path.exists(server_file):
            with open(server_file, 'r') as f:
                content = f.read()
            
            if 'allow_origins=["*"]' in content:
                security_metrics["vulnerabilities"].append({
                    "issue": "CORS allows all origins",
                    "severity": "medium",
                    "recommendation": "Restrict CORS to specific domains in production"
                })
            
            # Check for rate limiting
            if "ratelimit" not in content.lower():
                security_metrics["vulnerabilities"].append({
                    "issue": "No rate limiting detected",
                    "severity": "medium",
                    "recommendation": "Implement rate limiting to prevent abuse"
                })
        
        # Check for environment variables
        env_file = "/workspace/backend/.env"
        if os.path.exists(env_file):
            security_metrics["best_practices"].append({
                "check": "Environment variables",
                "status": "✅ .env file exists",
                "recommendation": "Ensure .env is in .gitignore"
            })
        
        self.results["security"] = security_metrics
    
    def generate_recommendations(self):
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Frontend recommendations
        if self.results["frontend"].get("bundle_analysis", {}).get("total_size_kb", 0) > 5000:
            recommendations.append({
                "priority": "HIGH",
                "category": "Frontend",
                "issue": "Large bundle size",
                "recommendation": "Implement code splitting, lazy loading, and tree shaking",
                "impact": "Reduce initial load time by 40-60%"
            })
        
        # Backend recommendations
        slow_endpoints = [ep for ep, data in self.results["backend"].get("api_response_times", {}).items() 
                         if isinstance(data, dict) and data.get("response_time_ms", 0) > 500]
        if slow_endpoints:
            recommendations.append({
                "priority": "HIGH",
                "category": "Backend",
                "issue": f"{len(slow_endpoints)} slow endpoints detected",
                "endpoints": slow_endpoints,
                "recommendation": "Implement Redis caching and query optimization",
                "impact": "Improve API response times by 70%"
            })
        
        # Database recommendations
        if self.results["database"].get("index_opportunities"):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Database",
                "issue": "Missing database indexes",
                "recommendation": "Add indexes on foreign keys and frequently queried columns",
                "impact": "Improve query performance by 50-80%"
            })
        
        # Security recommendations
        vulnerabilities = self.results["security"].get("vulnerabilities", [])
        if vulnerabilities:
            recommendations.append({
                "priority": "HIGH",
                "category": "Security",
                "issue": f"{len(vulnerabilities)} security issues found",
                "recommendation": "Address CORS configuration and implement rate limiting",
                "impact": "Prevent potential security vulnerabilities"
            })
        
        self.results["recommendations"] = sorted(recommendations, 
                                               key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["priority"]])
    
    def save_results(self):
        """Save audit results to file"""
        output_file = f"/workspace/performance_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✅ Performance audit complete! Results saved to: {output_file}")
        
        # Print summary
        print("\n📊 PERFORMANCE AUDIT SUMMARY")
        print("=" * 50)
        
        if self.results["frontend"].get("bundle_analysis"):
            total_size = self.results["frontend"]["bundle_analysis"].get("total_size_kb", 0)
            print(f"Frontend Bundle Size: {total_size:.2f} KB")
        
        if self.results["backend"].get("api_response_times"):
            avg_response = sum(d.get("response_time_ms", 0) for d in self.results["backend"]["api_response_times"].values() 
                             if isinstance(d, dict) and "response_time_ms" in d)
            count = len([d for d in self.results["backend"]["api_response_times"].values() 
                        if isinstance(d, dict) and "response_time_ms" in d])
            if count > 0:
                print(f"Average API Response Time: {avg_response/count:.2f} ms")
        
        print(f"\nTotal Recommendations: {len(self.results['recommendations'])}")
        print(f"High Priority Issues: {len([r for r in self.results['recommendations'] if r['priority'] == 'HIGH'])}")
        
        return output_file

async def main():
    auditor = PerformanceAuditor()
    await auditor.run_full_audit()

if __name__ == "__main__":
    asyncio.run(main())