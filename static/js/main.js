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
            showToast('Something went wrong. Please try again shortly.', 'error');
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
    toast.addEventListener('click', () => toast.remove());
}

window.showToast = showToast;

function bindInboxActions() {
    document.querySelectorAll('.reply-btn').forEach(btn => {
        btn.onclick = function () {
            const li = btn.closest('.message-item');
            const senderId = li.dataset.senderId;
            const houseId = li.dataset.houseId;

            // Prefill the message form
            document.getElementById('form-receiver-id').value = senderId;
            document.getElementById('form-house-id').value = houseId;
            document.getElementById('message-text').focus();

            showToast("Replying to sender...", "info");

            // Optional: Scroll to or open message form
            document.getElementById("house-detail-panel").scrollIntoView({ behavior: 'smooth' });
        };
    });

    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.onclick = function () {
            const li = btn.closest('.message-item');
            const messageId = li.dataset.messageId;

            fetch('/clear_notification', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message_id: messageId })
            })
            .then(res => {
                if (!res.ok) throw new Error('Request failed');
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    li.remove();
                    showToast("Message removed from inbox", "success");
                } else {
                    showToast(data.error || "Failed to delete", "error");
                }
            })
            .catch(err => {
                console.error(err);
                showToast("Could not delete message", "error");
            });
        };
    });
}
