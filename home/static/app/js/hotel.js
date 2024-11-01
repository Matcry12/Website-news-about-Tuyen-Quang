// Save the scroll position before the page is unloaded
window.addEventListener("beforeunload", function() {
    // Store the current scroll position in localStorage
    localStorage.setItem("scrollX", window.scrollX);
    localStorage.setItem("scrollY", window.scrollY);
});

// Restore the scroll position when the page is loaded
window.addEventListener("load", function() {
    const scrollX = localStorage.getItem("scrollX");
    const scrollY = localStorage.getItem("scrollY");

    // Only scroll if the stored positions exist
    if (scrollX !== null && scrollY !== null) {
        window.scrollTo(parseFloat(scrollX), parseFloat(scrollY));
    }

    // Optional: Clear the stored scroll positions after restoring
    localStorage.removeItem("scrollX");
    localStorage.removeItem("scrollY");

});

document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    const serviceForm = document.getElementById('serviceForm');
    const resetButton = document.getElementById('resetButton');
    let resetClicked = false; // Flag to track if reset button is clicked

    // Add event listener for checkboxes
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const searchQuery = document.querySelector('input[name="q"]').value;

            // Only auto-submit service form if there is no active search query and reset was not clicked
            if (searchQuery.trim() === "" && !resetClicked) {
                serviceForm.submit();  // Auto-submit service form when no search is happening
            }
        });
    });

    // Add event listener to the reset button
    resetButton.addEventListener('click', function() {
        resetClicked = true; // Set the flag to true

        // Untick all checkboxes
        checkboxes.forEach(function(checkbox) {
            checkbox.checked = false; // Uncheck the checkbox
        });

        // Submit the form
        serviceForm.submit();
    });

    // Reset the flag after the form is submitted
    serviceForm.addEventListener('submit', function() {
        resetClicked = false; // Reset the flag
    });
});