// 1. ESTADO
let evals = [];
let currentPage = 1;
const PER_PAGE = 4;

const TIPO_LABEL  = { tp: 'TP', parcial: '1ºP', final: 'F', recup: 'R' };
const INST_LABEL  = { regular: 'Evaluación Regular', recup: 'Instancia de Recuperación' };


// 2. FECHA
function deadlineStatus(dl) {
  if (!dl) return { cls: 'ok', txt: 'Sin fecha límite' };
  const d = new Date(dl), today = new Date();
  today.setHours(0, 0, 0, 0);
  const diff = Math.ceil((d - today) / (1000 * 60 * 60 * 24));
  if (diff < 0) return { cls: 'late', txt: 'Vencido' };
  if (diff <= 7) return { cls: 'warn', txt: `Vence en ${diff}d` };
  return { cls: 'ok', txt: `${d.toLocaleDateString('es-AR', { day: '2-digit', month: 'short' })}` };
}

function formatDate(str) {
  if (!str) return '—';
  const d = new Date(str + 'T00:00:00');
  return d.toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' });
}


// 3. API
async function fetchEvals() {
  try {
    const r = await fetch('/api/evaluaciones');
    const data = await r.json();
    // El back devuelve { listado: [...] }
    evals = data.listado || [];
  } catch (e) {
    showToast('⚠️ Error al cargar evaluaciones');
    evals = [];
  }
  render();
}

