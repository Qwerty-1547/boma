document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.bookmark-btn').forEach(button => {
        button.addEventListener('click', () => {
            const houseId = button.getAttribute('data-house-id');

            button.disabled = true;

            fetch('/toggle_bookmark', {
                method: 'POST',
                headers:{
                    'content-type' : 'application/json'
                },
                body: JSON.stringify({house_id: houseId})
            })
            .then(response => {
                if(!response.ok){
                    throw new Error(`server error: ${response.status}`);
                }
                return response.json()
            }   )
            .then(data => {
                const icon = document.getElementById(`bookmark-icon-${houseId}`);
                if (data.status == 'added'){
                    icon.textContent = '✅';
                    button.title = 'Remove bookmark';
                } else if (data.status == 'removed'){
                    icon.textContent = '🔖';
                    button.title = 'add bookmark';
                }
            })
            .catch (error => {
                alert('failed to toggle bookmark: ${error.message}');
                console.error('bookmark toggle error:', error);
            })
            .finally(() => {
                button.disabled = false;
            })
        });
    });
});