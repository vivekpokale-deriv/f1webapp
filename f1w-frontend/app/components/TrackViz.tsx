"use client";

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface TrackVizProps {
  data: any;
  type: 'gear-shift' | 'track-dominance';
  width?: number;
  height?: number;
  className?: string;
}

export default function TrackViz({
  data,
  type,
  width = 800,
  height = 600,
  className = ''
}: TrackVizProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (svgRef.current && data) {
      const svg = d3.select(svgRef.current);
      svg.selectAll("*").remove(); // Clear previous render

      if (type === 'gear-shift') {
        renderGearShift(svg, data, width, height);
      } else if (type === 'track-dominance') {
        renderTrackDominance(svg, data, width, height);
      }
    }
  }, [data, type, width, height]);

const renderGearShift = (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, data: any, width: number, height: number) => {
  const track = data.track;
  const gears = data.gears;

  const xValues = track.x.map(Number).filter((d: number) => !isNaN(d));
  const yValues = track.y.map(Number).filter((d: number) => !isNaN(d));
  const gearValues = gears.map(Number).filter((d: number) => !isNaN(d)); // Ensure gears are also numbers

  if (xValues.length === 0 || yValues.length === 0 || gearValues.length === 0 ||
      xValues.length !== yValues.length || xValues.length !== gearValues.length) {
    // Add more specific warnings for debugging
    console.warn("Gear shift data is incomplete or inconsistent.", { xValues, yValues, gearValues });
    return;
  }

  // Directly pass xValues and yValues.
  // We can confidently assert as [number, number] because we've already checked that
  // the arrays are not empty. d3.extent will return numbers for non-empty number arrays.
  const xDomain = d3.extent(xValues).map(Number) as [number, number];
  const yDomain = d3.extent(yValues).map(Number) as [number, number];

    const x = d3.scaleLinear().domain(xDomain as [number, number]).range([20, width - 20]);
    const y = d3.scaleLinear().domain(yDomain as [number, number]).range([height - 20, 20]);

    const line = d3.line<{x: number, y: number}>()
      .x(d => x(d.x))
      .y(d => y(d.y));

    const color = d3.scaleSequential(d3.interpolateTurbo).domain([1, 8]);

    svg.append("g")
      .selectAll("path")
      .data(d3.pairs(track.x.map((_: any, i: number) => ({x: track.x[i], y: track.y[i], gear: gears[i]}))))
      .enter()
      .append("path")
      .attr("d", (d: any) => line(d))
      .attr("stroke", (d: any) => color(d[0].gear))
      .attr("stroke-width", 2);
  };

  const renderTrackDominance = (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, data: any, width: number, height: number) => {
    const track = data.track;
    const miniSectors = data.miniSectors;

    const xValues = track.x.map(Number).filter((d: number) => !isNaN(d));
    const yValues = track.y.map(Number).filter((d: number) => !isNaN(d));

    if (xValues.length === 0 || yValues.length === 0) {
      return;
    }

  const xDomain = d3.extent(xValues).map(Number) as [number, number];
  const yDomain = d3.extent(yValues).map(Number) as [number, number];

    const x = d3.scaleLinear().domain(xDomain as [number, number]).range([20, width - 20]);
    const y = d3.scaleLinear().domain(yDomain as [number, number]).range([height - 20, 20]);

    const line = d3.line<{x: number, y: number}>()
      .x(d => x(d.x))
      .y(d => y(d.y));

    svg.append("g")
      .selectAll("path")
      .data(miniSectors)
      .enter()
      .append("path")
      .attr("d", (d: any) => line(d.coordinates.x.map((_: any, i: number) => ({x: d.coordinates.x[i], y: d.coordinates.y[i]}))))
      .attr("stroke", (d: any) => d.color)
      .attr("stroke-width", 5);
  };

  return (
    <div className={`track-viz-container ${className}`} style={{ width: `${width}px`, height: `${height}px` }}>
      <svg ref={svgRef} width={width} height={height}></svg>
    </div>
  );
}
