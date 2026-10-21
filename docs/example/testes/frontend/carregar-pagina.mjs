// Carrega o index.html no jsdom e deixa o app.js rodar de verdade, com o fetch do Node.
import { JSDOM } from "jsdom";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
export const PASTA_DO_FRONTEND = path.resolve(AQUI, process.env.FRONTEND ?? "../../frontend");

export async function carregarPagina({ confirmar = () => true } = {}) {
  const html = fs.readFileSync(path.join(PASTA_DO_FRONTEND, "index.html"), "utf8");
  const dom = new JSDOM(html, { url: "http://127.0.0.1:5500/" });
  globalThis.window = dom.window;
  globalThis.document = dom.window.document;
  window.confirm = confirmar;
  await import(pathToFileURL(path.join(PASTA_DO_FRONTEND, "app.js")).href + `?v=${Math.random()}`);
  return dom.window.document;
}

export async function esperar(condicao, descricao, limiteMs = 4000) {
  const inicio = Date.now();
  while (Date.now() - inicio < limiteMs) {
    if (await condicao()) return;
    await new Promise((r) => setTimeout(r, 25));
  }
  throw new Error(`Tempo esgotado esperando: ${descricao}`);
}

export const cartoes = (doc) => [...doc.querySelectorAll("#lista-grupos .cartao")];
export const nomesNaTela = (doc) => cartoes(doc).map((c) => c.querySelector("h3").textContent);
