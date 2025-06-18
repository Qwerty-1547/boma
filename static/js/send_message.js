document.addEventListener('DOMContentLoaded', () => {
    const messageForm = document.getElementById('panel-message-form');
    if (!messageForm) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const receiverId = document.getElementById('receiver_id').value;
        const houseId = document.getElementById('house_id').value;
        const message = document.getElementById('message-text').value;
        const statusDiv = messageForm.querySelector(".message-status");

        if(!message.trim()) {
            statusDiv.textContent = "Type in a message.";
            return;
        }

        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ receiver_id: receiverId, house_id: houseId, message: message })
        })
        .then(res => {
            if(!res.ok) throw new error("Network error");
            return res.json();
        })
        .then(data => {
            statusDiv.textContent = "Message sent!";
            statusDiv.style.color = "green";
            messageForm.reset();
        })
        .catch(err => {
            console.error('Error sending message:', err);
            statusDiv.textContent = "Failed to send message";
            statusDiv.style.color = "red";
        });
    });
});
