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
    if (window.location.hash === '#hotel-section') {
        const element = document.getElementById('hotel-section');
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' }); // Smooth scroll to the element
        }
    }
    const forms = document.querySelectorAll("form"); // Select all forms
    const productContainer = document.getElementById("productContainer");

    // Add event listener to all forms
    forms.forEach((form) => {
        form.addEventListener("change", function (event) {
            event.preventDefault();

            const formData = new FormData(form);

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
});

let map;           // Declare the map variable globally to avoid reinitializing it
let marker;        // Declare the marker variable globally to manage its state

function openMapModal(mapLocationString, maptitle) {
    // Display the modal
    document.getElementById("mapModal").style.display = "flex";

    // Parse the mapLocationString into latitude and longitude
    const [latitude, longitude] = mapLocationString.split(", ").map(Number);
    const hotelCoordinates = { lat: latitude, lng: longitude };

    // Construct the Google Maps embed URL dynamically using the latitude and longitude
    const mapSrc = `https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d502.437568808432!2d${longitude}!3d${latitude}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1svi!2s!4v1733844849741!5m2!1svi!2s`;

    //https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d1309.5585609494601!2d105.21661813191884!3d21.81928036056359!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1svi!2s!4v1733844751938!5m2!1svi!2s
    //https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d2202.437568808432!2d105.21496987226264!3d21.817241889317526!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1svi!2s!4v1733844849741!5m2!1svi!2s
    // Get the iframe element inside the modal
    const iframe = document.getElementById('mapContainer').querySelector('iframe');

    console.log(mapSrc);
    
    // Update the iframe src to the dynamically constructed map URL
    iframe.src = mapSrc;

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