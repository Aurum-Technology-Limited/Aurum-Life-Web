#!/usr/bin/env python3
"""
JWT TOKEN DECODER - DEBUGGING USER ID MISMATCH
Decode the JWT token to see what user ID is being used.
"""

import requests
import json
import base64
import sys

# Configuration
BACKEND_URL = "https://fa85c789-1504-48f1-9b33-719ff2e79ef1.preview.emergentagent.com/api"

def decode_jwt_payload(token):
    """Decode JWT payload without verification"""
    try:
        # JWT has 3 parts separated by dots
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Decode the payload (second part)
        payload = parts[1]
        
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        # Decode base64
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"Error decoding JWT: {e}")
        return None

def test_jwt_decoding():
    """Test JWT decoding to see user ID"""
    print("🔍 JWT TOKEN ANALYSIS")
    print("=" * 50)
    
    session = requests.Session()
    
    # Login to get token
    print("\n1. Getting JWT Token...")
    login_data = {
        "email": "marc.alleyne@aurumtechnologyltd.com",
        "password": "password"
    }
    
    try:
        response = session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            print(f"   ✅ Token received")
            
            # Decode the token
            print("\n2. Decoding JWT Token...")
            payload = decode_jwt_payload(access_token)
            
            if payload:
                print(f"   ✅ Token decoded successfully")
                print(f"   Full payload: {json.dumps(payload, indent=2)}")
                
                # Extract user ID
                user_id = payload.get('sub') or payload.get('user_id') or payload.get('id')
                print(f"\n3. User ID Analysis:")
                print(f"   User ID from token: {user_id}")
                print(f"   Expected in DB: 272edb74-8be3-4504-818c-b1dd42c63ebe")
                print(f"   Match: {'✅ YES' if user_id == '272edb74-8be3-4504-818c-b1dd42c63ebe' else '❌ NO'}")
                
                if user_id != '272edb74-8be3-4504-818c-b1dd42c63ebe':
                    print(f"\n🚨 USER ID MISMATCH CONFIRMED!")
                    print(f"   The authentication system is using: {user_id}")
                    print(f"   But the database has: 272edb74-8be3-4504-818c-b1dd42c63ebe")
                    print(f"   This explains why pillar creation fails with foreign key errors.")
                
                return user_id
            else:
                print(f"   ❌ Failed to decode token")
                return None
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")
        return None

def main():
    """Run JWT analysis"""
    print("🔍 JWT TOKEN ANALYSIS - DEBUGGING USER ID MISMATCH")
    print("=" * 60)
    
    user_id = test_jwt_decoding()
    
    print("\n" + "=" * 60)
    print("📊 ANALYSIS RESULTS")
    print("=" * 60)
    
    if user_id:
        if user_id == '272edb74-8be3-4504-818c-b1dd42c63ebe':
            print("✅ SUCCESS: User IDs match!")
            print("   The issue might be elsewhere.")
        else:
            print("❌ CONFIRMED: User ID mismatch!")
            print(f"   Auth system user ID: {user_id}")
            print(f"   Database user ID: 272edb74-8be3-4504-818c-b1dd42c63ebe")
            print("\n🔧 SOLUTION NEEDED:")
            print("   Either:")
            print(f"   1. Update the public.users table to use ID: {user_id}")
            print(f"   2. Or fix the auth system to use ID: 272edb74-8be3-4504-818c-b1dd42c63ebe")
    else:
        print("❌ FAILURE: Could not analyze token")
    
    print("=" * 60)
    return user_id is not None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)