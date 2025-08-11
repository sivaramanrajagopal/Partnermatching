# Google Maps API Setup Guide

This guide will help you set up Google Maps API integration for the Partner Prediction app.

## 🔑 Getting a Google Maps API Key

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable billing for your project (required for API usage)

### Step 2: Enable Required APIs
1. Go to the [APIs & Services > Library](https://console.cloud.google.com/apis/library)
2. Search for and enable these APIs:
   - **Places API** - For location search and autocomplete
   - **Maps JavaScript API** - For map functionality
   - **Geocoding API** - For coordinate conversion

### Step 3: Create API Key
1. Go to [APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" > "API Key"
3. Copy the generated API key

### Step 4: Restrict API Key (Recommended)
1. Click on the created API key
2. Under "Application restrictions", select "HTTP referrers"
3. Add your domain(s):
   - `localhost:5001/*` (for development)
   - `yourdomain.com/*` (for production)
4. Under "API restrictions", select "Restrict key"
5. Select the APIs you enabled in Step 2

## 🚀 Setting Up the Application

### Option 1: Environment Variable (Recommended)
```bash
export GOOGLE_MAPS_API_KEY="your-api-key-here"
python3 app.py
```

### Option 2: Direct Configuration
Edit `config.py` and replace the default value:
```python
GOOGLE_MAPS_API_KEY = 'your-actual-api-key-here'
```

### Option 3: .env File
Create a `.env` file in your project root:
```
GOOGLE_MAPS_API_KEY=your-api-key-here
```

## 📍 Features Added

### Location Search
- **Autocomplete**: Type city names and get suggestions
- **India-focused**: Restricted to Indian cities for better accuracy
- **Auto-coordinates**: Automatically fills latitude and longitude
- **Timezone detection**: Automatically sets IST (UTC+5:30) for Indian locations

### User Experience
- **Bilingual support**: Works in both English and Tamil
- **Visual feedback**: Styled autocomplete dropdown
- **Error handling**: Graceful fallback if API is unavailable
- **Responsive design**: Works on all device sizes

## 🔧 Configuration Options

### Customizing Location Restrictions
Edit `config.py` to modify India bounds:
```python
INDIA_BOUNDS = {
    'lat_min': 6.0,   # Southernmost point
    'lat_max': 37.0,  # Northernmost point
    'lng_min': 68.0,  # Westernmost point
    'lng_max': 97.0   # Easternmost point
}
```

### Timezone Offset
Default IST offset can be modified in `config.py`:
```python
DEFAULT_TZ_OFFSET = 5.5  # IST = UTC+5:30
```

## 💰 Cost Considerations

### Free Tier Limits
- **Places API**: 1,000 requests/day
- **Maps JavaScript API**: 25,000 map loads/day
- **Geocoding API**: 2,500 requests/day

### Typical Usage
For a partner prediction app:
- ~2 API calls per user (male + female location)
- Estimated cost: < $1/month for 1,000 users

### Cost Optimization Tips
1. **Restrict API key** to your domain only
2. **Cache results** for frequently searched locations
3. **Use billing alerts** to monitor usage
4. **Implement rate limiting** if needed

## 🛠️ Troubleshooting

### Common Issues

#### "Google Maps API not loaded"
- Check if API key is correct
- Verify API is enabled in Google Cloud Console
- Check browser console for errors

#### "No suggestions appearing"
- Ensure Places API is enabled
- Check API key restrictions
- Verify billing is enabled

#### "Coordinates not filling"
- Check browser console for JavaScript errors
- Verify Google Maps API script is loading
- Check if location input fields exist

### Debug Mode
Enable debug logging in browser console:
```javascript
// Add to browser console
localStorage.setItem('debug', 'true');
```

## 🔒 Security Best Practices

1. **Never expose API key** in client-side code (already implemented)
2. **Use HTTP referrer restrictions** in Google Cloud Console
3. **Monitor API usage** regularly
4. **Implement rate limiting** for production
5. **Use environment variables** for API keys

## 📱 Mobile Support

The location search works on mobile devices with:
- Touch-friendly autocomplete
- Responsive design
- Native keyboard support
- GPS integration (if available)

## 🌐 Production Deployment

### Environment Variables
Set in your deployment platform:
```bash
GOOGLE_MAPS_API_KEY=your-production-api-key
```

### Domain Restrictions
Update API key restrictions to include your production domain:
- `yourdomain.com/*`
- `www.yourdomain.com/*`

### Monitoring
- Set up Google Cloud Console alerts
- Monitor API usage in Google Cloud Console
- Check application logs for errors
