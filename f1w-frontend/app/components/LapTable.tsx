"use client";

import { useState } from 'react';

interface LapTableProps {
  laps: any[];
  selectedDrivers: string[];
  onLapSelect: (lap: any) => void;
}

export default function LapTable({ laps, selectedDrivers, onLapSelect }: LapTableProps) {
  return (
    <div className="mt-4 overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-700">
        <thead className="bg-gray-800">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Lap</th>
            {selectedDrivers.map(driver => (
              <th key={driver} className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">{driver}</th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-gray-900 divide-y divide-gray-700">
          {Array.from(new Set(laps.map(l => l.lapNumber))).map(lapNumber => (
            <tr key={lapNumber}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">{lapNumber}</td>
              {selectedDrivers.map(driver => {
                const lap = laps.find(l => l.driverCode === driver && l.lapNumber === lapNumber);
                return (
                  <td key={`${driver}-${lapNumber}`} className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    <button onClick={() => onLapSelect(lap)} className="w-full text-left">
                      {lap && lap.lapTime ? lap.lapTime.toFixed(3) : 'N/A'}
                    </button>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
