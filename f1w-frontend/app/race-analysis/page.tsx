"use client";

import { useState, useEffect } from "react";
import PageHeader from "../components/PageHeader";
import Card from "../components/Card";
import Button from "../components/Button";
import Chart from "../components/Chart";

export default function RaceAnalysisPage() {
  const [year, setYear] = useState("2023");
  const [races, setRaces] = useState<any[]>([]);
  const [drivers, setDrivers] = useState<any[]>([]);
  const [race, setRace] = useState("Bahrain");
  const [analysisType, setAnalysisType] = useState("race-pace");
  const [session, setSession] = useState("R");
  const [selectedDrivers, setSelectedDrivers] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [racePaceData, setRacePaceData] = useState<any>(null);
  const [teamPaceData, setTeamPaceData] = useState<any>(null);
  const [lapSectionsData, setLapSectionsData] = useState<any>(null);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const racesResponse = await fetch(`/api/info/races?year=${year}`);
        const racesData = await racesResponse.json();
        if (racesData.success) {
          setRaces(racesData.data.races);
        }

        const driversResponse = await fetch(`/api/info/all-drivers?year=${year}`);
        const driversData = await driversResponse.json();
        if (driversData.success) {
          setDrivers(driversData.data.drivers);
        }
      } catch (error) {
        console.error("Error fetching initial data:", error);
      }
    };

    fetchInitialData();
  }, [year]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (analysisType === "race-pace") {
        const response = await fetch(
          `/api/race-analysis/race-pace/${year}/${race}?drivers=${drivers}`
        );
        const data = await response.json();
        if (data.success) {
          setRacePaceData(data.data);
        } else {
          throw new Error(data.error || "Failed to load race pace data");
        }
      } else if (analysisType === "team-pace") {
        const response = await fetch(
          `/api/race-analysis/team-pace/${year}/${race}`
        );
        const data = await response.json();
        if (data.success) {
          setTeamPaceData(data.data);
        } else {
          throw new Error(data.error || "Failed to load team pace data");
        }
      } else if (analysisType === "lap-sections") {
        const response = await fetch(
          `/api/race-analysis/lap-sections/${year}/${race}/${session}?drivers=${drivers}`
        );
        const data = await response.json();
        if (data.success) {
          setLapSectionsData(data.data);
        } else {
          throw new Error(data.error || "Failed to load lap sections data");
        }
      }
    } catch (error) {
      console.error("Error loading race analysis data:", error);
      alert("Error loading race analysis data. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // Update session availability based on analysis type
  const handleAnalysisTypeChange = (type: string) => {
    setAnalysisType(type);
    if (type === "race-pace" || type === "team-pace") {
      setSession("R");
    }
  };

  return (
    <div>
      <PageHeader
        title="F1 Race Analysis"
        description="Interactive Formula 1 race data analysis"
      />

      <div className="container mx-auto px-4 py-8">
        <Card title="Select Data to Analyze" className="mb-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
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
                <label htmlFor="analysisType" className="block text-sm font-medium text-gray-700 mb-1">
                  Analysis Type
                </label>
                <select
                  id="analysisType"
                  value={analysisType}
                  onChange={(e) => handleAnalysisTypeChange(e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-[#e10600] focus:ring-[#e10600] sm:text-sm"
                >
                  <option value="race-pace">Race Pace</option>
                  <option value="team-pace">Team Pace</option>
                  <option value="lap-sections">Lap Sections</option>
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
                  disabled={analysisType === "race-pace" || analysisType === "team-pace"}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-[#e10600] focus:ring-[#e10600] sm:text-sm disabled:bg-gray-100 disabled:text-gray-500"
                >
                  <option value="R">Race</option>
                  <option value="Q">Qualifying</option>
                  <option value="FP1">Practice 1</option>
                  <option value="FP2">Practice 2</option>
                  <option value="FP3">Practice 3</option>
                </select>
              </div>

              <div>
                <label htmlFor="drivers" className="block text-sm font-medium text-gray-700 mb-1">
                  Drivers (optional)
                </label>
                <input
                  type="text"
                  id="drivers"
                  value={selectedDrivers}
                  onChange={(e) => setSelectedDrivers(e.target.value)}
                  placeholder="VER,HAM,LEC"
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-[#e10600] focus:ring-[#e10600] sm:text-sm"
                />
              </div>

              <div className="flex items-end">
                <Button type="submit" className="w-full">
                  {isLoading ? "Loading..." : "Load Data"}
                </Button>
              </div>
            </div>

          </form>
        </Card>
        {analysisType === "race-pace" && (
          <Card title="Race Pace Comparison" className="mb-8">
            <div className="visualization-container" style={{ height: "450px" }}>
              {isLoading ? (
                <div className="flex flex-col items-center justify-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#e10600]"></div>
                  <p className="mt-4 text-gray-600">Loading race pace data...</p>
                </div>
              ) : racePaceData ? (
                <Chart type="line" data={racePaceData} />
              ) : (
                <div className="text-center text-gray-500">
                  <p>Select parameters and click "Load Data" to view the visualization</p>
                </div>
              )}
            </div>
          </Card>
        )}

        {analysisType === "team-pace" && (
          <Card title="Team Pace Comparison" className="mb-8">
            <div className="visualization-container" style={{ height: "500px" }}>
              {isLoading ? (
                <div className="flex flex-col items-center justify-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#e10600]"></div>
                  <p className="mt-4 text-gray-600">Loading team pace data...</p>
                </div>
              ) : teamPaceData ? (
                <Chart type="bar" data={teamPaceData} />
              ) : (
                <div className="text-center text-gray-500">
                  <p>Select parameters and click "Load Data" to view the visualization</p>
                </div>
              )}
            </div>
          </Card>
        )}

        {analysisType === "lap-sections" && (
          <Card title="Lap Sections Analysis" className="mb-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {lapSectionsData && lapSectionsData.sections.map((section: any) => (
                    <div key={section.name}>
                      <h3 className="text-lg font-semibold mb-3">{section.name.replace('_', ' ')}</h3>
                      <div className="visualization-container" style={{ height: "250px" }}>
                        {isLoading ? (
                          <div className="flex flex-col items-center justify-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#e10600]"></div>
                          </div>
                        ) : (
                          <Chart type="line" data={section} />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
            </Card>
        )}
      </div>
    </div>
  );
}

function getAnalysisTitle(analysisType: string): string {
  switch (analysisType) {
    case "race-pace":
      return "Race Pace Comparison";
    case "team-pace":
      return "Team Pace Comparison";
    case "lap-sections":
      return "Lap Sections Analysis";
    default:
      return "Race Analysis";
  }
}
