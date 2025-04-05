function showToast(type, message, delay=4000) {
    const toastContainer = document.getElementById("toastContainer");

    // Criando um ID único para o toast
    const toastId = `toast-${Date.now()}`;

    // Definindo a classe de cor baseada no tipo de mensagem
    let toastClass;
    if (type === "success") toastClass = "text-bg-success";
    else if (type === "error") toastClass = "text-bg-danger";
    else if (type === "warning") toastClass = "text-bg-warning";
    else toastClass = "text-bg-primary"; // Default

    // Criando o HTML do toast
    const toastHTML = `
        <div class="toast ${toastClass} border-0 show" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="3500">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    // Adicionando o toast ao container
    toastContainer.insertAdjacentHTML("beforeend", toastHTML);

    // Inicializando o toast do Bootstrap
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: delay });
    toast.show();

    // Remover o toast após o tempo definido (para evitar acúmulo)
    toastElement.addEventListener("hidden.bs.toast", () => {
        toastElement.remove();
    });
}

