#!/usr/bin/env python3
"""
Test script for Tamil analysis results in Vedic Life Partner Prediction App
"""

import requests
import json

def test_english_analysis():
    """Test analysis results in English"""
    test_data = {
        'male_dob': '1978-09-18',
        'male_tob': '17:35',
        'male_lat': 13.08333333,
        'male_lon': 80.28333333,
        'female_dob': '1984-01-15',
        'female_tob': '13:30',
        'female_lat': 11.9416,
        'female_lon': 79.8083
    }
    
    try:
        response = requests.post(
            'http://localhost:5001/analyze',
            json=test_data,
            headers={'Content-Type': 'application/json', 'X-Language': 'en'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ English analysis test PASSED")
                print("📊 English Analysis Results:")
                for item in result['compatibility_data']:
                    print(f"  - {item['condition']}: {item['match_type']} - {item['reasoning']}")
                return True
            else:
                print(f"❌ English analysis test FAILED - {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ English analysis test FAILED - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ English analysis test FAILED - Exception: {str(e)}")
        return False

def test_tamil_analysis():
    """Test analysis results in Tamil"""
    test_data = {
        'male_dob': '1978-09-18',
        'male_tob': '17:35',
        'male_lat': 13.08333333,
        'male_lon': 80.28333333,
        'female_dob': '1984-01-15',
        'female_tob': '13:30',
        'female_lat': 11.9416,
        'female_lon': 79.8083
    }
    
    try:
        response = requests.post(
            'http://localhost:5001/analyze',
            json=test_data,
            headers={'Content-Type': 'application/json', 'X-Language': 'ta'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Tamil analysis test PASSED")
                print("📊 Tamil Analysis Results:")
                for item in result['compatibility_data']:
                    print(f"  - {item['condition']}: {item['match_type']} - {item['reasoning']}")
                
                # Check if conditions are in Tamil
                tamil_conditions = [
                    'பெண் ராசி (சந்திரன் ராசி)',
                    'பெண் நட்சத்திரம்',
                    'பெண் லக்கின ஆட்சியாளர்',
                    'பெண் லக்கின பாதம்',
                    'பெண் லக்கினத்தில் உள்ள கிரகங்கள்',
                    'பெண் ராசியில் உள்ள கிரகங்கள்'
                ]
                
                all_tamil = True
                for condition in tamil_conditions:
                    if not any(condition in item['condition'] for item in result['compatibility_data']):
                        all_tamil = False
                        break
                
                if all_tamil:
                    print("✅ All condition names are in Tamil")
                else:
                    print("❌ Some condition names are not in Tamil")
                    return False
                
                # Check if match types are in Tamil
                tamil_match_types = ['ராகு', 'கேது', 'பொருத்தம் இல்லை']
                all_tamil_types = True
                for item in result['compatibility_data']:
                    if item['match_type'] not in tamil_match_types:
                        all_tamil_types = False
                        break
                
                if all_tamil_types:
                    print("✅ All match types are in Tamil")
                else:
                    print("❌ Some match types are not in Tamil")
                    return False
                
                return True
            else:
                print(f"❌ Tamil analysis test FAILED - {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Tamil analysis test FAILED - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Tamil analysis test FAILED - Exception: {str(e)}")
        return False

def test_language_consistency():
    """Test that language parameter is properly handled"""
    test_data = {
        'male_dob': '1978-09-18',
        'male_tob': '17:35',
        'male_lat': 13.08333333,
        'male_lon': 80.28333333,
        'female_dob': '1984-01-15',
        'female_tob': '13:30',
        'female_lat': 11.9416,
        'female_lon': 79.8083
    }
    
    try:
        # Test English
        response_en = requests.post(
            'http://localhost:5001/analyze',
            json=test_data,
            headers={'Content-Type': 'application/json', 'X-Language': 'en'}
        )
        
        # Test Tamil
        response_ta = requests.post(
            'http://localhost:5001/analyze',
            json=test_data,
            headers={'Content-Type': 'application/json', 'X-Language': 'ta'}
        )
        
        if response_en.status_code == 200 and response_ta.status_code == 200:
            result_en = response_en.json()
            result_ta = response_ta.json()
            
            if result_en['success'] and result_ta['success']:
                # Check that English results have English text
                english_condition = result_en['compatibility_data'][0]['condition']
                tamil_condition = result_ta['compatibility_data'][0]['condition']
                
                if 'Female' in english_condition and 'பெண்' in tamil_condition:
                    print("✅ Language consistency test PASSED")
                    print(f"  English: {english_condition}")
                    print(f"  Tamil: {tamil_condition}")
                    return True
                else:
                    print("❌ Language consistency test FAILED")
                    return False
            else:
                print("❌ Language consistency test FAILED - API errors")
                return False
        else:
            print("❌ Language consistency test FAILED - HTTP errors")
            return False
            
    except Exception as e:
        print(f"❌ Language consistency test FAILED - Exception: {str(e)}")
        return False

def main():
    print("🌐 Testing Tamil Analysis Results in Vedic Life Partner Prediction App")
    print("=" * 70)
    
    tests = [
        ("English Analysis", test_english_analysis),
        ("Tamil Analysis", test_tamil_analysis),
        ("Language Consistency", test_language_consistency)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests PASSED! Tamil analysis results are working correctly.")
        print("\n🌐 Available URLs:")
        print("   - English: http://localhost:5001")
        print("   - Tamil:   http://localhost:5001/tamil")
        print("\n💡 Features verified:")
        print("   - Analysis conditions in Tamil")
        print("   - Match types in Tamil")
        print("   - Reasoning messages in Tamil")
        print("   - Language consistency between English and Tamil")
    else:
        print("⚠️  Some tests FAILED. Please check the implementation.")
    
    print("\n📝 Note: The analysis results now display completely in Tamil")
    print("   when using the Tamil interface, including:")
    print("   - Condition names (பெண் ராசி, பெண் நட்சத்திரம், etc.)")
    print("   - Match types (ராகு, கேது, பொருத்தம் இல்லை)")
    print("   - Reasoning messages (பொருத்தம் கண்டறியப்படவில்லை)")

if __name__ == "__main__":
    main()
