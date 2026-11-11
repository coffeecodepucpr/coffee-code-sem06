export const API_URL = "http://127.0.0.1:8000";

export class ErroDeRede extends Error {
    constructor() {
        super("Não foi possível falar com a API. Ela está ligada?");
        this.name = "ErroDeRede";
    }
}

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
        throw new ErroDeRede();
    }
    const dados = resposta.status === 204 ? null : await resposta.json().catch(() => null);
    if (!resposta.ok) throw new ErroHttp(resposta.status, dados);
    return { dados, resposta };
}

export async function listarMaterias(){
    const recebido = await pedir('/materias');
    return recebido.dados;
}

export async function listarGrupos({busca='', materiaId='', limite=4, deslocamento=0}={}) {
    const parametros = new URLSearchParams({limit: limite, offset: deslocamento});
    if (busca) parametros.set("q", busca);
    if (materiaId) parametros.set("materia_id", materiaId);

    const {dados, resposta} = await pedir(`/grupos?${parametros}`);
    const total = resposta.headers.get("X-Total-Count");
    if (total === null){
        console.warn("X-Total-Count não está visível. Certifique-se de incluí-lo em expose_headers no CORS da API");
    }
    return {grupos: dados, total: total === null ? dados.length : Number(total)};
}

export async function criarGrupo(corpo) {
    return (await pedir("/grupos", {metodo: "POST", corpo})).dados; 
}

export async function alterarGrupo(id, corpo) {
    return (await pedir(`/grupos/${id}`, {metodo: "PATCH", corpo})).dados; 
}

export async function apagarGrupo(id) {
    await pedir(`/grupos/${id}`, {metodo: "DELETE"}); 
}