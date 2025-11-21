import requests
from metar import Metar
import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY", "")
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY", "")

def get_metar(icao_code: str) -> str:
    """
    Fetch METAR with fallback chain:
    1. Aviation Weather API
    2. OpenWeatherMap API
    3. WeatherAPI
    4. Mock data
    """
    # Try Aviation Weather API first
    result = _try_aviation_weather_api(icao_code)
    if result:
        return result
    
    # Try OpenWeatherMap
    #if OPENWEATHER_KEY:
        result = _try_openweather(icao_code)
        if result:
            return result
    
    # Try WeatherAPI
    if WEATHERAPI_KEY:
        result = _try_weatherapi(icao_code)
        if result:
            return result
    
    # Fall back to mock
    print(f"⚠️  All APIs failed. Using mock data for {icao_code}")
    return _get_mock_metar(icao_code)


def _try_aviation_weather_api(icao: str) -> str:
    """Try aviation weather API"""
    try:
        url = "https://aviationweather.gov/adds/dataserver_current/httpparam"
        params = {
            "dataSource": "metars",
            "requestType": "retrieve",
            "format": "json",
            "stationString": icao.upper(),
            "hoursBeforeNow": 1
        }
        headers = {"User-Agent": "FlightLens/1.0"}
        
        response = requests.get(url, params=params, headers=headers, timeout=3)
        response.raise_for_status()
        data = response.json()
        
        if data.get("data", {}).get("METAR"):
            return data["data"]["METAR"][0]["raw_text"]
    except:
        pass
    return None


#def _try_openweather(icao: str) -> str:
    """Try OpenWeatherMap API"""
    airports = {
        "KDFW": (32.8975, -97.0382),
        "KLAX": (33.9425, -118.4081),
    }
    
    if icao not in airports:
        return None
    
    try:
        lat, lon = airports[icao]
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}"
        response = requests.get(url, timeout=3)
        data = response.json()
        return f"OpenWeather: {data['weather'][0]['description']}"
    except:
        pass
    return None

def _try_weatherapi(icao: str) -> str:
    """Try WeatherAPI"""
    if not WEATHERAPI_KEY:
        return None
    
    airports = {
        "KDFW": "Dallas, Texas",
        "KLAX": "Los Angeles, California",
        "KJFK": "New York, New York",
        "KORD": "Chicago, Illinois",
    }
    
    if icao not in airports:
        return None
    
    try:
        location = airports[icao]
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": WEATHERAPI_KEY,
            "q": location,
            "aqi": "no"
        }
        
        response = requests.get(url, params=params, timeout=3)
        response.raise_for_status()
        data = response.json()
        
        current = data['current']
        temp = current['temp_c']
        wind_kph = current['wind_kph']
        wind_deg = current['wind_degree']
        pressure_mb = current['pressure_mb']
        
        # Convert to METAR-like format
        wind_kt = int(wind_kph * 0.539)  # Convert kph to knots
        pressure_inhg = pressure_mb / 33.864  # Convert mb to inHg
        
        metar = f"METAR {icao} Z {wind_deg:03d}{wind_kt:02d}KT {temp:.0f}°C A{pressure_inhg:.2f}"
        print(f"✅ Real-time weather from WeatherAPI: {icao}")
        return metar
    
    except Exception as e:
        print(f"⚠️  WeatherAPI error: {e}")
        return None


def _get_mock_metar(icao: str) -> str:
    """Return mock data"""
    mock = {
        "KDFW": "METAR KDFW 091856Z 18010KT 10SM FEW050 25/18 A3012",
        "KLAX": "METAR KLAX 091853Z 26008KT 10SM SCT015 22/20 A2990",
    }
    return mock.get(icao, f"METAR {icao} 091856Z 18010KT 10SM SKC 25/18 A3012")


def decode_metar(raw_text: str) -> str:
    """Decode METAR string"""
    try:
        report = Metar.Metar(raw_text)
        return report.string()
    except Exception as e:
        return f"Error decoding: {e}"
