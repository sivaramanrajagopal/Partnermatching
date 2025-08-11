from flask import Flask, render_template, request, jsonify
import swisseph as swe
import datetime
from collections import OrderedDict
import pandas as pd
import json
from translations import get_text
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Your existing data structures
nakshatras = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Tamil nakshatra names
nakshatras_tamil = [
    "அசுவினி", "பரணி", "கிருத்திகை", "ரோகிணி", "மிருகசீரிடம்", "ஆருத்ரா",
    "புனர்வசு", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்தரம்",
    "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை",
    "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்",
    "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"
]

# Nakshatra name mapping
nakshatra_mapping = dict(zip(nakshatras, nakshatras_tamil))

rasis = [
    "Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
    "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"
]

# Tamil rasi names
rasis_tamil = [
    "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி",
    "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
]

# Rasi name mapping
rasi_mapping = dict(zip(rasis, rasis_tamil))

# Nakshatra lords mapping
nakshatra_lords = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury"
] * 3

# Rasi lords mapping
rasi_lords = {
    "Mesha": "Mars", "Rishaba": "Venus", "Mithuna": "Mercury", "Kataka": "Moon",
    "Simha": "Sun", "Kanni": "Mercury", "Thula": "Venus", "Vrischika": "Mars",
    "Dhanus": "Jupiter", "Makara": "Saturn", "Kumbha": "Saturn", "Meena": "Jupiter"
}

swe.set_ephe_path('.')
swe.set_sid_mode(swe.SIDM_LAHIRI)

