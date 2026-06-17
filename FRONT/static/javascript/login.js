document.addEventListener("DOMContentLoaded", () => {

    /* CARRUSEL DE FONDO */
    const images = document.querySelectorAll("#background-carousel img");
    let currentIndex = 0;

    if (images.length > 0) {
        setInterval(() => {
            images[currentIndex].style.opacity = 0;
            currentIndex = (currentIndex + 1) % images.length;
            images[currentIndex].style.opacity = 1;
        }, 4000);
    }


    /* MOSTRAR / OCULTAR PASSWORD */
    const passwordInput = document.getElementById("password");
    const togglePasswordSvg = document.getElementById("toggle-password");

    if (passwordInput && togglePasswordSvg) {
        togglePasswordSvg.addEventListener("click", () => {
            passwordInput.type =
                passwordInput.type === "password" ? "text" : "password";
        });
    }


    /* ERROR LOGIN */
    const form = document.querySelector("form");
    const usuario = document.getElementById("nombre_profesor");
    const password = document.getElementById("password");
    const error = document.getElementById("error-message");

    function mostrarError(texto) {
        error.innerHTML = `
            <svg viewBox="0 0 24 24">
                <path d="M11.953 2C6.465 2 2 6.486 2 12s4.465 10 9.953 10c5.52 0 10.047-4.5 10.047-10S17.473 2 11.953 2zM13 17h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
            <span>${texto}</span>
        `;

        // Mostrar con transición
        error.style.display = "flex";
        error.style.opacity = "1";
        error.style.transform = "translateY(0)";

        // Animación
        error.animate([
            { transform: "translateX(0)" },
            { transform: "translateX(-5px)" },
            { transform: "translateX(5px)" },
            { transform: "translateX(-3px)" },
            { transform: "translateX(0)" }
        ], { duration: 350, easing: "ease" });

        // Ocultar 
        setTimeout(() => ocultarError(), 3500);
    }

    function ocultarError() {
        error.style.opacity = "0";
        error.style.transform = "translateY(-10px)";
        setTimeout(() => error.style.display = "none", 300);
    }

    form.addEventListener("submit", (e) => {
        ocultarError();

        const email = usuario.value.trim();
        const clave = password.value.trim();

        // if (!email.includes("@")) {
        //     e.preventDefault();
        //     mostrarError("El usuario debe incluir @");
        //     return;
        // }

        // if (!email.endsWith("@fi.uba.ar")) {
        //     e.preventDefault();
        //     mostrarError("Ingresá un correo @fi.uba.ar");
        //     return;
        // }

        if (clave.length < 4) {
            e.preventDefault();
            mostrarError("Usuario o contraseña incorrectos");
            return;
        }
    });

    usuario.addEventListener("input", ocultarError);
    password.addEventListener("input", ocultarError);

});
