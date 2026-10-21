// Uma resposta lenta e velha não pode sobrescrever uma resposta rápida e nova.
import assert from "node:assert/strict";
import { carregarPagina, esperar, cartoes, nomesNaTela } from "./carregar-pagina.mjs";

const fetchOriginal = globalThis.fetch;
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
// A segunda página SEM filtro de matéria demora 500 ms:
// ela será a resposta velha.
globalThis.fetch = async (url, opcoes) => {
  const endereco = String(url);
  if (endereco.includes("offset=4") && !/materia_?[iI]d=/.test(endereco)) {
    await dormir(500);
  }
  return fetchOriginal(url, opcoes);
};

const doc = await carregarPagina();
const $ = (id) => doc.getElementById(id);
await esperar(() => cartoes(doc).length === 4, "a primeira página");

$("proxima").dispatchEvent(new doc.defaultView.MouseEvent("click", { bubbles: true }));     // pedido A: lento
$("filtro-materia").value = "3";
$("filtro-materia").dispatchEvent(new doc.defaultView.Event("change", { bubbles: true }));  // pedido B: rápido e mais novo
await esperar(() => cartoes(doc).length === 1, "o pedido novo (filtro por matéria)");
assert.deepEqual(nomesNaTela(doc), ["Modelagem e SQL"]);

await dormir(800);   // a resposta velha (A) chega agora
assert.deepEqual(nomesNaTela(doc), ["Modelagem e SQL"], "a resposta velha NÃO pode sobrescrever a nova");
assert.equal($("pagina-atual").textContent, "Página 1 de 1 (1 grupo)");
console.log("  OK  a resposta velha (lenta) foi descartada, e a tela mostra a mais nova");
process.exit(0);