def get_chart_info(longitude, speed=None):
    return {
        'longitude': longitude,
        'retrograde': speed < 0 if speed is not None else None,
        'rasi': rasis[int(longitude // 30)],
        'nakshatra': nakshatras[int((longitude % 360) // (360 / 27))],
        'pada': int(((longitude % (360 / 27)) / (360 / 27 / 4)) + 1)
    }

def get_house_from_longitude(longitude, asc_deg):
    lagna_rasi = int(asc_deg // 30)
    planet_rasi = int(longitude // 30)
    house = (planet_rasi - lagna_rasi) % 12 + 1
    return house

def get_planet_positions(jd, lat, lon):
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    results = {}
    swe.set_topo(lon, lat, 0)

    # Get regular planets
    for pid in range(10):
        name = swe.get_planet_name(pid)
        lonlat = swe.calc_ut(jd, pid, flags)[0]
        results[name] = get_chart_info(lonlat[0], lonlat[3])

    # Get Rahu and Ketu
    rahu = swe.calc_ut(jd, swe.TRUE_NODE, flags)[0]
    results['Rahu'] = get_chart_info(rahu[0], rahu[3])
    ketu_lon = (rahu[0] + 180.0) % 360.0
    ketu_info = get_chart_info(ketu_lon, rahu[3])
    ketu_info['retrograde'] = True
    results['Ketu'] = ketu_info

    # Get Ascendant
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'O', flags=flags)
    results['Ascendant'] = get_chart_info(ascmc[0])

    return results, ascmc[0], cusps

def get_nakshatra_lord(nakshatra_name):
    """Get the lord of a nakshatra"""
    if nakshatra_name in nakshatras:
        index = nakshatras.index(nakshatra_name)
        return nakshatra_lords[index]
    return None

def translate_nakshatra_name(nakshatra_name, lang='en'):
    """Translate nakshatra name based on language"""
    if lang == 'ta' and nakshatra_name in nakshatra_mapping:
        return nakshatra_mapping[nakshatra_name]
    return nakshatra_name

def translate_rasi_name(rasi_name, lang='en'):
    """Translate rasi name based on language"""
    if lang == 'ta' and rasi_name in rasi_mapping:
        return rasi_mapping[rasi_name]
    return rasi_name

def get_planets_in_rasi(planet_data, target_rasi):
    """Get all planets placed in a specific rasi"""
    planets_in_rasi = []
    for planet, info in planet_data.items():
        if planet != 'Ascendant' and info['rasi'] == target_rasi:
            planets_in_rasi.append(planet)
    return planets_in_rasi

def get_planets_in_house(planet_data, asc_deg, house_number):
    """Get all planets placed in a specific house"""
    planets_in_house = []
    for planet, info in planet_data.items():
        if planet != 'Ascendant':
            planet_house = get_house_from_longitude(info['longitude'], asc_deg)
            if planet_house == house_number:
                planets_in_house.append(planet)
    return planets_in_house

def life_partner_prediction(male_chart_data, female_chart_data, male_asc, female_asc, lang='en'):
    """
    Main function for life partner prediction based on Rahu-Ketu compatibility
    """
    # Extract male Rahu and Ketu details
    male_rahu = male_chart_data['Rahu']
    male_ketu = male_chart_data['Ketu']
    
    # Get Nakshatra lords for Rahu and Ketu
    rahu_nakshatra_lord = get_nakshatra_lord(male_rahu['nakshatra'])
    ketu_nakshatra_lord = get_nakshatra_lord(male_ketu['nakshatra'])
    
    # Female chart analysis
    female_moon = female_chart_data['Moon']
    female_moon_rasi = female_moon['rasi']
    female_moon_nakshatra = female_moon['nakshatra']
    female_lagna_rasi = female_chart_data['Ascendant']['rasi']
    female_lagna_lord = rasi_lords[female_lagna_rasi]
    female_lagna_pada = female_chart_data['Ascendant']['pada']
    
    # Get planets in female's lagna (1st house) and rasi (moon sign house)
    planets_in_female_lagna = get_planets_in_house(female_chart_data, female_asc, 1)
    planets_in_female_rasi = get_planets_in_rasi(female_chart_data, female_moon_rasi)
    
    # Detailed conditions with degrees and full info
    conditions = {
        get_text('female_rasi_moon_sign', lang): {
            'value': translate_rasi_name(female_moon_rasi, lang),
            'details': f"{female_moon['longitude']:.2f}° in {translate_rasi_name(female_moon_rasi, lang)}",
            'lord': rasi_lords.get(female_moon_rasi),
            'nakshatra_lord': get_nakshatra_lord(female_moon_nakshatra)
        },
        get_text('female_nakshatra', lang): {
            'value': translate_nakshatra_name(female_moon_nakshatra, lang),
            'details': f"{translate_nakshatra_name(female_moon_nakshatra, lang)} Pada {female_moon['pada']}",
            'lord': get_nakshatra_lord(female_moon_nakshatra),
            'nakshatra_lord': get_nakshatra_lord(female_moon_nakshatra)
        },
        get_text('female_lagna_lord', lang): {
            'value': female_lagna_lord,
            'details': f"Lagna: {female_chart_data['Ascendant']['longitude']:.2f}° in {translate_rasi_name(female_lagna_rasi, lang)}",
            'lord': female_lagna_lord,
            'nakshatra_lord': None
        },
        get_text('female_lagna_pada', lang): {
            'value': f"Pada {female_lagna_pada}",
            'details': f"Ascendant Pada {female_lagna_pada} in {translate_nakshatra_name(female_chart_data['Ascendant']['nakshatra'], lang)}",
            'lord': None,
            'nakshatra_lord': None
        },
        get_text('planets_in_female_lagna', lang): {
            'value': planets_in_female_lagna,
            'details': ", ".join([f"{p} ({female_chart_data[p]['longitude']:.1f}°)" for p in planets_in_female_lagna]) if planets_in_female_lagna else get_text('none', lang),
            'lord': planets_in_female_lagna,
            'nakshatra_lord': None
        },
        get_text('planets_in_female_rasi', lang): {
            'value': planets_in_female_rasi,
            'details': ", ".join([f"{p} ({female_chart_data[p]['longitude']:.1f}°)" for p in planets_in_female_rasi]) if planets_in_female_rasi else get_text('none', lang),
            'lord': planets_in_female_rasi,
            'nakshatra_lord': None
        }
    }
    
    # Check matches with Rahu Nakshatra Lord (Primary)
    rahu_matches = []
    rahu_reasoning = []
    
    # Check Rasi lord match
    if rahu_nakshatra_lord == rasi_lords.get(female_moon_rasi):
        rahu_matches.append(get_text('female_rasi_moon_sign', lang))
        rahu_reasoning.append(f"{get_text('rahu_lord', lang)} {rahu_nakshatra_lord} = {get_text('female_moon_sign_lord', lang)} {rasi_lords.get(female_moon_rasi)}")
    
    # Check Nakshatra lord match
    if rahu_nakshatra_lord == get_nakshatra_lord(female_moon_nakshatra):
        rahu_matches.append(get_text('female_nakshatra', lang))
        rahu_reasoning.append(f"{get_text('rahu_lord', lang)} {rahu_nakshatra_lord} = {get_text('female_moon_nakshatra_lord', lang)} {get_nakshatra_lord(female_moon_nakshatra)}")
    
    # Check Lagna lord match
    if rahu_nakshatra_lord == female_lagna_lord:
        rahu_matches.append(get_text('female_lagna_lord', lang))
        rahu_reasoning.append(f"{get_text('rahu_lord', lang)} {rahu_nakshatra_lord} = {get_text('female_lagna_lord_match', lang)} {female_lagna_lord}")
    
    # Check planets in lagna
    if rahu_nakshatra_lord in planets_in_female_lagna:
        rahu_matches.append(get_text('planets_in_female_lagna', lang))
        rahu_reasoning.append(f"{get_text('rahu_lord', lang)} {rahu_nakshatra_lord} {get_text('present_in_female_lagna', lang)}")
    
    # Check planets in rasi
    if rahu_nakshatra_lord in planets_in_female_rasi:
        rahu_matches.append(get_text('planets_in_female_rasi', lang))
        rahu_reasoning.append(f"{get_text('rahu_lord', lang)} {rahu_nakshatra_lord} {get_text('present_in_female_moon_sign', lang)}")
    
    # Check matches with Ketu Nakshatra Lord (Secondary)
    ketu_matches = []
    ketu_reasoning = []
    
    # Always check Ketu matches (not just when Rahu fails)
    # Check Rasi lord match
    if ketu_nakshatra_lord == rasi_lords.get(female_moon_rasi):
        ketu_matches.append(get_text('female_rasi_moon_sign', lang))
        ketu_reasoning.append(f"{get_text('ketu_lord', lang)} {ketu_nakshatra_lord} = {get_text('female_moon_sign_lord', lang)} {rasi_lords.get(female_moon_rasi)}")
    
    # Check Nakshatra lord match
    if ketu_nakshatra_lord == get_nakshatra_lord(female_moon_nakshatra):
        ketu_matches.append(get_text('female_nakshatra', lang))
        ketu_reasoning.append(f"{get_text('ketu_lord', lang)} {ketu_nakshatra_lord} = {get_text('female_moon_nakshatra_lord', lang)} {get_nakshatra_lord(female_moon_nakshatra)}")
    
    # Check Lagna lord match
    if ketu_nakshatra_lord == female_lagna_lord:
        ketu_matches.append(get_text('female_lagna_lord', lang))
        ketu_reasoning.append(f"{get_text('ketu_lord', lang)} {ketu_nakshatra_lord} = {get_text('female_lagna_lord_match', lang)} {female_lagna_lord}")
    
    # Check planets in lagna
    if ketu_nakshatra_lord in planets_in_female_lagna:
        ketu_matches.append(get_text('planets_in_female_lagna', lang))
        ketu_reasoning.append(f"{get_text('ketu_lord', lang)} {ketu_nakshatra_lord} {get_text('present_in_female_lagna', lang)}")
    
    # Check planets in rasi
    if ketu_nakshatra_lord in planets_in_female_rasi:
        ketu_matches.append(get_text('planets_in_female_rasi', lang))
        ketu_reasoning.append(f"{get_text('ketu_lord', lang)} {ketu_nakshatra_lord} {get_text('present_in_female_moon_sign', lang)}")
    
    return {
        'male_rahu': male_rahu,
        'male_ketu': male_ketu,
        'male_rahu_nakshatra': translate_nakshatra_name(male_rahu['nakshatra'], lang),
        'male_ketu_nakshatra': translate_nakshatra_name(male_ketu['nakshatra'], lang),
        'rahu_nakshatra_lord': rahu_nakshatra_lord,
        'ketu_nakshatra_lord': ketu_nakshatra_lord,
        'conditions': conditions,
        'rahu_matches': rahu_matches,
        'ketu_matches': ketu_matches,
        'rahu_reasoning': rahu_reasoning,
        'ketu_reasoning': ketu_reasoning,
        'total_matches': len(rahu_matches) + len(ketu_matches),
        'primary_match_type': 'Rahu' if rahu_matches else 'Ketu' if ketu_matches else 'None'
    }

def create_birth_chart(dob, tob, lat, lon, tz_offset=5.5):
    """Create birth chart from birth details"""
    local_dt = datetime.datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    utc_dt = local_dt - datetime.timedelta(hours=tz_offset)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)

    planet_data, asc_deg, cusps = get_planet_positions(jd, lat, lon)
    return planet_data, asc_deg

@app.route('/')
def index():
    return render_template('index.html', lang='en', get_text=get_text)

@app.route('/tamil')
def index_tamil():
    return render_template('index.html', lang='ta', get_text=get_text)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        
        # Get language from request headers or default to English
        lang = request.headers.get('X-Language', 'en')
        
        # Extract male data
        male_dob = data['male_dob']
        male_tob = data['male_tob']
        male_lat = float(data['male_lat'])
        male_lon = float(data['male_lon'])
        
        # Extract female data
        female_dob = data['female_dob']
        female_tob = data['female_tob']
        female_lat = float(data['female_lat'])
        female_lon = float(data['female_lon'])
        
        # Generate charts
        male_chart, male_asc = create_birth_chart(male_dob, male_tob, male_lat, male_lon)
        female_chart, female_asc = create_birth_chart(female_dob, female_tob, female_lat, female_lon)
        
        # Run compatibility analysis
        result = life_partner_prediction(male_chart, female_chart, male_asc, female_asc, lang)
        
        # Prepare data for frontend
        compatibility_data = []
        conditions = result['conditions']
        rahu_matches = result['rahu_matches']
        ketu_matches = result['ketu_matches']
        rahu_reasoning = result['rahu_reasoning']
        ketu_reasoning = result['ketu_reasoning']
        
        # Create a mapping for condition names based on language
        condition_mapping = {
            'female_rasi_moon_sign': get_text('female_rasi_moon_sign', lang),
            'female_nakshatra': get_text('female_nakshatra', lang),
            'female_lagna_lord': get_text('female_lagna_lord', lang),
            'female_lagna_pada': get_text('female_lagna_pada', lang),
            'planets_in_female_lagna': get_text('planets_in_female_lagna', lang),
            'planets_in_female_rasi': get_text('planets_in_female_rasi', lang)
        }
        
        # Get the correct condition name based on language
        for condition_key, details in conditions.items():
            # Map the condition key to the correct language
            condition_name = condition_mapping.get(condition_key, condition_key)
            
            rahu_match = condition_name in rahu_matches
            ketu_match = condition_name in ketu_matches
            match_type = get_text('rahu_match', lang) if rahu_match else get_text('ketu_match', lang) if ketu_match else get_text('no_match_type', lang)
            
            # Get reasoning for this condition
            reasoning = ""
            if rahu_match:
                for reason in rahu_reasoning:
                    if any(keyword in reason.lower() for keyword in condition_name.lower().split()):
                        reasoning = f"🟢 {reason}"
                        break
            elif ketu_match:
                for reason in ketu_reasoning:
                    if any(keyword in reason.lower() for keyword in condition_name.lower().split()):
                        reasoning = f"🟡 {reason}"
                        break
            else:
                reasoning = get_text('no_match_found', lang)
            
            compatibility_data.append({
                'condition': condition_name,
                'value': details['details'],
                'match_type': match_type,
                'status': 'match' if (rahu_match or ketu_match) else 'no_match',
                'reasoning': reasoning
            })
        
        # Determine compatibility verdict
        if result['total_matches'] >= 3:
            verdict = get_text('highly_compatible', lang)
            verdict_class = "high"
            message = get_text('high_message', lang)
        elif result['total_matches'] >= 1:
            verdict = get_text('moderately_compatible', lang)
            verdict_class = "moderate"
            message = get_text('moderate_message', lang)
        else:
            verdict = get_text('low_compatibility', lang)
            verdict_class = "low"
            message = get_text('low_message', lang)
        
        response = {
            'success': True,
            'male_rahu': result['male_rahu'],
            'male_ketu': result['male_ketu'],
            'male_rahu_nakshatra': result['male_rahu_nakshatra'],
            'male_ketu_nakshatra': result['male_ketu_nakshatra'],
            'rahu_nakshatra_lord': result['rahu_nakshatra_lord'],
            'ketu_nakshatra_lord': result['ketu_nakshatra_lord'],
            'total_matches': result['total_matches'],
            'primary_match_type': result['primary_match_type'],
            'rahu_matches': result['rahu_matches'],
            'ketu_matches': result['ketu_matches'],
            'rahu_reasoning': result['rahu_reasoning'],
            'ketu_reasoning': result['ketu_reasoning'],
            'compatibility_data': compatibility_data,
            'verdict': verdict,
            'verdict_class': verdict_class,
            'message': message
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
