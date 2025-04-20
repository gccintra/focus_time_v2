
function inicializateToDoTooltips(){
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    console.log(`Tooltip List: ${tooltipList}`)

};


document.addEventListener('DOMContentLoaded', function () {
    inicializateToDoTooltips();
});

function reinitializateToDoTooltipsAfterDOMUpdate(){
    inicializateToDoTooltips();
};
