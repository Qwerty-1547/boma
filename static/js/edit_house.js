document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', () => {
            const houseId = button.getAttribute('data-id');
            loadEditForm(houseId);
        });
    });
});

function loadEditForm(houseId) {
    fetch('/partials/edit_house/${houseId}')
        .then(response => response.text())
        .then(html =>{
            const container = document.getElementById('Content-area');
            container.innerHTML = html;
        })
        .catch(error => {
            console.error('Cannot fetch edit form right now:', error)
        });
}