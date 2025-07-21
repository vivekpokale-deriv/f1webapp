"use client";

import { useState, useEffect } from "react";
import PageHeader from "../components/PageHeader";
import Card from "../components/Card";
import Button from "../components/Button";
import { teamColors } from "../utils/color_mapping";

interface DriverStanding {
  position: number;
  driver: {
    code: string;
    name: string;
    number: string;
  };
  team: string;
  points: number;
}

interface ConstructorStanding {
  position: number;
  team: string;
  points: number;
}

interface RaceEvent {
  type: string;
  startTime: string;
  placeholder?: boolean;
}

interface Race {
  round: number;
  name: string;
  country: string;
  location: string;
  flagUrl?: string;
  events: RaceEvent[];
}

interface EventsByStatus {
  current: Race[];
  upcoming: Race[];
  past: Race[];
}

export default function InformationPage() {
  const [activeTab, setActiveTab] = useState("drivers");
  const [driverYear, setDriverYear] = useState("2023");
  const [constructorYear, setConstructorYear] = useState("2023");
  const [scheduleYear, setScheduleYear] = useState("2023");
  
  const [driverStandings, setDriverStandings] = useState<DriverStanding[]>([]);
  const [constructorStandings, setConstructorStandings] = useState<ConstructorStanding[]>([]);
  const [eventsByStatus, setEventsByStatus] = useState<EventsByStatus>({
    current: [],
    upcoming: [],
    past: []
  });
  
  const [isLoadingDrivers, setIsLoadingDrivers] = useState(false);
  const [isLoadingConstructors, setIsLoadingConstructors] = useState(false);
  const [isLoadingSchedule, setIsLoadingSchedule] = useState(false);

  // Team colors will be loaded from the color_mapping utility

  // Load driver standings
  const loadDriverStandings = async (year: string) => {
    setIsLoadingDrivers(true);
    try {
      const response = await fetch(`/api/info/drivers?year=${year}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      if (data.success && data.data && data.data.standings) {
        setDriverStandings(data.data.standings);
      } else {
        throw new Error('Invalid data structure');
      }
    } catch (error) {
      console.error('Error loading driver standings:', error);
      setDriverStandings([]);
    } finally {
      setIsLoadingDrivers(false);
    }
  };

  // Load constructor standings
  const loadConstructorStandings = async (year: string) => {
    setIsLoadingConstructors(true);
    try {
      const response = await fetch(`/api/info/constructors?year=${year}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      if (data.success && data.data && data.data.standings) {
        setConstructorStandings(data.data.standings);
      } else {
        throw new Error('Invalid data structure');
      }
    } catch (error) {
      console.error('Error loading constructor standings:', error);
      setConstructorStandings([]);
    } finally {
      setIsLoadingConstructors(false);
    }
  };

  // Load race schedule
  const loadRaceSchedule = async (year: string) => {
    setIsLoadingSchedule(true);
    try {
      const response = await fetch(`/api/info/events-by-status?year=${year}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      if (data.success && data.data) {
        setEventsByStatus({
          current: data.data.current || [],
          upcoming: data.data.upcoming || [],
          past: data.data.past || []
        });
      } else {
        throw new Error('Invalid data structure');
      }
    } catch (error) {
      console.error('Error loading race schedule:', error);
      setEventsByStatus({
        current: [],
        upcoming: [],
        past: []
      });
    } finally {
      setIsLoadingSchedule(false);
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Load initial data
  useEffect(() => {
    loadDriverStandings(driverYear);
  }, []);

  // Handle tab changes
  useEffect(() => {
    if (activeTab === 'drivers' && driverStandings.length === 0) {
      loadDriverStandings(driverYear);
    } else if (activeTab === 'constructors' && constructorStandings.length === 0) {
      loadConstructorStandings(constructorYear);
    } else if (activeTab === 'schedule' && 
              (eventsByStatus.current.length === 0 && 
               eventsByStatus.upcoming.length === 0 && 
               eventsByStatus.past.length === 0)) {
      loadRaceSchedule(scheduleYear);
    }
  }, [activeTab]);

  return (
    <div>
      <PageHeader
        title="F1 Information"
        description="Driver standings, constructor standings, and race schedules"
      />

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('drivers')}
                className={`${
                  activeTab === 'drivers'
                    ? 'border-[#e10600] text-[#e10600]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Driver Standings
              </button>
              <button
                onClick={() => setActiveTab('constructors')}
                className={`${
                  activeTab === 'constructors'
                    ? 'border-[#e10600] text-[#e10600]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Constructor Standings
              </button>
              <button
                onClick={() => setActiveTab('schedule')}
                className={`${
                  activeTab === 'schedule'
                    ? 'border-[#e10600] text-[#e10600]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Race Schedule
              </button>
            </nav>
          </div>
        </div>

        {/* Driver Standings Tab */}
        {activeTab === 'drivers' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Driver Standings</h2>
              <div className="w-32">
                <select
                  value={driverYear}
                  onChange={(e) => {
                    setDriverYear(e.target.value);
                    loadDriverStandings(e.target.value);
                  }}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-[#e10600] focus:ring-[#e10600] sm:text-sm"
                >
                  <option value="2023">2023</option>
                  <option value="2022">2022</option>
                  <option value="2021">2021</option>
                </select>
              </div>
            </div>

            <Card title="Driver Championship Standings" className="mb-8">
              {isLoadingDrivers ? (
                <div className="flex justify-center items-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#e10600]"></div>
                </div>
              ) : driverStandings.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Pos
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Driver
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Team
                        </th>
                        <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Points
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {driverStandings.map((item) => (
                        <tr key={item.position} className="hover:bg-gray-50 transition-colors">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#15151e] text-white text-sm">
                              {item.position}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div>
                                <div className="text-sm font-medium text-gray-900">
                                  {item.driver.code} - {item.driver.name}
                                </div>
                                <div className="text-sm text-gray-500">
                                  #{item.driver.number}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <span 
                                className="w-3 h-3 rounded-full mr-2" 
                                style={{ backgroundColor: teamColors[item.team] || '#CCCCCC' }}
                              ></span>
                              <span className="text-sm text-gray-900">{item.team}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <span className="font-bold">{item.points}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500">No driver standings data available.</p>
                </div>
              )}
            </Card>
          </div>
        )}

        {/* Constructor Standings Tab */}
        {activeTab === 'constructors' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Constructor Standings</h2>
              <div className="w-32">
                <select
                  value={constructorYear}
                  onChange={(e) => {
                    setConstructorYear(e.target.value);
                    loadConstructorStandings(e.target.value);
                  }}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-[#e10600] focus:ring-[#e10600] sm:text-sm"
                >
                  <option value="2023">2023</option>
                  <option value="2022">2022</option>
                  <option value="2021">2021</option>
                </select>
              </div>
            </div>

            <Card title="Constructor Championship Standings" className="mb-8">
              {isLoadingConstructors ? (
                <div className="flex justify-center items-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#e10600]"></div>
                </div>
              ) : constructorStandings.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Pos
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Team
                        </th>
                        <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Points
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {constructorStandings.map((item) => (
                        <tr key={item.position} className="hover:bg-gray-50 transition-colors">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#15151e] text-white text-sm">
                              {item.position}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <span 
                                className="w-3 h-3 rounded-full mr-2" 
                                style={{ backgroundColor: teamColors[item.team] || '#CCCCCC' }}
                              ></span>
                              <span className="text-sm font-medium text-gray-900">{item.team}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <span className="font-bold">{item.points}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500">No constructor standings data available.</p>
                </div>
              )}
            </Card>
          </div>
        )}

        {/* Race Schedule Tab */}
        {activeTab === 'schedule' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Race Schedule</h2>
              <div className="w-32">
                <select
                  value={scheduleYear}
                  onChange={(e) => {
                    setScheduleYear(e.target.value);
                    loadRaceSchedule(e.target.value);
                  }}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-[#e10600] focus:ring-[#e10600] sm:text-sm"
                >
                  <option value="2023">2023</option>
                  <option value="2022">2022</option>
                  <option value="2021">2021</option>
                </select>
              </div>
            </div>

            {isLoadingSchedule ? (
              <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#e10600]"></div>
              </div>
            ) : (eventsByStatus.current.length > 0 || eventsByStatus.upcoming.length > 0 || eventsByStatus.past.length > 0) ? (
              <div className="space-y-8">
                {/* Current Events */}
                {eventsByStatus.current.length > 0 && (
                  <div>
                    <h3 className="text-lg font-bold mb-4 text-[#e10600]">Current Events</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {eventsByStatus.current.map((race: Race) => {
                        // Find the race event
                        const raceEvent = race.events.find((event: RaceEvent) => event.type === 'Race');
                        const raceDate = raceEvent ? formatDate(raceEvent.startTime) : 'Date TBD';

                        return (
                          <Card key={race.round} title={`Round ${race.round}`} className="h-full border-l-4 border-[#e10600]">
                            <div className="flex flex-col h-full">
                              <div className="mb-4">
                                <h3 className="text-lg font-semibold">{race.name}</h3>
                                <p className="text-gray-600">{race.location}, {race.country}</p>
                                <p className="text-gray-700 mt-2">
                                  <span className="font-medium">Race:</span> {raceDate}
                                </p>
                              </div>
                              
                              <div className="mt-auto">
                                <h4 className="font-medium text-sm text-gray-700 mb-2">Event Schedule</h4>
                                <ul className="space-y-2">
                                  {race.events.map((event: RaceEvent, index: number) => (
                                    <li key={index} className="flex justify-between text-sm">
                                      <span>{event.type}</span>
                                      <span className="text-gray-600">{formatDate(event.startTime)}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          </Card>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Upcoming Events */}
                {eventsByStatus.upcoming.length > 0 && (
                  <div>
                    <h3 className="text-lg font-bold mb-4 text-blue-600">Upcoming Events</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {eventsByStatus.upcoming.map((race: Race) => {
                        // Find the race event
                        const raceEvent = race.events.find((event: RaceEvent) => event.type === 'Race');
                        const raceDate = raceEvent ? formatDate(raceEvent.startTime) : 'Date TBD';

                        return (
                          <Card key={race.round} title={`Round ${race.round}`} className="h-full border-l-4 border-blue-600">
                            <div className="flex flex-col h-full">
                              <div className="mb-4">
                                <h3 className="text-lg font-semibold">{race.name}</h3>
                                <p className="text-gray-600">{race.location}, {race.country}</p>
                                <p className="text-gray-700 mt-2">
                                  <span className="font-medium">Race:</span> {raceDate}
                                </p>
                              </div>
                              
                              <div className="mt-auto">
                                <h4 className="font-medium text-sm text-gray-700 mb-2">Event Schedule</h4>
                                <ul className="space-y-2">
                                  {race.events.map((event: RaceEvent, index: number) => (
                                    <li key={index} className="flex justify-between text-sm">
                                      <span>{event.type}</span>
                                      <span className="text-gray-600">{formatDate(event.startTime)}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          </Card>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Past Events */}
                {eventsByStatus.past.length > 0 && (
                  <div>
                    <h3 className="text-lg font-bold mb-4 text-gray-600">Past Events</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {eventsByStatus.past.map((race: Race) => {
                        // Find the race event
                        const raceEvent = race.events.find((event: RaceEvent) => event.type === 'Race');
                        const raceDate = raceEvent ? formatDate(raceEvent.startTime) : 'Date TBD';

                        return (
                          <Card key={race.round} title={`Round ${race.round}`} className="h-full border-l-4 border-gray-400">
                            <div className="flex flex-col h-full">
                              <div className="mb-4">
                                <h3 className="text-lg font-semibold">{race.name}</h3>
                                <p className="text-gray-600">{race.location}, {race.country}</p>
                                <p className="text-gray-700 mt-2">
                                  <span className="font-medium">Race:</span> {raceDate}
                                </p>
                              </div>
                              
                              <div className="mt-auto">
                                <h4 className="font-medium text-sm text-gray-700 mb-2">Event Schedule</h4>
                                <ul className="space-y-2">
                                  {race.events.map((event: RaceEvent, index: number) => (
                                    <li key={index} className="flex justify-between text-sm">
                                      <span>{event.type}</span>
                                      <span className="text-gray-600">{formatDate(event.startTime)}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          </Card>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500">No race schedule data available.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