async function saveModal() {
  const nombre      = document.getElementById('f-nombre').value.trim();
  const tipo        = document.getElementById('f-tipo').value;
  const instancia   = document.getElementById('f-instancia').value;
  const fecha       = document.getElementById('f-fecha').value;
  const deadline    = document.getElementById('f-deadline').value;
  const obs         = document.getElementById('f-obs').value;
  const id_materia  = document.getElementById('f-materia').value;  // ver nota abajo

  if (!nombre || !tipo || !id_materia) {
    showToast('⚠️ Completá los campos obligatorios');
    return;
  }

  const body = { nombre, tipo, instancia, fecha, deadline: deadline || null, obs, id_materia: Number(id_materia) };

  const editingId = document.getElementById('modal-overlay').dataset.editingId;

  try {
    if (editingId) {
      await fetch(`/api/evaluaciones/${editingId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      showToast('✅ Evaluación actualizada');
    } else {
      await fetch('/api/evaluaciones', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      showToast('✅ Evaluación creada');
    }
  } catch (e) {
    showToast('⚠️ Error al guardar');
  }

  closeModal();
  await fetchEvals();
}

async function confirmDelete() {
  const id = document.getElementById('confirm-overlay').dataset.deletingId;
  if (!id) return;
  try {
    await fetch(`/api/evaluaciones/${id}`, { method: 'DELETE' });
    showToast('🗑️ Evaluación eliminada');
  } catch (e) {
    showToast('⚠️ Error al eliminar');
  }
  closeConfirm();
  await fetchEvals();
}


// 4. FILTRADO Y PAGINACIÓN
function getFiltered() {
  const q  = document.getElementById('search-input').value.toLowerCase();
  const ft = document.getElementById('filter-tipo').value;
  const fe = document.getElementById('filter-estado').value;
  return evals.filter(e => {
    // El back devuelve campos en MAYÚSCULAS
    const nombre = (e.NOMBRE || e.nombre || '').toLowerCase();
    const tipo   = e.TIPO   || e.tipo   || '';
    const dl     = e.DEADLINE || e.deadline || '';
    if (q  && !nombre.includes(q)) return false;
    if (ft && tipo !== ft) return false;
    if (fe && deadlineStatus(dl).cls !== fe) return false;
    return true;
  });
}

function filterCards() { currentPage = 1; render(); }


// 5. RENDER
function render() {
  const filtered   = getFiltered();
  const total      = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / PER_PAGE));
  if (currentPage > totalPages) currentPage = totalPages;
  const slice = filtered.slice((currentPage - 1) * PER_PAGE, currentPage * PER_PAGE);

  const list  = document.getElementById('eval-list');
  const empty = document.getElementById('empty-state');
  list.innerHTML = '';

  if (slice.length === 0) {
    empty.setAttribute('data-state', 'visible');
  } else {
    empty.removeAttribute('data-state');
  }

  slice.forEach(ev => {
    // mayúsculas/minúsculas del back
    const nombre    = ev.NOMBRE    || ev.nombre    || '';
    const tipo      = (ev.TIPO     || ev.tipo      || 'tp').toLowerCase();
    const instancia = (ev.INSTANCIA|| ev.instancia || 'regular').toLowerCase();
    const fecha     = ev.FECHA     || ev.fecha     || '';
    const deadline  = ev.DEADLINE  || ev.deadline  || '';
    const id        = ev.ID        || ev.id;

    const dl   = deadlineStatus(deadline);
    const card = document.createElement('div');
    card.innerHTML = `
      <div data-avatar="${tipo}">${TIPO_LABEL[tipo] || tipo}</div>
      <div>
        <h2>${nombre}</h2>
        <div>
          <span data-tag="${instancia}">${INST_LABEL[instancia] || instancia}</span>
          <span>📅 ${formatDate(fecha)}</span>
          <span data-deadline="${dl.cls}">⏱ ${dl.txt}</span>
        </div>
      </div>
      <div>
        <button onclick="verNotas(${id})" title="Ver notas">👁️</button>
        <button onclick="openEdit(${id})" title="Editar">✏️</button>
        <button onclick="openConfirm(${id})" title="Eliminar">🗑️</button>
      </div>
    `;
    list.appendChild(card);
  });

  document.getElementById('page-info').textContent =
    total === 0 ? '0 resultados'
    : `Mostrando ${(currentPage - 1) * PER_PAGE + 1}–${Math.min(currentPage * PER_PAGE, total)} de ${total}`;

  const pb = document.getElementById('page-buttons');
  pb.innerHTML = '';

  const prev = document.createElement('button');
  prev.textContent = '‹'; prev.disabled = currentPage === 1;
  prev.onclick = () => { currentPage--; render(); };
  pb.appendChild(prev);

  for (let p = 1; p <= totalPages; p++) {
    const b = document.createElement('button');
    if (p === currentPage) b.setAttribute('data-active', 'true');
    b.textContent = p;
    b.onclick = () => { currentPage = p; render(); };
    pb.appendChild(b);
  }

  const next = document.createElement('button');
  next.textContent = '›'; next.disabled = currentPage === totalPages;
  next.onclick = () => { currentPage++; render(); };
  pb.appendChild(next);
}


// 6. MODALES
function openModal() {
  delete document.getElementById('modal-overlay').dataset.editingId;
  document.getElementById('modal-title').textContent = 'Nueva Evaluación';
  ['f-nombre','f-fecha','f-deadline','f-obs'].forEach(id => document.getElementById(id).value = '');
  document.getElementById('f-tipo').value      = 'tp';
  document.getElementById('f-instancia').value = 'regular';
  document.getElementById('modal-overlay').setAttribute('data-state', 'open');
}

function openEdit(id) {
  const ev = evals.find(e => (e.ID || e.id) === id);
  if (!ev) return;
  document.getElementById('modal-overlay').dataset.editingId = id;
  document.getElementById('modal-title').textContent = 'Editar Evaluación';
  document.getElementById('f-nombre').value    = ev.NOMBRE    || ev.nombre    || '';
  document.getElementById('f-tipo').value      = (ev.TIPO     || ev.tipo      || 'tp').toLowerCase();
  document.getElementById('f-instancia').value = (ev.INSTANCIA|| ev.instancia || 'regular').toLowerCase();
  document.getElementById('f-fecha').value     = ev.FECHA     || ev.fecha     || '';
  document.getElementById('f-deadline').value  = ev.DEADLINE  || ev.deadline  || '';
  document.getElementById('f-obs').value       = ev.OBS       || ev.obs       || '';
  document.getElementById('modal-overlay').setAttribute('data-state', 'open');
}

function closeModal() { document.getElementById('modal-overlay').removeAttribute('data-state'); }
function closeModalOutside(e) { if (e.target.id === 'modal-overlay') closeModal(); }

let _confirmId = null;
function openConfirm(id) {
  document.getElementById('confirm-overlay').dataset.deletingId = id;
  document.getElementById('confirm-overlay').setAttribute('data-state', 'open');
}
function closeConfirm() { document.getElementById('confirm-overlay').removeAttribute('data-state'); }
function closeConfirmOutside(e) { if (e.target.id === 'confirm-overlay') closeConfirm(); }

function verNotas(id) {
  const urlParams = new URLSearchParams(window.location.search);
  const profesor  = urlParams.get('nombre_profesor') || '';
  window.location.href = `/notas?nombre_profesor=${encodeURIComponent(profesor)}&id_evaluacion=${id}`;
}

function switchTab(btn, tab) {
  document.querySelectorAll('#tabs button').forEach(b => b.removeAttribute('data-active'));
  btn.setAttribute('data-active', 'true');
  if (tab === 'historial') showToast('📋 Historial — próximamente');
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.setAttribute('data-state', 'show');
  setTimeout(() => t.removeAttribute('data-state'), 2800);
}


// 7. ARRANQUE
fetchEvals();
