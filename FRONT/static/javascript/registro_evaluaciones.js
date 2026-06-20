let evals = JSON.parse(localStorage.getItem('evals')) || [];
let currentPage = 1;
const PER_PAGE = 4;

const TIPO_LABEL = { tp: 'TP', parcial: '1ºP', final: 'F', recup: 'R' };
const INST_LABEL = { regular: 'Evaluación Regular', recup: 'Instancia de Recuperación' };

function syncStorage() {
  localStorage.setItem('evals', JSON.stringify(evals));
  render();
}

function saveModal() {
  const nombre = document.getElementById('f-nombre').value.trim();
  const tipo = document.getElementById('f-tipo').value;
  const instancia = document.getElementById('f-instancia').value;
  const fecha = document.getElementById('f-fecha').value;
  const deadline = document.getElementById('f-deadline').value;
  const obs = document.getElementById('f-obs').value;
  const id_materia = document.getElementById('f-materia').value;

  if (!nombre || !tipo || !id_materia) {
    alert('⚠️ Completá los campos obligatorios');
    return;
  }

  const editingId = document.getElementById('modal-overlay').dataset.editingId;
  const data = { id: editingId ? Number(editingId) : Date.now(), nombre, tipo, instancia, fecha, deadline, obs, id_materia: Number(id_materia) };

  if (editingId) {
    const index = evals.findIndex(e => e.id === Number(editingId));
    evals[index] = data;
  } else {
    evals.push(data);
  }

  syncStorage();
  closeModal();
}

function confirmDelete() {
  const id = document.getElementById('confirm-overlay').dataset.deletingId;
  evals = evals.filter(e => e.id !== Number(id));
  syncStorage();
  closeConfirm();
}

function render() {
  const list = document.getElementById('eval-list');
  list.innerHTML = '';
  
  evals.forEach(ev => {
    const card = document.createElement('div');
    card.innerHTML = `
      <div>${TIPO_LABEL[ev.tipo] || ev.tipo}</div>
      <h2>${ev.nombre}</h2>
      <div>
        <span>${INST_LABEL[ev.instancia] || ev.instancia}</span>
        <button onclick="verNotas(${ev.id})">👁️</button>
        <button onclick="openEdit(${ev.id})">✏️</button>
        <button onclick="openConfirm(${ev.id})">🗑️</button>
      </div>
    `;
    list.appendChild(card);
  });
}

function verNotas(id) {
  window.location.href = `/notas.html?id_evaluacion=${id}`;
}

render();
