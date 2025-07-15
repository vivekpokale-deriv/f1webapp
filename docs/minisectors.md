# Mini-Sectors in FastF1

## Overview

Mini-sectors are a way to divide a race track into smaller segments for more detailed analysis. While FastF1 doesn't have built-in mini-sectors, it provides the necessary data to create them manually, which is what we've implemented in our application.

## Implementation in F1 Web App

In our F1 Web App, we've implemented mini-sectors in the `MiniSectorAnalyzer` class in `services/telemetry_service.py`. This implementation:

1. Divides the track into a configurable number of segments (default: 20, set in `config.py`)
2. Analyzes which driver is fastest in each mini-sector
3. Visualizes the results on a track map with color-coding

## How Mini-Sectors Are Created

There are three methods for creating mini-sectors:

### 1. Distance-Based Mini-Sectors

This is the default method. The track is divided into equal segments based on distance:

```python
telemetry['MiniSector'] = pd.cut(
    telemetry['Distance'], 
    num_sectors, 
    labels=False
)
```

### 2. Time-Based Mini-Sectors

The track is divided into segments where drivers spend approximately equal time:

```python
telemetry['MiniSector'] = pd.cut(
    telemetry['Time'].dt.total_seconds(), 
    num_sectors, 
    labels=False
)
```

### 3. Angle-Based Mini-Sectors

The track is divided based on changes in direction, which can better represent corners:

```python
# Calculate track angle
x_diff = telemetry['X'].diff()
y_diff = telemetry['Y'].diff()
angles = np.arctan2(y_diff, x_diff)
# Normalize angles to 0-2π range
angles = (angles + 2 * np.pi) % (2 * np.pi)

telemetry['MiniSector'] = pd.cut(
    angles, 
    num_sectors, 
    labels=False
)
```

## Finding the Fastest Driver in Each Mini-Sector

Once mini-sectors are created, we can find the fastest driver in each:

```python
# Calculate the time spent in each mini-sector for each driver
time_spent = mini_sectors.groupby(['Driver', 'MiniSector']).apply(
    lambda df: df['Time'].diff().sum()
).reset_index().rename(columns={0: 'TimeSpent'})

# Find the fastest driver in each mini-sector
fastest_per_mini_sector = time_spent.loc[
    time_spent.groupby('MiniSector')['TimeSpent'].idxmin()
]
```

## Customizing Mini-Sectors

You can customize mini-sectors by:

1. Changing the number of sectors in `config.py` (DEFAULT_MINI_SECTORS)
2. Selecting a different method for creating mini-sectors (distance, time, or angle)
3. Implementing custom logic for sector creation

## Comparison to Official F1 Mini-Sectors

Official F1 broadcasts typically use around 20-30 mini-sectors per track. Our implementation allows for a similar level of granularity, though the exact placement of sector boundaries may differ from the official ones.

## Limitations

- FastF1 doesn't provide official mini-sector data, so our implementation is an approximation
- The accuracy depends on the telemetry data sampling rate
- Very small mini-sectors may not have enough data points for accurate analysis

## Future Improvements

Potential improvements to our mini-sector implementation:

1. Adaptive mini-sectors that are smaller in complex sections (like chicanes) and larger on straights
2. Machine learning to identify natural track segments based on driving patterns
3. Importing official mini-sector definitions if they become available in the FastF1 API
