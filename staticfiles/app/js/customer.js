var nameUser = user

if (nameUser === "AnonymousUser") {
    nameUser = "Khách hàng"
    console.log("User are not logged");
} 
else {
    nameUser = userName
}

var customerName = document.getElementById('customerDef');

customerName.innerHTML = nameUser;
