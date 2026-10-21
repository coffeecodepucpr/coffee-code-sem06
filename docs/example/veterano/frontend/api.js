// Camada de acesso à API padronizada: { dados, meta } nas respostas e { erro, meta } nos erros.

export const API_URL = "http://127.0.0.1:8000";

export class ErroDeRede extends Error {
  constructor() {
    super("Não foi possível falar com a API. Ela está ligada?");
    this.name = "ErroDeRede";
  }
}

/** A API respondeu com um erro. Como o formato é único, dá para ler `codigo`, `detalhes` e `requestId`. */
export class ErroHttp extends Error {
  constructor(status, corpo, requestId) {
    super(corpo?.erro?.mensagem ?? `A API respondeu ${status}`);
    this.name = "ErroHttp";
    this.status = status;
    this.codigo = corpo?.erro?.codigo ?? null;
    this.detalhes = corpo?.erro?.detalhes ?? [];
    this.requestId = requestId ?? corpo?.meta?.requestId ?? null;
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

  const envelope = resposta.status === 204
    ? null
    : await resposta.json().catch(() => null);
  if (!resposta.ok) {
    const idDoPedido = resposta.headers.get("X-Request-ID");
    throw new ErroHttp(resposta.status, envelope, idDoPedido);
  }
  return { dados: envelope?.dados ?? null, meta: envelope?.meta ?? null };
}

export async function listarMaterias() {
  return (await pedir("/materias")).dados;
}

export async function listarGrupos({ busca = "", materiaId = "", limite = 4, deslocamento = 0 } = {}) {
  const parametros = new URLSearchParams({ limit: limite, offset: deslocamento });
  if (busca) parametros.set("q", busca);
  if (materiaId) parametros.set("materiaId", materiaId);
  const { dados, meta } = await pedir(`/grupos?${parametros}`);
  // o total agora vem no corpo, não em um cabeçalho
  return { grupos: dados, total: meta.total };
}

export async function criarGrupo(corpo) {
  return (await pedir("/grupos", { metodo: "POST", corpo })).dados;
}

export async function alterarGrupo(id, corpo) {
  return (await pedir(`/grupos/${id}`, { metodo: "PATCH", corpo })).dados;
}

export async function apagarGrupo(id) {
  await pedir(`/grupos/${id}`, { metodo: "DELETE" });
}
