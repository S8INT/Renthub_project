document.addEventListener('DOMContentLoaded', () => {
    // Auto-hide the search bar on small screens
    const searchBar = document.querySelector('.search-bar');
    const searchInput = searchBar.querySelector('input');

    searchInput.addEventListener('focus', () => {
        searchBar.style.width = '100%';
    });

    searchInput.addEventListener('blur', () => {
        searchBar.style.width = '50%';
    });
});

