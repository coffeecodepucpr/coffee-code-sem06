const usuarioMock = {
    id: 1,
    nome: "Luís Medina",
    email: "medina@email.com"
};

const nomePerfil = document.querySelector("#profile-name");
const emailPerfil = document.querySelector("#profile-email");
const botaoEditarNome = document.querySelector("#edit-name-button");

function renderizarPerfil() {
    nomePerfil.textContent = usuarioMock.nome;
    emailPerfil.textContent = usuarioMock.email;
}

renderizarPerfil();

botaoEditarNome.addEventListener("click", function () {
    const novoNome = prompt("Digite seu novo nome:");

    if (novoNome === null) {
        return;
    }

    const nomeLimpo = novoNome.trim();

    if (nomeLimpo === "") {
        return;
    }

    usuarioMock.nome = nomeLimpo;

    renderizarPerfil();
});