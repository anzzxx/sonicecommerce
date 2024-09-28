function validateOtpForm() {
    const otp = document.getElementById("otp").value;
    if (otp === "") {
        alert("Please enter the OTP.");
        return false;
    }
    return true;
}

function startTimer(duration, display) {
    let timer = duration, minutes, seconds;
    const interval = setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            clearInterval(interval);
            display.textContent = "00:00";
            document.getElementById('resendOtpBtn').style.display = 'block';
        }
    }, 1000);
}

function resendOtp() {
    fetch("{% url 'resend_otp' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({})  // Sending empty body as phone number is handled on server side
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('OTP has been resent.');
            document.getElementById('resendOtpBtn').style.display = 'none';
            startTimer(60, document.querySelector('#timer'));
        } else {
            alert('Failed to resend OTP. Please try again.');
        }
    })
    .catch(error => console.error('Error:', error));
}

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

window.onload = function () {
    const oneMinute = 60,  // 60 seconds
          display = document.querySelector('#timer');
    startTimer(oneMinute, display);
};
