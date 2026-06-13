// ==========================================
// 1. ELIMINAR CLASES
// ==========================================
let deleteId = null;

function openDelete(id, nombre){
    deleteId = id;
    document.getElementById("form-delete").action =
        "/eliminar_clase/" + id + "?nombre_profesor=" + encodeURIComponent(nombre);

    document.getElementById("delete-overlay").style.display = "flex";
}

function closeDelete(){
    document.getElementById("delete-overlay").style.display = "none";
}


// ==========================================
// 2. MODAL EDITAR CLASES
// ==========================================
// ==========================================
// 2. MODAL EDITAR CLASES
// ==========================================
function openEditClase(id, fecha, tema, horario, d1, d2, d3){
    document.getElementById("edit-id").value = id;
    document.getElementById("edit-fecha").value = fecha;
    document.getElementById("edit-tema").value = tema;
    document.getElementById("edit-horario").value = horario;
    document.getElementById("edit-doc1").value = d1;
    document.getElementById("edit-doc2").value = d2;
    document.getElementById("edit-doc3").value = d3;

    document.getElementById("form-editar").action = "/editar_clase/" + id;
    
    // Abrimos usando únicamente manipulación de estilos nativos en línea
    document.getElementById("modal-overlay").style.display = "flex";
}

function closeModal(){
    const modal = document.getElementById("modal-overlay");
    if (modal) {
        modal.style.display = "none"; // Cierre directo
    }
    
    // CRÍTICO PARA EL CACHÉ: Reseteamos el formulario al cerrar o actualizar
    // Al vaciar los datos residuales, el navegador no fuerza la accesibilidad del div
    const formEditar = document.getElementById("form-editar");
    if (formEditar) {
        formEditar.reset(); 
    }

    const errorMsgEdit = document.getElementById("error-msg-edit");
    if (errorMsgEdit) {
        errorMsgEdit.style.display = "none"; // Ocultamos el cartel de error con style directo
    }
}

function closeModalOutside(e){
    if(e.target.id === "modal-overlay") closeModal();
}

// ==========================================
// 3. VALIDACIÓN E INTERCEPTACIÓN DE ERRORES
// ==========================================
document.addEventListener("DOMContentLoaded", function () {
    const formEditar = document.getElementById("form-editar");
    const errorMsgEdit = document.getElementById("error-msg-edit");
    const dataContainer = document.getElementById("asistencia-data");

    // A. EVITA EL PANTALLAZO Y EL BUG DEL CACHÉ
    if (formEditar && errorMsgEdit) {
        formEditar.addEventListener("submit", function (e) {
            const fecha = document.getElementById("edit-fecha").value;
            const tema = document.getElementById("edit-tema").value.trim();
            const horario = document.getElementById("edit-horario").value;

            // 1. PRIMER FILTRO: Validar campos estrictamente vacíos
            if (!fecha || !tema || !horario) {
                e.preventDefault(); // CONGELA EL FORMULARIO INMEDIATAMENTE
                errorMsgEdit.textContent = "⚠️ Campos obligatorios incompletos o inválidos";
                errorMsgEdit.style.display = "block"; // Estilo directo permitido
                return; 
            }

            // 2. SEGUNDO FILTRO: Validar año mínimo de forma segura
            const partes = fecha.split("-");
            const añoInput = parseInt(partes[0], 10);

            if (isNaN(añoInput) || añoInput < 2025) {
                e.preventDefault(); // Frena el envío
                errorMsgEdit.textContent = "⚠️ La fecha no puede ser anterior al año 2025";
                errorMsgEdit.style.display = "block";
                return;
            }

            // =========================================================
            // LA LÍNEA MÁGICA: Si pasa los filtros, lo ocultamos ACÁ 
            // antes de que viaje. Así el navegador lo procesa cerrado.
            // =========================================================
            document.getElementById("modal-overlay").style.display = "none";
            errorMsgEdit.style.display = "none";
        });
    }

    // B. RECOGE EL ERROR DEL SERVIDOR (Solo si el servidor reporta un fallo real)
    if (dataContainer) {
        const editErrorId = (dataContainer.dataset.editErrorId || "").trim();
        const editErrorFecha = (dataContainer.dataset.editErrorFecha || "").trim();

        if (!editErrorId || !editErrorFecha) return;

        if (editErrorId && editErrorId !== "None" && editErrorId !== "" && editErrorFecha && editErrorFecha !== "None" && editErrorFecha !== "") {
            if (errorMsgEdit) {
                errorMsgEdit.textContent = "⚠️ " + editErrorFecha;
                errorMsgEdit.style.display = "block";
            }

            document.getElementById("edit-id").value = editErrorId;
            document.getElementById("form-editar").action = "/editar_clase/" + editErrorId;
            
            const modal = document.getElementById("modal-overlay");
            if (modal) modal.style.display = "flex";
        }
    }
});