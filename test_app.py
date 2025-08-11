#!/usr/bin/env python3
"""
Test script for the enhanced Vedic Life Partner Prediction App
"""

import requests
import json

def test_compatibility_analysis():
    """Test the compatibility analysis with sample data"""
    
    # Test data
    test_data = {
        'male_dob': '1978-09-18',
        'male_tob': '17:35',
        'male_lat': 13.08333333,
        'male_lon': 80.28333333,
        'female_dob': '1982-03-15',
        'female_tob': '08:30',
        'female_lat': 13.08333333,
        'female_lon': 80.28333333
    }
    
    try:
        # Send request to the Flask app
        response = requests.post(
            'http://localhost:5001/analyze',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result['success']:
                print("✅ Test PASSED - Compatibility analysis successful!")
                print(f"📊 Results:")
                print(f"   - Male Rahu: {result['male_rahu_nakshatra']} (Lord: {result['rahu_nakshatra_lord']})")
                print(f"   - Male Ketu: {result['male_ketu_nakshatra']} (Lord: {result['ketu_nakshatra_lord']})")
                print(f"   - Total Matches: {result['total_matches']}")
                print(f"   - Rahu Matches: {len(result['rahu_matches'])}")
                print(f"   - Ketu Matches: {len(result['ketu_matches'])}")
                print(f"   - Verdict: {result['verdict']}")
                
                print(f"\n🔍 Detailed Analysis:")
                for item in result['compatibility_data']:
                    print(f"   - {item['condition']}: {item['value']} | {item['match_type']} | {item['reasoning']}")
                
                if result['rahu_reasoning']:
                    print(f"\n🟢 Rahu Reasoning:")
                    for reason in result['rahu_reasoning']:
                        print(f"   • {reason}")
                
                if result['ketu_reasoning']:
                    print(f"\n🟡 Ketu Reasoning:")
                    for reason in result['ketu_reasoning']:
                        print(f"   • {reason}")
                
            else:
                print(f"❌ Test FAILED - Error: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ Test FAILED - HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Test FAILED - Could not connect to server. Make sure the Flask app is running on port 5001.")
    except Exception as e:
        print(f"❌ Test FAILED - Exception: {str(e)}")

def test_web_interface():
    """Test if the web interface is accessible"""
    try:
        response = requests.get('http://localhost:5001/')
        
        if response.status_code == 200:
            print("✅ Web interface is accessible!")
            if 'Vedic Life Partner Prediction' in response.text:
                print("✅ HTML content is correct!")
            else:
                print("⚠️  HTML content might be incomplete")
        else:
            print(f"❌ Web interface test failed - HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Web interface test failed - Could not connect to server")
    except Exception as e:
        print(f"❌ Web interface test failed - Exception: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Enhanced Vedic Life Partner Prediction App")
    print("=" * 60)
    
    print("\n1. Testing Web Interface...")
    test_web_interface()
    
    print("\n2. Testing Compatibility Analysis...")
    test_compatibility_analysis()
    
    print("\n" + "=" * 60)
    print("🎉 Test completed! Open http://localhost:5001 in your browser to use the app.")
    print("💡 Add ?sample=true to the URL to pre-fill sample data for testing.")
