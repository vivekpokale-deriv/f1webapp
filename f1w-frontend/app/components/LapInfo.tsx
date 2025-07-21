"use client";

import { useState } from 'react';

interface LapInfoProps {
  lap: any;
}

export default function LapInfo({ lap }: LapInfoProps) {
  if (!lap) {
    return null;
  }

  const formatTime = (timeInSeconds: number) => {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    const milliseconds = Math.round((timeInSeconds - (minutes * 60) - seconds) * 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{lap.driverCode} - Lap {lap.lapNumber}</p>
          <p className="text-2xl font-bold text-white">{formatTime(lap.lapTime)}</p>
        </div>
        <div>
          <img src={`/tyres/${lap.compound.toLowerCase()}.png`} alt={lap.compound} className="w-12 h-12" />
        </div>
      </div>
    </div>
  );
}
