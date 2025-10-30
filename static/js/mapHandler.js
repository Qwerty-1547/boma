console.log("map handler triggered")
document.addEventListener("sectionLoaded", () => {
    const panel = document.getElementById("house-detail-panel");

    if(!panel) return;

    panel.addEventListener('click', (event) => {
        const btn = event.target.closest('#view-map-btn');
        if(!btn) return;

        console.log("view map button clicked");

        const lat = parseFloat(btn.dataset.lat);
        const lng = parseFloat(btn.dataset.lng);


        if(!lat || !lng) {
            showToast("Coordinates for this house are not available", 'error');
            return;
        }

        const mapFrame = document.getElementById("map-frame");
        const streetFrame = document.getElementById('street-view-frame');
        const mapContainer = document.getElementById('map-container');

        if(!mapFrame || !streetFrame || !mapContainer) {
            console.error("map elements not found in DOM");
            return;
        }
        mapFrame.src = `https://www.google.com/maps?q=${lat},${lng}&z=15&output=embed`;
        streetFrame.src = `https://www.google.com/maps?q=&layer=c&cbll=${lat},${lng}&cbp=11,0,0,0,0&output=svembed`;

        mapContainer.style.display = 'block';
        setTimeout(() => mapContainer.classList.add('show'), 20);
        mapContainer.scrollIntoView({ behavior: 'smooth'});
    });
});