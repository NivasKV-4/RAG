import sys
from pathlib import Path

# Ensure FlightLens root is in sys.path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root)) 

from src.integrations.aviation_weather import get_metar, decode_metar

def test_metar_fetch_and_decode():
    airport = "KDFW"
    raw = get_metar(airport)
    print("Raw METAR:", raw)
    decoded = decode_metar(raw)
    print("Decoded METAR:", decoded)

if __name__ == "__main__":
    test_metar_fetch_and_decode()
