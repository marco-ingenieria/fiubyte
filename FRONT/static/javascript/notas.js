// 1. ESTADO
let alumnos      = [];
let id_evaluacion = null;


// 2. CARGA INICIAL
async function init() {
  // Leer id_evaluacion de la URL
  const params  = new URLSearchParams(window.location.search);
  id_evaluacion = params.get('id_evaluacion');

  if (!id_evaluacion) {
    showToast('⚠️ No se indicó una evaluación');
    renderTabla();
    return;
  }

  try {
    const r    = await fetch(`/api/notas?id_evaluacion=${id_evaluacion}`);
    const data = await r.json();
    const notas = data.listado || [];

    // Convertir el listado de notas al formato que usa la tabla
    // Cada nota tiene: PADRON_ALUMNO, NOTA, ID_EVALUACION
    alumnos = notas.map(n => ({
      padron:    n.PADRON_ALUMNO || n.padron_alumno,
      nombre:    n.NOMBRE_ALUMNO || n.nombre || '—',   // si el back lo devuelve
      nota:      n.NOTA          || n.nota   || '',
      id_nota:   n.ID            || n.id,
    }));
  } catch (e) {
    showToast('⚠️ Error al cargar las notas');
    alumnos = [];
  }

  renderTabla();
}


// 3. RENDER
function renderTabla() {
  const tbody = document.getElementById('tabla-body');
  tbody.innerHTML = '';

  alumnos.forEach((al, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${al.padron}</td>
      <td><strong>${al.nombre}</strong></td>
      <td>
        <input type="number" min="1" max="10"
          value="${al.nota}" placeholder="—"
          data-idx="${i}" data-key="nota"
          ${colorNotaAttr(al.nota)}
          oninput="onNotaChange(this)">
      </td>
    `;
    tbody.appendChild(tr);
  });

  updateStats();
}

function colorNotaAttr(v) {
  if (v === '' || v === undefined) return '';
  const n = Number(v);
  if (n >= 6) return 'data-color="alta"';
  if (n < 4)  return 'data-color="baja"';
  return '';
}


// 4. COLOR DE APROBACION/DESAPROBACIOM
function onNotaChange(inp) {
  const i = Number(inp.dataset.idx);
  const v = inp.value;
  alumnos[i].nota = v;

  const n = Number(v);
  if (v === '') inp.removeAttribute('data-color');
  else if (n >= 6) inp.setAttribute('data-color', 'alta');
  else if (n < 4)  inp.setAttribute('data-color', 'baja');
  else inp.removeAttribute('data-color');

  updateStats();
}

function updateStats() {
  const notas = alumnos.map(a => Number(a.nota)).filter(n => n > 0);
  const ap    = notas.filter(n => n >= 6).length;
  const des   = notas.filter(n => n < 6 && n > 0).length;
  const prom  = notas.length
    ? (notas.reduce((a, b) => a + b, 0) / notas.length).toFixed(1)
    : '—';

  document.getElementById('stat-ap').textContent   = ap;
  document.getElementById('stat-des').textContent  = des;
  document.getElementById('stat-prom').textContent = prom;
}


// 5. GUARDAR — envía cada nota al back con POST /api/notas
async function guardarCambios() {
  if (!id_evaluacion) {
    showToast('⚠️ No hay evaluación seleccionada');
    return;
  }

  const btn = document.getElementById('btn-guardar');
  btn.disabled = true;

  let errores = 0;

  for (const al of alumnos) {
    if (al.nota === '' || al.nota === undefined) continue;
    try {
      const r = await fetch('/api/notas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          padron:        al.padron,
          id_evaluacion: Number(id_evaluacion),
          nota:          Number(al.nota)
        })
      });
      if (!r.ok) errores++;
    } catch (e) {
      errores++;
    }
  }

  btn.disabled = false;

  if (errores === 0) {
    btn.textContent = '✅ Guardado';
    btn.setAttribute('data-saved', 'true');
    showToast('✅ Notas guardadas correctamente');
    setTimeout(() => {
      btn.textContent = '💾 Guardar Cambios';
      btn.removeAttribute('data-saved');
    }, 2500);
  } else {
    showToast(`⚠️ ${errores} nota(s) no se pudieron guardar`);
  }
}


// 6. DESCARGA CSV
function openDL(mode) {
  const isTP = mode === 'tp';
  document.getElementById('dl-title').textContent  = isTP ? 'Descargar TPs' : 'Descargar Exámenes';
  document.getElementById('dl-overlay').setAttribute('data-state', 'open');
}

function closeDL()  { document.getElementById('dl-overlay').removeAttribute('data-state'); }
function closeDLOutside(e) { if (e.target.id === 'dl-overlay') closeDL(); }

function downloadCSV(key) {
  const labels = { nota: 'Nota' };
  const rows   = [['Padrón', 'Nombre', 'Nota']];
  alumnos.forEach(a => rows.push([a.padron, a.nombre, a.nota || '']));
  const csv = rows.map(r => r.map(c => `"${c}"`).join(',')).join('\n');
  triggerDownload(csv, `notas_evaluacion_${id_evaluacion}.csv`, 'text/csv');
  closeDL();
  showToast('📄 Descargando...');
}

function downloadPlanilla() {
  downloadCSV('nota');
}

function triggerDownload(content, filename, mime) {
  const blob = new Blob([content], { type: mime });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.setAttribute('data-state', 'show');
  setTimeout(() => t.removeAttribute('data-state'), 2800);
}


// 7. ARRANQUE
init();
