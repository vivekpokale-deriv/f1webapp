"use client";

import { useState } from 'react';

interface DriverGridProps {
  drivers: any[];
  selectedDrivers: string[];
  onDriverSelect: (driver: string) => void;
}

export default function DriverGrid({ drivers, selectedDrivers, onDriverSelect }: DriverGridProps) {
  return (
    <div className="grid grid-cols-5 gap-2">
      {drivers.map(driver => (
        <button
          key={driver.driverId}
          onClick={() => onDriverSelect(driver.code)}
          className={`px-2 py-1 rounded-md text-xs font-medium ${
            selectedDrivers.includes(driver.code)
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300'
          }`}
        >
          {driver.code}
        </button>
      ))}
    </div>
  );
}
