/**
 * Dynamic KPI Statistics Handler
 */
const StatisticsModule = {
    updateKPIs: function (params = "") {
        fetch(`/api/statistics${params}`)
            .then(res => res.json())
            .then(data => {
                document.getElementById("kpiDangerous").innerText = data.total_dangerous_places || 0;
                document.getElementById("kpiIncidents").innerText = data.total_incidents || 0;
                document.getElementById("kpiFatal").innerText = data.fatal_accidents || 0;
                document.getElementById("kpiNonFatal").innerText = data.non_fatal_accidents || 0;
                document.getElementById("kpiTraffic").innerText = data.traffic_jams || 0;
                document.getElementById("kpiBlackspots").innerText = data.blackspots || 0;
                document.getElementById("kpiRoadLength").innerText = `${data.total_road_length_km || 0} km`;
                document.getElementById("kpiCounties").innerText = data.counties_crossed || 0;
            });
    }
};