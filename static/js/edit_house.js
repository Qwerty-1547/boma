document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', () => {
            const houseId = button.getAttribute('data-id');
            loadEditForm(houseId);
        });
    });
});

function loadEditForm(houseId) {
    fetch(`/partials/edit_house/${houseId}`)
        .then(response => response.text())
        .then(html => {
            const container = document.getElementById('content-area');
            container.innerHTML = html;

            // 🔥 Initialize remove buttons after HTML loads
            initializeRemoveImageButtons();
        })
        .catch(error => {
            console.error('Cannot fetch edit form right now:', error);
        });
}

function initializeRemoveImageButtons() {
    document.querySelectorAll('.remove-image-btn').forEach(button => {
        button.addEventListener('click', () => {
            const imageId = button.getAttribute('data-img-id');

            if (confirm('Are you sure you want to delete this image?')) {
                fetch(`/delete_house_image/${imageId}`, { method: 'POST' })
                    .then(response => {
                        if (response.ok) {
                            // ✅ Remove image preview from DOM
                            button.closest('.image-preview').remove();
                        } else {
                            alert('Failed to delete the image. Please try again.');
                        }
                    })
                    .catch(error => {
                        console.error('Error deleting image:', error);
                        alert('An unexpected error occurred. Please try again.');
                    });
            }
        });
    });
}
