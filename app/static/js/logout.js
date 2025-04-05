document.getElementById("logout").addEventListener("click", function(event) {
    event.preventDefault();

    fetch("/auth/logout", {
        method: "POST",
        credentials: "include" // Envia os cookies na requisição
    })
    .then(response => {
        if (response.ok) {
            window.location.href = "/";  
        } else {
            console.error("Erro ao fazer logout");
        }
    })
    .catch(error => console.error("Erro ao se comunicar com o servidor:", error));
});