// 1. BANCO DE EVALUACIONES (MOCK DATA)
let evals = [
  {id:1, nombre:'TRABAJO PRÁCTICO 1 – 2026', tipo:'tp', instancia:'regular', fecha:'2026-04-10', deadline:'2026-04-25', obs:''},
  {id:2, nombre:'TRABAJO PRÁCTICO 2 – 2026', tipo:'tp', instancia:'regular', fecha:'2026-05-20', deadline:'2026-06-05', obs:''},
  {id:3, nombre:'1ER PARCIAL – 2026',        tipo:'parcial', instancia:'regular', fecha:'2026-05-14', deadline:'2026-05-28', obs:''},
  {id:4, nombre:'2DO PARCIAL – 2026',        tipo:'parcial', instancia:'regular', fecha:'2026-06-25', deadline:'2026-07-10', obs:''},
  {id:5, nombre:'FINAL 1 – 2026',            tipo:'final',   instancia:'regular', fecha:'2026-07-15', deadline:'2026-07-30', obs:''},
  {id:6, nombre:'1ER RECUPERATORIO – 2026',  tipo:'recup',   instancia:'recup',   fecha:'2026-06-30', deadline:'2026-07-15', obs:''},
];
let currentPage = 1;
const PER_PAGE = 4;

const TIPO_LABEL = {tp:'TP', parcial:'1ºP', final:'F', recup:'R'};
const INST_LABEL = {regular:'Evaluación Regular', recup:'Instancia de Recuperación'};


// 2. PROCESAMIENTO Y FILTRADO DE FECHAS
// Evalúa los plazos de entrega y devuelve el estado semántico de alertas
function deadlineStatus(dl){
  if(!dl) return {cls:'ok', txt:'Sin fecha límite'};
  const d = new Date(dl), today = new Date();
  today.setHours(0,0,0,0);
  const diff = Math.ceil((d-today)/(1000*60*60*24));
  if(diff < 0) return {cls:'late', txt:`Vencido`};
  if(diff <= 7) return {cls:'warn', txt:`Vence en ${diff}d`};
  return {cls:'ok', txt:`${d.toLocaleDateString('es-AR',{day:'2-digit',month:'short'})}`};
}

// Formatea strings de fecha al estándar local
function formatDate(str){
  if(!str) return '—';
  const d = new Date(str+'T00:00:00');
  return d.toLocaleDateString('es-AR',{day:'2-digit',month:'short',year:'numeric'});
}

// Resuelve el filtro cruzado por inputs de búsqueda y selectores
function getFiltered(){
  const q = document.getElementById('search-input').value.toLowerCase();
  const ft = document.getElementById('filter-tipo').value;
  const fe = document.getElementById('filter-estado').value;
  return evals.filter(e=>{
    if(q && !e.nombre.toLowerCase().includes(q)) return false;
    if(ft && e.tipo !== ft) return false;
    if(fe){
      const st = deadlineStatus(e.deadline).cls;
      if(fe !== st) return false;
    }
    return true;
  });
}


// 3. RENDERIZADO DE INTERFAZ Y PAGINACIÓN

