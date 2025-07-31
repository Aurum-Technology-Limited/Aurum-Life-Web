#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://7767cc54-7d42-422d-ae92-93a862d5b150.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_areas_performance():
    """Test the specific Areas API endpoint mentioned in the N+1 issue"""
    print("🔍 TESTING AREAS API PERFORMANCE - N+1 QUERY INVESTIGATION")
    print("="*70)
    
    # Test user credentials from test_result.md
    test_credentials = [
        {"email": "final.test@aurumlife.com", "password": "TestPass123!"},
        {"email": "contextual.test@aurumlife.com", "password": "TestPass123!"},
        {"email": "performance.test@aurumlife.com", "password": "TestPass123!"}
    ]
    
    async with aiohttp.ClientSession() as session:
        auth_token = None
        
        # Try to authenticate with existing test users
        for creds in test_credentials:
            try:
                async with session.post(f"{API_BASE}/auth/login", json=creds) as response:
                    if response.status == 200:
                        data = await response.json()
                        auth_token = data["access_token"]
                        print(f"✅ Authenticated with {creds['email']}")
                        break
                    else:
                        print(f"❌ Failed to authenticate with {creds['email']}: {response.status}")
            except Exception as e:
                print(f"❌ Auth error with {creds['email']}: {e}")
                
        if not auth_token:
            print("❌ Could not authenticate with any test user")
            return
            
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test the critical Areas API endpoint
        print(f"\n🎯 Testing GET /api/areas?include_projects=true&include_archived=false")
        
        start_time = time.time()
        
        try:
            async with session.get(f"{API_BASE}/areas?include_projects=true&include_archived=false", headers=headers) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                print(f"⏱️  Response time: {response_time_ms:.2f}ms")
                print(f"📊 Status code: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"📦 Data size: {len(str(data))} characters")
                    print(f"📋 Areas returned: {len(data) if isinstance(data, list) else 'N/A'}")
                    
                    # Analyze data structure for N+1 indicators
                    if isinstance(data, list) and len(data) > 0:
                        sample_area = data[0]
                        if isinstance(sample_area, dict):
                            nested_fields = [k for k, v in sample_area.items() if isinstance(v, (list, dict))]
                            print(f"🔍 Nested fields in areas: {nested_fields}")
                            
                            if 'projects' in sample_area and isinstance(sample_area['projects'], list):
                                total_projects = sum(len(area.get('projects', [])) for area in data)
                                print(f"📊 Total projects across all areas: {total_projects}")
                                
                    # Performance analysis
                    if response_time_ms > 3000:
                        print("🚨 CRITICAL: Response time > 3 seconds - SEVERE N+1 REGRESSION!")
                    elif response_time_ms > 1000:
                        print("⚠️  WARNING: Response time > 1 second - Possible N+1 regression")
                    elif response_time_ms > 500:
                        print("⚠️  CAUTION: Response time > 500ms - Performance degraded from optimized target")
                    else:
                        print("✅ GOOD: Response time within acceptable range")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Request failed: {error_text}")
                    
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            print(f"❌ Request exception: {e}")
            print(f"⏱️  Time before failure: {response_time_ms:.2f}ms")
            
        # Test simpler endpoint for comparison
        print(f"\n🔍 Testing GET /api/areas (without include_projects) for comparison")
        
        start_time = time.time()
        
        try:
            async with session.get(f"{API_BASE}/areas", headers=headers) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                print(f"⏱️  Response time: {response_time_ms:.2f}ms")
                print(f"📊 Status code: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"📋 Areas returned: {len(data) if isinstance(data, list) else 'N/A'}")
                    
        except Exception as e:
            print(f"❌ Simple areas request failed: {e}")

async def main():
    """Main test execution"""
    print("🚀 N+1 QUERY PERFORMANCE REGRESSION INVESTIGATION")
    print("🎯 Focus: Areas API endpoint performance analysis")
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print()
    
    await test_areas_performance()
    
    print("\n" + "="*70)
    print("📋 INVESTIGATION SUMMARY:")
    print("- Check backend logs for individual Supabase queries")
    print("- Look for patterns like: GET /rest/v1/pillars?select=*&id=eq.PILLAR_ID")
    print("- Multiple individual queries indicate N+1 pattern regression")
    print("- Optimized batch fetching should use ≤5 queries total")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())