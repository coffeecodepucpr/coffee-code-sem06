// ui.js — o ÚNICO arquivo que lê e escreve a página. Não sabe nada da API.
// Dados vindos de fora entram SEMPRE com textContent (nunca innerHTML).

const $ = (id) => document.getElementById(id);

// ==================== Regras de exibição do preço ====================

export function formatarPreco(valor) {
    return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function calcularStatus(produto) {
    if (produto.precoAtual === null) return "aguardando";
    if (produto.precoMaximo === null) return "nao-definido";
    if (produto.precoAtual < produto.precoMaximo) return "abaixo";
    if (produto.precoAtual > produto.precoMaximo) return "acima";
    return "na-meta";
}

function calcularDiferenca(produto) {
    return Math.abs(produto.precoAtual - produto.precoMaximo);
}

function obterClasseStatus(produto) {
    const status = calcularStatus(produto);
    if (status === "abaixo" || status === "na-meta") return "status-success";
    if (status === "acima") {
        return calcularDiferenca(produto) > 100 ? "status-error" : "status-warning";
    }
    return "status-neutral";
}

function exibirStatus(produto) {
    const status = calcularStatus(produto);
    if (status === "nao-definido") return "— Sem meta definida";
    if (status === "na-meta") return "= Na meta";
    if (status === "aguardando") return "— Aguardando atualização";

    const seta = status === "acima" ? "↑" : "↓";
    return `${seta} ${formatarPreco(calcularDiferenca(produto))} ${status} da meta`;
}

function exibirVerificacao(produto) {
    if (!produto.ultimaVerificacao) return "Ainda não verificado";
    const data = new Date(produto.ultimaVerificacao);
    const dia = data.toLocaleDateString("pt-BR");
    const hora = data.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    return `${dia} às ${hora}`;
}

// Só aceita links http(s): evita que um "javascript:..." vire um link clicável
function linkSeguro(url) {
    return /^https?:\/\//i.test(url) ? url : null;
}

// ==================== Mensagens e estado da API ====================

export function mostrarMensagem(texto, tipo = "info") {
    const el = $("mensagem");
    el.textContent = texto;
    el.className = `page-message ${tipo === "erro" ? "page-message-erro" : ""}`;
    el.hidden = texto === "";
}

export function mostrarEstadoApi(estado) {
    const el = $("estado-api");
    const textos = {
        verificando: "Verificando API...",
        conectada: "API conectada",
        fora: "API fora do ar",
    };
    el.textContent = textos[estado];
    el.className = `api-status api-status-${estado}`;
}

// ==================== Categorias ====================

export function preencherCategorias(categorias) {
    const filtro = $("filtro-categoria");
    const campo = $("product-category");

    for (const c of categorias) {
        const opcaoFiltro = document.createElement("option");
        opcaoFiltro.value = c.id;
        opcaoFiltro.textContent = c.nome;
        filtro.append(opcaoFiltro);

        const opcaoCampo = document.createElement("option");
        opcaoCampo.value = c.id;
        opcaoCampo.textContent = c.nome;
        campo.append(opcaoCampo);
    }
}

// ==================== Lista de produtos ====================

function criarCartao(produto, nomesDasCategorias, { aoEditar, aoApagar }) {
    const item = document.createElement("li");
    item.className = "product-card";

    // Imagem
    const caixaImagem = document.createElement("div");
    caixaImagem.className = "product-image";
    const img = document.createElement("img");
    img.src = produto.imagem || "assets/images/imagem-vazia.png";
    img.alt = produto.nome;
    caixaImagem.append(img);

    // Informações
    const info = document.createElement("div");
    info.className = "product-info";

    const topo = document.createElement("div");
    topo.className = "product-top";

    const titulo = document.createElement("h2");
    titulo.textContent = produto.nome;

    // Menu de ações (⋮)
    const acoes = document.createElement("div");
    acoes.className = "product-actions";

    const botaoMenu = document.createElement("button");
    botaoMenu.type = "button";
    botaoMenu.className = "menu-button";
    botaoMenu.textContent = "⋮";
    botaoMenu.setAttribute("aria-label", `Opções do ${produto.nome}`);
    botaoMenu.setAttribute("aria-expanded", "false");

    const menu = document.createElement("div");
    menu.className = "product-menu";

    const botaoEditar = document.createElement("button");
    botaoEditar.type = "button";
    botaoEditar.className = "menu-item";
    botaoEditar.textContent = "Editar";
    botaoEditar.addEventListener("click", () => {
        fecharMenus();
        aoEditar(produto);
    });

    const botaoExcluir = document.createElement("button");
    botaoExcluir.type = "button";
    botaoExcluir.className = "delete-product";
    botaoExcluir.textContent = "Excluir";
    botaoExcluir.addEventListener("click", () => {
        fecharMenus();
        aoApagar(produto);
    });

    botaoMenu.addEventListener("click", () => {
        const abrir = !menu.classList.contains("active");
        fecharMenus();
        menu.classList.toggle("active", abrir);
        botaoMenu.setAttribute("aria-expanded", String(abrir));
    });

    menu.append(botaoEditar, botaoExcluir);
    acoes.append(botaoMenu, menu);
    topo.append(titulo, acoes);

    // Loja e categoria (o link leva à página original do produto)
    const nomeCategoria = nomesDasCategorias.get(produto.categoriaId) ?? "Sem categoria";
    const loja = document.createElement(linkSeguro(produto.url) ? "a" : "p");
    loja.className = "product-store";
    loja.textContent = `${produto.loja} · ${nomeCategoria}`;
    if (linkSeguro(produto.url)) {
        loja.href = linkSeguro(produto.url);
        loja.target = "_blank";
        loja.rel = "noopener noreferrer";
    }

    const preco = document.createElement("p");
    preco.className = "product-price";
    preco.textContent = produto.precoAtual === null
        ? "Aguardando atualização"
        : formatarPreco(produto.precoAtual);

    const detalhes = document.createElement("div");
    detalhes.className = "product-details";
    const meta = document.createElement("span");
    meta.textContent = `Meta: ${produto.precoMaximo === null ? "Não definida" : formatarPreco(produto.precoMaximo)}`;
    const status = document.createElement("span");
    status.className = `status ${obterClasseStatus(produto)}`;
    status.textContent = exibirStatus(produto);
    detalhes.append(meta, status);

    const verificacao = document.createElement("p");
    verificacao.className = "last-update";
    const rotulo = document.createElement("span");
    rotulo.textContent = "Última verificação";
    const valor = document.createElement("span");
    valor.textContent = exibirVerificacao(produto);
    verificacao.append(rotulo, document.createElement("br"), valor);

    info.append(topo, loja, preco, detalhes, verificacao);
    item.append(caixaImagem, info);
    return item;
}

export function renderizarProdutos(produtos, nomesDasCategorias, acoes) {
    const lista = $("lista-produtos");
    lista.replaceChildren(); // esvazia antes de desenhar, para não acumular cartões

    if (produtos.length === 0) {
        const vazio = document.createElement("li");
        vazio.className = "empty-state";
        vazio.textContent = "Nenhum produto encontrado.";
        lista.append(vazio);
        return;
    }

    for (const produto of produtos) {
        lista.append(criarCartao(produto, nomesDasCategorias, acoes));
    }
}

export function limparLista() {
    $("lista-produtos").replaceChildren();
}

export function fecharMenus() {
    document.querySelectorAll(".product-menu.active").forEach((menu) => {
        menu.classList.remove("active");
        menu.previousElementSibling?.setAttribute("aria-expanded", "false");
    });
}

// ==================== Paginação ====================

export function renderizarPaginacao({ pagina, totalDePaginas, total }) {
    const palavra = total === 1 ? "produto" : "produtos";
    $("pagina-atual").textContent =
        `Página ${pagina} de ${totalDePaginas} (${total} ${palavra})`;
    $("anterior").disabled = pagina <= 1;
    $("proxima").disabled = pagina >= totalDePaginas;
    $("paginacao").hidden = false;
}

export function esconderPaginacao() {
    $("paginacao").hidden = true;
}

// ==================== Formulário (criar e editar) ====================

const CAMPO_DO_ERRO = {
    nome: { erro: "erro-nome", campo: "product-name" },
    url: { erro: "erro-url", campo: "product-url" },
    categoriaId: { erro: "erro-categoria", campo: "product-category" },
    precoMaximo: { erro: "erro-preco", campo: "target-price" },
};

export function lerFormulario() {
    const precoTexto = $("target-price").value;
    return {
        nome: $("product-name").value.trim(),
        url: $("product-url").value.trim(),
        categoriaId: Number($("product-category").value),
        // campo vazio = sem meta (null); a API decide se o número é válido
        precoMaximo: precoTexto === "" ? null : Number(precoTexto),
    };
}

export function preencherFormulario(produto) {
    $("product-name").value = produto.nome;
    $("product-url").value = produto.url;
    $("product-category").value = produto.categoriaId;
    $("target-price").value = produto.precoMaximo ?? "";
    $("modal-title").textContent = "Editar produto";
    $("modal-subtitle").textContent = "Altere os dados de acompanhamento do produto.";
    $("submit-button").textContent = "Salvar alterações";
}

export function limparFormulario() {
    $("product-form").reset();
    $("modal-title").textContent = "Adicionar produto";
    $("modal-subtitle").textContent = "Cadastre um produto para acompanhar seu preço.";
    $("submit-button").textContent = "+ Adicionar produto";
    limparErros();
}

export function mostrarErroDeCampo(campo, texto) {
    const alvo = CAMPO_DO_ERRO[campo];
    if (!alvo) return false;
    $(alvo.erro).textContent = texto;
    $(alvo.campo).classList.add("input-error");
    $(alvo.campo).setAttribute("aria-invalid", "true");
    return true;
}

export function mostrarErroDoFormulario(texto) {
    $("form-error").textContent = texto;
}

export function limparErros() {
    for (const { erro, campo } of Object.values(CAMPO_DO_ERRO)) {
        $(erro).textContent = "";
        $(campo).classList.remove("input-error");
        $(campo).removeAttribute("aria-invalid");
    }
    $("form-error").textContent = "";
}

// Desabilita o botão durante o envio, para evitar o clique duplo
export function travarFormulario(travado) {
    $("submit-button").disabled = travado;
    $("submit-button").setAttribute("aria-busy", String(travado));
}

// ==================== Modal ====================

let focoAntesDoModal = null;

export function abrirModal() {
    focoAntesDoModal = document.activeElement;
    $("add-product-modal").classList.add("active");
    $("product-name").focus();
}

export function fecharModal() {
    $("add-product-modal").classList.remove("active");
    focoAntesDoModal?.focus?.();
}

export function modalAberto() {
    return $("add-product-modal").classList.contains("active");
}

// ==================== Tema ====================

export function alternarTema() {
    const html = document.documentElement;
    const botao = $("theme-button");

    if (html.getAttribute("data-theme") === "dark") {
        html.setAttribute("data-theme", "light");
        botao.textContent = "☾";
        botao.setAttribute("aria-label", "Ativar tema escuro");
    } else {
        html.setAttribute("data-theme", "dark");
        botao.textContent = "☀";
        botao.setAttribute("aria-label", "Ativar tema claro");
    }
}
