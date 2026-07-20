/**
 * Interactive Plotly Chart Generation
 */
const ChartsModule = {
    renderAll: function (params = "") {
        this.renderRoadLengthChart(params);
        this.renderAccidentsChart(params);
        this.renderVehiclesChart(params);
        this.renderTrafficChart(params);
    },

    renderRoadLengthChart: function (params) {
        fetch(`/api/chart/road_length${params}`)
            .then(res => res.json())
            .then(data => {
                if (!data || data.length === 0) {
                    Plotly.purge('chartRoadLength');
                    return;
                }

                const counties = data.map(d => d.County || 'Unknown');

                // Define stacked traces for road classifications
                const traceGround = {
                    x: counties,
                    y: data.map(d => d.Ground || 0),
                    name: 'Ground',
                    type: 'bar',
                    marker: { color: '#2A9D8F' }
                };

                const traceElevated = {
                    x: counties,
                    y: data.map(d => d.Elevated || 0),
                    name: 'Elevated',
                    type: 'bar',
                    marker: { color: '#2980B9' }
                };

                const traceEmbankment = {
                    x: counties,
                    y: data.map(d => d.Embankment || 0),
                    name: 'Embankment',
                    type: 'bar',
                    marker: { color: '#D35400' }
                };

                const layout = {
                    barmode: 'stack',
                    margin: { t: 10, b: 60, l: 50, r: 10 },
                    xaxis: { type: 'category', tickangle: -25 },
                    yaxis: { title: 'Length (km)' },
                    legend: { orientation: 'h', y: 1.15 }
                };

                Plotly.newPlot('chartRoadLength', [traceGround, traceElevated, traceEmbankment], layout, { responsive: true });
            })
            .catch(err => console.error("Error loading road length chart:", err));
    },

    renderAccidentsChart: function (params) {
        fetch(`/api/chart/accidents${params}`)
            .then(res => res.json())
            .then(data => {
                if (!data || data.length === 0) {
                    Plotly.purge('chartAccidents');
                    return;
                }

                const trace = {
                    x: data.map(d => d.County),
                    y: data.map(d => d.Count),
                    type: 'bar',
                    marker: { color: '#E74C3C' }
                };
                const layout = {
                    margin: { t: 10, b: 60, l: 40, r: 10 },
                    xaxis: { type: 'category', tickangle: -25 }
                };
                Plotly.newPlot('chartAccidents', [trace], layout, { responsive: true });
            })
            .catch(err => console.error("Error loading accidents chart:", err));
    },

    renderVehiclesChart: function (params) {
        fetch(`/api/chart/vehicles${params}`)
            .then(res => res.json())
            .then(data => {
                if (!data || data.length === 0) {
                    Plotly.purge('chartVehicles');
                    return;
                }

                const trace = {
                    x: data.map(d => d.Count),
                    y: data.map(d => d.Vehicle),
                    type: 'bar',
                    orientation: 'h',
                    marker: { color: '#3498DB' }
                };
                const layout = {
                    margin: { t: 10, b: 40, l: 120, r: 10 },
                    yaxis: { autorange: 'reversed' }
                };
                Plotly.newPlot('chartVehicles', [trace], layout, { responsive: true });
            })
            .catch(err => console.error("Error loading vehicles chart:", err));
    },

    renderTrafficChart: function (params) {
        fetch(`/api/chart/traffic${params}`)
            .then(res => res.json())
            .then(data => {
                if (!data || data.length === 0) {
                    Plotly.purge('chartTraffic');
                    return;
                }

                const counties = data.map(d => d.County);
                const trace1 = { x: counties, y: data.map(d => d.Accident || 0), name: 'Accident', type: 'bar', marker: { color: '#E67E22' } };
                const trace2 = { x: counties, y: data.map(d => d['Traffic Jam'] || 0), name: 'Traffic Jam', type: 'bar', marker: { color: '#F1C40F' } };

                const layout = {
                    barmode: 'group',
                    margin: { t: 10, b: 60, l: 40, r: 10 },
                    xaxis: { type: 'category', tickangle: -25 },
                    legend: { orientation: 'h', y: 1.15 }
                };
                Plotly.newPlot('chartTraffic', [trace1, trace2], layout, { responsive: true });
            })
            .catch(err => console.error("Error loading traffic chart:", err));
    }
};