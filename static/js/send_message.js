document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('message-form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const receiverId = document.getElementById('receiver_id').value;
        const houseId = document.getElementById('house_id').value;
        const message = document.getElementById('message-text').value;

        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ receiver_id: receiverId, house_id: houseId, message: message })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('message-status').textContent = 'Message sent!';
                document.getElementById('message-text').value = '';
            } else {
                alert('Failed to send message');
            }
        })
        .catch(err => {
            console.error('Error sending message:', err);
            alert('Server error.');
        });
    });
});
