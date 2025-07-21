"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import PageHeader from "./components/PageHeader";
import Card from "./components/Card";
import Button from "./components/Button";

interface RaceEvent {
  type: string;
  startTime: string;
}

interface NextRace {
  name: string;
  round: number;
  country: string;
  location: string;
  events: RaceEvent[];
}

export default function Home() {
  const [nextRace, setNextRace] = useState<NextRace | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load next race information
  useEffect(() => {
    const fetchNextRace = async () => {
      try {
        const response = await fetch('/api/info/next-event');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.success && data.data) {
          setNextRace(data.data);
        } else {
          throw new Error('Invalid data structure');
        }
      } catch (error) {
        console.error('Error loading next race:', error);
        setNextRace(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNextRace();
  }, []);

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZoneName: 'short'
    });
  };
  return (
    <div>
      <PageHeader 
        title="F1 Data Visualization" 
        description="Interactive Formula 1 data analysis and visualization"
      />
      
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Card title="Telemetry">
            <div className="flex flex-col h-full">
              <h3 className="text-xl font-semibold mb-2">Driver Telemetry</h3>
              <p className="text-gray-600 mb-4 flex-grow">
                Compare speed traces, gear shifts, and track dominance between drivers.
                Analyze detailed telemetry data from any F1 session.
              </p>
              <Button href="/telemetry">Explore Telemetry</Button>
            </div>
          </Card>
          
          <Card title="Race Analysis">
            <div className="flex flex-col h-full">
              <h3 className="text-xl font-semibold mb-2">Race Performance</h3>
              <p className="text-gray-600 mb-4 flex-grow">
                Analyze race pace, team pace, and lap sections.
                Get insights into race strategies and performance.
              </p>
              <Button href="/race-analysis">Explore Race Analysis</Button>
            </div>
          </Card>
          
          <Card title="Information">
            <div className="flex flex-col h-full">
              <h3 className="text-xl font-semibold mb-2">F1 Information</h3>
              <p className="text-gray-600 mb-4 flex-grow">
                View driver standings, constructor standings, and race schedules.
                Stay updated with the latest Formula 1 information.
              </p>
              <Button href="/information">Explore Information</Button>
            </div>
          </Card>
        </div>
        
        <Card title="Next Race" className="mb-12">
          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#e10600]"></div>
            </div>
          ) : nextRace ? (
            <div className="flex flex-col md:flex-row">
              <div className="md:w-1/2 mb-4 md:mb-0 md:pr-4">
                <h3 className="text-xl font-semibold mb-2">{nextRace.name}</h3>
                <p className="text-gray-600 mb-2">
                  <strong>Location:</strong> {nextRace.location}, {nextRace.country}
                </p>
                <p className="text-gray-600 mb-2">
                  <strong>Round:</strong> {nextRace.round}
                </p>
                {nextRace.events.find(event => event.type === 'Race') && (
                  <p className="text-gray-600 mb-4">
                    <strong>Race Date:</strong> {formatDate(nextRace.events.find(event => event.type === 'Race')!.startTime)}
                  </p>
                )}
                <Button href="/information">View Full Schedule</Button>
              </div>
              
              <div className="md:w-1/2 md:pl-4 border-t md:border-t-0 md:border-l border-gray-200 pt-4 md:pt-0 md:pl-8">
                <h4 className="font-semibold mb-2">Event Schedule</h4>
                <ul className="space-y-2">
                  {nextRace.events.map((event, index) => (
                    <li key={index} className="flex justify-between">
                      <span>{event.type}</span>
                      <span className="text-gray-600">{formatDate(event.startTime)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500">No upcoming race information available.</p>
              <Button href="/information" className="mt-4">View Full Schedule</Button>
            </div>
          )}
        </Card>
        
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-6">Formula 1 Data Analysis Platform</h2>
          <p className="text-gray-600 max-w-3xl mx-auto mb-8">
            This platform provides interactive visualizations and analysis of Formula 1 data,
            including telemetry, race analysis, and information about drivers, teams, and schedules.
            Built with Next.js and powered by FastF1.
          </p>
          <div className="flex justify-center gap-4">
            <Button href="/telemetry">Get Started</Button>
            <Button href="https://github.com" variant="outline">View on GitHub</Button>
          </div>
        </div>
      </div>
    </div>
  );
}
