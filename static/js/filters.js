    document.addEventListener('DOMContentLoaded', () => {
        //console.log("✅ filters.js running");

        const amenitySpans = document.querySelectorAll('.amenity-option');
        const hiddenAmenityInput = document.getElementById('amenities-hidden');
        const selectedAmenityTags = document.getElementById('selected-amenities');

        amenitySpans.forEach(span => {
            span.addEventListener('click', () => {
                //console.log('Amenity clicked:', span.dataset.value);
                span.classList.toggle('selected');
                updateSelectedAmenities();
            });
        });

        function updateSelectedAmenities() {
            const selected = Array.from(amenitySpans)
                .filter(span => span.classList.contains('selected'))
                .map(span => span.dataset.value);

            hiddenAmenityInput.value = selected.join(',');

            // ✅ Safe check before modifying DOM
            if (selectedAmenityTags) {
                selectedAmenityTags.innerHTML = ''; // clear previous
                selected.forEach(amenity => {
                    const tag = document.createElement('span');
                    tag.className = 'selected-amenity-tag';
                    tag.textContent = amenity;
                    selectedAmenityTags.appendChild(tag); // ✅ this line
                });
            } else {
                console.warn("⚠️ selectedAmenityTags is null — element not found in DOM.");
            }
        }
        const filterForm = document.getElementById('filterForm');

        if(filterForm) {
            filterForm.addEventListener('submit', function(e) {
                e.preventDefault();

                const formData = new FormData(filterForm);
                const filters = {};

                for (let [key, value] of formData.entries()) {
                    filters[key] = value;
                }

                console.log('submititng filters', filters);

                fetch('/filter_houses', {
                    method: 'POST',
                    headers: {
                        'content-Type': 'application/json',
                    },
                    body: JSON.stringify(filters)
                })
                .then(res => res.text())
                .then(html => {
                    const contentArea = document.getElementById('content-area');
                    contentArea.innerHTML = html;
                })
                .catch(err => {
                    console.error("filter request failed", err);
                });
            });
        }
    });
