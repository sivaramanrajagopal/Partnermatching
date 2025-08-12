"""
Vedic Life Partner Prediction App
A Flask web application for astrological compatibility analysis using Vedic astrology principles.
"""

from flask import Flask, render_template, request, jsonify
import swisseph as swe
import datetime
import os
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from translations import get_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# APPLICATION SETUP
# =============================================================================

app = Flask(__name__)

# Configuration Management
try:
    from config import Config
    app.config.from_object(Config)
    logger.info("Configuration loaded from config.py")
except ImportError:
    # Fallback configuration using environment variables
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        'DEBUG': os.environ.get('DEBUG', 'False').lower() == 'true'
    })
    logger.info("Configuration loaded from environment variables")

# =============================================================================
# ASTROLOGICAL DATA CONSTANTS
# =============================================================================

@dataclass
class AstroConstants:
    """Container for astrological constants"""
    
    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]

    NAKSHATRAS_TAMIL = [
        "அசுவினி", "பரணி", "கிருத்திகை", "ரோகிணி", "மிருகசீரிடம்", "ஆருத்ரா",
        "புனர்வசு", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்தரம்",
        "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை",
        "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்",
        "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"
    ]

    RASIS = [
        "Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
        "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"
    ]

    RASIS_TAMIL = [
        "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி",
        "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
    ]

    # Nakshatra lords cycle (9 planets repeated 3 times for 27 nakshatras)
    NAKSHATRA_LORDS = [
        "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
        "Jupiter", "Saturn", "Mercury"
    ] * 3

    # Rasi lords mapping
    RASI_LORDS = {
        "Mesha": "Mars", "Rishaba": "Venus", "Mithuna": "Mercury", "Kataka": "Moon",
        "Simha": "Sun", "Kanni": "Mercury", "Thula": "Venus", "Vrischika": "Mars",
        "Dhanus": "Jupiter", "Makara": "Saturn", "Kumbha": "Saturn", "Meena": "Jupiter"
    }

# Initialize constants
ASTRO = AstroConstants()

# Create mapping dictionaries
NAKSHATRA_MAPPING = dict(zip(ASTRO.NAKSHATRAS, ASTRO.NAKSHATRAS_TAMIL))
RASI_MAPPING = dict(zip(ASTRO.RASIS, ASTRO.RASIS_TAMIL))

# =============================================================================
# SWISS EPHEMERIS INITIALIZATION
# =============================================================================

def initialize_ephemeris():
    """Initialize Swiss Ephemeris with proper error handling"""
    try:
        swe.set_ephe_path('.')
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        logger.info("Swiss Ephemeris initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Swiss Ephemeris: {e}")
        raise

initialize_ephemeris()

# =============================================================================
# CORE ASTROLOGICAL CALCULATION CLASSES
# =============================================================================

@dataclass
class PlanetInfo:
    """Data class for planet information"""
    longitude: float
    retrograde: bool
    rasi: str
    degree_in_sign: float
    nakshatra: str
    nakshatra_index: int
    nakshatra_lord: str
    pada: int

