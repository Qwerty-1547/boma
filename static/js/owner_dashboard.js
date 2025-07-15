document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.delete-btn');

    deleteButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const houseId = button.dataset.id;
            const houseTitle = button.dataset.title || 'this house';
            const houseLocation = button.dataset.location;

            const confirmed = confirm(`Are you sure you want to delete "${houseTitle}", "${houseLocation}"? This action cannot be undone.`);

            if(!confirmed) return;

            try{
                const response = await fetch(`/delete_house/${houseId}`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XmlHttpRequest',
                        'Content-Type': 'application/json',
                    },
                    credentials:'same-origin'
                });

                if(response.ok) {
                    const card = button.closest('.house-card');
                    if (card) card.remove();

                    showToast(`Deleted "${houseTitle}", "${houseLocation}", success`);
                }else{
                    const msg = await response.text();
                    showToast(`Failed to delete: ${msg}`, error);
                }
            }catch(err) {
                console.error('Error deleting house:', err);
                showToast('Something went wrong, try again later', 'error');
            }
        });
    });
});