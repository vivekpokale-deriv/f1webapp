"use client";

import { useState, useEffect } from 'react';
import { useDataFetching } from '../utils/useDataFetching';
import DriverGrid from './DriverGrid';
import LapInfo from './LapInfo';
import Chart from './Chart';
import Button from './Button';
import { driverColors } from '../utils/chartConfig';

interface SessionViewProps {
  year: string;
  race: string;
  session: string;
}

export default function SessionView({ year, race, session }: SessionViewProps) {
  const { drivers, sessions, error } = useDataFetching(year);
  const [laps, setLaps] = useState<any[]>([]);
  const [selectedDrivers, setSelectedDrivers] = useState<string[]>([]);
  const [lapTimeData, setLapTimeData] = useState<any>(null);
  const [selectedLaps, setSelectedLaps] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchLaps = async () => {
      if (race && session) {
        setIsLoading(true);
        try {
          const response = await fetch(`/api/telemetry/session-laps/${year}/${race}/${session}`);
          const data = await response.json();
          if (data.success) {
            setLaps(data.data.laps);
            const uniqueDrivers = Array.from(new Set(data.data.laps.map((l: any) => l.driverCode)));
            setSelectedDrivers(uniqueDrivers.slice(0, 4) as string[]);
          }
        } catch (error) {
          console.error("Error fetching session laps:", error);
        } finally {
          setIsLoading(false);
        }
      }
    };

    fetchLaps();
  }, [year, race, session]);

  useEffect(() => {
    if (laps.length > 0 && selectedDrivers.length > 0) {
      const chartData = {
        labels: Array.from(new Set(laps.map(l => l.lapNumber))),
        datasets: selectedDrivers.map(driver => {
          const driverLaps = laps.filter(l => l.driverCode === driver);
          return {
            label: driver,
            data: driverLaps.map(l => ({ x: l.lapNumber, y: l.lapTime })),
            borderColor: driverColors[driver] || '#FFFFFF',
            backgroundColor: 'transparent',
          };
        }),
      };
      setLapTimeData(chartData);
    }
  }, [laps, selectedDrivers]);

  const handleDriverSelection = (driver: string) => {
    setSelectedDrivers(prev =>
      prev.includes(driver)
        ? prev.filter(d => d !== driver)
        : [...prev, driver]
    );
  };

  const handleLapSelection = (lap: any) => {
    setSelectedLaps(prev => {
      const isSelected = prev.find(l => l.driverCode === lap.driverCode && l.lapNumber === lap.lapNumber);
      if (isSelected) {
        return prev.filter(l => !(l.driverCode === lap.driverCode && l.lapNumber === lap.lapNumber));
      } else {
        return [...prev, lap];
      }
    });
  };

  const handleCompareFastest = () => {
    const fastestLaps = selectedDrivers.map(driver => {
      const driverLaps = laps.filter(l => l.driverCode === driver);
      return driverLaps.reduce((fastest, current) => {
        if (!fastest || current.lapTime < fastest.lapTime) {
          return current;
        }
        return fastest;
      }, null);
    });
    setSelectedLaps(fastestLaps.filter(l => l));
  };

  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="md:col-span-1">
          <DriverGrid drivers={drivers} selectedDrivers={selectedDrivers} onDriverSelect={handleDriverSelection} />
        </div>
        <div className="md:col-span-3">
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
            </div>
          ) : lapTimeData ? (
            <Chart type="line" data={lapTimeData} />
          ) : (
            <div className="flex justify-center items-center h-64">
              <p>No data to display.</p>
            </div>
          )}
        </div>
      </div>
      <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
        {selectedLaps.map(lap => (
          <LapInfo key={`${lap.driverCode}-${lap.lapNumber}`} lap={lap} />
        ))}
      </div>
      <div className="mt-4">
        <Button onClick={handleCompareFastest}>Compare Fastest Laps</Button>
      </div>
    </div>
  );
}
