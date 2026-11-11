const formularioLogin = document.querySelector(".login-form");
const campoEmail = document.querySelector("#login-email");
const campoSenha = document.querySelector("#login-password");

const erroEmail = document.querySelector("#email-error");
const erroSenha = document.querySelector("#password-error");

formularioLogin.addEventListener("submit", function (evento) {
    evento.preventDefault();

    // Limpa os erros da tentativa anterior
    erroEmail.textContent = "";
    erroSenha.textContent = "";

    campoEmail.classList.remove("input-error");
    campoSenha.classList.remove("input-error");

    const email = campoEmail.value.trim();
    const senha = campoSenha.value.trim();

    let valido = true;

    // Validação do e-mail
    if (email === "") {
        erroEmail.textContent = "Digite seu e-mail.";
        campoEmail.classList.add("input-error");
        valido = false;
    } else if (!email.includes("@")) {
        erroEmail.textContent = "Digite um e-mail válido.";
        campoEmail.classList.add("input-error");
        valido = false;
    }

    // Validação da senha
    if (senha === "") {
        erroSenha.textContent = "Digite sua senha.";
        campoSenha.classList.add("input-error");
        valido = false;
    } else if (senha.length < 8) {
        erroSenha.textContent = "A senha deve ter pelo menos 8 caracteres.";
        campoSenha.classList.add("input-error");
        valido = false;
    }

    if (valido) {
        console.log("Login válido!");
    }
});