// Funciones básicas para abrir y cerrar ventanas
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
    } else if (tipo === 'eliminar') {
        // Limpiamos los campos al cerrar para que no queden datos viejos si vuelve a abrir
        document.getElementById('eliminar-usuario-id').value = "";
        document.getElementById('confirmar-palabra').value = "";
        document.getElementById('btn-eliminar-submit').disabled = true;
        document.getElementById('modal-eliminar').close();
    }
}

// Esperar a que el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Habilitar el botón de borrado solo si escriben "ELIMINAR"
    const inputConfirmar = document.getElementById('confirmar-palabra');
    const btnEliminarSubmit = document.getElementById('btn-eliminar-submit');

    inputConfirmar.addEventListener('input', (e) => {
        if (e.target.value === 'ELIMINAR') {
            btnEliminarSubmit.disabled = false;
        } else {
            btnEliminarSubmit.disabled = true;
        }
    });

    // Controlar el envío del formulario de eliminación (Simulación)
    const formEliminar = document.getElementById('form-eliminar');

    formEliminar.addEventListener('submit', function(e) {
        e.preventDefault(); // Evitamos que la página intente recargarse
        
        // Capturamos lo que el usuario escribió en la cajita de ID
        const idAGrabar = document.getElementById('eliminar-usuario-id').value;
        
        // Alerta de prueba para verificar que funciona
        alert("Acción simulada: Enviando orden para eliminar al usuario ID: " + idAGrabar);
        
        // Cerramos la ventana limpia
        cerrarModal('eliminar');
    });
});