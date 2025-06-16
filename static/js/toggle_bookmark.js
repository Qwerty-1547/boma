function initBookmarkButtons() {
    document.querySelectorAll('.bookmark-btn').forEach(button => {
        // Avoid rebinding if already bound
        if (button.dataset.bound === 'true') return;

        const houseId = button.getAttribute('data-house-id');
        const icon = document.getElementById(`bookmark-icon-${houseId}`);

        button.addEventListener('click', () => {
            if (!icon) {
                console.warn(`Bookmark icon not found for house ID ${houseId}`);
                return;
            }

            button.disabled = true;

            fetch('/toggle_bookmark', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ house_id: houseId })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'added') {
                    icon.textContent = '✅';
                    button.title = 'Remove bookmark';
                } else if (data.status === 'removed') {
                    icon.textContent = '🔖';
                    button.title = 'Add bookmark';
                }
            })
            .catch(error => {
                alert(`Failed to toggle bookmark: ${error.message}`);
                console.error('Bookmark toggle error:', error);
            })
            .finally(() => {
                button.disabled = false;
            });
        });

        // Mark as bound to avoid rebinding later
        button.dataset.bound = 'true';
    });
}

// Initial run when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    initBookmarkButtons();
});

// Expose function globally for section_loader.js
window.initBookmarkButtons = initBookmarkButtons;
