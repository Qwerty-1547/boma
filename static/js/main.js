function initAddHouseForm() {
    const form = document.getElementById('addHouseForm');
    if (!form) return;

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = new FormData(form);

        try {
            const response = await fetch('/partials/add_house', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                showToast(data.error || 'An error occurred.', 'error');
                return;
            }

            showToast(data.success || 'House added successfully!', 'success');
            loadSection('owner_dashboard');

        } catch (err) {
            console.error(err);
            showToast('Something went wrong. Please try again.', 'error');
        }
    });
}
window.initAddHouseForm = initAddHouseForm;


function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    toast.textContent = message;

    const container = document.getElementById('toast-container');
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('opacity-0');
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}
toast.addEventListener('click', () => toast.remove());

window.showToast = showToast;