class AstrologyCalculator:
    """Core astrology calculation engine"""
    
    @staticmethod
    def normalize_longitude(longitude: float) -> float:
        """Normalize longitude to 0-360 range"""
        return longitude % 360
    
    @staticmethod
    def get_nakshatra_info(longitude: float) -> Dict[str, Any]:
        """Calculate nakshatra and pada information from longitude"""
        longitude = AstrologyCalculator.normalize_longitude(longitude)
        
        # Calculate nakshatra span (360° / 27 nakshatras)
        nakshatra_span = 360.0 / 27.0
        
        # Calculate nakshatra index
        nakshatra_index = int(longitude // nakshatra_span)
        nakshatra_index = min(nakshatra_index, 26)  # Safety bound
        
        # Calculate position within nakshatra
        nakshatra_position = longitude % nakshatra_span
        
        # Calculate pada (1-4)
        pada = int((nakshatra_position / (nakshatra_span / 4.0)) + 1)
        pada = min(max(pada, 1), 4)  # Ensure pada is 1-4
        
        return {
            'nakshatra': ASTRO.NAKSHATRAS[nakshatra_index],
            'nakshatra_index': nakshatra_index,
            'nakshatra_lord': ASTRO.NAKSHATRA_LORDS[nakshatra_index],
            'pada': pada
        }
    
    @staticmethod
    def get_planet_info(longitude: float, speed: Optional[float] = None) -> PlanetInfo:
        """Get comprehensive planet information"""
        longitude = AstrologyCalculator.normalize_longitude(longitude)
        nakshatra_info = AstrologyCalculator.get_nakshatra_info(longitude)
        
        return PlanetInfo(
            longitude=longitude,
            retrograde=speed < 0 if speed is not None else False,
            rasi=ASTRO.RASIS[int(longitude // 30)],
            degree_in_sign=longitude % 30,
            **nakshatra_info
        )
    
    @staticmethod
    def get_house_number(planet_longitude: float, asc_longitude: float) -> int:
        """Calculate house number from planet and ascendant longitudes"""
        lagna_rasi = int(asc_longitude // 30)
        planet_rasi = int(planet_longitude // 30)
        return (planet_rasi - lagna_rasi) % 12 + 1
    
    @staticmethod
    def calculate_planetary_positions(jd: float, lat: float, lon: float) -> Tuple[Dict[str, PlanetInfo], float, List[float]]:
        """Calculate all planetary positions for a given time and location"""
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        results = {}
        
        try:
            # Calculate regular planets (0-9, excluding mean Node)
            for planet_id in range(10):
                name = swe.get_planet_name(planet_id)
                
                if name == "mean Node":
                    continue
                
                lonlat = swe.calc_ut(jd, planet_id, flags)[0]
                results[name] = AstrologyCalculator.get_planet_info(lonlat[0], lonlat[3])
            
            # Calculate Rahu (Mean Node)
            rahu_lonlat = swe.calc_ut(jd, swe.MEAN_NODE, flags)[0]
            rahu_longitude = rahu_lonlat[0]
            
            results['Rahu'] = AstrologyCalculator.get_planet_info(rahu_longitude, rahu_lonlat[3])
            results['Rahu'].retrograde = True  # Rahu is always retrograde
            
            # Calculate Ketu (180° opposite to Rahu)
            ketu_longitude = (rahu_longitude + 180.0) % 360.0
            results['Ketu'] = AstrologyCalculator.get_planet_info(ketu_longitude, rahu_lonlat[3])
            results['Ketu'].retrograde = True  # Ketu is always retrograde
            
            # Calculate Ascendant
            cusps, ascmc = swe.houses_ex(jd, lat, lon, b'O', flags=flags)
            results['Ascendant'] = AstrologyCalculator.get_planet_info(ascmc[0])
            
            return results, ascmc[0], cusps
            
        except Exception as e:
            logger.error(f"Error calculating planetary positions: {e}")
            raise

# =============================================================================
# COMPATIBILITY ANALYSIS ENGINE
# =============================================================================

class CompatibilityAnalyzer:
    """Life partner compatibility analysis engine"""
    
    @staticmethod
    def get_planets_in_rasi(chart_data: Dict[str, PlanetInfo], target_rasi: str) -> List[str]:
        """Get all planets in a specific rasi"""
        return [
            planet for planet, info in chart_data.items()
            if planet != 'Ascendant' and info.rasi == target_rasi
        ]
    
    @staticmethod
    def get_planets_in_house(chart_data: Dict[str, PlanetInfo], asc_longitude: float, house_number: int) -> List[str]:
        """Get all planets in a specific house"""
        planets = []
        for planet, info in chart_data.items():
            if planet != 'Ascendant':
                house = AstrologyCalculator.get_house_number(info.longitude, asc_longitude)
                if house == house_number:
                    planets.append(planet)
        return planets
    
    @staticmethod
    def analyze_compatibility(
        male_chart: Dict[str, PlanetInfo], 
        female_chart: Dict[str, PlanetInfo],
        male_asc: float, 
        female_asc: float, 
        lang: str = 'en'
    ) -> Dict[str, Any]:
        """Perform comprehensive compatibility analysis"""
        
        # Extract key information
        male_rahu = male_chart['Rahu']
        male_ketu = male_chart['Ketu']
        female_moon = female_chart['Moon']
        female_asc_info = female_chart['Ascendant']
        
        # Get nakshatra lords
        rahu_lord = male_rahu.nakshatra_lord
        ketu_lord = male_ketu.nakshatra_lord
        
        # Female chart analysis points
        female_moon_rasi_lord = ASTRO.RASI_LORDS[female_moon.rasi]
        female_lagna_lord = ASTRO.RASI_LORDS[female_asc_info.rasi]
        
        # Get planets in specific positions
        planets_in_lagna = CompatibilityAnalyzer.get_planets_in_house(female_chart, female_asc, 1)
        planets_in_rasi = CompatibilityAnalyzer.get_planets_in_rasi(female_chart, female_moon.rasi)
        
        # Analyze matches
        rahu_matches, rahu_reasoning = CompatibilityAnalyzer._check_matches(
            rahu_lord, female_chart, female_moon_rasi_lord, female_lagna_lord,
            planets_in_lagna, planets_in_rasi, 'rahu', lang
        )
        
        ketu_matches, ketu_reasoning = CompatibilityAnalyzer._check_matches(
            ketu_lord, female_chart, female_moon_rasi_lord, female_lagna_lord,
            planets_in_lagna, planets_in_rasi, 'ketu', lang
        )
        
        # Prepare detailed conditions
        conditions = CompatibilityAnalyzer._prepare_conditions(
            female_chart, female_asc_info, planets_in_lagna, planets_in_rasi, lang
        )
        
        return {
            'male_rahu': male_rahu,
            'male_ketu': male_ketu,
            'male_rahu_nakshatra': CompatibilityAnalyzer._translate_nakshatra(male_rahu.nakshatra, lang),
            'male_ketu_nakshatra': CompatibilityAnalyzer._translate_nakshatra(male_ketu.nakshatra, lang),
            'rahu_nakshatra_lord': rahu_lord,
            'ketu_nakshatra_lord': ketu_lord,
            'conditions': conditions,
            'rahu_matches': rahu_matches,
            'ketu_matches': ketu_matches,
            'rahu_reasoning': rahu_reasoning,
            'ketu_reasoning': ketu_reasoning,
            'total_matches': len(rahu_matches) + len(ketu_matches),
            'primary_match_type': 'Rahu' if rahu_matches else 'Ketu' if ketu_matches else 'None'
        }
    
    @staticmethod
    def _check_matches(lord: str, female_chart: Dict[str, PlanetInfo], 
                      moon_rasi_lord: str, lagna_lord: str,
                      planets_in_lagna: List[str], planets_in_rasi: List[str],
                      node_type: str, lang: str) -> Tuple[List[str], List[str]]:
        """Check matches for a specific node (Rahu/Ketu)"""
        matches = []
        reasoning = []
        
        node_text = get_text(f'{node_type}_lord', lang)
        
        # Check various compatibility conditions
        if lord == moon_rasi_lord:
            matches.append(get_text('female_rasi_moon_sign', lang))
            reasoning.append(f"{node_text} {lord} = {get_text('female_moon_sign_lord', lang)} {moon_rasi_lord}")
        
        if lord == female_chart['Moon'].nakshatra_lord:
            matches.append(get_text('female_nakshatra', lang))
            reasoning.append(f"{node_text} {lord} = {get_text('female_moon_nakshatra_lord', lang)} {female_chart['Moon'].nakshatra_lord}")
        
        if lord == lagna_lord:
            matches.append(get_text('female_lagna_lord', lang))
            reasoning.append(f"{node_text} {lord} = {get_text('female_lagna_lord_match', lang)} {lagna_lord}")
        
        if lord in planets_in_lagna:
            matches.append(get_text('planets_in_female_lagna', lang))
            reasoning.append(f"{node_text} {lord} {get_text('present_in_female_lagna', lang)}")
        
        if lord in planets_in_rasi:
            matches.append(get_text('planets_in_female_rasi', lang))
            reasoning.append(f"{node_text} {lord} {get_text('present_in_female_moon_sign', lang)}")
        
        return matches, reasoning
    
    @staticmethod
    def _prepare_conditions(female_chart: Dict[str, PlanetInfo], asc_info: PlanetInfo,
                          planets_in_lagna: List[str], planets_in_rasi: List[str],
                          lang: str) -> Dict[str, Dict[str, Any]]:
        """Prepare detailed condition information"""
        moon = female_chart['Moon']
        
        return {
            get_text('female_rasi_moon_sign', lang): {
                'value': CompatibilityAnalyzer._translate_rasi(moon.rasi, lang),
                'details': f"{moon.longitude:.2f}° in {CompatibilityAnalyzer._translate_rasi(moon.rasi, lang)}",
                'lord': ASTRO.RASI_LORDS.get(moon.rasi),
                'nakshatra_lord': moon.nakshatra_lord
            },
            get_text('female_nakshatra', lang): {
                'value': CompatibilityAnalyzer._translate_nakshatra(moon.nakshatra, lang),
                'details': f"{CompatibilityAnalyzer._translate_nakshatra(moon.nakshatra, lang)} Pada {moon.pada}",
                'lord': moon.nakshatra_lord,
                'nakshatra_lord': moon.nakshatra_lord
            },
            get_text('female_lagna_lord', lang): {
                'value': ASTRO.RASI_LORDS[asc_info.rasi],
                'details': f"Lagna: {asc_info.longitude:.2f}° in {CompatibilityAnalyzer._translate_rasi(asc_info.rasi, lang)}",
                'lord': ASTRO.RASI_LORDS[asc_info.rasi],
                'nakshatra_lord': None
            },
            get_text('female_lagna_pada', lang): {
                'value': f"Pada {asc_info.pada}",
                'details': f"Ascendant Pada {asc_info.pada} in {CompatibilityAnalyzer._translate_nakshatra(asc_info.nakshatra, lang)}",
                'lord': None,
                'nakshatra_lord': None
            },
            get_text('planets_in_female_lagna', lang): {
                'value': planets_in_lagna,
                'details': ", ".join([f"{p} ({female_chart[p].longitude:.1f}°)" for p in planets_in_lagna]) if planets_in_lagna else get_text('none', lang),
                'lord': planets_in_lagna,
                'nakshatra_lord': None
            },
            get_text('planets_in_female_rasi', lang): {
                'value': planets_in_rasi,
                'details': ", ".join([f"{p} ({female_chart[p].longitude:.1f}°)" for p in planets_in_rasi]) if planets_in_rasi else get_text('none', lang),
                'lord': planets_in_rasi,
                'nakshatra_lord': None
            }
        }
    
    @staticmethod
    def _translate_nakshatra(nakshatra: str, lang: str) -> str:
        """Translate nakshatra name based on language"""
        if lang == 'ta' and nakshatra in NAKSHATRA_MAPPING:
            return NAKSHATRA_MAPPING[nakshatra]
        return nakshatra
    
    @staticmethod
    def _translate_rasi(rasi: str, lang: str) -> str:
        """Translate rasi name based on language"""
        if lang == 'ta' and rasi in RASI_MAPPING:
            return RASI_MAPPING[rasi]
        return rasi

# =============================================================================
# CHART CREATION SERVICE
# =============================================================================

class ChartService:
    """Service for creating birth charts"""
    
    @staticmethod
    def create_birth_chart(dob: str, tob: str, lat: float, lon: float, tz_offset: float = 5.5) -> Tuple[Dict[str, PlanetInfo], float]:
        """Create birth chart from birth details"""
        try:
            # Parse date and time
            local_dt = datetime.datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
            
            # Convert to UTC
            utc_dt = local_dt - datetime.timedelta(hours=tz_offset)
            
            # Calculate Julian Day
            jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)
            
            # Calculate planetary positions
            planet_data, asc_deg, _ = AstrologyCalculator.calculate_planetary_positions(jd, lat, lon)
            
            logger.info(f"Birth chart created successfully for {dob} {tob}")
            return planet_data, asc_deg
            
        except Exception as e:
            logger.error(f"Error creating birth chart: {e}")
            raise

# =============================================================================
# FLASK ROUTES
# =============================================================================

@app.route('/')
def index():
    """Home page - English"""
    return render_template('index.html', lang='en', get_text=get_text)

@app.route('/tamil')
def index_tamil():
    """Home page - Tamil"""
    return render_template('index.html', lang='ta', get_text=get_text)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint"""
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        lang = request.headers.get('X-Language', 'en')
        
        # Validate and extract data
        required_fields = ['male_dob', 'male_tob', 'male_lat', 'male_lon',
                          'female_dob', 'female_tob', 'female_lat', 'female_lon']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Extract and validate coordinates
        try:
            male_lat = float(data['male_lat'])
            male_lon = float(data['male_lon'])
            female_lat = float(data['female_lat'])
            female_lon = float(data['female_lon'])
            male_tz_offset = float(data.get('male_tz_offset', 5.5))
            female_tz_offset = float(data.get('female_tz_offset', 5.5))
        except (ValueError, TypeError) as e:
            return jsonify({'success': False, 'error': f'Invalid coordinate data: {e}'}), 400
        
        # Create birth charts
        male_chart, male_asc = ChartService.create_birth_chart(
            data['male_dob'], data['male_tob'], male_lat, male_lon, male_tz_offset
        )
        
        female_chart, female_asc = ChartService.create_birth_chart(
            data['female_dob'], data['female_tob'], female_lat, female_lon, female_tz_offset
        )
        
        # Perform compatibility analysis
        analysis_result = CompatibilityAnalyzer.analyze_compatibility(
            male_chart, female_chart, male_asc, female_asc, lang
        )
        
        # Prepare compatibility data for frontend
        compatibility_data = _prepare_frontend_data(analysis_result, lang)
        
        # Determine verdict
        verdict_info = _determine_verdict(analysis_result['total_matches'], lang)
        
        # Prepare response
        response = {
            'success': True,
            **analysis_result,
            'compatibility_data': compatibility_data,
            **verdict_info
        }
        
        logger.info(f"Analysis completed successfully. Total matches: {analysis_result['total_matches']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'static_files': {
            'css_exists': os.path.exists('static/css/style.css'),
            'js_exists': os.path.exists('static/js/script.js')
        },
        'ephemeris_initialized': True
    })

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _prepare_frontend_data(analysis_result: Dict[str, Any], lang: str) -> List[Dict[str, Any]]:
    """Prepare compatibility data for frontend display"""
    compatibility_data = []
    conditions = analysis_result['conditions']
    rahu_matches = analysis_result['rahu_matches']
    ketu_matches = analysis_result['ketu_matches']
    rahu_reasoning = analysis_result['rahu_reasoning']
    ketu_reasoning = analysis_result['ketu_reasoning']
    
    condition_mapping = {
        'female_rasi_moon_sign': get_text('female_rasi_moon_sign', lang),
        'female_nakshatra': get_text('female_nakshatra', lang),
        'female_lagna_lord': get_text('female_lagna_lord', lang),
        'female_lagna_pada': get_text('female_lagna_pada', lang),
        'planets_in_female_lagna': get_text('planets_in_female_lagna', lang),
        'planets_in_female_rasi': get_text('planets_in_female_rasi', lang)
    }
    
    for condition_key, details in conditions.items():
        condition_name = condition_mapping.get(condition_key, condition_key)
        
        rahu_match = condition_name in rahu_matches
        ketu_match = condition_name in ketu_matches
        match_type = (get_text('rahu_match', lang) if rahu_match 
                     else get_text('ketu_match', lang) if ketu_match 
                     else get_text('no_match_type', lang))
        
        # Find reasoning
        reasoning = get_text('no_match_found', lang)
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
        
        compatibility_data.append({
            'condition': condition_name,
            'value': details['details'],
            'match_type': match_type,
            'status': 'match' if (rahu_match or ketu_match) else 'no_match',
            'reasoning': reasoning
        })
    
    return compatibility_data

def _determine_verdict(total_matches: int, lang: str) -> Dict[str, str]:
    """Determine compatibility verdict based on matches"""
    if total_matches >= 3:
        return {
            'verdict': get_text('highly_compatible', lang),
            'verdict_class': 'high',
            'message': get_text('high_message', lang)
        }
    elif total_matches >= 1:
        return {
            'verdict': get_text('moderately_compatible', lang),
            'verdict_class': 'moderate',
            'message': get_text('moderate_message', lang)
        }
    else:
        return {
            'verdict': get_text('low_compatibility', lang),
            'verdict_class': 'low',
            'message': get_text('low_message', lang)
        }

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = app.config.get('DEBUG', False)
    
    logger.info(f"Starting application on port {port} with debug={debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)