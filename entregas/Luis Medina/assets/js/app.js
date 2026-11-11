// app.js — a orquestração: eventos, estado da página e estados da tela.

import * as api from "./api.js";
import * as ui from "./ui.js";

const TAMANHO_DA_PAGINA = 4;

const estado = {
    busca: "",
    categoriaId: "",
    pagina: 1,
    total: 0,
    editandoId: null,              // null = criando; um número = editando esse produto
    nomesDasCategorias: new Map(), // categoriaId -> nome
};

// Numera os pedidos de listagem, para descartar respostas atrasadas
let ultimoPedido = 0;

// ==================== Listagem ====================

async function carregarProdutos() {
    const numero = ++ultimoPedido;
    ui.mostrarMensagem("Carregando...");

    try {
        const { produtos, total } = await api.listarProdutos({
            busca: estado.busca,
            categoriaId: estado.categoriaId,
            limite: TAMANHO_DA_PAGINA,
            deslocamento: (estado.pagina - 1) * TAMANHO_DA_PAGINA,
        });

        // Já existe um pedido mais novo: esta resposta é velha
        if (numero !== ultimoPedido) return;

        const totalDePaginas = Math.max(1, Math.ceil(total / TAMANHO_DA_PAGINA));

        // A página pedida deixou de existir (ex.: apagou o último item da última página)
        if (estado.pagina > totalDePaginas) {
            estado.pagina = totalDePaginas;
            return carregarProdutos();
        }

        // Se a API estava fora do ar no início, as categorias ainda não vieram
        if (estado.nomesDasCategorias.size === 0) await carregarCategorias();

        estado.total = total;
        ui.mostrarEstadoApi("conectada");
        ui.renderizarProdutos(produtos, estado.nomesDasCategorias, {
            aoEditar: iniciarEdicao,
            aoApagar: apagar,
        });
        ui.renderizarPaginacao({ pagina: estado.pagina, totalDePaginas, total });
        ui.mostrarMensagem("");
    } catch (erro) {
        if (numero !== ultimoPedido) return;
        ui.limparLista();
        ui.esconderPaginacao();
        tratarErro(erro);
    }
}

function tratarErro(erro) {
    if (erro instanceof api.ErroDeRede) {
        ui.mostrarEstadoApi("fora");
        ui.mostrarMensagem(erro.message, "erro");
    } else if (erro instanceof api.ErroHttp) {
        ui.mostrarMensagem(`A API respondeu com o código ${erro.status}.`, "erro");
    } else {
        console.error(erro);
        ui.mostrarMensagem("Algo inesperado aconteceu. Veja o console.", "erro");
    }
}

// ==================== Criar e editar ====================

function abrirCriacao() {
    estado.editandoId = null;
    ui.limparFormulario();
    ui.abrirModal();
}

function iniciarEdicao(produto) {
    estado.editandoId = produto.id;
    ui.limparErros();
    ui.preencherFormulario(produto);
    ui.abrirModal();
}

function cancelarEdicao() {
    estado.editandoId = null;
    ui.limparFormulario();
    ui.fecharModal();
}

// Pydantic escreve "Value error, ..." nas regras escritas à mão: tiramos o prefixo
function textoDoProblema(problema) {
    return problema.msg.replace(/^Value error, /, "");
}

function mostrarErrosDeValidacao(detail) {
    let algumSemCampo = false;
    for (const problema of detail) {
        // ["body", "nome"] -> "nome"
        const campo = problema.loc[problema.loc.length - 1];
        if (!ui.mostrarErroDeCampo(campo, textoDoProblema(problema))) algumSemCampo = true;
    }
    ui.mostrarErroDoFormulario(
        algumSemCampo ? "Dados inválidos. Confira o formulário." : "Corrija os campos indicados."
    );
}

