/**
 * Generates custom HTML Popups for Map Layers
 */
const PopupHandler = {
    createFeaturePopup: function (properties) {
        let content = `<div class="p-1">`;
        content += `<h6 class="fw-bold border-bottom pb-1 mb-2">${properties.Location || 'Location N/A'}</h6>`;
        content += `<table class="table table-sm table-borderless mb-0 small">`;
        
        if (properties.County) content += `<tr><th>County:</th><td>${properties.County}</td></tr>`;
        if (properties.Road_Section) content += `<tr><th>Road Section:</th><td>${properties.Road_Section}</td></tr>`;
        if (properties.Event_Type) content += `<tr><th>Event Type:</th><td><span class="badge bg-secondary">${properties.Event_Type}</span></td></tr>`;
        if (properties.Vehicle) content += `<tr><th>Vehicle:</th><td>${properties.Vehicle}</td></tr>`;
        if (properties.Severity) content += `<tr><th>Severity:</th><td>${properties.Severity}</td></tr>`;
        
        content += `<tr><th>Date:</th><td>${properties.Date || 'N/A'}</td></tr>`;
        if (properties.Remarks) content += `<tr><th>Remarks:</th><td>${properties.Remarks}</td></tr>`;
        if (properties.Source) content += `<tr><th>Source:</th><td><small class="text-muted">${properties.Source}</small></td></tr>`;
        
        content += `</table></div>`;
        return content;
    }
};