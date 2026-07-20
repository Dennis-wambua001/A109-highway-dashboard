/**
 * Layer Management & Categorized Symbology
 */
const LayerManager = {
    getPointMarker: function (feature, latlng) {
        const props = feature ? (feature.properties || {}) : {};
        
        // Read 'Event Type' (with space) or fallback to 'Event_Type'
        const eventType = (props['Event Type'] || props.Event_Type || '').toString().toLowerCase();
        const remarks = (props.Remarks || '').toString().toLowerCase();

        let color = '#3498DB'; // Default Blue (Dangerous Place)

        // Classify based on Event Type & Remarks text
        if (eventType.includes('fatal') || remarks.includes('fatal')) {
            color = '#E74C3C'; // Red: Fatal Accident
        } else if (eventType.includes('accident') || remarks.includes('accident') || remarks.includes('injury')) {
            color = '#F39C12'; // Orange: Non-Fatal Accident
        } else if (eventType.includes('jam') || eventType.includes('traffic')) {
            color = '#F1C40F'; // Yellow: Traffic Jam
        } else if (eventType.includes('blackspot') || eventType.includes('danger')) {
            color = '#2ECC71'; // Green: Blackspot
        }

        return L.circleMarker(latlng, {
            radius: 7,
            fillColor: color,
            color: '#FFFFFF',
            weight: 1.5,
            opacity: 1,
            fillOpacity: 0.85
        });
    },

    getRoadStyle: function (feature) {
        if (!feature || !feature.properties) {
            return { color: '#2a9d8f', weight: 3, opacity: 0.85 };
        }
        
        const props = feature.properties;
        const level = (props['Road Level'] || props.Road_Level || props.Road_Type || '').toString().trim().toLowerCase();

        let color = '#2a9d8f'; // Ground / At Grade: Teal
        let weight = 3;

        if (level === 'bridge') {
           color = '#e63946'; // Bridge: Red
           weight = 5;
        } else if (level === 'elevated') {
           color = '#2980b9'; // Elevated: Blue
           weight = 4;
        } else if (level === 'embankment') {
           color = '#d35400'; // Embankment: Orange/Brown
           weight = 4;
        }

        return {
           color: color,
           weight: weight,
           opacity: 0.85
        };
    }
};