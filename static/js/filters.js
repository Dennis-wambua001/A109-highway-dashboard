/**
 * Global Filters Synchronization Module
 */
const FilterModule = {
    init: function () {
        const updateAll = () => {
            const queryParams = this.getFilterQueryParams();
            MapModule.loadLayers(queryParams);
            StatisticsModule.updateKPIs(queryParams);
            ChartsModule.renderAll(queryParams);
        };

        document.getElementById('filterCounty').addEventListener('change', updateAll);
        document.getElementById('filterVehicle').addEventListener('change', updateAll);
        document.getElementById('filterEventType').addEventListener('change', updateAll);

        document.getElementById('resetFilters').addEventListener('click', () => {
            document.getElementById('filterCounty').value = '';
            document.getElementById('filterVehicle').value = '';
            document.getElementById('filterEventType').value = '';
            updateAll();
        });

        // Layer Toggles listener
        document.getElementById('layerDangerous').addEventListener('change', (e) => MapModule.toggleLayer('dangerous', e.target.checked));
        document.getElementById('layerIncidents').addEventListener('change', (e) => MapModule.toggleLayer('incidents', e.target.checked));
        document.getElementById('layerRoads').addEventListener('change', (e) => MapModule.toggleLayer('roads', e.target.checked));
        document.getElementById('layerHillshade').addEventListener('change', (e) => MapModule.toggleLayer('hillshade', e.target.checked));
        document.getElementById('layerSlope').addEventListener('change', (e) => MapModule.toggleLayer('slope', e.target.checked));
    },

    getFilterQueryParams: function () {
        const county = document.getElementById('filterCounty').value;
        const vehicle = document.getElementById('filterVehicle').value;
        const eventType = document.getElementById('filterEventType').value;

        const params = new URLSearchParams();
        if (county) params.append('county', county);
        if (vehicle) params.append('vehicle', vehicle);
        if (eventType) params.append('event_type', eventType);

        const queryString = params.toString();
        return queryString ? `?${queryString}` : '';
    }
};