// Dibuja las tarjetas de evaluación y los botones de paginación
function render(){
  const filtered = getFiltered();
  const total = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total/PER_PAGE));
  if(currentPage > totalPages) currentPage = totalPages;
  const slice = filtered.slice((currentPage-1)*PER_PAGE, currentPage*PER_PAGE);

  const list = document.getElementById('eval-list');
  const empty = document.getElementById('empty-state');
  list.innerHTML='';

  if(slice.length === 0){ empty.setAttribute('data-state', 'visible'); }
  else { empty.removeAttribute('data-state'); }

  slice.forEach((ev)=>{
    const dl = deadlineStatus(ev.deadline);
    const card = document.createElement('div');
    card.innerHTML = `
      <div data-avatar="${ev.tipo}">${TIPO_LABEL[ev.tipo]}</div>
      <div>
        <h2>${ev.nombre}</h2>
        <div>
          <span data-tag="${ev.instancia}">${INST_LABEL[ev.instancia]}</span>
          <span>📅 ${formatDate(ev.fecha)}</span>
          <span data-deadline="${dl.cls}">⏱ ${dl.txt}</span>
        </div>
      </div>
      <div>
        <button onclick="verNotas(${ev.id})" title="Ver notas">👁️</button>
        <button onclick="openEdit(${ev.id})" title="Editar">✏️</button>
        <button onclick="openConfirm(${ev.id})" title="Eliminar">🗑️</button>
      </div>
    `;
    list.appendChild(card);
  });

  document.getElementById('page-info').textContent = total===0 ? '0 resultados' : `Mostrando ${(currentPage-1)*PER_PAGE+1}–${Math.min(currentPage*PER_PAGE,total)} de ${total}`;
  const pb = document.getElementById('page-buttons');
  pb.innerHTML='';
  
  const prevBtn = document.createElement('button');
  prevBtn.textContent = '‹'; prevBtn.disabled = currentPage===1;
  prevBtn.onclick = ()=>{currentPage--; render();};
  pb.appendChild(prevBtn);
  
  for(let p=1; p<=totalPages; p++){
    const b = document.createElement('button');
    if(p === currentPage) b.setAttribute('data-active', 'true');
    b.textContent = p;
    b.onclick = ()=>{currentPage=p; render();};
    pb.appendChild(b);
  }
  
  const nextBtn = document.createElement('button');
  nextBtn.textContent = '›'; nextBtn.disabled = currentPage===totalPages;
  nextBtn.onclick = ()=>{currentPage++; render();};
  pb.appendChild(nextBtn);
}

function filterCards(){ currentPage=1; render(); }


// 4. CONTROL DE MODALES Y NAVEGACIÓN
// Abre y limpia el modal para crear una nueva evaluación
function openModal(){
  document.getElementById('modal-title').textContent='Nueva Evaluación';
  document.getElementById('f-nombre').value='';
  document.getElementById('f-tipo').value='tp';
  document.getElementById('f-instancia').value='regular';
  document.getElementById('f-fecha').value='';
  document.getElementById('f-deadline').value='';
  document.getElementById('f-obs').value='';
  document.getElementById('modal-overlay').setAttribute('data-state', 'open');
}

// Carga los datos de una evaluación existente para editarla
function openEdit(id){
  const ev = evals.find(e=>e.id===id);
  if(!ev) return;
  document.getElementById('modal-title').textContent='Editar Evaluación';
  document.getElementById('f-nombre').value=ev.nombre;
  document.getElementById('f-tipo').value=ev.tipo;
  document.getElementById('f-instancia').value=ev.instancia;
  document.getElementById('f-fecha').value=ev.fecha||'';
  document.getElementById('f-deadline').value=ev.deadline||'';
  document.getElementById('f-obs').value=ev.obs||'';
  document.getElementById('modal-overlay').setAttribute('data-state', 'open');
}

function closeModal(){ document.getElementById('modal-overlay').removeAttribute('data-state'); }
function closeModalOutside(e){ if(e.target.id==='modal-overlay') closeModal(); }

// Derivación dinámica conservando los query params del profesor
function verNotas(id){ 
  const urlParams = new URLSearchParams(window.location.search);
  const profesor = urlParams.get('nombre_profesor') || '';
  window.location.href = '/notas?nombre_profesor=' + encodeURIComponent(profesor); 
}

// Cambia de pestaña activa en la interfaz superior
function switchTab(btn, tab){
  document.querySelectorAll('#tabs button').forEach(b=>b.removeAttribute('data-active'));
  btn.setAttribute('data-active', 'true');
  if(tab==='historial') showToast('📋 Historial — próximamente');
}

// Dispara el sistema de notificaciones globales
function showToast(msg){
  const t=document.getElementById('toast');
  t.textContent=msg; t.setAttribute('data-state', 'show');
  setTimeout(()=>t.removeAttribute('data-state'), 2800);
}

// Inicialización de la vista
render();
