function showHouseDetailFromBase64(el) {
    try {
        const base64 = el.getAttribute("data-house");
        //console.log("RAW  data-house: ", json)
        const jsonString = atob(base64);
        const house = JSON.parse(jsonString);
        showHouseDetail(house);
    } catch (err) {
        console.error("Invalid house JSON:", err);
    }
}


function showHouseDetail(house) {
    console.log('Selected house:', house); // ✅ Logging house for debug

    // Fill panel content
    document.getElementById("detail-title").textContent = house.title;
    document.getElementById("detail-desc").textContent = house.description;
    document.getElementById("detail-price").textContent = parseInt(house.price).toLocaleString();
    document.getElementById("detail-area").textContent = house.area_name;
    document.getElementById("detail-owner").textContent = house.owner_name;
    document.getElementById("detail-contact").textContent = house.owner_contact;
    document.getElementById("detail-verified").textContent = house.owner_verified ? "Yes" : "No";

    // Show the panel
    const panel = document.getElementById("house-detail-panel");
    panel.classList.remove("hidden");
    panel.classList.add("show");

    // Reset images (if you want to later support multiple images)
    const imageDiv = document.getElementById("detail-images");
    imageDiv.innerHTML = "";

    const imageUrl = house.image_filename
        ? `/static/uploads/${house.image_filename}`
        : `/static/uploads/placeholder.jpeg`;

    const img = document.createElement("img");
    img.src = imageUrl;
    img.alt = "House Image";
    img.style = "width: 100%; margin-bottom: 1rem;";
    imageDiv.appendChild(img);
}

function hideHouseDetail() {
    const panel = document.getElementById("house-detail-panel");
    panel.classList.remove("show");
    setTimeout(() => panel.classList.add("hidden"), 300);
}
