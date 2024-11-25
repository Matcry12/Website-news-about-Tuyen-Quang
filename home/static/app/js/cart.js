var updateButton = document.getElementsByClassName('update-status-btn');

// Iterate over all the update buttons
for (let i = 0; i < updateButton.length; i++) {
    updateButton[i].addEventListener('click', function () {
        var orderId = this.dataset.order; // Get the order ID from the button's data-room attribute
        var action = this.dataset.action; // Get the action (true/false) from the button's data-action attribute

        // Check if the user is logged in and their role
        if (userRole === "AnonymousUser") {
            console.log('User is not logged in');
        } else if (userRole === "seller") {
            updateUserComfirm(orderId, action);
        } else {
            console.log('Unauthorized user role');
        }
        window.location.reload();
    });
}

function updateUserComfirm(orderId, action) {
    console.log('orderId:', orderId, 'action:', action);
    console.log('user:', user);
    console.log('csrftoken:', csrftoken);

    var url = '/update_order/';  // The URL to send the request to

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken // Ensure csrftoken is available
        },
        body: JSON.stringify({'orderId':orderId,'action':action}) // Send data in JSON format
    })
    .then((response)=> {
        response.json()
    })
    .then((data)=>{
        console.log('data', data)
    })
}

