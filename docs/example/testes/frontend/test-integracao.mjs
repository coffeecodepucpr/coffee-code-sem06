import assert from "node:assert/strict";
import { carregarPagina, esperar, cartoes, nomesNaTela } from "./carregar-pagina.mjs";

let ok = 0;
const passo = async (nome, funcao) => { await funcao(); ok += 1; console.log(`  OK  ${nome}`); };
const mensagem = (d) => d.getElementById("mensagem").textContent;

const doc = await carregarPagina();
const $ = (id) => doc.getElementById(id);
const digitar = (id, valor) => { $(id).value = valor; };
const enviarFormulario = () => $("form-grupo").dispatchEvent(new doc.defaultView.Event("submit", { bubbles: true, cancelable: true }));
const clicar = (el) => el.dispatchEvent(new doc.defaultView.MouseEvent("click", { bubbles: true }));

await passo("a página carrega: estado da API, matérias e a primeira página de grupos", async () => {
  await esperar(() => cartoes(doc).length > 0, "a lista aparecer");
  assert.equal($("estado-api").dataset.estado, "conectada");
  assert.equal($("estado-api").textContent, "API conectada");
  assert.equal($("filtro-materia").options.length, 7);   // "Todas" + 6 matérias
  assert.equal($("materia").options.length, 6);
  assert.equal(cartoes(doc).length, 4);
  assert.deepEqual(nomesNaTela(doc), ["Cálculo passo a passo", "Estruturas na prática", "Modelagem e SQL", "Processos e memória"]);
});

await passo("a paginação mostra o total de grupos informado pela API", async () => {
  assert.equal($("pagina-atual").textContent, "Página 1 de 2 (6 grupos)");
  assert.equal($("anterior").disabled, true);
  assert.equal($("proxima").disabled, false);
});

await passo("o botão Próxima carrega a segunda página", async () => {
  clicar($("proxima"));
  await esperar(() => $("pagina-atual").textContent.startsWith("Página 2"), "a página 2");
  assert.deepEqual(nomesNaTela(doc), ["Redes na unha", "Requisitos e histórias"]);
  assert.equal($("proxima").disabled, true);
  clicar($("anterior"));
  await esperar(() => $("pagina-atual").textContent.startsWith("Página 1"), "voltar à página 1");
});

await passo("a busca por nome filtra a lista (com atraso) e volta à página 1", async () => {
  digitar("busca", "prática");
  $("busca").dispatchEvent(new doc.defaultView.Event("input", { bubbles: true }));
  await esperar(() => cartoes(doc).length === 1, "o filtro");
  assert.deepEqual(nomesNaTela(doc), ["Estruturas na prática"]);
  assert.equal($("pagina-atual").textContent, "Página 1 de 1 (1 grupo)");
  digitar("busca", "zzz");
  $("busca").dispatchEvent(new doc.defaultView.Event("input", { bubbles: true }));
  await esperar(() => doc.querySelector("#lista-grupos .vazio"), "o estado vazio");
  assert.equal(doc.querySelector(".vazio").textContent, "Nenhum grupo encontrado.");
  digitar("busca", "");
  $("busca").dispatchEvent(new doc.defaultView.Event("input", { bubbles: true }));
  await esperar(() => cartoes(doc).length === 4, "a lista completa");
});

await passo("o filtro por matéria devolve só os grupos dela", async () => {
  $("filtro-materia").value = "3";
  $("filtro-materia").dispatchEvent(new doc.defaultView.Event("change", { bubbles: true }));
  await esperar(() => cartoes(doc).length === 1, "o filtro de matéria");
  assert.deepEqual(nomesNaTela(doc), ["Modelagem e SQL"]);
  $("filtro-materia").value = "";
  $("filtro-materia").dispatchEvent(new doc.defaultView.Event("change", { bubbles: true }));
  await esperar(() => cartoes(doc).length === 4, "voltar a todas");
});

await passo("um texto com HTML vindo da API aparece como texto, e não vira elemento", async () => {
  digitar("nome", "<img src=x onerror=alert(1)>");
  digitar("materia", "1");
  enviarFormulario();
  await esperar(() => mensagem(doc) === "Grupo criado.", "criar o grupo de teste");
  // na ordem alfabética, "<" vem antes das letras: o grupo aparece no topo da página 1
  assert.equal(nomesNaTela(doc)[0], "<img src=x onerror=alert(1)>");
  assert.equal(doc.querySelectorAll("#lista-grupos img").length, 0);   // nenhum elemento img foi criado
  // limpeza: apagar o grupo de teste
  clicar([...cartoes(doc)[0].querySelectorAll("button")].find((b) => b.textContent === "Apagar"));
  await esperar(() => mensagem(doc) === "Grupo apagado.", "apagar o grupo de teste");
  assert.equal($("pagina-atual").textContent, "Página 1 de 2 (6 grupos)");
});

