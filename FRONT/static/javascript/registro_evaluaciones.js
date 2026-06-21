let evals = JSON.parse(localStorage.getItem('evals')) || [];
let editingId = null;

function toggleDateFields() {
    const tipo = document.getElementById('f-tipo').value;
    const groupFechaUnica = document.getElementById('group-fecha-unica');
    const groupFechasTp = document.getElementById('group-fechas-tp');
    const groupInstancia = document.getElementById('group-instancia');

    if (tipo === 'tp-individual' || tipo === 'tp-grupal') {
        groupFechaUnica.style.display = 'none';
        groupFechasTp.style.display = 'block';
        if (groupInstancia) groupInstancia.style.display = 'none';
    } else {
        groupFechaUnica.style.display = 'block';
        groupFechasTp.style.display = 'none';
        if (groupInstancia) groupInstancia.style.display = 'block';
    }
}

function openModal(modo = null) {
    const overlay = document.getElementById('modal-overlay');
    const titulo = document.getElementById('modal-title');
    const selectTipo = document.getElementById('f-tipo');

    if (modo === 'tp') {
        editingId = null;
        titulo.textContent = 'Nuevo Trabajo Práctico';
        selectTipo.innerHTML = `
            <option value="tp-individual">TP Individual</option>
            <option value="tp-grupal">TP Grupal</option>
        `;
        limpiarFormulario();
        toggleDateFields();
    } else if (modo === 'eval') {
        editingId = null;
        titulo.textContent = 'Nueva Evaluación / Examen';
        selectTipo.innerHTML = `
            <option value="parcial">Parcial</option>
            <option value="final">Final</option>
            <option value="recup">Recuperatorio</option>
        `;
        limpiarFormulario();
        toggleDateFields();
    } else if (modo !== null) {
        const ev = evals.find(e => e.id === modo);
        if (!ev) return;

        editingId = modo;
        titulo.textContent = 'Editar Registro';

        if (ev.tipo === 'tp-individual' || ev.tipo === 'tp-grupal') {
            selectTipo.innerHTML = `
                <option value="tp-individual">TP Individual</option>
                <option value="tp-grupal">TP Grupal</option>
            `;
        } else {
            selectTipo.innerHTML = `
                <option value="parcial">Parcial</option>
                <option value="final">Final</option>
                <option value="recup">Recuperatorio</option>
            `;
        }

        document.getElementById('f-nombre').value = ev.nombre;
        selectTipo.value = ev.tipo;
        if (document.getElementById('f-instancia')) {
            document.getElementById('f-instancia').value = ev.instancia || 'regular';
        }
        document.getElementById('f-obs').value = ev.obs || '';
        
        toggleDateFields();

        if (ev.tipo === 'tp-individual' || ev.tipo === 'tp-grupal') {
            document.getElementById('f-fecha-inicio').value = ev.fechaInicio || '';
            document.getElementById('f-fecha-entrega').value = ev.fechaEntrega || '';
            document.getElementById('f-fecha').value = '';
        } else {
            document.getElementById('f-fecha').value = ev.fecha || '';
            document.getElementById('f-fecha-inicio').value = '';
            document.getElementById('f-fecha-entrega').value = '';
        }
    }
    overlay.setAttribute('data-state', 'open');
}

function closeModal() {
    document.getElementById('modal-overlay').removeAttribute('data-state');
    editingId = null;
}

function closeModalOutside(e) {
    if (e.target.id === 'modal-overlay') closeModal();
}

