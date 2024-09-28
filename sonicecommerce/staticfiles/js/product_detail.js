// JavaScript for zoom effect on main image
document.addEventListener('DOMContentLoaded', function () {
    const zoomImg = document.querySelector('.zoom-img');
    let zoomed = false;

    // Check if zoomImg exists
    if (!zoomImg) {
        console.error('Element with class "zoom-img" not found.');
        return;
    }

    zoomImg.addEventListener('mousemove', function (e) {
        if (!zoomed) {
            zoomed = true;
            zoomImg.style.transition = 'transform .2s';
            zoomImg.style.transform = 'scale(1.5)';
        }
    });

    zoomImg.addEventListener('mouseleave', function () {
        zoomed = false;
        zoomImg.style.transition = 'transform .2s';
        zoomImg.style.transform = 'scale(1)';
    });
});

// JavaScript function to change the main image when clicking on sub-images
function changeImage(imageUrl) {
    document.getElementById('main-image').src = imageUrl;
    document.getElementById('main-image-link').href = imageUrl;
}
document.addEventListener('DOMContentLoaded', function() {
    const swatches = document.querySelectorAll('.color-swatch');
    swatches.forEach(swatch => {
        swatch.addEventListener('click', function() {
            swatches.forEach(s => s.classList.remove('active'));
            this.classList.add('active');
            const selectedColor = this.getAttribute('data-color');
            console.log('Selected color:', selectedColor);
        });
    });
});
