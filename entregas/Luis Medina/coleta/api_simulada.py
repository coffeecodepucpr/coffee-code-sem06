import argparse
import copy
import json
import threading
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PRODUTOS = {
    "MLB001": {"id": "MLB001", "title": "Teclado mecânico", "price": 349.90,
               "currency_id": "BRL", "available_quantity": 5, "status": "active",
               "permalink": "https://produto.mercadolivre.com.br/MLB001",
               "last_updated": "2026-10-01T10:00:00.000-03:00"},
    "MLB002": {"id": "MLB002", "title": "Mouse sem fio", "price": 89.0,
               "currency_id": "BRL", "available_quantity": 0, "status": "active",
               "permalink": "https://produto.mercadolivre.com.br/MLB002",
               "last_updated": "2026-10-01T10:00:00.000-03:00"},
    "MLB003": {"id": "MLB003", "title": "Produto quebrado", "price": 10.0,
               "currency_id": "BRL", "available_quantity": 1, "status": "active",
               "permalink": "https://produto.mercadolivre.com.br/MLB003",
               "last_updated": "2026-10-01T10:00:00.000-03:00"},
    "MLB004": {"id": "MLB004", "title": "Fone bluetooth", "price": 129.90,
               "currency_id": "BRL", "available_quantity": 8, "status": "active",
               "permalink": "https://produto.mercadolivre.com.br/MLB004",
               "last_updated": "2026-10-01T10:00:00.000-03:00"},
}

PRODUTOS_ORIGINAIS = copy.deepcopy(PRODUTOS)

ESTADO = {"tokens_validos": {"tok-1"}, "geracao": 1, "refresh_atual": "ref-1"}
PRODUTOS_REMOVIDOS = set()
CONTADOR_INSTAVEL = defaultdict(int)
TRAVA = threading.Lock()


class Manipulador(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _responder_json(self, codigo, corpo):
        bruto = json.dumps(corpo).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(bruto)))
        self.end_headers()
        self.wfile.write(bruto)

    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)

        if url.path == "/items":
            token = (self.headers.get("Authorization") or "").removeprefix("Bearer ")
            with TRAVA:
                token_ok = token in ESTADO["tokens_validos"]
            if not token_ok:
                return self._responder_json(401, {"message": "invalid_token"})

            if "simular" in q:
                chave = q["simular"][0]
                falhas = int(q.get("falhas", ["1"])[0])
                with TRAVA:
                    CONTADOR_INSTAVEL[chave] += 1
                    vez = CONTADOR_INSTAVEL[chave]
                if vez <= falhas:
                    codigo = int(chave) if chave.isdigit() else 503
                    return self._responder_json(codigo, {"message": "instavel"})

            ids = q.get("ids", [""])[0].split(",")
            resultado = []
            for id_ in ids:
                produto = None if id_ in PRODUTOS_REMOVIDOS else PRODUTOS.get(id_)
                if produto is None:
                    resultado.append({"code": 404, "body": {"error": "not_found"}})
                else:
                    resultado.append({"code": 200, "body": produto})
            return self._responder_json(200, resultado)

        if url.path == "/_dev/reset":
            with TRAVA:
                CONTADOR_INSTAVEL.clear()
                ESTADO["tokens_validos"] = {"tok-1"}
                ESTADO["geracao"] = 1
                ESTADO["refresh_atual"] = "ref-1"
                PRODUTOS_REMOVIDOS.clear()
                PRODUTOS.clear()
                PRODUTOS.update(copy.deepcopy(PRODUTOS_ORIGINAIS))
            return self._responder_json(200, {"ok": True})

        if url.path == "/_dev/remover":
            PRODUTOS_REMOVIDOS.add(q["id"][0])
            return self._responder_json(200, {"ok": True})

        if url.path == "/_dev/preco":
            PRODUTOS[q["id"][0]]["price"] = float(q["valor"][0])
            return self._responder_json(200, {"ok": True})

        return self._responder_json(404, {"message": "not_found"})

    def do_POST(self):
        if self.path != "/oauth/token":
            return self._responder_json(404, {"message": "not_found"})

        tamanho = int(self.headers.get("Content-Length", 0))
        corpo = parse_qs(self.rfile.read(tamanho).decode("utf-8"))
        refresh_recebido = corpo.get("refresh_token", [""])[0]

        with TRAVA:
            if refresh_recebido != ESTADO["refresh_atual"]:
                return self._responder_json(400, {"error": "invalid_grant"})
            ESTADO["geracao"] += 1
            novo_token = f"tok-{ESTADO['geracao']}"
            novo_refresh = f"ref-{ESTADO['geracao']}"
            ESTADO["tokens_validos"].add(novo_token)
            ESTADO["refresh_atual"] = novo_refresh

        return self._responder_json(200, {
            "access_token": novo_token, "token_type": "bearer",
            "expires_in": 21600, "refresh_token": novo_refresh,
        })


def criar_servidor(porta=8199):
    ThreadingHTTPServer.daemon_threads = True
    return ThreadingHTTPServer(("127.0.0.1", porta), Manipulador)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--porta", type=int, default=8188)
    a = ap.parse_args()

    print(f"API simulada do Mercado Livre em http://127.0.0.1:{a.porta}  (produtos: {', '.join(PRODUTOS)})")
    print("Pra demonstrar uma mudança (preço ou produto removido), em outro terminal:")
    print(f"  curl \"http://127.0.0.1:{a.porta}/_dev/preco?id=MLB001&valor=239.90\"")
    print(f"  curl \"http://127.0.0.1:{a.porta}/_dev/remover?id=MLB002\"")
    print("Ctrl+C pra parar.")
    servidor = criar_servidor(porta=a.porta)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor parado.")
