import fastf1
from fastf1 import plotting

print("FastF1 version:", fastf1.__version__)
print("\nAvailable attributes in fastf1.plotting:")
for attr in dir(plotting):
    if not attr.startswith('_'):
        print(f"- {attr}")

# Try to access driver_color
try:
    print("\nTrying to access driver_color:")
    if hasattr(plotting, 'driver_color'):
        print("plotting.driver_color exists")
    else:
        print("plotting.driver_color does not exist")
        
    # Check if it's a function or a dictionary
    if callable(getattr(plotting, 'driver_color', None)):
        print("plotting.driver_color is callable (function)")
    elif isinstance(getattr(plotting, 'driver_color', None), dict):
        print("plotting.driver_color is a dictionary")
        
    # Check for similar attributes
    similar_attrs = [attr for attr in dir(plotting) if 'color' in attr.lower() or 'driver' in attr.lower()]
    if similar_attrs:
        print("\nSimilar attributes found:")
        for attr in similar_attrs:
            print(f"- {attr}")
except Exception as e:
    print(f"Error: {e}")
