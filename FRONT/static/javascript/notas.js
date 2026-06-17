// 1. ESTADO
let alumnos = JSON.parse(localStorage.getItem('notas_eval')) || [];
let id_evaluacion = new URLSearchParams(window.location.search).get('id_evaluacion');

// 2. LÓGICA DE NOTAS
function renderTabla() {
  const tbody = document.getElementById('tabla-body');
  tbody.innerHTML = '';

  // Filtrar notas solo para esta evaluación
  const notasFiltradas = alumnos.filter(a => a.id_evaluacion == id_evaluacion);

  notasFiltradas.forEach((al, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${al.padron}</td>
      <td>${al.nombre}</td>
      <td><input type="number" value="${al.nota}" oninput="actualizarNota(${i}, this.value)"></td>
    `;
    tbody.appendChild(tr);
  });
}

function actualizarNota(index, nuevaNota) {
  alumnos[index].nota = nuevaNota;
  localStorage.setItem('notas_eval', JSON.stringify(alumnos));
}

function guardarCambios() {
  alert('✅ Notas guardadas');
}

// Inicialización
renderTabla();
