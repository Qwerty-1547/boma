// ✅ This runs once when the page is first loaded
document.addEventListener('DOMContentLoaded', () => {
    // ❗ This won't work if the form is loaded dynamically (e.g., via a panel fragment).
    // ❗ Use a reusable bind function instead (shown below).

    bindMessageForm(); // ✅ Run this at first load (in case it's present), and also after loading fragments
});

// ✅ Make this a reusable function so you can call it after dynamically loading the panel
function bindMessageForm() {
    const messageForm = document.getElementById('panel-message-form');
    if (!messageForm) return; // 🔧 FIXED: this was okay

    messageForm.onsubmit = function (e) {
        e.preventDefault();

        const sendBtn = messageForm.querySelector('button[type="submit"]');
        sendBtn.disabled = true;

        // 📌 FIXED: input IDs were wrong. Your hidden fields use "form-receiver-id", not "form-receiver_id"
        const receiverId = document.getElementById('form-receiver-id').value;
        const houseId = document.getElementById('form-house-id').value;
        const message = document.getElementById('message-text').value;
        const statusDiv = messageForm.querySelector(".message-status");

        if (!message.trim()) {
            statusDiv.textContent = "Type in a message.";
            statusDiv.style.color = "red"; // 📌 Added for feedback visibility
            sendBtn.disabled = false;
            return;
        }

        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                receiver_id: receiverId,
                house_id: houseId,
                message: message
            })
        })
        .then(res => {
            if (!res.ok) throw new Error("Network error"); // 📌 FIXED typo: was 'error' instead of 'Error'
            return res.json();
        })
        .then(data => {
            if (data.success) { // ✅ Check the success flag from Flask
                showToast(`Message sent!`, 'success');
                statusDiv.textContent = "";
                messageForm.reset();
            } else {
                showToast(data.error || "Failed to send message.", 'error')
            }
        })
        .catch(err => {
            console.error('Error sending message:', err);
            showToast("Failed to send message. Check your connection", 'error')
            statusDiv.textContent = "";
        })
        .finally(() => {
            sendBtn.disabled = false;
        });
    };
}
