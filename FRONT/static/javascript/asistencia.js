// ABRIR MODAL EDITAR
function openEditClase(id, fecha, tema, horario, d1, d2, d3){
    document.getElementById("edit-id").value = id;
    document.getElementById("edit-fecha").value = fecha;
    document.getElementById("edit-tema").value = tema;
    document.getElementById("edit-horario").value = horario;
    document.getElementById("edit-doc1").value = d1;
    document.getElementById("edit-doc2").value = d2;
    document.getElementById("edit-doc3").value = d3;

    document.getElementById("form-editar").action = "/editar_clase/" + id;

    document.getElementById("modal-overlay").style.display = "flex";
}

function closeModal(){
    document.getElementById("modal-overlay").style.display = "none";
}

function closeModalOutside(e){
    if(e.target.id === "modal-overlay") closeModal();
}


// ELIMINAR
let deleteId = null;

function openDelete(id){
    deleteId = id;
    document.getElementById("form-delete").action = "/eliminar_clase/" + id;
    document.getElementById("delete-overlay").style.display = "flex";
}

function closeDelete(){
    document.getElementById("delete-overlay").style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {

    const data = document.getElementById("asistencia-data");

    if (!data) return;

    const editErrorId = data.dataset.editErrorId;
    const editErrorFecha = data.dataset.editErrorFecha;
    const editErrorHorario = data.dataset.editErrorHorario;

    if (editErrorId && editErrorId !== "None" && editErrorId !== "") {

        const modal = document.getElementById("modal-overlay");

        if (modal) {
            modal.style.display = "flex";

            const inputId = document.getElementById("edit-id");
            if (inputId) inputId.value = editErrorId;
        }
    }

});