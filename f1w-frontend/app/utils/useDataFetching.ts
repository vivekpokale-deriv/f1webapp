import { useState, useEffect } from 'react';

export function useDataFetching(year: string) {
  const [races, setRaces] = useState<any[]>([]);
  const [drivers, setDrivers] = useState<any[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const racesResponse = await fetch(`/api/info/races?year=${year}`);
        const racesData = await racesResponse.json();
        if (racesData.success) {
          setRaces(racesData.data.races);
        } else {
          throw new Error(racesData.error || 'Failed to fetch races');
        }

        const driversResponse = await fetch(`/api/info/all-drivers?year=${year}`);
        const driversData = await driversResponse.json();
        if (driversData.success) {
          setDrivers(driversData.data.drivers);
        } else {
          throw new Error(driversData.error || 'Failed to fetch drivers');
        }
      } catch (err: any) {
        setError(err.message);
        console.error("Error fetching initial data:", err);
      }
    };

    fetchInitialData();
  }, [year]);

  const fetchSessions = async (race: string) => {
    try {
      const response = await fetch(`/api/telemetry/sessions/${year}/${race}`);
      const data = await response.json();
      if (data.success) {
        setSessions(data.data.sessions);
      } else {
        throw new Error(data.error || 'Failed to fetch sessions');
      }
    } catch (err: any) {
      setError(err.message);
      console.error("Error fetching sessions:", err);
    }
  };

  return { races, drivers, sessions, error, fetchSessions };
}
