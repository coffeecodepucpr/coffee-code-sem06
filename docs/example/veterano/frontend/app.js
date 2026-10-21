// Orquestra a página: junta a camada de API com a camada de interface.
import * as api from "./api.js";
import * as ui from "./ui.js";

const TAMANHO_DA_PAGINA = 4;

const estado = {
  busca: "",
  materiaId: "",
  pagina: 1,
  total: 0,
  nomesDeMaterias: new Map(),
  editandoId: null,
};

function tratarErro(erro) {
  if (erro instanceof api.ErroDeRede) {
    ui.mostrarEstadoApi("fora");
    ui.mostrarMensagem(erro.message, "erro");
  } else if (erro instanceof api.ErroHttp) {
    // O requestId liga a tela ao log do servidor: quem der suporte procura por ele.
    ui.mostrarMensagem(`${erro.message} (pedido ${erro.requestId})`, "erro");
  } else {
    console.error(erro);
    ui.mostrarMensagem("Algo inesperado aconteceu. Veja o console.", "erro");
  }
}

let ultimoPedido = 0; // numera os pedidos de listagem, para descartar respostas atrasadas

async function carregarGrupos() {
  const numero = ++ultimoPedido;
  ui.mostrarMensagem("Carregando...");
  try {
    const { grupos, total } = await api.listarGrupos({
      busca: estado.busca,
      materiaId: estado.materiaId,
      limite: TAMANHO_DA_PAGINA,
      deslocamento: (estado.pagina - 1) * TAMANHO_DA_PAGINA,
    });
    if (numero !== ultimoPedido) return; // já existe um pedido mais novo: esta resposta é velha

    const totalDePaginas = Math.max(1, Math.ceil(total / TAMANHO_DA_PAGINA));
    if (estado.pagina > totalDePaginas) {
      // a página pedida deixou de existir (por exemplo, o último item dela foi apagado)
      estado.pagina = totalDePaginas;
      return carregarGrupos();
    }

    estado.total = total;
    ui.mostrarEstadoApi("conectada");
    ui.renderizarGrupos(grupos, estado.nomesDeMaterias, { aoEditar: iniciarEdicao, aoApagar: apagar });
    ui.renderizarPaginacao({ pagina: estado.pagina, totalDePaginas, total });
    ui.mostrarMensagem("");
  } catch (erro) {
    if (numero !== ultimoPedido) return;
    tratarErro(erro);
  }
}

function iniciarEdicao(grupo) {
  estado.editandoId = grupo.grupoId;
  ui.limparErros();
  ui.preencherFormulario(grupo);
}

function cancelarEdicao() {
  estado.editandoId = null;
  ui.limparFormulario();
}

async function apagar(grupo) {
  if (!window.confirm(`Apagar o grupo "${grupo.nomeGrupo}"?`)) return;
  try {
    await api.apagarGrupo(grupo.grupoId);
    if (estado.editandoId === grupo.grupoId) cancelarEdicao();
    await carregarGrupos();
    ui.mostrarMensagem("Grupo apagado.");
  } catch (erro) {
    if (erro instanceof api.ErroHttp && erro.codigo === "nao_encontrado") {
      ui.mostrarMensagem("Esse grupo já não existe. A lista foi atualizada.", "erro");
      await carregarGrupos();
    } else {
      tratarErro(erro);
    }
  }
}

function mostrarErrosDeValidacao(detalhes) {
  for (const problema of detalhes) {
    const campo = problema.campo.split(".").pop(); // "body.nomeGrupo" -> "nomeGrupo"
    ui.mostrarErroDeCampo(campo, problema.mensagem);
  }
  ui.mostrarMensagem("Corrija os campos indicados.", "erro");
}

async function salvar(evento) {
  evento.preventDefault();
  ui.limparErros();
  ui.travarFormulario(true);
  const corpo = ui.lerFormulario();
  try {
    let aviso;
    if (estado.editandoId === null) {
      await api.criarGrupo(corpo);
      aviso = "Grupo criado.";
    } else {
      await api.alterarGrupo(estado.editandoId, corpo);
      aviso = "Grupo atualizado.";
    }
    cancelarEdicao();
    await carregarGrupos();
    ui.mostrarMensagem(aviso); // depois de recarregar, porque carregarGrupos limpa a mensagem
  } catch (erro) {
    if (erro instanceof api.ErroHttp && erro.codigo === "validacao") {
      mostrarErrosDeValidacao(erro.detalhes);
    } else if (erro instanceof api.ErroHttp && erro.codigo === "regra_de_negocio") {
      ui.mostrarMensagem(erro.message, "erro");
    } else if (erro instanceof api.ErroHttp && erro.codigo === "conflito") {
      ui.mostrarErroDeCampo("nomeGrupo", "Já existe um grupo com esse nome nessa matéria.");
      ui.mostrarMensagem("Conflito: escolha outro nome.", "erro");
    } else if (erro instanceof api.ErroHttp && erro.codigo === "nao_encontrado") {
      ui.mostrarMensagem("Esse grupo já não existe.", "erro");
      cancelarEdicao();
      await carregarGrupos();
    } else {
      tratarErro(erro);
    }
  } finally {
    ui.travarFormulario(false);
  }
}

function comAtraso(funcao, milissegundos) {
  let temporizador;
  return (...argumentos) => {
    clearTimeout(temporizador);
    temporizador = setTimeout(() => funcao(...argumentos), milissegundos);
  };
}

export async function iniciar() {
  const el = ui.elementos();
  el.formulario.addEventListener("submit", salvar);
  el.cancelar.addEventListener("click", cancelarEdicao);
  el.anterior.addEventListener("click", () => {
    estado.pagina -= 1;
    carregarGrupos();
  });
  el.proxima.addEventListener("click", () => {
    estado.pagina += 1;
    carregarGrupos();
  });
  el.busca.addEventListener("input", comAtraso(() => {
    estado.busca = el.busca.value.trim();
    estado.pagina = 1;
    carregarGrupos();
  }, 300));
  el.filtroMateria.addEventListener("change", () => {
    estado.materiaId = el.filtroMateria.value;
    estado.pagina = 1;
    carregarGrupos();
  });

  try {
    const materias = await api.listarMaterias();
    estado.nomesDeMaterias = new Map(materias.map((m) => [m.materiaId, m.nome]));
    ui.preencherMaterias(materias);
  } catch (erro) {
    tratarErro(erro);
    return;
  }
  await carregarGrupos();
}

iniciar();
