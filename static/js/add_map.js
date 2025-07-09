document.addEventListener('sectionLoaded', () => {
    console.log("✅ add_map.js loaded and sectionLoaded triggered");

    const mapDiv = document.getElementById('map');
    if(!mapDiv || typeof L === 'undefined') return;

    //avoid reinitializing the map if already done
    if(mapDiv.dataset.initialized) return;
    mapDiv.dataset.initialized = 'true';

    //default center Nairobi
    const defaultLat = -1.286389;
    const defaultLng = 36.817223;
    const map = L.map('map').setView([defaultLat, defaultLng], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution:
        '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
    }).addTo(map);

    let marker;
    map.on('click', function (e){
        const {lat, lng } = e.latlng;

        if(marker) {
            marker.setLatLng(e.latlng);
        }else{
            marker = L.marker(e.latlng).addTo(map);
        }

        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lng;

        const streetViewUrl = `https://www.google.com/maps?q=&layer=c&cbll=${lat},${lng}&cbp=11,0,0,0,0&output=svembed`;
        const streetViewFrame = document.getElementById('street-view-frame');

        if(streetViewFrame) {
            streetViewFrame.src = streetViewUrl;
            streetViewFrame.style.display = 'block';
            console.log("street vew updated", streetViewUrl);
        }
    })
})