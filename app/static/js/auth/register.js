document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const email = document.getElementById('email').value.trim();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();

    fetch("/auth/register/create_account", {
        method: "POST",
        headers: {
        "Content-Type": "application/json"
        },
        body: JSON.stringify({ email: email, username: username, password: password })
    })
    .then(response => response.json())
    .then(({ success, message, data, error }) => {
        if (success){
            showToast('success', message);
            setTimeout(function() {
                window.location.href = `/`;
            }, 2000);
        } else {
            showToast('error', message || 'Erro ao se registrar');
            console.log(error)
        }
    })
    .catch((error) => {
        showToast('error', 'Something went wrong while creating a task. Please try again later.');
        console.error("Erro ao criar Task: ", error);
    }); 
    
  
});