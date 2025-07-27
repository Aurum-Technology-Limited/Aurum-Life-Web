#!/usr/bin/env python3
"""
Simple Aurum Life Application Test
Tests basic setup without external dependencies
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"{text}")
    print(f"{'='*60}\n")

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✓ {description} found: {filepath}")
        return True
    else:
        print(f"✗ {description} not found: {filepath}")
        return False

def check_directory_structure():
    """Check if the project structure is correct"""
    print_header("Checking Project Structure")
    
    required_items = [
        ("backend/", "Backend directory"),
        ("frontend/", "Frontend directory"),
        ("backend/server.py", "Backend server file"),
        ("backend/requirements.txt", "Backend requirements"),
        ("frontend/package.json", "Frontend package.json"),
        ("README.md", "README file"),
    ]
    
    all_good = True
    for item, description in required_items:
        if not check_file_exists(item, description):
            all_good = False
    
    return all_good

def check_python_setup():
    """Check Python environment"""
    print_header("Checking Python Setup")
    
    print(f"Python version: {sys.version}")
    if sys.version_info >= (3, 8):
        print("✓ Python version is 3.8 or higher")
    else:
        print("✗ Python version is too old (need 3.8+)")
        return False
    
    # Check if pip is available
    try:
        result = subprocess.run(["pip3", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ pip is installed: {result.stdout.strip()}")
        else:
            print("✗ pip is not available")
            return False
    except:
        print("✗ Could not check pip")
        return False
    
    return True

def setup_minimal_env():
    """Set up minimal environment files"""
    print_header("Setting Up Environment Files")
    
    # Backend .env
    backend_env = Path("backend/.env")
    if not backend_env.exists():
        env_content = """# Minimal Test Configuration
MONGODB_URI=mongodb://localhost:27017/aurum_test
JWT_SECRET_KEY=test_secret_key_123
ENVIRONMENT=development
DEBUG=True
PORT=8000
"""
        backend_env.write_text(env_content)
        print("✓ Created backend/.env with test configuration")
    else:
        print("ℹ backend/.env already exists")
    
    # Frontend .env
    frontend_env = Path("frontend/.env")
    if not frontend_env.exists():
        env_content = """REACT_APP_API_URL=http://localhost:8000
"""
        frontend_env.write_text(env_content)
        print("✓ Created frontend/.env with test configuration")
    else:
        print("ℹ frontend/.env already exists")
    
    return True

def check_backend_dependencies():
    """Check if backend dependencies can be installed"""
    print_header("Checking Backend Dependencies")
    
    req_file = Path("backend/requirements.txt")
    if req_file.exists():
        print("✓ requirements.txt found")
        
        # Read and display key dependencies
        with open(req_file, 'r') as f:
            lines = f.readlines()
            print("\nKey dependencies:")
            for line in lines[:10]:  # Show first 10
                line = line.strip()
                if line and not line.startswith('#'):
                    print(f"  • {line}")
        
        print("\nTo install dependencies, run:")
        print("  pip3 install -r backend/requirements.txt")
    else:
        print("✗ requirements.txt not found")
        return False
    
    return True

def check_frontend_setup():
    """Check frontend setup"""
    print_header("Checking Frontend Setup")
    
    package_json = Path("frontend/package.json")
    if package_json.exists():
        print("✓ package.json found")
        
        # Check if node_modules exists
        if Path("frontend/node_modules").exists():
            print("✓ Frontend dependencies appear to be installed")
        else:
            print("ℹ Frontend dependencies not installed")
            print("  To install, run:")
            print("  cd frontend && yarn install")
    else:
        print("✗ package.json not found")
        return False
    
    # Check for yarn or npm
    try:
        result = subprocess.run(["yarn", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Yarn is installed: v{result.stdout.strip()}")
        else:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ npm is installed: v{result.stdout.strip()}")
            else:
                print("✗ Neither yarn nor npm found")
    except:
        print("ℹ Could not check for yarn/npm")
    
    return True

def display_test_files():
    """Display available test files"""
    print_header("Available Test Files")
    
    test_files = sorted(Path(".").glob("*test*.py"))
    if test_files:
        print(f"Found {len(test_files)} test files:")
        for i, test_file in enumerate(test_files[:10], 1):  # Show first 10
            print(f"  {i}. {test_file}")
        
        if len(test_files) > 10:
            print(f"  ... and {len(test_files) - 10} more")
    else:
        print("No test files found")
    
    return True

def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("AURUM LIFE APPLICATION - SIMPLE TEST")
    print("="*60)
    
    checks = [
        check_directory_structure,
        check_python_setup,
        setup_minimal_env,
        check_backend_dependencies,
        check_frontend_setup,
        display_test_files,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Error in check: {e}")
            results.append(False)
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All basic checks passed!")
        print("\nNext steps to run the application:")
        print("1. Install backend dependencies:")
        print("   pip3 install -r backend/requirements.txt")
        print("\n2. Install frontend dependencies:")
        print("   cd frontend && yarn install")
        print("\n3. Start the backend server:")
        print("   cd backend && python3 server.py")
        print("\n4. Start the frontend (in a new terminal):")
        print("   cd frontend && yarn start")
        print("\n5. Open http://localhost:3000 in your browser")
    else:
        print("\n⚠ Some checks failed. Please fix the issues above.")
    
    print("\nTo run a specific test file, use:")
    print("  python3 <test_filename>")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())