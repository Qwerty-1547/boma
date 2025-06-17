document.addEventListener("DOMContentLoaded", function () {
    window.showHouseDetailFromBase64 = function (el) {
        try {
            const base64 = el.getAttribute("data-house");
            const jsonString = atob(base64);
            const house = JSON.parse(jsonString);
            showHouseDetail(house);
        } catch (err) {
            console.error("Invalid house JSON:", err);
        }
    }

    function showHouseDetail(house) {
        console.log('Selected house:', house);

        document.getElementById("detail-title").textContent = house.title;
        document.getElementById("detail-desc").textContent = house.description;
        document.getElementById("detail-price").textContent = parseInt(house.price).toLocaleString();
        document.getElementById("detail-area").textContent = house.area_name;
        document.getElementById("detail-owner").textContent = house.owner_name;
        document.getElementById("detail-contact").textContent = house.owner_contact;
        document.getElementById("detail-verified").textContent = house.owner_verified ? "Yes" : "No";

        const panel = document.getElementById("house-detail-panel");
        panel.classList.remove("hidden");
        panel.classList.add("show");

        const imageContainer = document.getElementById("detail-images");
        imageContainer.innerHTML = "";

        if(house.images && house.images.length > 0) {
            house.images.forEach(img=> {
                const image = document.createElement("img");
                image.src = `/${img}`;
                image.alt = house.title;
                image.style.maxWidth = "100%";
                image.style.borderRadius = "8px";
                image.style.marginBottom = "10px";
                imageContainer.appendChild(image);
            });
        }else{
            imageContainer.innerHTML = "<p>No images available.</p>"
        }
    }

    window.hideHouseDetail = function () {
        const panel = document.getElementById("house-detail-panel");
        panel.classList.remove("show");
        setTimeout(() => panel.classList.add("hidden"), 300);
    }
});
