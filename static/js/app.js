/**
 * Main Application Entrance
 */
document.addEventListener('DOMContentLoaded', function () {
    // 1. Initialize Map
    MapModule.init();

    // 2. Load Layers, KPIs & Analytics
    MapModule.loadLayers();
    StatisticsModule.updateKPIs();
    ChartsModule.renderAll();

    // 3. Initialize Filters & Event Listeners
    FilterModule.init();
});