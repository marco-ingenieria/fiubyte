function abrirModal(id) {
    document.getElementById(id).showModal();
}

function cerrarModal(modalId, formId) {
    document.getElementById(modalId).close();
    document.getElementById(formId).reset();
}