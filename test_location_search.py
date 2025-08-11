#!/usr/bin/env python3
"""
Test script to verify location search functionality
"""

import requests
import json
import os

def test_location_search():
    """Test location search functionality"""
    
    print("🔍 Testing Location Search Functionality...")
    print("=" * 50)
    
    # Test 1: Check if the app loads with location search fields
    print("\n1. Testing app loading with location search...")
    try:
        response = requests.get("http://127.0.0.1:5001/")
        if response.status_code == 200:
            print("✅ App loads successfully")
            
            # Check if location search fields are present
            if 'male_location' in response.text and 'female_location' in response.text:
                print("✅ Location search fields are present in HTML")
            else:
                print("⚠️  Location search fields not found in HTML")
                
        else:
            print(f"❌ App failed to load: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing app: {e}")
    
    # Test 2: Check Tamil version
    print("\n2. Testing Tamil version with location search...")
    try:
        response = requests.get("http://127.0.0.1:5001/tamil")
        if response.status_code == 200:
            print("✅ Tamil app loads successfully")
            
            # Check if Tamil location search fields are present
            if 'பிறந்த இடம்' in response.text:
                print("✅ Tamil location search fields are present")
            else:
                print("⚠️  Tamil location search fields not found")
                
        else:
            print(f"❌ Tamil app failed to load: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing Tamil app: {e}")
    
    # Test 3: Test API with timezone offsets
    print("\n3. Testing API with timezone offsets...")
    try:
        test_data = {
            "male_dob": "1990-05-15",
            "male_tob": "14:30",
            "male_lat": 13.0833,
            "male_lon": 80.2833,
            "male_tz_offset": 5.5,
            "female_dob": "1992-08-20",
            "female_tob": "16:45",
            "female_lat": 11.9416,
            "female_lon": 79.8083,
            "female_tz_offset": 5.5
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-Language': 'en'
        }
        
        response = requests.post(
            "http://127.0.0.1:5001/analyze",
            headers=headers,
            json=test_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ API call with timezone offsets successful")
                print(f"   Male timezone offset: {test_data['male_tz_offset']}")
                print(f"   Female timezone offset: {test_data['female_tz_offset']}")
            else:
                print(f"❌ API call failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ API call failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
    
    # Test 4: Check configuration
    print("\n4. Checking configuration...")
    try:
        from config import Config
        
        print(f"   Google Maps API Key configured: {'Yes' if Config.GOOGLE_MAPS_API_KEY != 'YOUR_GOOGLE_MAPS_API_KEY' else 'No'}")
        print(f"   Default timezone offset: {Config.DEFAULT_TZ_OFFSET}")
        print(f"   India bounds: {Config.INDIA_BOUNDS}")
        
        if Config.GOOGLE_MAPS_API_KEY == 'YOUR_GOOGLE_MAPS_API_KEY':
            print("⚠️  Please set your Google Maps API key in config.py or environment variable")
        else:
            print("✅ Google Maps API key is configured")
            
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")
    
    # Test 5: Environment variable check
    print("\n5. Checking environment variables...")
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    if api_key:
        print(f"✅ GOOGLE_MAPS_API_KEY environment variable is set")
        print(f"   Key length: {len(api_key)} characters")
    else:
        print("⚠️  GOOGLE_MAPS_API_KEY environment variable not set")
        print("   You can set it with: export GOOGLE_MAPS_API_KEY='your-api-key'")
    
    print("\n" + "=" * 50)
    print("🏁 Location search functionality test completed!")
    print("\n📝 Next Steps:")
    print("1. Get a Google Maps API key from Google Cloud Console")
    print("2. Set the API key in config.py or as environment variable")
    print("3. Enable Places API in Google Cloud Console")
    print("4. Test the location search functionality in the browser")

if __name__ == "__main__":
    test_location_search()
