#!/usr/bin/env python3
"""
Debug the FastAPI application routes
"""

import sys
import os
sys.path.append('/app/backend')

from server import app

print("🔍 Debugging FastAPI routes...")

# Print all registered routes
print("\n📋 All registered routes:")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"  {route.methods} {route.path}")
    elif hasattr(route, 'path'):
        print(f"  {route.path}")

# Print router information
print(f"\n📊 Total routes: {len(app.routes)}")

# Check if auth_router routes are included
auth_routes = [route for route in app.routes if hasattr(route, 'path') and 'auth' in route.path]
print(f"\n🔐 Auth routes found: {len(auth_routes)}")
for route in auth_routes:
    if hasattr(route, 'methods'):
        print(f"  {route.methods} {route.path}")
    else:
        print(f"  {route.path}")

# Check API router specifically
api_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith('/api')]
print(f"\n🚀 API routes found: {len(api_routes)}")
for route in api_routes[:10]:  # Show first 10
    if hasattr(route, 'methods'):
        print(f"  {route.methods} {route.path}")
    else:
        print(f"  {route.path}")