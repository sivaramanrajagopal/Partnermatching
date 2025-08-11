# Partner Prediction App

A Flask-based web application for astrological partner compatibility analysis using Swiss Ephemeris. The app provides detailed compatibility predictions based on birth charts, supporting both English and Tamil languages.

## Features

- **Astrological Compatibility Analysis**: Uses Swiss Ephemeris for accurate planetary positions
- **Bilingual Support**: Full English and Tamil language interface
- **Detailed Reports**: Comprehensive compatibility analysis with multiple factors
- **Responsive Design**: Modern, mobile-friendly UI
- **Real-time Calculations**: Instant compatibility predictions

## Technology Stack

- **Backend**: Flask (Python)
- **Astrological Calculations**: Swiss Ephemeris (swisseph)
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with modern design
- **Deployment**: Render-ready with gunicorn

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/sivaramanrajagopal/Partnermatching.git
   cd Partnermatching
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export SECRET_KEY="your-secret-key-here"
   export DEBUG="True"
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - English version: http://127.0.0.1:5001
   - Tamil version: http://127.0.0.1:5001/tamil

## Deployment on Render

### Automatic Deployment

1. **Connect your GitHub repository** to Render
2. **Create a new Web Service** using the repository
3. **Configure environment variables**:
   - `SECRET_KEY`: Generate a secure secret key
   - `DEBUG`: Set to `false` for production
   - `GOOGLE_MAPS_API_KEY`: (Optional) For future location features

### Manual Deployment

1. **Push your code** to the GitHub repository
2. **Create a new Web Service** on Render
3. **Use the following settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3.9

## Usage

### Input Requirements

For each partner, provide:
- **Date of Birth**: Exact birth date
- **Time of Birth**: Precise birth time (24-hour format)
- **Latitude**: Birth location latitude (decimal degrees)
- **Longitude**: Birth location longitude (decimal degrees)

### Example Coordinates

- **Chennai, India**: 13.0833°N, 80.2833°E
- **Mumbai, India**: 19.0760°N, 72.8777°E
- **Delhi, India**: 28.7041°N, 77.1025°E

### Analysis Results

The app provides:
- **Compatibility Score**: Overall compatibility percentage
- **Planetary Positions**: Detailed planetary positions for both partners
- **Nakshatra Analysis**: Birth star compatibility
- **Rasi Analysis**: Moon sign compatibility
- **Detailed Reasoning**: Explanations for each compatibility factor

## Project Structure

```
Partner Prediction App/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── translations.py       # Bilingual text translations
├── requirements.txt      # Python dependencies
├── render.yaml          # Render deployment configuration
├── static/
│   ├── css/
│   │   └── style.css    # Application styling
│   └── js/
│       └── script.js    # Frontend JavaScript
├── templates/
│   └── index.html       # Main application template
└── tests/
    ├── test_app.py      # Application tests
    ├── test_languages.py # Language functionality tests
    └── test_tamil_analysis.py # Tamil analysis tests
```

## API Endpoints

- `GET /` - English version of the application
- `GET /tamil` - Tamil version of the application
- `POST /analyze` - Compatibility analysis API

### API Request Format

```json
{
  "male_dob": "1990-01-01",
  "male_tob": "14:30",
  "male_lat": 13.0833,
  "male_lon": 80.2833,
  "female_dob": "1992-05-15",
  "female_tob": "16:45",
  "female_lat": 19.0760,
  "female_lon": 72.8777
}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Swiss Ephemeris**: For accurate astrological calculations
- **Flask**: For the web framework
- **Render**: For hosting infrastructure

## Support

For support and questions, please open an issue on GitHub or contact the maintainer.

---

**Note**: This application is for entertainment and educational purposes. Astrological predictions should not be considered as definitive advice for life decisions.
