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


function openEditClase(id, fecha, tema, horario, d1, d2, d3){
    document.getElementById("edit-id").value = id;
    document.getElementById("edit-fecha").value = fecha;
    
    const selectTema = document.getElementById("edit-tema");
    if (selectTema) {
        selectTema.value = tema;
    }
    
    document.getElementById("edit-horario").value = horario;
    document.getElementById("edit-doc1").value = d1;
    document.getElementById("edit-doc2").value = d2;
    document.getElementById("edit-doc3").value = d3;

    document.getElementById("form-editar").action = "/editar_clase/" + id;
    
    document.getElementById("modal-overlay").style.display = "flex";
}

function closeModal(){
    const modal = document.getElementById("modal-overlay");
    if (modal) {
        modal.style.display = "none"; 
    }
    
    const formEditar = document.getElementById("form-editar");
    if (formEditar) {
        formEditar.reset(); 
    }

    const errorMsgEdit = document.getElementById("error-msg-edit");
    if (errorMsgEdit) {
        errorMsgEdit.style.display = "none"; 
    }
}

function closeModalOutside(e){
    if(e.target.id === "modal-overlay") closeModal();
}

document.addEventListener("DOMContentLoaded", function () {
    const formEditar = document.getElementById("form-editar");
    const errorMsgEdit = document.getElementById("error-msg-edit");
    const dataContainer = document.getElementById("asistencia-data");

    if (formEditar && errorMsgEdit) {
        formEditar.addEventListener("submit", function (e) {
            const fecha = document.getElementById("edit-fecha").value;
            const tema = document.getElementById("edit-tema").value.trim();
            const horario = document.getElementById("edit-horario").value;

            if (!fecha || !tema || !horario) {
                e.preventDefault(); 
                errorMsgEdit.textContent = "⚠️ Campos obligatorios incompletos o inválidos";
                errorMsgEdit.style.display = "block"; 
                return; 
            }

            const partes = fecha.split("-");
            const añoInput = parseInt(partes[0], 10);

            if (isNaN(añoInput) || añoInput < 2025) {
                e.preventDefault(); 
                errorMsgEdit.textContent = "⚠️ La fecha no puede ser anterior al año 2025";
                errorMsgEdit.style.display = "block";
                return;
            }

            document.getElementById("modal-overlay").style.display = "none";
            errorMsgEdit.style.display = "none";
        });
    }

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