function cerrarSiAfuera(e) {
    if (e.target.id === 'modal-overlay') {
        document.getElementById('modal-overlay').removeAttribute('data-state');
    }
}


function filtrar() {
    const texto = document.getElementById('search-input').value.toLowerCase();
    const tipo = document.getElementById('filter-tipo').value;
    const tarjetas = document.querySelectorAll('#eval-list > div');
    let visibles = 0;

    tarjetas.forEach(t => {
        const nombre = t.getAttribute('data-nombre').toLowerCase();
        const tTipo = t.getAttribute('data-tipo');
        
        const coincideTexto = nombre.includes(texto);
        const coincideTipo = !tipo || tTipo === tipo;
        
        if (coincideTexto && coincideTipo) {
            t.style.display = 'flex';
            visibles++;
        } else {
            t.style.display = 'none';
        }
    });
    
    // "no encontrado"
    const emptyState = document.getElementById('empty-state');
    if (emptyState) {
        emptyState.setAttribute('data-state', visibles === 0 ? 'visible' : '');
    }
}

// Formulario
document.addEventListener('DOMContentLoaded', () => {
    const tipoSelect = document.getElementById('tipo-select');
    const tpExtras = document.getElementById('tp-extras');
    const fechaGeneral = document.getElementById('fecha-general');

    if (tipoSelect) {
        tipoSelect.addEventListener('change', function() {
            if (this.value === 'TP') {
                tpExtras.style.display = 'block';
                fechaGeneral.style.display = 'none';
            } else {
                tpExtras.style.display = 'none';
                fechaGeneral.style.display = 'block';
            }
        });
    }
});


function abrirModalCrear() {
    document.getElementById('id_editar').value = '';
    document.getElementById('modal-titulo').textContent = 'Nueva Evaluación';
    document.getElementById('btn-modal-guardar').textContent = 'Guardar';
    
    document.getElementById('input-nombre').value = '';
    document.getElementById('tipo-select').value = 'Parcial';
    document.getElementById('textarea-notas').value = '';
    
    document.getElementById('modal-overlay').setAttribute('data-state', 'open');
}

function abrirModalEditar(id, nombre, tipo, idMateria, fechaEval, modalidad, fechaIni, fechaEnt, notas) {
    document.getElementById('id_editar').value = id;
    document.getElementById('modal-titulo').textContent = 'Editar Evaluación';
    document.getElementById('btn-modal-guardar').textContent = 'Guardar Cambios';

    document.getElementById('input-nombre').value = nombre || '';
    document.getElementById('tipo-select').value = tipo || 'Parcial';
    document.querySelector('select[name="id_materia"]').value = idMateria || '';
    document.getElementById('input-fecha-evaluacion').value = fechaEval || '';
    document.getElementById('select-modalidad').value = modalidad || 'Individual';
    document.getElementById('input-fecha-inicio').value = fechaIni || '';
    document.getElementById('input-fecha-entrega').value = fechaEnt || '';
    document.getElementById('textarea-notas').value = notas || '';

    document.getElementById('tipo-select').dispatchEvent(new Event('change'));

    document.getElementById('modal-overlay').setAttribute('data-state', 'open');
}