await passo("criar um grupo válido: mensagem, formulário limpo e total atualizado", async () => {
  digitar("nome", "Cálculo II na prática");
  digitar("materia", "1");
  digitar("limite", "5");
  digitar("descricao", "Listas às quartas");
  enviarFormulario();
  await esperar(() => mensagem(doc) === "Grupo criado.", "a mensagem de sucesso");
  assert.equal($("nome").value, "");
  assert.equal($("pagina-atual").textContent, "Página 1 de 2 (7 grupos)");
});

await passo("o 422 de validação aparece no campo certo", async () => {
  digitar("nome", "ab");
  enviarFormulario();
  await esperar(() => $("erro-nome").textContent !== "", "o erro do campo");
  assert.equal($("erro-nome").textContent, "String should have at least 3 characters");
  assert.equal(mensagem(doc), "Corrija os campos indicados.");
  assert.equal($("salvar").disabled, false);   // o botão volta a funcionar
});

await passo("o 409 de nome repetido vira mensagem e erro no campo", async () => {
  digitar("nome", "Cálculo II na prática");
  digitar("materia", "1");
  enviarFormulario();
  await esperar(() => mensagem(doc).startsWith("Conflito"), "a mensagem de conflito");
  assert.equal($("erro-nome").textContent, "Já existe um grupo com esse nome nessa matéria.");
});

await passo("editar: o formulário é preenchido, o PATCH atualiza e o card muda", async () => {
  $("nome").value = ""; $("erro-nome").textContent = "";
  const card = cartoes(doc).find((c) => c.querySelector("h3").textContent === "Cálculo II na prática");
  assert.ok(card, "o grupo criado deveria estar na página 1 (ordem alfabética)");
  clicar([...card.querySelectorAll("button")].find((b) => b.textContent === "Editar"));
  assert.equal($("titulo-form").textContent, "Editar grupo");
  assert.equal($("nome").value, "Cálculo II na prática");
  assert.equal($("cancelar").hidden, false);
  digitar("limite", "8");
  enviarFormulario();
  await esperar(() => mensagem(doc) === "Grupo atualizado.", "a mensagem de edição");
  assert.equal($("titulo-form").textContent, "Novo grupo");
  const depois = cartoes(doc).find((c) => c.querySelector("h3").textContent === "Cálculo II na prática");
  assert.match(depois.textContent, /Até 8 participantes/);
});

await passo("apagar pede confirmação: cancelar não apaga, confirmar apaga", async () => {
  const card = () => cartoes(doc).find((c) => c.querySelector("h3").textContent === "Cálculo II na prática");
  window.confirm = () => false;
  clicar([...card().querySelectorAll("button")].find((b) => b.textContent === "Apagar"));
  await new Promise((r) => setTimeout(r, 150));
  assert.ok(card(), "o grupo deveria continuar na tela");
  window.confirm = () => true;
  clicar([...card().querySelectorAll("button")].find((b) => b.textContent === "Apagar"));
  await esperar(() => mensagem(doc) === "Grupo apagado.", "apagar");
  assert.equal($("pagina-atual").textContent, "Página 1 de 2 (6 grupos)");
});

await passo("apagar o último item da última página volta para a última página que existe", async () => {
  const totalNaTela = () => Number($("pagina-atual").textContent.match(/\((\d+) grupos\)/)[1]);
  const criar = async (nome) => {
    const antes = totalNaTela();
    digitar("nome", nome); digitar("materia", "1");
    enviarFormulario();
    await esperar(() => totalNaTela() === antes + 1 && mensagem(doc) === "Grupo criado.", `criar ${nome}`);
  };
  for (const n of ["Zzz 1", "Zzz 2", "Zzz 3"]) await criar(n);       // 9 grupos: páginas de 4, 4 e 1
  assert.equal($("pagina-atual").textContent, "Página 1 de 3 (9 grupos)");
  clicar($("proxima")); await esperar(() => $("pagina-atual").textContent.startsWith("Página 2"), "a página 2");
  clicar($("proxima")); await esperar(() => $("pagina-atual").textContent.startsWith("Página 3"), "a página 3");
  assert.deepEqual(nomesNaTela(doc), ["Zzz 3"]);
  clicar([...cartoes(doc)[0].querySelectorAll("button")].find((b) => b.textContent === "Apagar"));
  await esperar(() => mensagem(doc) === "Grupo apagado.", "apagar o único item da página 3");
  assert.equal($("pagina-atual").textContent, "Página 2 de 2 (8 grupos)");   // e não "Página 3 de 2"
  assert.equal(cartoes(doc).length, 4);
  // limpeza: apagar Zzz 1 e Zzz 2, que estão na página 2
  for (const nome of ["Zzz 2", "Zzz 1"]) {
    const card = cartoes(doc).find((c) => c.querySelector("h3").textContent === nome);
    clicar([...card.querySelectorAll("button")].find((b) => b.textContent === "Apagar"));
    await esperar(() => !nomesNaTela(doc).includes(nome) && mensagem(doc) === "Grupo apagado.", `apagar ${nome}`);
  }
  assert.equal($("pagina-atual").textContent, "Página 2 de 2 (6 grupos)");
  clicar($("anterior")); await esperar(() => $("pagina-atual").textContent.startsWith("Página 1"), "voltar à página 1");
});

console.log(`\n${ok} passos conferidos`);
process.exit(0);
