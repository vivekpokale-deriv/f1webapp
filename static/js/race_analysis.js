/**
 * F1 Race Analysis JavaScript Module
 * 
 * This module provides functions for fetching and visualizing F1 race analysis data.
 */

console.log('Loading F1RaceAnalysis module...');

const F1RaceAnalysis = (function() {
    // Store chart instances for cleanup
    const chartInstances = {};
    
    /**
     * Fetch race pace data from the API.
     * 
     * @param {number} year - The year of the race
     * @param {string} race - The race name
     * @param {string} drivers - Optional comma-separated list of driver codes
     * @returns {Promise<Object>} - The race pace data
     */
    async function fetchRacePaceData(year, race, drivers = '') {
        let url = `/api/race-analysis/race-pace/${year}/${race}`;
        if (drivers) {
            url += `?drivers=${drivers}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to fetch race pace data');
        }
        
        return data.data;
    }
    
    /**
     * Visualize race pace data using Chart.js.
     * 
     * @param {Object} data - The race pace data
     * @param {string} chartId - The ID of the canvas element
     */
    function visualizeRacePace(data, chartId) {
        const canvas = document.getElementById(chartId);
        if (!canvas) {
            console.error(`Canvas element with ID ${chartId} not found`);
            return;
        }
        
        // Make sure the canvas has dimensions
        if (!canvas.width || !canvas.height) {
            canvas.width = canvas.parentNode.clientWidth;
            canvas.height = canvas.parentNode.clientHeight;
        }
        
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error(`Could not get 2D context for canvas ${chartId}`);
            return;
        }
        
        // Clean up existing chart
        if (chartInstances[chartId]) {
            chartInstances[chartId].destroy();
        }
        
        // Prepare data for violin plot-like visualization
        const datasets = [];
        const labels = [];
        
        // Create a dataset for each driver
        data.drivers.forEach(driver => {
            labels.push(driver.code);
            
            // Create scatter plot data points
            const scatterData = [];
            for (let i = 0; i < driver.lapTimes.length; i++) {
                const lapTime = driver.lapTimes[i];
                const compound = driver.compounds[i];
                
                // Add jitter to x position for better visualization
                const jitter = (Math.random() - 0.5) * 0.4;
                
                scatterData.push({
                    x: labels.length - 1 + jitter,
                    y: lapTime,
                    compound: compound
                });
            }
            
            // Add dataset for this driver
            datasets.push({
                label: driver.name,
                data: scatterData,
                backgroundColor: getCompoundColors(driver.compounds),
                borderColor: driver.color,
                borderWidth: 1,
                pointRadius: 5,
                pointHoverRadius: 7
            });
        });
        
        // Create the chart
        chartInstances[chartId] = new Chart(ctx, {
            type: 'scatter',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        min: -0.5,
                        max: labels.length - 0.5,
                        ticks: {
                            callback: function(value) {
                                return labels[Math.round(value)];
                            },
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: 'Driver'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Lap Time (s)'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const point = context.raw;
                                const driver = data.drivers[Math.round(point.x)];
                                return `${driver.name}: ${point.y.toFixed(3)}s (${point.compound})`;
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: `Race Pace Comparison - ${data.session.name} ${data.session.year}`
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    /**
     * Fetch team pace data from the API.
     * 
     * @param {number} year - The year of the race
     * @param {string} race - The race name
     * @returns {Promise<Object>} - The team pace data
     */
    async function fetchTeamPaceData(year, race) {
        const response = await fetch(`/api/race-analysis/team-pace/${year}/${race}`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to fetch team pace data');
        }
        
        return data.data;
    }
    
    /**
     * Visualize team pace data using Chart.js.
     * 
     * @param {Object} data - The team pace data
     * @param {string} chartId - The ID of the canvas element
     */
    function visualizeTeamPace(data, chartId) {
        const canvas = document.getElementById(chartId);
        if (!canvas) {
            console.error(`Canvas element with ID ${chartId} not found`);
            return;
        }
        
        // Make sure the canvas has dimensions
        if (!canvas.width || !canvas.height) {
            canvas.width = canvas.parentNode.clientWidth;
            canvas.height = canvas.parentNode.clientHeight;
        }
        
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error(`Could not get 2D context for canvas ${chartId}`);
            return;
        }
        
        // Clean up existing chart
        if (chartInstances[chartId]) {
            chartInstances[chartId].destroy();
        }
        
        // Prepare data for box plot visualization
        const labels = [];
        const boxplotData = [];
        const colors = [];
        
        // Process each team
        data.teams.forEach(team => {
            labels.push(team.name);
            boxplotData.push({
                min: team.lapTimes.min,
                q1: team.lapTimes.q1,
                median: team.lapTimes.median,
                q3: team.lapTimes.q3,
                max: team.lapTimes.max
            });
            colors.push(team.color);
        });
        
        // Create custom box plot using Chart.js
        chartInstances[chartId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    // Min to Max line
                    {
                        label: 'Min to Max',
                        data: boxplotData.map((bp, i) => ({
                            x: i,
                            y: bp.min,
                            yMax: bp.max
                        })),
                        backgroundColor: 'rgba(0,0,0,0)',
                        borderColor: colors,
                        borderWidth: 2,
                        type: 'line'
                    },
                    // Q1 to Q3 box
                    {
                        label: 'Q1 to Q3',
                        data: boxplotData.map(bp => bp.q3 - bp.q1),
                        backgroundColor: colors.map(c => `${c}80`), // Add transparency
                        borderColor: colors,
                        borderWidth: 1,
                        barPercentage: 0.3,
                        categoryPercentage: 1,
                        base: boxplotData.map(bp => bp.q1)
                    },
                    // Median line
                    {
                        label: 'Median',
                        data: boxplotData.map((bp, i) => ({
                            x: i,
                            y: bp.median
                        })),
                        backgroundColor: 'rgba(0,0,0,0)',
                        borderColor: '#FFFFFF',
                        borderWidth: 2,
                        type: 'line',
                        pointStyle: 'line',
                        pointBorderWidth: 10,
                        pointBorderColor: '#FFFFFF'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Team'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Lap Time (s)'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const datasetIndex = context.datasetIndex;
                                const index = context.dataIndex;
                                const bp = boxplotData[index];
                                const team = labels[index];
                                
                                if (datasetIndex === 0) {
                                    return [
                                        `${team}`,
                                        `Min: ${bp.min.toFixed(3)}s`,
                                        `Max: ${bp.max.toFixed(3)}s`
                                    ];
                                } else if (datasetIndex === 1) {
                                    return [
                                        `${team}`,
                                        `Q1: ${bp.q1.toFixed(3)}s`,
                                        `Q3: ${bp.q3.toFixed(3)}s`
                                    ];
                                } else {
                                    return [
                                        `${team}`,
                                        `Median: ${bp.median.toFixed(3)}s`
                                    ];
                                }
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: `Team Pace Comparison - ${data.session.name} ${data.session.year}`
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    /**
     * Fetch lap sections data from the API.
     * 
     * @param {number} year - The year of the race
     * @param {string} race - The race name
     * @param {string} session - The session type
     * @param {string} drivers - Optional comma-separated list of driver codes
     * @returns {Promise<Object>} - The lap sections data
     */
    async function fetchLapSectionsData(year, race, session, drivers = '') {
        let url = `/api/race-analysis/lap-sections/${year}/${race}/${session}`;
        if (drivers) {
            url += `?drivers=${drivers}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to fetch lap sections data');
        }
        
        return data.data;
    }
    
    /**
     * Visualize lap sections data using Chart.js.
     * 
     * @param {Object} data - The lap sections data
     */
    function visualizeLapSections(data) {
        // Map section names to chart IDs
        const sectionChartIds = {
            'braking': 'braking-chart',
            'cornering': 'cornering-chart',
            'acceleration': 'acceleration-chart',
            'full_throttle': 'full-throttle-chart'
        };
        
        // Process each section
        data.sections.forEach(section => {
            const chartId = sectionChartIds[section.name];
            if (!chartId) return;
            
            const canvas = document.getElementById(chartId);
            if (!canvas) {
                console.error(`Canvas element with ID ${chartId} not found`);
                return;
            }
            
            // Make sure the canvas has dimensions
            if (!canvas.width || !canvas.height) {
                canvas.width = canvas.parentNode.clientWidth;
                canvas.height = canvas.parentNode.clientHeight;
            }
            
            const ctx = canvas.getContext('2d');
            if (!ctx) {
                console.error(`Could not get 2D context for canvas ${chartId}`);
                return;
            }
            
            // Clean up existing chart
            if (chartInstances[chartId]) {
                chartInstances[chartId].destroy();
            }
            
            // Prepare datasets
            const datasets = section.drivers.map(driver => ({
                label: driver.code,
                data: driver.speed.map((speed, i) => ({
                    x: driver.time[i],
                    y: speed
                })),
                borderColor: driver.color,
                backgroundColor: `${driver.color}20`,
                borderWidth: 2,
                fill: false,
                tension: 0.4
            }));
            
            // Create the chart
            chartInstances[chartId] = new Chart(ctx, {
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
                            position: 'bottom',
                            title: {
                                display: true,
                                text: 'Time (s)'
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
                            display: false
                        }
                    }
                }
            });
        });
    }
    
    /**
     * Get colors for tire compounds.
     * 
     * @param {Array<string>} compounds - Array of tire compound names
     * @returns {Array<string>} - Array of colors
     */
    function getCompoundColors(compounds) {
        const compoundColors = {
            'SOFT': '#FF3333',
            'MEDIUM': '#FFCC33',
            'HARD': '#FFFFFF',
            'INTERMEDIATE': '#33CC33',
            'WET': '#3333FF'
        };
        
        return compounds.map(compound => compoundColors[compound] || '#CCCCCC');
    }
    
    // Public API
    return {
        chartInstances,
        fetchRacePaceData,
        visualizeRacePace,
        fetchTeamPaceData,
        visualizeTeamPace,
        fetchLapSectionsData,
        visualizeLapSections
    };
})();

// Export to window object
window.F1RaceAnalysis = F1RaceAnalysis;
