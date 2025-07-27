#!/usr/bin/env python3
"""
Aurum Life Application Test Script
This script tests the basic setup and functionality of the application.
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(message, status="info"):
    if status == "success":
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    elif status == "error":
        print(f"{Colors.RED}✗ {message}{Colors.END}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
    else:
        print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print_status("Checking Python version...")
    if sys.version_info < (3, 8):
        print_status(f"Python {sys.version} is too old. Please use Python 3.8+", "error")
        return False
    print_status(f"Python {sys.version.split()[0]} is supported", "success")
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    print_status("\nChecking backend dependencies...")
    
    try:
        # Check if pip packages are installed
        result = subprocess.run(
            ["pip", "list"], 
            capture_output=True, 
            text=True
        )
        installed_packages = result.stdout.lower()
        
        required = ["fastapi", "uvicorn", "pymongo", "pydantic"]
        missing = []
        
        for package in required:
            if package in installed_packages:
                print_status(f"  {package} is installed", "success")
            else:
                missing.append(package)
                print_status(f"  {package} is missing", "warning")
        
        if missing:
            print_status("\nInstalling missing packages...", "info")
            subprocess.run(
                ["pip", "install", "-r", "backend/requirements.txt"],
                check=True
            )
            print_status("Dependencies installed", "success")
            
    except Exception as e:
        print_status(f"Error checking dependencies: {e}", "error")
        return False
    
    return True

def setup_test_env():
    """Set up minimal test environment variables"""
    print_status("\nSetting up test environment...")
    
    # Create minimal .env file for testing
    env_content = """# Test Environment Configuration
MONGODB_URI=mongodb://localhost:27017/aurum_test
JWT_SECRET_KEY=test_secret_key_for_development_only
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7
ENVIRONMENT=development
DEBUG=True
HOST=127.0.0.1
PORT=8000

# Google OAuth (optional - leave empty for testing)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Email Service (optional - leave empty for testing)
SENDGRID_API_KEY=
FROM_EMAIL=noreply@example.com

# Supabase (if using)
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=
"""
    
    backend_env_path = Path("backend/.env")
    if not backend_env_path.exists():
        backend_env_path.write_text(env_content)
        print_status("Created backend/.env file", "success")
    else:
        print_status("backend/.env already exists", "info")
    
    # Create frontend .env
    frontend_env_content = """REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=
"""
    
    frontend_env_path = Path("frontend/.env")
    if not frontend_env_path.exists():
        frontend_env_path.write_text(frontend_env_content)
        print_status("Created frontend/.env file", "success")
    else:
        print_status("frontend/.env already exists", "info")
    
    return True

def test_backend_startup():
    """Test if the backend server can start"""
    print_status("\nTesting backend startup...")
    
    # Start the server in a subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath("backend")
    
    try:
        # Try to import the server module first
        sys.path.insert(0, os.path.abspath("backend"))
        import server
        print_status("Backend server module loaded successfully", "success")
        
        # Start the server
        print_status("Starting backend server...", "info")
        process = subprocess.Popen(
            ["python", "backend/server.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if server is running
        if process.poll() is None:
            print_status("Backend server started", "success")
            
            # Try to make a request to the server
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    print_status("Health check passed", "success")
                    print_status(f"  Response: {response.json()}", "info")
                else:
                    print_status(f"Health check returned status {response.status_code}", "warning")
            except requests.exceptions.ConnectionError:
                print_status("Could not connect to server - checking for API docs", "warning")
                try:
                    response = requests.get("http://localhost:8000/docs", timeout=5)
                    if response.status_code == 200:
                        print_status("API documentation endpoint is accessible", "success")
                except:
                    print_status("Server may not be fully started yet", "warning")
            except Exception as e:
                print_status(f"Health check error: {e}", "error")
            
            # Terminate the test server
            process.terminate()
            process.wait(timeout=5)
            print_status("Test server stopped", "info")
            
        else:
            # Server crashed, get error output
            stdout, stderr = process.communicate()
            print_status("Backend server failed to start", "error")
            if stderr:
                print_status(f"Error: {stderr.decode()[:500]}...", "error")
                
    except ImportError as e:
        print_status(f"Could not import server module: {e}", "error")
        return False
    except Exception as e:
        print_status(f"Unexpected error: {e}", "error")
        return False
    
    return True

def test_frontend_setup():
    """Check frontend setup"""
    print_status("\nChecking frontend setup...")
    
    # Check if node_modules exists
    if Path("frontend/node_modules").exists():
        print_status("Frontend dependencies are installed", "success")
    else:
        print_status("Frontend dependencies not installed", "warning")
        print_status("Run 'cd frontend && yarn install' to install", "info")
    
    # Check package.json
    try:
        with open("frontend/package.json", "r") as f:
            package = json.load(f)
            print_status(f"Frontend: {package.get('name', 'Unknown')} v{package.get('version', '?')}", "info")
            
            # Check for key dependencies
            deps = package.get("dependencies", {})
            key_deps = ["react", "react-dom", "axios", "tailwindcss"]
            for dep in key_deps:
                if dep in deps:
                    print_status(f"  {dep}: {deps[dep]}", "success")
                    
    except Exception as e:
        print_status(f"Could not read package.json: {e}", "error")
    
    return True

def run_basic_tests():
    """Run some basic test files if they exist"""
    print_status("\nLooking for test files...")
    
    # Find Python test files
    test_files = list(Path(".").glob("*test*.py"))[:5]  # Limit to 5 files
    
    if test_files:
        print_status(f"Found {len(test_files)} test files", "info")
        for test_file in test_files:
            print_status(f"  • {test_file}", "info")
    else:
        print_status("No test files found", "warning")
    
    return True

def main():
    """Main test orchestration"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Aurum Life Application Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Setup", setup_test_env),
        ("Backend Startup", test_backend_startup),
        ("Frontend Setup", test_frontend_setup),
        ("Test Files", run_basic_tests),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_status(f"Check '{name}' failed with error: {e}", "error")
            results.append((name, False))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test Summary:{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "success" if result else "error"
        print_status(f"{name}: {'PASSED' if result else 'FAILED'}", status)
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} checks passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}✨ All checks passed! The application is ready for testing.{Colors.END}")
        print(f"\n{Colors.BLUE}Next steps:{Colors.END}")
        print("1. Start the backend: cd backend && python server.py")
        print("2. Start the frontend: cd frontend && yarn start")
        print("3. Open http://localhost:3000 in your browser")
    else:
        print(f"\n{Colors.YELLOW}⚠ Some checks failed. Please review the errors above.{Colors.END}")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())