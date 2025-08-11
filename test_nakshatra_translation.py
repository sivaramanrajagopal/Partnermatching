#!/usr/bin/env python3
"""
Test script to verify nakshatra name translations
"""

import requests
import json

def test_nakshatra_translation():
    """Test nakshatra name translation functionality"""
    
    # Test data that should give specific nakshatras
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
    
    print("🔍 Testing Nakshatra Name Translation...")
    print("=" * 50)
    
    # Test English response
    print("\n1. Testing English response...")
    try:
        headers_en = {
            'Content-Type': 'application/json',
            'X-Language': 'en'
        }
        
        response_en = requests.post(
            "http://127.0.0.1:5001/analyze",
            headers=headers_en,
            json=test_data
        )
        
        if response_en.status_code == 200:
            data_en = response_en.json()
            if data_en.get('success'):
                print("✅ English API call successful")
                print(f"   Male Rahu Nakshatra: {data_en.get('male_rahu_nakshatra', 'N/A')}")
                print(f"   Male Ketu Nakshatra: {data_en.get('male_ketu_nakshatra', 'N/A')}")
            else:
                print(f"❌ English API call failed: {data_en.get('error', 'Unknown error')}")
        else:
            print(f"❌ English API call failed with status: {response_en.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing English API: {e}")
    
    # Test Tamil response
    print("\n2. Testing Tamil response...")
    try:
        headers_ta = {
            'Content-Type': 'application/json',
            'X-Language': 'ta'
        }
        
        response_ta = requests.post(
            "http://127.0.0.1:5001/analyze",
            headers=headers_ta,
            json=test_data
        )
        
        if response_ta.status_code == 200:
            data_ta = response_ta.json()
            if data_ta.get('success'):
                print("✅ Tamil API call successful")
                print(f"   Male Rahu Nakshatra: {data_ta.get('male_rahu_nakshatra', 'N/A')}")
                print(f"   Male Ketu Nakshatra: {data_ta.get('male_ketu_nakshatra', 'N/A')}")
                
                # Check if nakshatra names are in Tamil
                rahu_nakshatra = data_ta.get('male_rahu_nakshatra', '')
                ketu_nakshatra = data_ta.get('male_ketu_nakshatra', '')
                
                # Check if they contain Tamil characters
                tamil_chars = any('\u0B80' <= char <= '\u0BFF' for char in rahu_nakshatra + ketu_nakshatra)
                
                if tamil_chars:
                    print("✅ Nakshatra names are properly translated to Tamil")
                else:
                    print("⚠️  Nakshatra names may not be in Tamil")
                    
                # Check condition details for Tamil rasi/nakshatra names
                compatibility_data = data_ta.get('compatibility_data', [])
                if compatibility_data:
                    print("\n   Condition details:")
                    for item in compatibility_data:
                        value = item.get('value', '')
                        details = item.get('details', '')
                        print(f"   - Value: {value}")
                        print(f"   - Details: {details}")
                        
            else:
                print(f"❌ Tamil API call failed: {data_ta.get('error', 'Unknown error')}")
        else:
            print(f"❌ Tamil API call failed with status: {response_ta.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing Tamil API: {e}")
    
    # Compare English vs Tamil
    print("\n3. Comparing English vs Tamil nakshatra names...")
    try:
        if response_en.status_code == 200 and response_ta.status_code == 200:
            data_en = response_en.json()
            data_ta = response_ta.json()
            
            if data_en.get('success') and data_ta.get('success'):
                rahu_en = data_en.get('male_rahu_nakshatra', '')
                rahu_ta = data_ta.get('male_rahu_nakshatra', '')
                ketu_en = data_en.get('male_ketu_nakshatra', '')
                ketu_ta = data_ta.get('male_ketu_nakshatra', '')
                
                print(f"   English Rahu: {rahu_en}")
                print(f"   Tamil Rahu: {rahu_ta}")
                print(f"   English Ketu: {ketu_en}")
                print(f"   Tamil Ketu: {ketu_ta}")
                
                if rahu_en != rahu_ta and ketu_en != ketu_ta:
                    print("✅ Nakshatra names are properly translated")
                else:
                    print("⚠️  Nakshatra names are the same (translation may not be working)")
                    
            else:
                print("❌ One or both API calls failed")
        else:
            print("❌ API calls failed")
            
    except Exception as e:
        print(f"❌ Error comparing nakshatra names: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Nakshatra translation test completed!")

if __name__ == "__main__":
    test_nakshatra_translation()
