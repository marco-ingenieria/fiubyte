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
    
    const emptyState = document.getElementById('empty-state');
    if (emptyState) {
        emptyState.setAttribute('data-state', visibles === 0 ? 'visible' : '');
    }
}

function abrirModalCrear() {
    document.getElementById('id_editar').value = '';
    document.getElementById('modal-titulo').textContent = 'Nueva Evaluación';
    document.getElementById('btn-modal-guardar').textContent = 'Guardar';

    document.getElementById('input-nombre').value = '';
    document.getElementById('tipo-select').value = 'Parcial';

    document.getElementById('modal-overlay').setAttribute('data-state', 'open');
}

function abrirModalEditar(id, nombre, tipo, idMateria, fechaEval, modalidad, fechaIni, fechaEnt, notas) {
    document.getElementById('id_editar').value = id;
    document.getElementById('modal-titulo').textContent = 'Editar Evaluación';
    document.getElementById('btn-modal-guardar').textContent = 'Guardar Cambios';
    document.getElementById('input-nombre').value = nombre || '';
    document.getElementById('tipo-select').value = tipo || 'Parcial';
    document.querySelector('select[name="id_materia"]').value = idMateria || '';
    document.getElementById('modal-overlay').setAttribute('data-state', 'open');
}
