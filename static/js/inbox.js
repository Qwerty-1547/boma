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
                    panel.classList.add('open');
                })
                .catch(error => {
                    content.innerHTML = `<p style="color: red;">Error loading inbox: ${error.message}</p>`;
                    panel.classList.add('open');
                    console.error('Inbox fetch error:', error);
                });
        });

        closeBtn.addEventListener('click', () => {
            panel.classList.remove('open');
        });
        document.addEventListener('click', (event) =>{
            const isClickInside= panel.contains(event.target) || openBtn.contains(event.target);
            if(!isClickInside) {
                panel.classList.remove('open')
            }
        })
    }
});
