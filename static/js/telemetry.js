/**
 * F1 Web App - Telemetry Visualization
 * 
 * This file contains functions for fetching and visualizing F1 telemetry data.
 */

// API base URL
const API_BASE_URL = '/api';

/**
 * Fetch speed trace data for two drivers
 * 
 * @param {number} year - Year of the session
 * @param {string} race - Race name or round number
 * @param {string} session - Session type (e.g., 'R', 'Q', 'FP1')
 * @param {string} driver1 - First driver code
 * @param {string} driver2 - Second driver code
 * @returns {Promise} - Promise that resolves to speed trace data
 */
async function fetchSpeedTraceData(year, race, session, driver1, driver2) {
    try {
        const response = await fetch(`${API_BASE_URL}/telemetry/speed-trace/${year}/${race}/${session}/${driver1}/${driver2}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data.data;
    } catch (error) {
        console.error('Error fetching speed trace data:', error);
        throw error;
    }
}

// Store chart instances for cleanup
let chartInstances = {};

/**
 * Visualize speed trace data using Chart.js
 * 
 * @param {Object} data - Speed trace data
 * @param {string} canvasId - ID of the canvas element to render the chart
 */
function visualizeSpeedTrace(data, canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas element with ID ${canvasId} not found`);
        return;
    }
    
    // Destroy existing chart if it exists
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
        delete chartInstances[canvasId];
    }
    
    const ctx = canvas.getContext('2d');
    
    try {
        // Validate data
        if (!data || !data.driver1 || !data.driver2 || !data.circuit || !data.session) {
            console.error('Invalid speed trace data structure:', data);
            return;
        }
        
        // Create datasets for the chart
        const datasets = [
            {
                label: `${data.driver1.name} - ${data.driver1.lapTime}`,
                data: data.driver1.distance.map((d, i) => ({ 
                    x: isNaN(d) ? null : d, 
                    y: isNaN(data.driver1.speed[i]) ? null : data.driver1.speed[i] 
                })).filter(point => point.x !== null && point.y !== null),
                borderColor: data.driver1.color,
                backgroundColor: 'transparent',
                borderWidth: 2,
                pointRadius: 0,
                tension: 0.1
            },
            {
                label: `${data.driver2.name} - ${data.driver2.lapTime}`,
                data: data.driver2.distance.map((d, i) => ({ 
                    x: isNaN(d) ? null : d, 
                    y: isNaN(data.driver2.speed[i]) ? null : data.driver2.speed[i] 
                })).filter(point => point.x !== null && point.y !== null),
                borderColor: data.driver2.color,
                backgroundColor: 'transparent',
                borderWidth: 2,
                pointRadius: 0,
                tension: 0.1
            }
        ];
        
        // Add vertical lines for corners
        const cornerAnnotations = data.circuit.corners
            .filter(corner => !isNaN(corner.distance))
            .map(corner => ({
                type: 'line',
                mode: 'vertical',
                scaleID: 'x',
                value: corner.distance,
                borderColor: 'rgba(128, 128, 128, 0.5)',
                borderWidth: 1,
                borderDash: [5, 5],
                label: {
                    content: `${corner.number}${corner.letter}`,
                    enabled: true,
                    position: 'bottom'
                }
            }));
        
        // Create the chart
        chartInstances[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'linear',
                        title: {
                            display: true,
                            text: 'Distance (m)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Speed (km/h)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: `Speed Trace - ${data.session.name} ${data.session.year}`
                    },
                    annotation: {
                        annotations: cornerAnnotations
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating speed trace chart:', error);
    }
}

/**
 * Fetch gear shift data for a driver
 * 
 * @param {number} year - Year of the session
 * @param {string} race - Race name or round number
 * @param {string} session - Session type (e.g., 'R', 'Q', 'FP1')
 * @param {string} driver - Driver code
 * @returns {Promise} - Promise that resolves to gear shift data
 */
async function fetchGearShiftData(year, race, session, driver) {
    try {
        const response = await fetch(`${API_BASE_URL}/telemetry/gear-shifts/${year}/${race}/${session}/${driver}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data.data;
    } catch (error) {
        console.error('Error fetching gear shift data:', error);
        throw error;
    }
}

/**
 * Visualize gear shift data for a single driver using D3.js
 * 
 * @param {Object} data - Gear shift data
 * @param {string} svgId - ID of the SVG element to render the visualization
 * @param {number} customWidth - Optional custom width for the visualization
 * @param {number} customHeight - Optional custom height for the visualization
 */
function visualizeGearShifts(data, svgId, customWidth, customHeight) {
    try {
        const svg = d3.select(`#${svgId}`);
        if (svg.empty()) {
            console.error(`SVG element with ID ${svgId} not found`);
            return;
        }
        
        // Clear the SVG
        svg.selectAll('*').remove();
        
        // Validate data
        if (!data || !data.track || !data.track.x || !data.track.y || !data.gears || !data.driver || !data.session) {
            console.error('Invalid gear shift data structure:', data);
            return;
        }
        
        // Set dimensions based on custom values or container size
        const containerWidth = customWidth || svg.node().parentNode.clientWidth;
        const containerHeight = customHeight || svg.node().parentNode.clientHeight;
        
        // Set SVG dimensions explicitly
        svg.attr('width', containerWidth)
           .attr('height', containerHeight);
        
        // Get dimensions
        const width = +svg.attr('width');
        const height = +svg.attr('height');
        
        // Update dimensions display if available
        const dimensionsDisplay = document.getElementById(`${svgId}-dimensions`);
        if (dimensionsDisplay) {
            dimensionsDisplay.textContent = `${width}×${height}`;
        }
        
        // Filter out NaN values
        const validTrackData = [];
        for (let i = 0; i < data.track.x.length; i++) {
            if (!isNaN(data.track.x[i]) && !isNaN(data.track.y[i])) {
                validTrackData.push({
                    x: data.track.x[i],
                    y: data.track.y[i],
                    gear: data.gears[i]
                });
            }
        }
        
        if (validTrackData.length < 2) {
            console.error('Not enough valid data points for visualization');
            return;
        }
        
        // Create scales
        const xScale = d3.scaleLinear()
            .domain(d3.extent(validTrackData, d => d.x))
            .range([20, width - 20]);
        
        const yScale = d3.scaleLinear()
            .domain(d3.extent(validTrackData, d => d.y))
            .range([height - 20, 20]);
        
        // Create a color scale for gears
        const colorScale = d3.scaleOrdinal()
            .domain([1, 2, 3, 4, 5, 6, 7, 8])
            .range(d3.schemeCategory10);
        
        // Create a line generator
        const line = d3.line()
            .x(d => xScale(d.x))
            .y(d => yScale(d.y))
            .defined(d => !isNaN(d.x) && !isNaN(d.y));
        
        // Draw the track outline
        svg.append('path')
            .datum(validTrackData)
            .attr('d', line)
            .attr('fill', 'none')
            .attr('stroke', '#333')
            .attr('stroke-width', 10);
        
        // Create segments for each gear
        for (let i = 0; i < validTrackData.length - 1; i++) {
            const current = validTrackData[i];
            const next = validTrackData[i + 1];
            
            // Skip if any coordinate is NaN
            if (isNaN(current.x) || isNaN(current.y) || isNaN(next.x) || isNaN(next.y)) {
                continue;
            }
            
            svg.append('line')
                .attr('x1', xScale(current.x))
                .attr('y1', yScale(current.y))
                .attr('x2', xScale(next.x))
                .attr('y2', yScale(next.y))
                .attr('stroke', colorScale(current.gear))
                .attr('stroke-width', 5);
        }
        
        // Add a title
        svg.append('text')
            .attr('x', width / 2)
            .attr('y', 20)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .text(`Gear Shifts - ${data.driver.name} - ${data.session.name} ${data.session.year}`);
        
        // Add a legend
        const legend = svg.append('g')
            .attr('transform', `translate(${width - 100}, 50)`);
        
        for (let i = 1; i <= 8; i++) {
            legend.append('rect')
                .attr('x', 0)
                .attr('y', (i - 1) * 20)
                .attr('width', 15)
                .attr('height', 15)
                .attr('fill', colorScale(i));
            
            legend.append('text')
                .attr('x', 20)
                .attr('y', (i - 1) * 20 + 12)
                .text(`Gear ${i}`)
                .style('font-size', '12px');
        }
    } catch (error) {
        console.error('Error creating gear shifts visualization:', error);
    }
}

/**
 * Visualize gear shift data for two drivers on a single SVG using D3.js
 * 
 * @param {Object} data1 - Gear shift data for driver 1
 * @param {Object} data2 - Gear shift data for driver 2
 * @param {string} svgId - ID of the SVG element to render the visualization
 * @param {number} customWidth - Optional custom width for the visualization
 * @param {number} customHeight - Optional custom height for the visualization
 */
function visualizeCombinedGearShifts(data1, data2, svgId, customWidth, customHeight) {
    try {
        const svg = d3.select(`#${svgId}`);
        if (svg.empty()) {
            console.error(`SVG element with ID ${svgId} not found`);
            return;
        }
        
        // Clear the SVG
        svg.selectAll('*').remove();
        
        // Validate data
        if (!data1 || !data1.track || !data1.track.x || !data1.track.y || !data1.gears || !data1.driver || !data1.session) {
            console.error('Invalid gear shift data structure for driver 1:', data1);
            return;
        }
        
        if (!data2 || !data2.track || !data2.track.x || !data2.track.y || !data2.gears || !data2.driver || !data2.session) {
            console.error('Invalid gear shift data structure for driver 2:', data2);
            return;
        }
        
        // Set dimensions based on custom values or container size
        const containerWidth = customWidth || svg.node().parentNode.clientWidth;
        const containerHeight = customHeight || svg.node().parentNode.clientHeight;
        
        // Set SVG dimensions explicitly
        svg.attr('width', containerWidth)
           .attr('height', containerHeight);
        
        // Get dimensions
        const width = +svg.attr('width');
        const height = +svg.attr('height');
        
        // Update dimensions display if available
        const dimensionsDisplay = document.getElementById(`${svgId}-dimensions`);
        if (dimensionsDisplay) {
            dimensionsDisplay.textContent = `${width}×${height}`;
        }
        
        // Process data for both drivers
        const processDriverData = (data) => {
            const validTrackData = [];
            for (let i = 0; i < data.track.x.length; i++) {
                if (!isNaN(data.track.x[i]) && !isNaN(data.track.y[i])) {
                    validTrackData.push({
                        x: data.track.x[i],
                        y: data.track.y[i],
                        gear: data.gears[i]
                    });
                }
            }
            return validTrackData;
        };
        
        const validTrackData1 = processDriverData(data1);
        const validTrackData2 = processDriverData(data2);
        
        if (validTrackData1.length < 2 || validTrackData2.length < 2) {
            console.error('Not enough valid data points for visualization');
            return;
        }
        
        // Calculate dimensions for each visualization
        const legendWidth = 120;
        const padding = 20;
        const vizWidth = (width - legendWidth - padding * 4) / 2;
        const vizHeight = height - padding * 2;
        
        // Create a color scale for gears
        const gearColorScale = d3.scaleOrdinal()
            .domain([1, 2, 3, 4, 5, 6, 7, 8])
            .range(d3.schemeCategory10);
        
        // Add a title for the entire visualization
        svg.append('text')
            .attr('x', width / 2)
            .attr('y', 20)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .text(`Gear Shifts Comparison - ${data1.session.name} ${data1.session.year}`);
        
        // Create a group for each driver's visualization and the legend
        const group1 = svg.append('g')
            .attr('transform', `translate(${padding}, ${padding + 20})`);
            
        const legendGroup = svg.append('g')
            .attr('transform', `translate(${padding * 2 + vizWidth}, ${padding + 50})`);
            
        const group2 = svg.append('g')
            .attr('transform', `translate(${padding * 3 + vizWidth + legendWidth}, ${padding + 20})`);
        
        // Function to draw a single driver's gear shifts
        const drawDriverGearShifts = (group, trackData, driver, vizWidth, vizHeight) => {
            // Find the extent of the data for scaling
            const xExtent = d3.extent(trackData, d => d.x);
            const yExtent = d3.extent(trackData, d => d.y);
            
            // Create scales for this visualization
            const xScale = d3.scaleLinear()
                .domain(xExtent)
                .range([0, vizWidth]);
            
            const yScale = d3.scaleLinear()
                .domain(yExtent)
                .range([vizHeight, 0]);
            
            // Create a line generator
            const line = d3.line()
                .x(d => xScale(d.x))
                .y(d => yScale(d.y))
                .defined(d => !isNaN(d.x) && !isNaN(d.y));
            
            // Draw the track outline
            group.append('path')
                .datum(trackData)
                .attr('d', line)
                .attr('fill', 'none')
                .attr('stroke', '#333')
                .attr('stroke-width', 6);
            
            // Draw gear segments
            for (let i = 0; i < trackData.length - 1; i++) {
                const current = trackData[i];
                const next = trackData[i + 1];
                
                // Skip if any coordinate is NaN
                if (isNaN(current.x) || isNaN(current.y) || isNaN(next.x) || isNaN(next.y)) {
                    continue;
                }
                
                group.append('line')
                    .attr('x1', xScale(current.x))
                    .attr('y1', yScale(current.y))
                    .attr('x2', xScale(next.x))
                    .attr('y2', yScale(next.y))
                    .attr('stroke', gearColorScale(current.gear))
                    .attr('stroke-width', 3);
            }
            
            // Add driver title
            group.append('text')
                .attr('x', vizWidth / 2)
                .attr('y', -5)
                .attr('text-anchor', 'middle')
                .style('font-size', '14px')
                .style('font-weight', 'bold')
                .attr('fill', driver.color)
                .text(`${driver.name} - ${driver.lapTime}`);
        };
        
        // Draw both visualizations
        drawDriverGearShifts(group1, validTrackData1, data1.driver, vizWidth, vizHeight);
        drawDriverGearShifts(group2, validTrackData2, data2.driver, vizWidth, vizHeight);
        
        // Add legend title
        legendGroup.append('text')
            .attr('x', legendWidth / 2)
            .attr('y', -10)
            .attr('text-anchor', 'middle')
            .style('font-size', '14px')
            .style('font-weight', 'bold')
            .text('Gears');
        
        // Add gear legend
        for (let i = 1; i <= 8; i++) {
            legendGroup.append('rect')
                .attr('x', (legendWidth - 40) / 2)
                .attr('y', (i - 1) * 20 + 10)
                .attr('width', 15)
                .attr('height', 15)
                .attr('fill', gearColorScale(i));
            
            legendGroup.append('text')
                .attr('x', (legendWidth - 40) / 2 + 25)
                .attr('y', (i - 1) * 20 + 22)
                .text(`Gear ${i}`)
                .style('font-size', '12px');
        }
    } catch (error) {
        console.error('Error creating combined gear shifts visualization:', error);
    }
}

/**
 * Fetch track dominance data for drivers
 * 
 * @param {number} year - Year of the session
 * @param {string} race - Race name or round number
 * @param {string} session - Session type (e.g., 'R', 'Q', 'FP1')
 * @param {Array} drivers - Array of driver codes
 * @returns {Promise} - Promise that resolves to track dominance data
 */
async function fetchTrackDominanceData(year, race, session, drivers = []) {
    try {
        const driversParam = drivers.length > 0 ? `?drivers=${drivers.join(',')}` : '';
        const response = await fetch(`${API_BASE_URL}/telemetry/track-dominance/${year}/${race}/${session}${driversParam}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data.data;
    } catch (error) {
        console.error('Error fetching track dominance data:', error);
        throw error;
    }
}

/**
 * Visualize track dominance data using D3.js
 * 
 * @param {Object} data - Track dominance data
 * @param {string} svgId - ID of the SVG element to render the visualization
 * @param {number} customWidth - Optional custom width for the visualization
 * @param {number} customHeight - Optional custom height for the visualization
 */
function visualizeTrackDominance(data, svgId, customWidth, customHeight) {
    try {
        const svg = d3.select(`#${svgId}`);
        if (svg.empty()) {
            console.error(`SVG element with ID ${svgId} not found`);
            return;
        }
        
        // Clear the SVG
        svg.selectAll('*').remove();
        
        // Validate data
        if (!data || !data.track || !data.track.x || !data.track.y || !data.miniSectors || !data.drivers || !data.session) {
            console.error('Invalid track dominance data structure:', data);
            return;
        }
        
        // Set dimensions based on custom values or container size
        let containerWidth = customWidth || svg.node().parentNode.clientWidth;
        let containerHeight = customHeight || svg.node().parentNode.clientHeight;
        
        // Enforce 2:3 aspect ratio (width:height)
        const aspectRatio = 2/3; // width:height
        
        // If custom dimensions are provided, respect them
        if (customWidth && customHeight) {
            // Use the provided dimensions directly
        } 
        // Otherwise calculate based on the aspect ratio
        else if (customWidth) {
            // Width is fixed, calculate height
            containerHeight = containerWidth / aspectRatio;
        } 
        else if (customHeight) {
            // Height is fixed, calculate width
            containerWidth = containerHeight * aspectRatio;
        } 
        else {
            // Neither is fixed, use container width and calculate height
            containerHeight = containerWidth / aspectRatio;
        }
        
        // Set SVG dimensions explicitly
        svg.attr('width', containerWidth)
           .attr('height', containerHeight);
        
        // Get dimensions
        const width = +svg.attr('width');
        const height = +svg.attr('height');
        
        // Update dimensions display if available
        const dimensionsDisplay = document.getElementById(`${svgId}-dimensions`);
        if (dimensionsDisplay) {
            dimensionsDisplay.textContent = `${width}×${height}`;
        }
        
        // Filter out NaN values from track data
        const validTrackData = [];
        for (let i = 0; i < data.track.x.length; i++) {
            if (!isNaN(data.track.x[i]) && !isNaN(data.track.y[i])) {
                validTrackData.push({
                    x: data.track.x[i],
                    y: data.track.y[i]
                });
            }
        }
        
        if (validTrackData.length < 2) {
            console.error('Not enough valid track data points for visualization');
            return;
        }
        
        // Create scales
        const xScale = d3.scaleLinear()
            .domain(d3.extent(validTrackData, d => d.x))
            .range([20, width - 20]);
        
        const yScale = d3.scaleLinear()
            .domain(d3.extent(validTrackData, d => d.y))
            .range([height - 20, 20]);
        
        // Create a line generator
        const line = d3.line()
            .x(d => xScale(d.x))
            .y(d => yScale(d.y))
            .defined(d => !isNaN(d.x) && !isNaN(d.y));
        
        // Draw the track outline
        svg.append('path')
            .datum(validTrackData)
            .attr('d', line)
            .attr('fill', 'none')
            .attr('stroke', '#333')
            .attr('stroke-width', 15);
        
        // Draw each mini-sector
        if (data.miniSectors && data.miniSectors.length > 0) {
            data.miniSectors.forEach(sector => {
                if (!sector || !sector.coordinates || !sector.coordinates.x || !sector.coordinates.y) {
                    return; // Skip invalid sectors
                }
                
                // Filter out NaN values from sector data
                const validSectorData = [];
                for (let i = 0; i < sector.coordinates.x.length; i++) {
                    if (!isNaN(sector.coordinates.x[i]) && !isNaN(sector.coordinates.y[i])) {
                        validSectorData.push({
                            x: sector.coordinates.x[i],
                            y: sector.coordinates.y[i]
                        });
                    }
                }
                
                if (validSectorData.length < 2) {
                    return; // Skip sectors with insufficient valid data
                }
                
                svg.append('path')
                    .datum(validSectorData)
                    .attr('d', line)
                    .attr('fill', 'none')
                    .attr('stroke', sector.color)
                    .attr('stroke-width', 8);
            });
        }
        
        // Add a title
        svg.append('text')
            .attr('x', width / 2)
            .attr('y', 20)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .text(`Track Dominance - ${data.session.name} ${data.session.year}`);
        
        // Add a legend
        if (data.drivers && data.drivers.length > 0) {
            const legend = svg.append('g')
                .attr('transform', `translate(${width - 150}, 50)`);
            
            data.drivers.forEach((driver, i) => {
                if (!driver || !driver.color) return;
                
                legend.append('rect')
                    .attr('x', 0)
                    .attr('y', i * 20)
                    .attr('width', 15)
                    .attr('height', 15)
                    .attr('fill', driver.color);
                
                legend.append('text')
                    .attr('x', 20)
                    .attr('y', i * 20 + 12)
                    .text(driver.code || '')
                    .style('font-size', '12px');
            });
        }
    } catch (error) {
        console.error('Error creating track dominance visualization:', error);
    }
}

/**
 * Update visualization size based on input fields
 * 
 * @param {string} svgId - ID of the SVG element to resize
 */
function updateVisualizationSize(svgId) {
    // Get width and height inputs
    const widthInput = document.getElementById(`${svgId}-width`);
    const heightInput = document.getElementById(`${svgId}-height`);
    
    if (!widthInput || !heightInput) {
        console.error(`Width or height input not found for ${svgId}`);
        return;
    }
    
    // Get values
    const width = parseInt(widthInput.value, 10);
    const height = parseInt(heightInput.value, 10);
    
    // Validate values
    if (isNaN(width) || isNaN(height) || width <= 0 || height <= 0) {
        console.error('Invalid width or height values');
        return;
    }
    
    // Get the SVG element
    const svg = document.getElementById(svgId);
    if (!svg) {
        console.error(`SVG element with ID ${svgId} not found`);
        return;
    }
    
    // Set new dimensions
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    
    // Update dimensions display
    const dimensionsDisplay = document.getElementById(`${svgId}-dimensions`);
    if (dimensionsDisplay) {
        dimensionsDisplay.textContent = `${width}×${height}`;
    }
    
    // Re-render the visualization with the new dimensions
    const year = document.getElementById('year').value;
    const race = document.getElementById('race').value;
    const session = document.getElementById('session').value;
    const driver1 = document.getElementById('driver1').value;
    const driver2 = document.getElementById('driver2').value;
    
    // Determine which visualization to update
    if (svgId === 'gear-shifts-svg') {
        // Fetch and visualize combined gear shifts data
        Promise.all([
            window.F1Telemetry.fetchGearShiftData(year, race, session, driver1),
            window.F1Telemetry.fetchGearShiftData(year, race, session, driver2)
        ])
        .then(([data1, data2]) => {
            window.F1Telemetry.visualizeCombinedGearShifts(data1, data2, svgId, width, height);
        })
        .catch(error => {
            console.error(`Error updating gear shifts visualization: ${error}`);
        });
    } else if (svgId === 'track-dominance-svg') {
        // Fetch and visualize track dominance data
        window.F1Telemetry.fetchTrackDominanceData(year, race, session, [driver1, driver2])
            .then(data => {
                window.F1Telemetry.visualizeTrackDominance(data, svgId, width, height);
            })
            .catch(error => {
                console.error(`Error updating track dominance visualization: ${error}`);
            });
    }
}

// Export functions and objects for use in other scripts
window.F1Telemetry = {
    fetchSpeedTraceData,
    visualizeSpeedTrace,
    fetchGearShiftData,
    visualizeGearShifts,
    visualizeCombinedGearShifts,
    fetchTrackDominanceData,
    visualizeTrackDominance,
    updateVisualizationSize,
    chartInstances  // Export chart instances for cleanup
};