function saveModal() {
    const nombre = document.getElementById('f-nombre').value.trim();
    const tipo = document.getElementById('f-tipo').value;
    const instanciaSelect = document.getElementById('f-instancia');
    const instancia = (instanciaSelect && (tipo !== 'tp-individual' && tipo !== 'tp-grupal')) ? instanciaSelect.value : '';
    const obs = document.getElementById('f-obs').value.trim();

    let fecha = '';
    let fechaInicio = '';
    let fechaEntrega = '';

    if (!nombre) {
        alert('⚠️ Por favor, completá el nombre.');
        return;
    }

    if (tipo === 'tp-individual' || tipo === 'tp-grupal') {
        fechaInicio = document.getElementById('f-fecha-inicio').value;
        fechaEntrega = document.getElementById('f-fecha-entrega').value;
        if (!fechaInicio || !fechaEntrega) {
            alert('⚠️ Por favor, completá la fecha de inicio y de entrega.');
            return;
        }
        fecha = fechaEntrega;
    } else {
        fecha = document.getElementById('f-fecha').value;
        if (!fecha) {
            alert('⚠️ Por favor, completá la fecha de la evaluación.');
            return;
        }
    }

    const eraEdicion = !!editingId;
    if (eraEdicion) {
        const idx = evals.findIndex(e => e.id === editingId);
        if (idx !== -1) {
            evals[idx] = { ...evals[idx], nombre, tipo, instancia, fecha, fechaInicio, fechaEntrega, obs };
        }
    } else {
        evals.push({ id: Date.now(), nombre, tipo, instancia, fecha, fechaInicio, fechaEntrega, obs });
    }

    localStorage.setItem('evals', JSON.stringify(evals));
    filterCards();
    closeModal();
    limpiarFormulario();
    mostrarToast(eraEdicion ? '✅ Registro actualizado.' : '✅ Registro guardado.');
}

function limpiarFormulario() {
    document.getElementById('f-nombre').value = '';
    document.getElementById('f-obs').value = '';
    document.getElementById('f-fecha').value = '';
    document.getElementById('f-fecha-inicio').value = '';
    document.getElementById('f-fecha-entrega').value = '';
}

function filterCards() {
    const texto = document.getElementById('search-input')?.value.toLowerCase() || '';
    const tipo = document.getElementById('filter-tipo')?.value || '';
    const filtrados = evals.filter(ev => ev.nombre.toLowerCase().includes(texto) && (!tipo || ev.tipo === tipo));
    render(filtrados);
}

function render(lista = evals) {
    const list = document.getElementById('eval-list');
    const emptyState = document.getElementById('empty-state');
    list.innerHTML = '';

    if (lista.length === 0) {
        emptyState.setAttribute('data-state', 'visible');
        return;
    } else {
        emptyState.removeAttribute('data-state');
    }

    lista.sort((a, b) => new Date(a.fecha) - new Date(b.fecha)).forEach(ev => {
        const card = document.createElement('div');
        const obsHtml = ev.obs ? `<p style="margin: 4px 0 0 0; color:#64748b; font-size:13px;">📝 ${ev.obs}</p>` : '';
        
        let fechaTexto = '';
        if (ev.tipo === 'tp-individual' || ev.tipo === 'tp-grupal') {
            fechaTexto = `📅 Inicio: ${ev.fechaInicio} · Entrega: ${ev.fechaEntrega}`;
        } else {
            let badgeInstancia = ev.instancia === 'recup' ? ' (Recuperatorio)' : '';
            fechaTexto = `📅 ${ev.fecha} · Evaluación${badgeInstancia}`;
        }

        let tipoDisplay = ev.tipo.replace('-', ' ').toUpperCase();
        
        card.innerHTML = `
            <div data-avatar="${ev.tipo}">${ev.tipo.charAt(0).toUpperCase()}</div>
            <div style="flex:1;">
                <h2 style="font-size:16px; margin:0; color:#1e293b;">${ev.nombre}</h2>
                <span style="font-size:11px; font-weight:700; color:#4f46e5; text-transform:uppercase; margin-right:8px;">${tipoDisplay}</span>
                <span style="font-size:13px; color:#64748b;">${fechaTexto}</span>
                ${obsHtml}
            </div>
            <div style="display:flex; gap:8px;">
                <button onclick="openModal(${ev.id})" style="background:none; border:none; cursor:pointer; font-size:16px;">✏️</button>
                <button onclick="eliminarEvaluacion(${ev.id})" style="background:none; border:none; cursor:pointer; font-size:16px;">🗑️</button>
            </div>
        `;
        list.appendChild(card);
    });
}

function eliminarEvaluacion(id) {
    if (confirm('¿Seguro que querés eliminar este registro?')) {
        evals = evals.filter(e => e.id !== id);
        localStorage.setItem('evals', JSON.stringify(evals));
        filterCards();
    }
}

function mostrarToast(mensaje) {
    let toast = document.getElementById('toast-evaluaciones') || document.createElement('div');
    toast.id = 'toast-evaluaciones';
    toast.style.cssText = "position:fixed; bottom:30px; left:50%; transform:translateX(-50%); background:#1e293b; color:#fff; padding:14px 24px; border-radius:12px; z-index:999;";
    toast.textContent = mensaje;
    if (!toast.parentNode) document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2800);
}

filterCards();
