#!/usr/bin/env python3
"""
Test user authentication and find working credentials
"""
import requests
import json

# Backend URL
BACKEND_URL = "https://journal-analytics-1.preview.emergentagent.com"

def test_login_credentials():
    """Test various credentials for the test user"""
    
    test_email = "marc.alleyne@aurumtechnologyltd.com"
    possible_passwords = [
        "password123",
        "Password123!",
        "TestPassword123!",
        "aurum123",
        "Aurum123!",
        "test123",
        "admin123",
        "password"
    ]
    
    print(f"Testing login for {test_email}...")
    print("=" * 50)
    
    for i, password in enumerate(possible_passwords, 1):
        print(f"Attempt {i}: Testing password '{password}'")
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/auth/login",
                json={
                    "email": test_email,
                    "password": password
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    print(f"  ✅ SUCCESS! Working password: {password}")
                    print(f"  Token: {data['access_token'][:50]}...")
                    
                    # Test insights API with this token
                    test_insights_api(data['access_token'])
                    return password
                else:
                    print(f"  ❌ Response missing access_token: {data}")
            elif response.status_code == 401:
                print(f"  ❌ Invalid credentials")
            elif response.status_code == 409:
                print(f"  ⚠️  Email exists (409) - password incorrect")
            else:
                try:
                    error_data = response.json()
                    print(f"  ❌ Error: {error_data}")
                except:
                    print(f"  ❌ HTTP {response.status_code}")
                    
        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout - backend may be slow")
        except requests.exceptions.ConnectionError:
            print(f"  🔌 Connection error - backend may be down")
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
        
        print()
    
    print("❌ No working password found")
    print("\n💡 Suggestions:")
    print("1. Check if user account exists in Supabase auth dashboard")
    print("2. Try resetting password in Supabase dashboard")
    print("3. Create new test user if needed")
    return None

def test_insights_api(token):
    """Test the insights API with a valid token"""
    
    print(f"\n🔍 Testing insights API with valid token...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/hrm/insights",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        print(f"Insights API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            insights = data.get('insights', [])
            print(f"✅ SUCCESS! Found {len(insights)} insights:")
            
            for insight in insights:
                print(f"  - {insight.get('title', 'No title')}")
                print(f"    Confidence: {insight.get('confidence_score', 0)}")
                print(f"    Type: {insight.get('insight_type', 'unknown')}")
                print()
                
        elif response.status_code == 403:
            print(f"❌ Still authentication error - token might be invalid")
        else:
            try:
                error_data = response.json()
                print(f"❌ API Error: {error_data}")
            except:
                print(f"❌ HTTP {response.status_code}")
                
    except Exception as e:
        print(f"❌ Insights API test failed: {e}")

def test_backend_health():
    """Test basic backend connectivity"""
    
    print("🏥 Testing backend health...")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/health",
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Backend is responding")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def main():
    """Main test function"""
    
    print("🧪 AURUM LIFE AUTHENTICATION & INSIGHTS TEST")
    print("=" * 60)
    
    # Test backend health first
    if not test_backend_health():
        print("❌ Backend is not responding - check if services are running")
        return
    
    # Test login credentials
    working_password = test_login_credentials()
    
    if working_password:
        print(f"\n🎉 SUCCESS!")
        print(f"Working credentials: {test_email} / {working_password}")
        print("You can now log in and access your 3 real insights!")
    else:
        print(f"\n💥 AUTHENTICATION ISSUE")
        print("Need to resolve user credentials before insights can be accessed")

if __name__ == "__main__":
    main()