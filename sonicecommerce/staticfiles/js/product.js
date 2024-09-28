// product.js
document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.querySelector('.search-button');
    const searchInput = document.querySelector('.search-input');

    searchButton.addEventListener('click', () => {
        const query = searchInput.value.toLowerCase();
        const rows = document.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const productName = row.children[1].textContent.toLowerCase();
            if (productName.includes(query)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });

    const addProductButton = document.querySelector('.add-product-btn');
    addProductButton.addEventListener('click', () => {
        // Handle adding new product logic here
        alert('Add product functionality goes here');
    });

    const editButtons = document.querySelectorAll('.edit-btn');
    const deleteButtons = document.querySelectorAll('.delete-btn');

    editButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Handle edit product logic here
            alert('Edit product functionality goes here');
        });
    });

    deleteButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Handle delete product logic here
            alert('Delete product functionality goes here');
        });
    });
});
document.addEventListener('DOMContentLoaded', () => {
    // Existing JavaScript logic

    // Additional logic for editing a product can go here
    const editButtons = document.querySelectorAll('.edit-btn');
    editButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            // Prevent default behavior if necessary
            // event.preventDefault();
            
            // Handle the edit button click, e.g., open the edit form
            // You can use AJAX to dynamically load the edit form or simply redirect to the edit page
        });
    });
});
