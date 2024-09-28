document.addEventListener('DOMContentLoaded', () => {
    const blockButtons = document.querySelectorAll('.block-btn');

    blockButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            const url = button.dataset.url;
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => {
                if (response.ok) {
                    if (button.textContent === 'Block') {
                        button.textContent = 'Unblock';
                        button.style.backgroundColor = '#4CAF50';
                    } else {
                        button.textContent = 'Block';
                        button.style.backgroundColor = '#ff4d4d';
                    }
                }
            });
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