async function salvar(evento) {
    evento.preventDefault();
    ui.limparErros();
    ui.travarFormulario(true);

    const corpo = ui.lerFormulario();

    try {
        let aviso;
        if (estado.editandoId === null) {
            await api.criarProduto(corpo);
            aviso = "Produto cadastrado.";
        } else {
            await api.alterarProduto(estado.editandoId, corpo);
            aviso = "Produto atualizado.";
        }

        cancelarEdicao();
        await carregarProdutos();
        // Depois de recarregar, porque carregarProdutos limpa a mensagem
        ui.mostrarMensagem(aviso);
    } catch (erro) {
        if (erro instanceof api.ErroHttp && erro.status === 422) {
            if (Array.isArray(erro.corpo?.detail)) mostrarErrosDeValidacao(erro.corpo.detail);
            else ui.mostrarErroDoFormulario(erro.corpo?.detail ?? "Dados inválidos.");
        } else if (erro instanceof api.ErroHttp && erro.status === 409) {
            ui.mostrarErroDeCampo("url", "Este produto já está cadastrado.");
            ui.mostrarErroDoFormulario("Conflito: esse link já está sendo acompanhado.");
        } else if (erro instanceof api.ErroHttp && erro.status === 404) {
            cancelarEdicao();
            await carregarProdutos();
            ui.mostrarMensagem("Esse produto já não existe. A lista foi atualizada.", "erro");
        } else if (erro instanceof api.ErroDeRede) {
            ui.mostrarEstadoApi("fora");
            ui.mostrarErroDoFormulario(erro.message);
        } else {
            console.error(erro);
            ui.mostrarErroDoFormulario("Algo inesperado aconteceu. Veja o console.");
        }
    } finally {
        // Roda sempre: com sucesso ou com erro, o botão volta ao normal
        ui.travarFormulario(false);
    }
}

// ==================== Apagar ====================

async function apagar(produto) {
    if (!window.confirm(`Excluir o produto "${produto.nome}"?`)) return;

    try {
        await api.apagarProduto(produto.id);
        if (estado.editandoId === produto.id) cancelarEdicao();
        await carregarProdutos();
        ui.mostrarMensagem("Produto excluído.");
    } catch (erro) {
        if (erro instanceof api.ErroHttp && erro.status === 404) {
            await carregarProdutos();
            ui.mostrarMensagem("Esse produto já não existe. A lista foi atualizada.", "erro");
        } else {
            tratarErro(erro);
        }
    }
}

// ==================== Início ====================

// Espera a pessoa parar de digitar, para não fazer um pedido por tecla
function comAtraso(funcao, ms) {
    let temporizador;
    return (...args) => {
        clearTimeout(temporizador);
        temporizador = setTimeout(() => funcao(...args), ms);
    };
}

async function carregarCategorias() {
    try {
        const categorias = await api.listarCategorias();
        estado.nomesDasCategorias = new Map(categorias.map((c) => [c.id, c.nome]));
        ui.preencherCategorias(categorias);
    } catch (erro) {
        // A lista ainda funciona sem os nomes; carregarProdutos mostra o estado da API
        console.warn("Não foi possível carregar as categorias.", erro);
    }
}

async function iniciar() {
    const $ = (id) => document.getElementById(id);

    $("theme-button").addEventListener("click", ui.alternarTema);

    // Modal
    $("open-modal").addEventListener("click", abrirCriacao);
    $("close-modal").addEventListener("click", cancelarEdicao);
    $("cancel-modal").addEventListener("click", cancelarEdicao);
    $("add-product-modal").addEventListener("click", (e) => {
        if (e.target === e.currentTarget) cancelarEdicao();
    });
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            ui.fecharMenus();
            if (ui.modalAberto()) cancelarEdicao();
        }
    });
    $("product-form").addEventListener("submit", salvar);

    // Fecha os menus (⋮) ao clicar fora deles
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".product-actions")) ui.fecharMenus();
    });

    // Busca e filtro voltam à página 1
    $("product-search").addEventListener("input", comAtraso(() => {
        estado.busca = $("product-search").value.trim();
        estado.pagina = 1;
        carregarProdutos();
    }, 300));

    $("filtro-categoria").addEventListener("change", () => {
        estado.categoriaId = $("filtro-categoria").value;
        estado.pagina = 1;
        carregarProdutos();
    });

    // Paginação
    $("anterior").addEventListener("click", () => {
        estado.pagina -= 1;
        carregarProdutos();
    });
    $("proxima").addEventListener("click", () => {
        estado.pagina += 1;
        carregarProdutos();
    });

    ui.mostrarEstadoApi("verificando");
    await carregarCategorias();
    await carregarProdutos();
}

iniciar();
