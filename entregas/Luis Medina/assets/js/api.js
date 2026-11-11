// api.js — o ÚNICO arquivo que conhece o endereço da API e chama o fetch.

export const API_URL = "http://127.0.0.1:8000";

// A API não respondeu (desligada, endereço errado ou bloqueio de CORS)
export class ErroDeRede extends Error {
    constructor() {
        super("Não foi possível falar com a API. Ela está ligada?");
        this.name = "ErroDeRede";
    }
}

// A API respondeu, mas com um código de erro (404, 409, 422, 500...)
export class ErroHttp extends Error {
    constructor(status, corpo) {
        super(`A API respondeu ${status}`);
        this.name = "ErroHttp";
        this.status = status;
        this.corpo = corpo;
    }
}

async function pedir(caminho, { metodo = "GET", corpo } = {}) {
    const opcoes = { method: metodo, headers: {} };

    if (corpo !== undefined) {
        opcoes.headers["Content-Type"] = "application/json";
        opcoes.body = JSON.stringify(corpo);
    }

    let resposta;
    try {
        resposta = await fetch(`${API_URL}${caminho}`, opcoes);
    } catch {
        // O fetch só rejeita quando não há resposta nenhuma
        throw new ErroDeRede();
    }

    // 204 não tem corpo: chamar .json() daria erro
    const dados = resposta.status === 204
        ? null
        : await resposta.json().catch(() => null);

    // O fetch NÃO rejeita em 404/422/500: quem confere é o resposta.ok
    if (!resposta.ok) throw new ErroHttp(resposta.status, dados);

    return { dados, resposta };
}

export async function listarCategorias() {
    return (await pedir("/categorias")).dados;
}

export async function listarProdutos(
    { busca = "", categoriaId = "", limite = 4, deslocamento = 0 } = {}
) {
    const parametros = new URLSearchParams({ limit: limite, offset: deslocamento });
    if (busca) parametros.set("q", busca);
    if (categoriaId) parametros.set("categoriaId", categoriaId);

    const { dados, resposta } = await pedir(`/produtos?${parametros}`);

    // Só é visível para o JS se a API listar o cabeçalho em expose_headers
    const total = resposta.headers.get("X-Total-Count");
    if (total === null) {
        console.warn(
            "X-Total-Count não está visível. Confira o expose_headers do CORS na API."
        );
    }

    return { produtos: dados, total: total === null ? dados.length : Number(total) };
}

export async function criarProduto(corpo) {
    return (await pedir("/produtos", { metodo: "POST", corpo })).dados;
}

export async function alterarProduto(id, corpo) {
    return (await pedir(`/produtos/${id}`, { metodo: "PATCH", corpo })).dados;
}

export async function apagarProduto(id) {
    await pedir(`/produtos/${id}`, { metodo: "DELETE" });
}
