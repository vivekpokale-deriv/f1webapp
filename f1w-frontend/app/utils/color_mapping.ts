/**
 * Color mapping utilities for F1 drivers and teams
 * This file provides functions to get consistent colors for F1 drivers and teams
 * by fetching them from the backend API
 */

// Cache for driver and team colors to avoid repeated API calls
let driverColorCache: Record<string, string> = {};
let teamColorCache: Record<string, string> = {};

// Default colors as fallbacks
const defaultDriverColors: Record<string, string> = {
  'VER': '#0600EF', // Red Bull
  'PER': '#0600EF', // Red Bull
  'HAM': '#00D2BE', // Mercedes
  'RUS': '#00D2BE', // Mercedes
  'LEC': '#DC0000', // Ferrari
  'SAI': '#DC0000', // Ferrari
  'NOR': '#FF8700', // McLaren
  'PIA': '#FF8700', // McLaren
  'ALO': '#006F62', // Aston Martin
  'STR': '#006F62', // Aston Martin
  'OCO': '#0090FF', // Alpine
  'GAS': '#0090FF', // Alpine
  'ALB': '#005AFF', // Williams
  'SAR': '#005AFF', // Williams
  'TSU': '#2B4562', // AlphaTauri
  'RIC': '#2B4562', // AlphaTauri
  'BOT': '#900000', // Alfa Romeo
  'ZHO': '#900000', // Alfa Romeo
  'HUL': '#FFFFFF', // Haas
  'MAG': '#FFFFFF', // Haas
};

const defaultTeamColors: Record<string, string> = {
  'Red Bull Racing': '#0600EF',
  'Mercedes': '#00D2BE',
  'Ferrari': '#DC0000',
  'McLaren': '#FF8700',
  'Aston Martin': '#006F62',
  'Alpine': '#0090FF',
  'Williams': '#005AFF',
  'AlphaTauri': '#2B4562',
  'Alfa Romeo': '#900000',
  'Haas F1 Team': '#FFFFFF'
};

/**
 * Get the color for a driver
 * @param driverCode The three-letter code for the driver (e.g., 'VER', 'HAM')
 * @param year Optional year to get historical colors
 * @returns The color for the driver as a hex string
 */
export async function getDriverColor(driverCode: string, year?: number): Promise<string> {
  // Return from cache if available
  const cacheKey = `${driverCode}_${year || 'current'}`;
  if (driverColorCache[cacheKey]) {
    return driverColorCache[cacheKey];
  }
  
  try {
    // Fetch from API
    const url = year 
      ? `/api/utils/driver-color/${driverCode}?year=${year}` 
      : `/api/utils/driver-color/${driverCode}`;
      
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.success && data.data && data.data.color) {
      // Cache the result
      driverColorCache[cacheKey] = data.data.color;
      return data.data.color;
    } else {
      throw new Error('Invalid data structure');
    }
  } catch (error) {
    console.error(`Error fetching color for driver ${driverCode}:`, error);
    // Fall back to default color
    return defaultDriverColors[driverCode] || '#CCCCCC';
  }
}

/**
 * Get the color for a team
 * @param teamName The name of the team
 * @param year Optional year to get historical colors
 * @returns The color for the team as a hex string
 */
export async function getTeamColor(teamName: string, year?: number): Promise<string> {
  // Return from cache if available
  const cacheKey = `${teamName}_${year || 'current'}`;
  if (teamColorCache[cacheKey]) {
    return teamColorCache[cacheKey];
  }
  
  try {
    // Fetch from API
    const url = year 
      ? `/api/utils/team-color?team=${encodeURIComponent(teamName)}&year=${year}` 
      : `/api/utils/team-color?team=${encodeURIComponent(teamName)}`;
      
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.success && data.data && data.data.color) {
      // Cache the result
      teamColorCache[cacheKey] = data.data.color;
      return data.data.color;
    } else {
      throw new Error('Invalid data structure');
    }
  } catch (error) {
    console.error(`Error fetching color for team ${teamName}:`, error);
    // Fall back to default color
    return defaultTeamColors[teamName] || '#CCCCCC';
  }
}

/**
 * Get all driver colors for a specific year
 * @param year Optional year to get historical colors
 * @returns A record mapping driver codes to colors
 */
export async function getAllDriverColors(year?: number): Promise<Record<string, string>> {
  try {
    // Fetch from API
    const url = year 
      ? `/api/utils/all-driver-colors?year=${year}` 
      : `/api/utils/all-driver-colors`;
      
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.success && data.data && data.data.colors) {
      // Cache all the results
      const colors = data.data.colors;
      Object.keys(colors).forEach(driverCode => {
        const cacheKey = `${driverCode}_${year || 'current'}`;
        driverColorCache[cacheKey] = colors[driverCode];
      });
      
      return colors;
    } else {
      throw new Error('Invalid data structure');
    }
  } catch (error) {
    console.error(`Error fetching all driver colors:`, error);
    // Fall back to default colors
    return defaultDriverColors;
  }
}

/**
 * Get all team colors for a specific year
 * @param year Optional year to get historical colors
 * @returns A record mapping team names to colors
 */
export async function getAllTeamColors(year?: number): Promise<Record<string, string>> {
  try {
    // Fetch from API
    const url = year 
      ? `/api/utils/all-team-colors?year=${year}` 
      : `/api/utils/all-team-colors`;
      
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.success && data.data && data.data.colors) {
      // Cache all the results
      const colors = data.data.colors;
      Object.keys(colors).forEach(teamName => {
        const cacheKey = `${teamName}_${year || 'current'}`;
        teamColorCache[cacheKey] = colors[teamName];
      });
      
      return colors;
    } else {
      throw new Error('Invalid data structure');
    }
  } catch (error) {
    console.error(`Error fetching all team colors:`, error);
    // Fall back to default colors
    return defaultTeamColors;
  }
}

// Export default colors for immediate use without API calls
export { defaultDriverColors as driverColors, defaultTeamColors as teamColors };
