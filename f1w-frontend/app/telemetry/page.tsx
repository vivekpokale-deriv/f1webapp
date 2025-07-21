"use client";

import { useState, useEffect } from "react";
import SessionView from '../components/SessionView';
import PageHeader from "../components/PageHeader";

export default function TelemetryPage() {
  const [year, setYear] = useState("2023");
  const [races, setRaces] = useState<any[]>([]);
  const [race, setRace] = useState("Bahrain");
  const [sessions, setSessions] = useState<any[]>([]);
  const [session, setSession] = useState("Q");

  useEffect(() => {
    const fetchRacesAndSessions = async () => {
      try {
        const racesResponse = await fetch(`/api/info/races?year=${year}`);
        const racesData = await racesResponse.json();
        if (racesData.success) {
          setRaces(racesData.data.races);
          if (racesData.data.races.length > 0) {
            const firstRace = racesData.data.races[0].name.replace(/ /g, '_');
            setRace(firstRace);
            const sessionsResponse = await fetch(`/api/telemetry/sessions/${year}/${firstRace}`);
            const sessionsData = await sessionsResponse.json();
            if (sessionsData.success) {
              setSessions(sessionsData.data.sessions);
            }
          }
        }
      } catch (error) {
        console.error("Error fetching initial data:", error);
      }
    };

    fetchRacesAndSessions();
  }, [year]);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const response = await fetch(`/api/telemetry/sessions/${year}/${race}`);
        const data = await response.json();
        if (data.success) {
          setSessions(data.data.sessions);
        }
      } catch (error) {
        console.error("Error fetching sessions:", error);
      }
    };

    if (race) {
      fetchSessions();
    }
  }, [race]);

  return (
    <div>
      <PageHeader
        title="F1 Telemetry Visualization"
        description="Interactive Formula 1 telemetry data visualization"
      />

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-1">
            <div className="space-y-4">
              <div>
                <label htmlFor="year" className="block text-sm font-medium text-gray-700 mb-1">
                  Year
                </label>
                <select
                  id="year"
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-[#e10600] focus:ring-[#e10600] sm:text-sm"
                >
                  <option value="2023">2023</option>
                  <option value="2022">2022</option>
                  <option value="2021">2021</option>
                </select>
              </div>
              <div>
                <label htmlFor="race" className="block text-sm font-medium text-gray-700 mb-1">
                  Race
                </label>
                <select
                  id="race"
                  value={race}
                  onChange={(e) => setRace(e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-[#e10600] focus:ring-[#e10600] sm:text-sm"
                >
                  {races.map((r: any) => (
                    <option key={r.name} value={r.name.replace(/ /g, '_')}>{r.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="session" className="block text-sm font-medium text-gray-700 mb-1">
                  Session
                </label>
                <select
                  id="session"
                  value={session}
                  onChange={(e) => setSession(e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-[#e10600] focus:ring-[#e10600] sm:text-sm"
                >
                  {sessions.map((s: any) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          <div className="md:col-span-3">
            <SessionView year={year} race={race} session={session} />
          </div>
        </div>
      </div>
    </div>
  );
}
