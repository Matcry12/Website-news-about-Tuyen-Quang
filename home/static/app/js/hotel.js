function resetSearch() {
    // Uncheck all checkboxes
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(function (checkbox) {
        checkbox.checked = false;
    });

    // Optionally submit the form to reflect the changes if necessary
    const serviceForm = document.getElementById("serviceForm");
    if (serviceForm) {
        serviceForm.submit();
    }
}


// Preserve scroll position
document.addEventListener("DOMContentLoaded", function () {
    // Save the scroll position before the page is unloaded
    // window.addEventListener("beforeunload", function () {
    //     localStorage.setItem("scrollX", window.scrollX);
    //     localStorage.setItem("scrollY", window.scrollY);
    // });

    // // Restore the scroll position
    // window.addEventListener("load", function () {
    //     const scrollX = localStorage.getItem("scrollX");
    //     const scrollY = localStorage.getItem("scrollY");

    //     if (scrollX !== null && scrollY !== null) {
    //         window.scrollTo(parseFloat(scrollX), parseFloat(scrollY));
    //     }

    //     // Clear the stored positions after restoring
    //     localStorage.removeItem("scrollX");
    //     localStorage.removeItem("scrollY");
    // });

    const serviceForm = document.getElementById("serviceForm");
    const productContainer = document.getElementById("productContainer");

    // Event listener for form changes
    serviceForm.addEventListener("change", function (event) {
        event.preventDefault();

        const formData = new FormData(serviceForm);

        fetch("{% url 'hotel' %}", {
            method: "POST",
            headers: {
                "X-CSRFToken": "{{ csrf_token }}",
                "X-Requested-With": "XMLHttpRequest", // Indicate it's an AJAX request
            },
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                productContainer.innerHTML = data.products_html; // Replace product container
            })
            .catch((error) => console.error("Error:", error));
    });
});

let map;           // Declare the map variable globally to avoid reinitializing it
let marker;        // Declare the marker variable globally to manage its state

function openMapModal(mapLocationString, maptitle) {
    // Display the modal
    document.getElementById("mapModal").style.display = "flex";

    // Parse the mapLocationString into latitude and longitude
    const [latitude, longitude] = mapLocationString.split(", ").map(Number);
    const hotelCoordinates = { lat: latitude, lng: longitude };

    // Initialize the map if it's not already initialized
    if (!map) {
        map = new google.maps.Map(document.getElementById("bigMap"), {
            zoom: 17,
            center: hotelCoordinates,
        });
    } else {
        map.setCenter(hotelCoordinates); // Center the map to new coordinates if map is already initialized
    }

    // If a marker already exists, remove it before creating a new one
    if (marker) {
        marker.setMap(null);
    }

    // Add a new marker for the current location
    marker = new google.maps.Marker({
        position: hotelCoordinates,
        map: map,
        title: maptitle,
    });
}

function closeMapModal() {
    document.getElementById("mapModal").style.display = "none";

    // Remove the marker from the map when the modal is closed
    if (marker) {
        marker.setMap(null);
        marker = null; // Reset the marker variable
    }
}