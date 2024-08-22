var nameUser = user

if (nameUser === "AnonymousUser") {
    nameUser = "Khách hàng"
    console.log("User are not logged");
} 
else {
    nameUser = user
}

var customerName = document.getElementById('customerDef');

customerName.innerHTML = nameUser;
