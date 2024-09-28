function downloadAndRedirect(orderId) {
    // Create a form element for the download request
    var form = document.createElement("form");
    form.method = "POST";
    form.action = "/orders/download-invoice/" + orderId + "/";
    form.style.display = "none";
    
    // Append form to the body and submit
    document.body.appendChild(form);
    form.submit();

    // Redirect to the order details page after download
    setTimeout(function() {
        window.location.href = "/orders/order_detail/" + orderId + "/";
    }, 1000); // Adjust timeout as needed
}

document.addEventListener("DOMContentLoaded", function() {
    // Replace 'YOUR_ORDER_ID' with the actual order ID dynamically
    downloadAndRedirect("{{ order.order_number }}");
});
