function marcarColorNota(input) {
  const valor = parseFloat(input.value);

  input.removeAttribute('data-color');

  if (isNaN(valor)) {
    return;
  }

  // Color (>= 6)
  if (valor >= 6) {
    input.setAttribute('data-color', 'alta');
  } else if (valor >= 0) {
    input.setAttribute('data-color', 'baja');
  }
}


document.addEventListener('DOMContentLoaded', () => {
  const inputs = document.querySelectorAll('#tabla-body input[type="number"]');
  inputs.forEach(marcarColorNota);
});
