document.addEventListener('DOMContentLoaded', () => {
    const openBtn = document.getElementById('open-inbox');
    const closeBtn = document.getElementById('closeInboxBtn');
    const panel = document.getElementById('inboxPanel');
    const content = document.getElementById('inboxContent');

    if (openBtn && closeBtn && panel && content) {
        openBtn.addEventListener('click', () => {
            fetch('/inbox_data')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Failed to fetch inbox: ${response.status}`);
                    }
                    return response.text();
                })
                .then(html => {
                    content.innerHTML = html;
                    document.body.classList.add("body-lock");
                    panel.classList.add('open');

                    bindInboxActions(); // ✅ Attach click handlers now that content is loaded
                })
                .catch(error => {
                    content.innerHTML = `<p style="color: red;">Error loading inbox: ${error.message}</p>`;
                    panel.classList.add('open');
                    console.error('Inbox fetch error:', error);
                });
        });

        closeBtn.addEventListener('click', () => {
            document.body.classList.remove("body-lock");
            panel.classList.remove('open');
        });

        document.addEventListener('click', (event) => {
            const isClickInside = panel.contains(event.target) || openBtn.contains(event.target);
            if (!isClickInside) {
                document.body.classList.remove("body-lock");
                panel.classList.remove('open');
            }
        });
    }
});


// ✅ Moved here as a reusable function
function bindInboxActions() {
    // Bind reply send buttons
    document.querySelectorAll('.send-reply-btn').forEach(btn => {
        btn.onclick = function () {
            const li = btn.closest('.message-item');
            const textarea = li.querySelector('.reply-text');
            const message = textarea ? textarea.value.trim() : "";

            if (!message) {
                showToast("Reply cannot be empty.", "error");
                return;
            }

            fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    receiver_id: li.dataset.senderId,
                    house_id: li.dataset.houseId,
                    message: message
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast("Reply sent!", "success");
                    if (textarea) textarea.value = "";
                } else {
                    showToast(data.error || "Failed to send reply.", "error");
                }
            })
            .catch(err => {
                console.error(err);
                showToast("Network error.", "error");
            });
        };
    });

    // ✅ Keep reply box open when clicking inside
    document.querySelectorAll('.reply-text').forEach(textarea => {
        textarea.addEventListener('focus', () => {
            const container = textarea.closest('.inline-reply');
            if (container) container.classList.add('sticky');
        });
    });

    // ✅ Hide sticky reply if click is outside
    document.addEventListener('click', (event) => {
        document.querySelectorAll('.inline-reply.sticky').forEach(container => {
            if (!container.contains(event.target)) {
                container.classList.remove('sticky');
            }
        });
    });

    // Re-bind delete buttons
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.onclick = function () {
            const li = btn.closest('.message-item');
            const messageId = li.dataset.messageId;

            fetch('/clear_notification', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message_id: messageId })
            })
            .then(res => res.json())
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


window.bindInboxActions = bindInboxActions;
