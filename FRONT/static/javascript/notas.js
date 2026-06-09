// 1. MODELO DE DATOS (MOCK UP ALUMNOS)
let alumnos = [
  {padron:'105432', nombre:'Juan Rodriguez',      tp1:'', tp2:'', p1:'', p2:'', final:'', notaFinal:'', estado:'APROBADO',    abandono:false},
  {padron:'106112', nombre:'Guillermo Francella', tp1:'', tp2:'', p1:'', p2:'', final:'', notaFinal:'', estado:'APROBADO',    abandono:false},
  {padron:'104873', nombre:'Ricardo Darín',       tp1:'', tp2:'', p1:'', p2:'', final:'', notaFinal:'', estado:'DESAPROBADO', abandono:true },
  {padron:'105991', nombre:'Evelyn Gómez',        tp1:'', tp2:'', p1:'', p2:'', final:'', notaFinal:'', estado:'DESAPROBADO', abandono:false},
  {padron:'102345', nombre:'Luis Brandoni',       tp1:'', tp2:'', p1:'', p2:'', final:'', notaFinal:'', estado:'APROBADO',    abandono:false},
];

// 2. RENDERIZADO Y CONTROL DE LA INTERFAZ
function renderTabla(){
  const tbody = document.getElementById('tabla-body');
  tbody.innerHTML='';
  alumnos.forEach((al,i)=>{
    const bl = al.abandono;
    const tr = document.createElement('tr');
    
    if(bl) tr.setAttribute('data-status', 'bloqueado');
    
    tr.innerHTML=`
      <td>${al.padron}</td>
      <td>
        <div>
          <strong>${al.nombre}</strong>
          ${bl?'<span>Abandono</span>':''}
        </div>
      </td>
      ${['tp1','tp2','p1','p2','final'].map(k=>`
        <td>
          <input type="number" min="1" max="10" 
            value="${al[k]}" placeholder="—"
            ${bl?'disabled':''}
            data-idx="${i}" data-key="${k}"
            ${colorNotaAttr(al[k])}
            oninput="onNotaChange(this)">
        </td>
      `).join('')}
      <td>
        <input type="number" min="1" max="10"
          value="${al.notaFinal}" placeholder="—"
          ${bl?'disabled':''}
          data-idx="${i}" data-key="notaFinal"
          ${colorNotaAttr(al.notaFinal)}
          oninput="onNotaChange(this)">
      </td>
      <td>
        <div>
          ${['APROBADO','DESAPROBADO'].map(est=>`
            <button data-est="${est.toLowerCase()}" ${!bl && al.estado===est?'data-active="true"':''}
              ${bl?'disabled':''}
              onclick="setEstado(${i},'${est}',this)">
              ${est==='APROBADO'?'✓ ':'✗ '}${est}
            </button>
           `).join('')}
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
  updateStats();
}

// Devuelve el atributo de color según la nota de la FIUBA
function colorNotaAttr(v){
  if(v===''||v===undefined) return '';
  const n=Number(v);
  if(n>=6) return 'data-color="alta"';
  if(n<4)  return 'data-color="baja"';
  return '';
}

// 3. GESTIÓN DE EVENTOS Y CÁLCULOS
// Escucha cambios en tiempo real en los inputs de notas
function onNotaChange(inp){
  const i=Number(inp.dataset.idx), k=inp.dataset.key;
  const v=inp.value;
  alumnos[i][k]=v;
  
  const n=Number(v);
  if(v==='') inp.removeAttribute('data-color');
  else if(n>=6) inp.setAttribute('data-color', 'alta');
  else if(n<4) inp.setAttribute('data-color', 'baja');
  else inp.removeAttribute('data-color');
  
  updateStats();
}

// Cambia el estado (Aprobado/Desaprobado) del alumno
function setEstado(i, estado, btn){
  alumnos[i].estado=estado;
  const container = btn.closest('div');
  container.querySelectorAll('button').forEach(b=>b.removeAttribute('data-active'));
  btn.setAttribute('data-active', 'true');
  updateStats();
}

// Recalcula estadísticas globales (excluye abandonos)
function updateStats(){
  const valid = alumnos.filter(a=>!a.abandono);
  const ap  = valid.filter(a=>a.estado==='APROBADO').length;
  const des = valid.filter(a=>a.estado==='DESAPROBADO').length;
  const notas = valid.map(a=>Number(a.notaFinal)).filter(n=>n>0);
  const prom = notas.length ? (notas.reduce((a,b)=>a+b,0)/notas.length).toFixed(1) : '—';
  
  document.getElementById('stat-ap').textContent=ap;
  document.getElementById('stat-des').textContent=des;
  document.getElementById('stat-prom').textContent=prom;
}

// Guarda cambios y muestra feedback visual efímero
function guardarCambios(){
  const btn=document.getElementById('btn-guardar');
  btn.textContent='✅ Guardado'; btn.setAttribute('data-saved', 'true');
  showToast('✅ Planilla guardada correctamente');
  setTimeout(()=>{
    btn.textContent='💾 Guardar Cambios'; btn.removeAttribute('data-saved');
  },2500);
}

// 4. EXPORTACIÓN DE ARCHIVOS (CSV) Y MODALES
// Configura y abre el modal de descarga según el modo (TP o Examen)
function openDL(mode){
  const isTP=mode==='tp';
  document.getElementById('dl-title').textContent=isTP?'Descargar Trabajos Prácticos':'Descargar Exámenes';
  document.getElementById('dl-desc').textContent='Elegí qué querés descargar:';
  
  const optPrimary = document.querySelector('div[data-download-option="primary"]');
  const optSecondary = document.querySelector('div[data-download-option="secondary"]');
  
  if(isTP){
    optPrimary.onclick=()=>downloadCSV('tp1');
    optPrimary.querySelector('h3').textContent='TP 1 – Lista de alumnos y notas';
    optPrimary.querySelector('p').textContent='CSV con padrón, nombre y calificación del TP 1';
    optSecondary.onclick=()=>downloadCSV('tp2');
    optSecondary.querySelector('h3').textContent='TP 2 – Lista de alumnos y notas';
    optSecondary.querySelector('p').textContent='CSV con padrón, nombre y calificación del TP 2';
  } else {
    optPrimary.onclick=()=>downloadCSV('p1');
    optPrimary.querySelector('h3').textContent='1er Parcial – Lista de alumnos y notas';
    optPrimary.querySelector('p').textContent='CSV con padrón, nombre y calificación del 1er Parcial';
    optSecondary.onclick=()=>downloadCSV('p2');
    optSecondary.querySelector('h3').textContent='2do Parcial – Lista de alumnos y notas';
    optSecondary.querySelector('p').textContent='CSV con padrón, nombre y calificación del 2do Parcial';
  }
  document.getElementById('dl-overlay').setAttribute('data-state', 'open');
}

function closeDL(){document.getElementById('dl-overlay').removeAttribute('data-state');}
function closeDLOutside(e){if(e.target.id==='dl-overlay')closeDL();}

// Genera y descarga el archivo CSV por columna específica
function downloadCSV(key){
  const labels={tp1:'TP1',tp2:'TP2',p1:'1er_Parcial',p2:'2do_Parcial',final:'Final'};
  const rows=[['Padrón','Apellido y Nombre','Nota '+labels[key],'Estado']];
  alumnos.forEach(a=>{
    rows.push([a.padron, a.nombre, a[key]||'', a.abandono?'DESAPROBADO':a.estado]);
  });
  const csv=rows.map(r=>r.map(c=>`"${c}"`).join(',')).join('\n');
  triggerDownload(csv, `notas_${labels[key]}_2026.csv`, 'text/csv');
  closeDL();
  showToast(`📄 Descargando ${labels[key]}...`);
}

// Genera y descarga la planilla completa
function downloadPlanilla(tipo){
  const rows=[['Padrón','Nombre','TP1','TP2','1er Parcial','2do Parcial','Final','Nota Final','Estado']];
  alumnos.forEach(a=>{
    rows.push([a.padron,a.nombre,a.tp1,a.tp2,a.p1,a.p2,a.final,a.notaFinal,a.abandono?'DESAPROBADO':a.estado]);
  });
  const csv=rows.map(r=>r.map(c=>`"${c}"`).join(',')).join('\n');
  triggerDownload(csv,'planilla_completa_2026.csv','text/csv');
  showToast('📊 Descargando planilla completa...');
}

// Inyecta el link en el DOM para forzar la descarga del Blob
function triggerDownload(content, filename, mime){
  const blob=new Blob([content],{type:mime});
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a');
  a.href=url; a.download=filename; a.click();
  URL.revokeObjectURL(url);
}

// Lanza la notificación emergente 
function showToast(msg){
  const t=document.getElementById('toast');
  t.textContent=msg; t.setAttribute('data-state', 'show');
  setTimeout(()=>t.removeAttribute('data-state'), 2800);
}

// Ejecución inicial al cargar el script
renderTabla();
