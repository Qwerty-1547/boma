function loadSection(section) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = '<p>Loading...</p>';

    fetch(`/partials/${section}`)
        .then(res => {
            if (!res.ok) throw new Error(`Failed to load section: ${res.status}`);
            return res.text();
        })
        .then(html => {
            contentArea.innerHTML = html;
            //reloading the add_house form in case of error
            if(section === 'add_house' && typeof window.initAddHouseForm === 'function'){
                window.initAddHouseForm();
            }

            // Reinitialize any dynamic JS behaviors needed after new content is loaded
            if (typeof window.initBookmarkButtons === 'function') {
                window.initBookmarkButtons();
            }

            // Optional: reinit other section-specific scripts here
            // if (section === 'inbox' && typeof window.initInbox === 'function') {
            //     window.initInbox();
            // }
        })
        .catch(error => {
            contentArea.innerHTML = `<p class="error text-red-600">Error loading section: ${error.message}</p>`;
            console.error('Section load error:', error);
        });
}
