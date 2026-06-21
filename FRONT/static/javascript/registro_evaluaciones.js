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
        const coincideTexto = t.getAttribute('data-nombre').includes(texto);
        const coincideTipo = !tipo || t.getAttribute('data-tipo') === tipo;
        if (coincideTexto && coincideTipo) {
            t.style.display = 'flex';
            visibles++;
        } else {
            t.style.display = 'none';
        }
    });
    document.getElementById('empty-state').setAttribute('data-state', visibles === 0 ? 'visible' : '');
}