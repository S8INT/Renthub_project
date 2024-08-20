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

document.addEventListener("DOMContentLoaded", function () {
    // Profile Picture Preview
    const profilePicInput = document.getElementById("profile-picture-input");
    const profilePicPreview = document.querySelector(".profile-section img");

    if (profilePicInput) {
        profilePicInput.addEventListener("change", function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    profilePicPreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Tooltip Functionality
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(function (element) {
        element.addEventListener("mouseover", function () {
            const tooltip = document.createElement("span");
            tooltip.className = "tooltip";
            tooltip.innerText = element.getAttribute("data-tooltip");
            document.body.appendChild(tooltip);

            const rect = element.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + "px";
            tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + "px";
        });

        element.addEventListener("mouseout", function () {
            document.querySelector(".tooltip").remove();
        });
    });
});

// CSS for Tooltip
const tooltipStyle = document.createElement("style");
tooltipStyle.innerHTML = `
    .tooltip {
        position: absolute;
        background-color: #333;
        color: #fff;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 14px;
        z-index: 1000;
    }
`;
document.head.appendChild(tooltipStyle);
