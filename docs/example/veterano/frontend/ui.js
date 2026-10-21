// Camada de interface: lê e escreve na página. Nenhum fetch aqui.

const $ = (id) => document.getElementById(id);

// Cada campo da API aponta para o elemento que mostra o erro dele.
const CAMPO_DO_ERRO = {
  nomeGrupo: "erro-nome",
  materiaId: "erro-materia",
  maxParticipantes: "erro-limite",
  descricao: "erro-descricao",
};

export function mostrarEstadoApi(estado) {
  const el = $("estado-api");
  el.dataset.estado = estado;
  el.textContent = estado === "conectada" ? "API conectada" : "API fora do ar";
}

export function mostrarMensagem(texto, tipo = "info") {
  const el = $("mensagem");
  el.textContent = texto;
  el.dataset.tipo = tipo;
}

export function preencherMaterias(materias) {
  for (const id of ["filtro-materia", "materia"]) {
    const select = $(id);
    const primeira = id === "filtro-materia" ? [select.options[0]] : [];
    select.replaceChildren(...primeira);
    for (const m of materias) {
      const opcao = document.createElement("option");
      opcao.value = m.materiaId;
      opcao.textContent = m.nome;
      select.append(opcao);
    }
  }
}

export function renderizarGrupos(grupos, nomesDeMaterias, { aoEditar, aoApagar }) {
  const lista = $("lista-grupos");
  lista.replaceChildren();

  if (grupos.length === 0) {
    const vazio = document.createElement("li");
    vazio.className = "vazio";
    vazio.textContent = "Nenhum grupo encontrado.";
    lista.append(vazio);
    return;
  }

  for (const g of grupos) {
    const item = document.createElement("li");
    item.className = "cartao";

    const titulo = document.createElement("h3");
    titulo.textContent = g.nomeGrupo; // textContent: o texto da API nunca vira HTML

    const materia = document.createElement("p");
    materia.className = "materia";
    materia.textContent = nomesDeMaterias.get(g.materiaId) ?? `Matéria ${g.materiaId}`;

    const limite = document.createElement("p");
    limite.textContent = `Até ${g.maxParticipantes} participantes`;

    item.append(titulo, materia, limite);

    if (g.descricao) {
      const descricao = document.createElement("p");
      descricao.textContent = g.descricao;
      item.append(descricao);
    }

    const acoes = document.createElement("div");
    acoes.className = "acoes";
    const editar = document.createElement("button");
    editar.type = "button";
    editar.className = "secundario";
    editar.textContent = "Editar";
    editar.addEventListener("click", () => aoEditar(g));
    const apagar = document.createElement("button");
    apagar.type = "button";
    apagar.className = "secundario";
    apagar.textContent = "Apagar";
    apagar.addEventListener("click", () => aoApagar(g));
    acoes.append(editar, apagar);

    item.append(acoes);
    lista.append(item);
  }
}

export function renderizarPaginacao({ pagina, totalDePaginas, total }) {
  const grupos = total === 1 ? "grupo" : "grupos";
  $("pagina-atual").textContent =
    `Página ${pagina} de ${totalDePaginas} (${total} ${grupos})`;
  $("anterior").disabled = pagina <= 1;
  $("proxima").disabled = pagina >= totalDePaginas;
}

export function lerFormulario() {
  const descricao = $("descricao").value.trim();
  return {
    nomeGrupo: $("nome").value.trim(),
    materiaId: Number($("materia").value),
    maxParticipantes: Number($("limite").value),
    descricao: descricao === "" ? null : descricao,
  };
}

export function preencherFormulario(g) {
  $("nome").value = g.nomeGrupo;
  $("materia").value = g.materiaId;
  $("limite").value = g.maxParticipantes;
  $("descricao").value = g.descricao ?? "";
  $("titulo-form").textContent = "Editar grupo";
  $("cancelar").hidden = false;
}

export function limparFormulario() {
  $("form-grupo").reset();
  $("limite").value = 10;
  $("titulo-form").textContent = "Novo grupo";
  $("cancelar").hidden = true;
  limparErros();
}

export function limparErros() {
  for (const id of Object.values(CAMPO_DO_ERRO)) $(id).textContent = "";
}

export function mostrarErroDeCampo(campo, texto) {
  const id = CAMPO_DO_ERRO[campo];
  if (id) $(id).textContent = texto;
}

export function travarFormulario(travado) {
  $("salvar").disabled = travado;
}

export function elementos() {
  return {
    busca: $("busca"), filtroMateria: $("filtro-materia"), formulario: $("form-grupo"),
    anterior: $("anterior"), proxima: $("proxima"), cancelar: $("cancelar"),
  };
}
