function abrirModal(tipo) {
    if (tipo === 'crear') {
        document.getElementById('modal-crear').showModal();
    } else if (tipo === 'eliminar') {
        document.getElementById('modal-eliminar').showModal();
    }
}

function cerrarModal(tipo) {
    if (tipo === 'crear') {
        document.getElementById('modal-crear').close();
        document.getElementById('form-crear').reset(); 
    } else if (tipo === 'eliminar') {
        document.getElementById('modal-eliminar').close();
        document.getElementById('form-eliminar').reset();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const inputConfirmar = document.getElementById('confirmar-palabra');
    const btnEliminarSubmit = document.getElementById('btn-eliminar-submit');

    inputConfirmar.addEventListener('input', (e) => {
        if (e.target.value === 'ELIMINAR') {
            btnEliminarSubmit.disabled = false;
        } else {
            btnEliminarSubmit.disabled = true;
        }
    });
});