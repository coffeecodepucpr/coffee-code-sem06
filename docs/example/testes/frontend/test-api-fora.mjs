// Rode com a API DESLIGADA: a página deve avisar, sem quebrar.
import assert from "node:assert/strict";
import { carregarPagina, esperar } from "./carregar-pagina.mjs";

const doc = await carregarPagina();
await esperar(() => doc.getElementById("estado-api").dataset.estado === "fora", "o aviso de API fora do ar");
assert.equal(doc.getElementById("estado-api").textContent, "API fora do ar");
assert.equal(doc.getElementById("mensagem").textContent, "Não foi possível falar com a API. Ela está ligada?");
assert.equal(doc.getElementById("mensagem").dataset.tipo, "erro");
console.log("  OK  com a API desligada, a página avisa em vez de quebrar");
process.exit(0);
