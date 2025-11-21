"""
Microsoft Flight Simulator SimConnect Integration
Provides real-time aircraft telemetry data
"""

# Try to import SimConnect (Windows only)
try:
    from SimConnect import SimConnect, AircraftRequests
    SIMCONNECT_AVAILABLE = True
except ImportError:
    SIMCONNECT_AVAILABLE = False
    print("⚠️  SimConnect not available (Windows + MSFS required)")

class MSFSContext:
    """
    Interface to Microsoft Flight Simulator telemetry
    Falls back to mock data if SimConnect unavailable
    """
    
    def __init__(self):
        self.connected = False
        self.mode = "MOCK"
        
        if SIMCONNECT_AVAILABLE:
            try:
                self.sm = SimConnect()
                self.aq = AircraftRequests(self.sm, _time=2000)
                self.connected = True
                self.mode = "LIVE"
                print("✅ SimConnect connected")
            except Exception as e:
                print(f"⚠️  SimConnect connection failed: {e}")
                print("   Using mock data mode")
        else:
            print("ℹ️  SimConnect not installed. Using mock data.")
    
    def get_status(self):
        """
        Get current aircraft status
        
        Returns:
            Dictionary with telemetry data
        """
        if not self.connected:
            return self._get_mock_status()
        
        try:
            return {
                "altitude": self.aq.get("INDICATED_ALTITUDE"),
                "airspeed": self.aq.get("AIRSPEED_INDICATED"),
                "heading": self.aq.get("HEADING_INDICATOR"),
                "vertical_speed": self.aq.get("VERTICAL_SPEED"),
                "fuel_quantity": self.aq.get("FUEL_TOTAL_QUANTITY"),
                "engine_rpm": self.aq.get("GENERAL_ENG_RPM:1"),
                "flaps": self.aq.get("FLAPS_HANDLE_INDEX"),
                "pitch": self.aq.get("PLANE_PITCH_DEGREES"),
                "roll": self.aq.get("PLANE_BANK_DEGREES"),
                "mode": "LIVE"
            }
        except Exception as e:
            print(f"Error reading telemetry: {e}")
            return self._get_mock_status()
    
    def _get_mock_status(self):
        """
        Return mock telemetry data for testing
        """
        return {
            "altitude": 5000,
            "airspeed": 120,
            "heading": 270,
            "vertical_speed": 0,
            "fuel_quantity": 45.5,
            "engine_rpm": 2400,
            "flaps": 0,
            "pitch": 2.5,
            "roll": 0.0,
            "mode": "MOCK"
        }
    
    def get_contextual_summary(self):
        """
        Get human-readable summary of current flight state
        """
        status = self.get_status()
        return (
            f"Altitude: {status['altitude']:.0f} ft, "
            f"Airspeed: {status['airspeed']:.0f} kts, "
            f"Heading: {status['heading']:.0f}°, "
            f"VS: {status['vertical_speed']:.0f} fpm"
        )


if __name__ == "__main__":
    # Test SimConnect
    sim = MSFSContext()
    print("\nCurrent Status:")
    status = sim.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\nSummary:")
    print(sim.get_contextual_summary())
