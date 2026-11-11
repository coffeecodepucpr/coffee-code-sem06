PS C:\\Users\\pedro> curl.exe -i -X OPTIONS http://127.0.0.1:8000/materias -H "Origin: http://127.0.0.1:5500" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: Content-Type"

HTTP/1.1 200 OK

date: Tue, 27 Oct 2026 22:58:55 GMT

server: uvicorn

vary: Origin, Access-Control-Request-Method, Access-Control-Request-Headers, Access-Control-Request-Private-Network

access-control-allow-methods: GET, POST, PATCH, DELETE

access-control-max-age: 600

access-control-allow-headers: Accept, Accept-Language, Content-Language, Content-Type

access-control-allow-origin: http://127.0.0.1:5500

content-length: 2

content-type: text/plain; charset=utf-8



OK

PS C:\\Users\\pedro> curl.exe -i -X OPTIONS http://127.0.0.1:8000/grupos -H "Origin: http://127.0.0.1:5500" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: Content-Type"

HTTP/1.1 200 OK

date: Tue, 27 Oct 2026 22:59:17 GMT

server: uvicorn

vary: Origin, Access-Control-Request-Method, Access-Control-Request-Headers, Access-Control-Request-Private-Network

access-control-allow-methods: GET, POST, PATCH, DELETE

access-control-max-age: 600

access-control-allow-headers: Accept, Accept-Language, Content-Language, Content-Type

access-control-allow-origin: http://127.0.0.1:5500

content-length: 2

content-type: text/plain; charset=utf-8



OK

