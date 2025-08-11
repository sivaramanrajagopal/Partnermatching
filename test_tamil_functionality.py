#!/usr/bin/env python3
"""
Test script to verify Tamil language functionality
"""

import requests
import json

def test_tamil_language():
    """Test Tamil language functionality"""
    
    # Test data
    test_data = {
        "male_dob": "1990-05-15",
        "male_tob": "14:30",
        "male_lat": 13.0833,
        "male_lon": 80.2833,
        "female_dob": "1992-08-20",
        "female_tob": "16:45",
        "female_lat": 11.9416,
        "female_lon": 79.8083
    }
    
    print("🔍 Testing Tamil Language Functionality...")
    print("=" * 50)
    
    # Test 1: Check if Tamil route loads
    print("\n1. Testing Tamil route accessibility...")
    try:
        response = requests.get("http://127.0.0.1:5001/tamil")
        if response.status_code == 200:
            print("✅ Tamil route is accessible")
        else:
            print(f"❌ Tamil route failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing Tamil route: {e}")
    
    # Test 2: Test API with Tamil language header
    print("\n2. Testing API with Tamil language...")
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-Language': 'ta'
        }
        
        response = requests.post(
            "http://127.0.0.1:5001/analyze",
            headers=headers,
            json=test_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ API call successful with Tamil language")
                
                # Check if verdict is in Tamil
                verdict = data.get('verdict', '')
                message = data.get('message', '')
                
                print(f"   Verdict: {verdict}")
                print(f"   Message: {message}")
                
                # Check if condition names are in Tamil
                compatibility_data = data.get('compatibility_data', [])
                if compatibility_data:
                    print("\n   Condition names:")
                    for item in compatibility_data:
                        condition = item.get('condition', '')
                        print(f"   - {condition}")
                
                # Check if reasoning is in Tamil
                rahu_reasoning = data.get('rahu_reasoning', [])
                ketu_reasoning = data.get('ketu_reasoning', [])
                
                if rahu_reasoning:
                    print(f"\n   Rahu reasoning: {rahu_reasoning}")
                if ketu_reasoning:
                    print(f"   Ketu reasoning: {ketu_reasoning}")
                    
            else:
                print(f"❌ API call failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ API call failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
    
    # Test 3: Test English vs Tamil comparison
    print("\n3. Comparing English vs Tamil responses...")
    try:
        # English request
        headers_en = {
            'Content-Type': 'application/json',
            'X-Language': 'en'
        }
        
        response_en = requests.post(
            "http://127.0.0.1:5001/analyze",
            headers=headers_en,
            json=test_data
        )
        
        # Tamil request
        headers_ta = {
            'Content-Type': 'application/json',
            'X-Language': 'ta'
        }
        
        response_ta = requests.post(
            "http://127.0.0.1:5001/analyze",
            headers=headers_ta,
            json=test_data
        )
        
        if response_en.status_code == 200 and response_ta.status_code == 200:
            data_en = response_en.json()
            data_ta = response_ta.json()
            
            if data_en.get('success') and data_ta.get('success'):
                print("✅ Both English and Tamil responses successful")
                
                # Compare verdicts
                verdict_en = data_en.get('verdict', '')
                verdict_ta = data_ta.get('verdict', '')
                
                print(f"   English verdict: {verdict_en}")
                print(f"   Tamil verdict: {verdict_ta}")
                
                # Check if they're different (indicating proper translation)
                if verdict_en != verdict_ta:
                    print("✅ Verdicts are properly translated")
                else:
                    print("⚠️  Verdicts are the same (might indicate translation issue)")
                    
            else:
                print("❌ One or both API calls failed")
        else:
            print(f"❌ API calls failed: EN={response_en.status_code}, TA={response_ta.status_code}")
            
    except Exception as e:
        print(f"❌ Error comparing languages: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Tamil language functionality test completed!")

if __name__ == "__main__":
    test_tamil_language()
