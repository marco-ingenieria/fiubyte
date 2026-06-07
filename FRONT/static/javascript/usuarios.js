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
        document.getElementById('form-crear').reset(); // Limpiar el formulario al cerrar
    } else if (tipo === 'eliminar') {
        document.getElementById('modal-eliminar').close();
        document.getElementById('form-eliminar').reset(); // Limpiar el formulario al cerrar
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

    
    const formCrear = document.getElementById('form-crear');
    formCrear.addEventListener('submit', function(e) {

        e.preventDefault();
        
        const nombre = formCrear.querySelector('input[type="text"]').value;
        const contrasenia = formCrear.querySelector('input[type="password"]').value;
        
        fetch('/crear_usuario', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre: nombre, contrasenia: contrasenia })
        })
        .then(response => response.json())
        .then(data => {
            alert('Usuario creado correctamente');
            cerrarModal('crear');
            location.reload();
        })
        .catch(error => {
            alert('Error al crear el usuario');
        });
    });


});