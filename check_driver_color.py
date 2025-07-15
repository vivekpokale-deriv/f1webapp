import fastf1
from fastf1 import plotting

print("FastF1 version:", fastf1.__version__)

# Check the signature of get_driver_color
import inspect
print("\nSignature of get_driver_color:")
print(inspect.signature(plotting.get_driver_color))

# Try to load a session and use get_driver_color
print("\nTrying to use get_driver_color with a session:")
try:
    # Enable cache
    fastf1.Cache.enable_cache('cache')
    
    # Load a session
    session = fastf1.get_session(2023, 'Bahrain', 'R')
    session.load()
    
    # Try different ways to get driver colors
    driver = 'VER'
    
    # Method 1: With session
    color1 = plotting.get_driver_color(driver, session)
    print(f"Color for {driver} with session: {color1}")
    
    # Method 2: Try with driver mapping
    driver_mapping = plotting.get_driver_color_mapping(session)
    color2 = driver_mapping[driver]
    print(f"Color for {driver} with mapping: {color2}")
    
except Exception as e:
    print(f"Error: {e}")
