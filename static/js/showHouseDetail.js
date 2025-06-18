document.addEventListener("DOMContentLoaded", function () {
    window.showHouseDetailFromBase64 = function (el) {
        try {
            const base64 = el.getAttribute("data-house");
            const jsonString = atob(base64);
            const briefHouse = JSON.parse(jsonString);
            showHouseDetail(briefHouse);

            fetch(`/house/${briefHouse.id}/details`)
                .then(response => {
                    if(!response.ok) throw new error("Failed to load house details");
                    return response.json();
                })
                .then(fullHouse => {
                    fullHouse.is_bookmarked = briefHouse.is_bookmarked;
                    showHouseDetail(fullHouse);
                })
                .catch(err => {
                    console.error("Error fetching details:", err);
                    showToast("connection error, could not load house details", 'error');
                });
        } catch (err) {
            console.error("Invalid house JSON:", err);
        }
    }

    function showHouseDetail(house) {
        //console.log('Selected house:', house);

        document.getElementById("detail-title").textContent = house.title;
        document.getElementById("detail-desc").textContent = house.description;
        document.getElementById("detail-price").textContent = parseInt(house.price).toLocaleString();
        document.getElementById("detail-area").textContent = house.area_name;
        document.getElementById("detail-owner").textContent = house.owner_name;
        document.getElementById("detail-contact").textContent = house.owner_contact;
        document.getElementById("form-receiver-id").value = house.owner_id;
        document.getElementById("form-house-id").value = house.id;
        //document.getElementById("bookmark-btn").setAttribute("data-house-id", house.id);
        const bookmarkBtn = document.querySelector(".bookmark-btn");

        const newBtn = bookmarkBtn.cloneNode(true);
        bookmarkBtn.parentNode.replaceChild(newBtn, bookmarkBtn);
        const bookmarkIcon = newBtn.querySelector(".bookmark-icon");

        newBtn.setAttribute("data-house-id", house.id);
        newBtn.title = house.is_bookmarked ? "Remove bookmark" : "Add bookmark";
        bookmarkIcon.textContent= house.is_bookmarked ? "✅Remove bookmark" : "🔖Add bookmark";

        newBtn.addEventListener("click", () => {
            newBtn.disabled = true;

            fetch('/toggle_bookmark', {
                method: 'POST',
                headers: {
                    'content-type': 'application/json'
                },
                body:JSON.stringify({ house_id: house.id})
            })
            .then(response => {
                if(!response.ok) throw new error(`server error: ${response.status}`);
                return response.json();
            })
            .then(data => {
                if(data.status === 'added'){
                    bookmarkIcon.textContent = '✅Remove bookmark';
                    newBtn.title = 'Remove Bookmark';
                }else if (data.status === 'removed'){
                    bookmarkIcon.textContent = '🔖Add bookmark';
                    newBtn.title = 'Add bookmark';
                }
            })
            .catch(error => {
                showToast(`failed to toggle bookmark: ${error.message}`, 'error');
            })
            .finally(() => {
                newBtn.disabled = false;
            })
        })

        const verifiedSpan = document.getElementById("detail-verified");
        verifiedSpan.textContent = house.owner_verified ? " Verified      ✔" : "Verification Pending      ⏳ ";
        verifiedSpan.className = house.owner_verified ? "yes" : "no";



        const panel = document.getElementById("house-detail-panel");
        document.body.classList.add("body-lock");
        panel.classList.remove("hidden");
        panel.classList.add("show");

        const imageContainer = document.getElementById("detail-images");
        imageContainer.innerHTML = "";
        
        //console.log("image list:", house.images)

        if(house.images && house.images.length > 0) {
            house.images.forEach(img=> {
                const image = document.createElement("img");
                image.src = `/static/uploads/${img}`;
                image.alt = house.title;
                image.style.maxWidth = "100%";
                image.style.borderRadius = "8px";
                image.style.marginBottom = "10px";
                imageContainer.appendChild(image);
            });
        }else{
            imageContainer.innerHTML = "<p>No images posted.</p>"
        }
    }

    window.hideHouseDetail = function () {
        const panel = document.getElementById("house-detail-panel");
        panel.classList.remove("show");
        document.body.classList.remove("body-lock");
        setTimeout(() => panel.classList.add("hidden"), 300);
    }

    document.addEventListener('click', function (event){
        const panel = document.getElementById("house-detail-panel");
        if(!panel.classList.contains("show")) return;
        if(!panel.contains(event.target)){
            window.hideHouseDetail();
        }
    })
});
