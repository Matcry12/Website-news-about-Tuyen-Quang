var updateButton = document.getElementsByClassName('update-cart')

for (i = 0; i < updateButton.length; i++){
    updateButton[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        if(user === "AnonymousUser"){
            console.log('User are not logged')
        }
        else{
            updateUserCart(productId, action)
        }
    })
}

function updateUserCart(productId, action){
    console.log('productId', productId,'action', action)
    console.log('user:', user)

    var url = '/updateItem/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({'productId': productId, 'action': action})
    })
    .then(response => {
        return response.json();
    })
    .then(data => {
        console.log('Data:', data);
        location.reload();
    })

}