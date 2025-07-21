"use client";

import { useEffect, useRef } from 'react';
import { Chart as ChartJS, registerables } from 'chart.js';
import { defaultChartOptions } from '../utils/chartConfig';

// Register all Chart.js components
ChartJS.register(...registerables);

interface ChartProps {
  type: 'line' | 'bar' | 'pie' | 'doughnut' | 'radar' | 'polarArea' | 'scatter' | 'bubble';
  data: any;
  options?: any;
  height?: number;
  width?: number;
  className?: string;
}

export default function Chart({ 
  type, 
  data, 
  options = {}, 
  height = 400, 
  width = 100, 
  className = '' 
}: ChartProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<ChartJS | null>(null);

  useEffect(() => {
    // Clean up any existing chart
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    // Create new chart if canvas and data are available
    if (chartRef.current && data) {
      const ctx = chartRef.current.getContext('2d');
      
      if (ctx) {
        // Merge default options with provided options
        const mergedOptions = {
          ...defaultChartOptions,
          ...options,
        };

        chartInstance.current = new ChartJS(ctx, {
          type,
          data,
          options: mergedOptions,
        });
      }
    }

    // Clean up on unmount
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [type, data, options]);

  return (
    <div className={`chart-container ${className}`} style={{ height: `${height}px`, width: `${width}%` }}>
      <canvas ref={chartRef} />
    </div>
  );
}
