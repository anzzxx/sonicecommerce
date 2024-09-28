document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const submitButton = document.querySelector('.submit-btn');

    const enableSubmit = () => {
        if (email.value && password.value) {
            submitButton.disabled = false;
            submitButton.style.cursor = 'pointer';
            submitButton.style.backgroundColor = '#4CAF50';
        } else {
            submitButton.disabled = true;
            submitButton.style.cursor = 'not-allowed';
            submitButton.style.backgroundColor = '#888';
        }
    };

    email.addEventListener('input', enableSubmit);
    password.addEventListener('input', enableSubmit);
});
