function loadSection(section){
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = '<p>Loading....</p>';

    fetch(`/partials/${section}`)
        .then(res=>{
            if(!res.ok) throw new Error(`Failed to load section: ${res.status}`);
            return res.text();
        })
        .then(html=>{
            contentArea.innerHTML= html;
        })
        .catch(error=>{
            contentArea.innerHTML = `<p class = "error">Error loading section: ${error.message}</p>`;
            console.error('section load error', error);
        });
}

document.addEventListener('DOMContentLoaded',()=>{
    loadSection('houses');
})