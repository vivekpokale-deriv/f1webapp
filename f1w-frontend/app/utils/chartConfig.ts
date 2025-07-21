import { ChartOptions, ChartData } from 'chart.js';

// Default chart options for dark mode
export const defaultChartOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: {
        color: '#ffffff',
        font: {
          family: 'Inter, sans-serif',
        },
      },
    },
    tooltip: {
      backgroundColor: '#15151e',
      titleColor: '#ffffff',
      bodyColor: '#ffffff',
      borderColor: '#e10600',
      borderWidth: 1,
      padding: 10,
      displayColors: true,
      usePointStyle: true,
      boxPadding: 5,
      callbacks: {
        label: function(context) {
          return `${context.dataset.label}: ${context.parsed.y}`;
        }
      }
    },
  },
  scales: {
    x: {
      grid: {
        color: 'rgba(255, 255, 255, 0.1)',
      },
      ticks: {
        color: '#ffffff',
      },
      title: {
        display: true,
        color: '#ffffff',
      },
    },
    y: {
      grid: {
        color: 'rgba(255, 255, 255, 0.1)',
      },
      ticks: {
        color: '#ffffff',
      },
      title: {
        display: true,
        color: '#ffffff',
      },
    },
  },
  elements: {
    line: {
      tension: 0.3,
    },
    point: {
      radius: 3,
      hoverRadius: 5,
    },
  },
  interaction: {
    mode: 'index',
    intersect: false,
  },
};

// Function to create speed trace chart data
export function createSpeedTraceData(
  distance: number[],
  driver1Speed: number[],
  driver2Speed: number[],
  driver1Name: string,
  driver2Name: string,
  driver1Color: string,
  driver2Color: string
): ChartData<'line'> {
  return {
    labels: distance.map(d => `${d}m`),
    datasets: [
      {
        label: driver1Name,
        data: driver1Speed,
        borderColor: driver1Color,
        backgroundColor: `${driver1Color}33`, // Add transparency
        fill: false,
        borderWidth: 2,
      },
      {
        label: driver2Name,
        data: driver2Speed,
        borderColor: driver2Color,
        backgroundColor: `${driver2Color}33`, // Add transparency
        fill: false,
        borderWidth: 2,
      },
    ],
  };
}

// Function to create race pace chart data
export function createRacePaceData(
  laps: number[],
  driverData: { name: string; color: string; lapTimes: number[] }[]
): ChartData<'line'> {
  return {
    labels: laps.map(lap => `Lap ${lap}`),
    datasets: driverData.map(driver => ({
      label: driver.name,
      data: driver.lapTimes,
      borderColor: driver.color,
      backgroundColor: `${driver.color}33`, // Add transparency
      fill: false,
      borderWidth: 2,
    })),
  };
}

// Function to create team pace chart data
export function createTeamPaceData(
  teams: string[],
  averagePace: number[],
  bestPace: number[]
): ChartData<'bar'> {
  return {
    labels: teams,
    datasets: [
      {
        label: 'Average Pace',
        data: averagePace,
        backgroundColor: '#e10600',
        borderColor: '#e10600',
        borderWidth: 1,
      },
      {
        label: 'Best Pace',
        data: bestPace,
        backgroundColor: '#0600EF',
        borderColor: '#0600EF',
        borderWidth: 1,
      },
    ],
  };
}

// Function to create driver standings chart data
export function createDriverStandingsData(
  drivers: string[],
  points: number[],
  colors: string[]
): ChartData<'bar'> {
  return {
    labels: drivers,
    datasets: [
      {
        label: 'Points',
        data: points,
        backgroundColor: colors,
        borderColor: colors,
        borderWidth: 1,
      },
    ],
  };
}

// Function to create constructor standings chart data
export function createConstructorStandingsData(
  constructors: string[],
  points: number[],
  colors: string[]
): ChartData<'bar'> {
  return {
    labels: constructors,
    datasets: [
      {
        label: 'Points',
        data: points,
        backgroundColor: colors,
        borderColor: colors,
        borderWidth: 1,
      },
    ],
  };
}

// Team colors mapping
export const teamColors: Record<string, string> = {
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

// Driver colors mapping (based on their teams)
export const driverColors: Record<string, string> = {
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
