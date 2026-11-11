Como rodar a API:



Python 3.10 ou superior instalado;



Selecionar a pasta em que estão mantidos os arquivos (ex: >cd /pasta-de-exemplo);



Criar (py -m venv .venv) e ativar (.venv\\Scripts\\activate) o ambiente virtual;



Verificar se o ambiente virtual está ativo \[(.venv) no começo da linha do CMD];



Instalar o FastAPI (pip install -r requirements.txt);



Ligar a API (executar com cd na pasta /api, >fastapi dev main.py);

&#x09;origem: http://127.0.0.1:8000



Ligar o servidor web embutido em outro terminal (rodar com cd na pasta /frontend, >py -m http.server 5500 --bind 127.0.0.1).

&#x09;origem: http://127.0.0.1:5500



================================================================================



Prpósito de cada arquivo:

* api/main.py - O corpo da API, com rotas, regras e o CORS configurado devidamente
* api/dados.py - Listas com dados usados para testar a API sem banco de dados conectado, um exemplo
* api/schemas.py - Estruturas / modelos que os dados seguem
* frontend/index.html - O esqueleto da página, sem funcionalidade e estilização própria
* frontend/estilos.css - Concede uma aparência mais agradável ao site, organizando de maneira mais visível
* frontend/api.js- Caminho que se comunica diretamente com a API, tendo o endereço e realizando todo o fetch
* frontend/ui.js - Um intermediário entre o JS e a página em si, criando formatações e estruturas para a renderização própria
* frontend/app.js - Um orquestrador, responsável por todo evento, estado e estado de tela, juntando as duas camadas funcionalmente



================================================================================



Regra da Mesma Origem:

* Uma política de segurança básica que impede o JS de uma página de acessar recursos de diferentes origens.



================================================================================



CORS:

* Origens permitidas: http://127.0.0.1:5500 e http://localhost:5500

  * Justificativa: Apesar de apontarem para o mesmo computador, localhost e 127.0.0.1 são origens diferentes, e são elas as origens esperadas para o servidor web que hospedará o frontend.



================================================================================



Estados da tela:

* Carregando: espera do resultado de carregarGrupos(), mostrando "Carregando..." na tela;
* Sucesso: renderizarGrupos() funcionou, mostrando uma lista de cards distribuídos entre páginas;
* Vazio: renderizarGrupos() funcionou, mas a lista estava sem itens, mostrando "Nenhum grupo encontrado...";
* Erro: quando ocorre um erro na execução, mostrando uma descrição concisa do erro ocorrido.



================================================================================



Mensagens de resposta:

* Criar Cálculo II na prática, matéria 1, limite 5: "Grupo criado." aparece no espaço de mensagem, com o grupo aparecendo como um card na lista;



* Enviar o nome ab: "Corrija os campos indicados." no espaço de mensagem, com "String should have at least 3 characters" abaixo do campo nome, a msg que vem junto de detail quando ocorre um erro. 

&#x20;

* Repetir Cálculo II na prática na matéria 1: aparece "Conflito: escolha outro nome." no espaço de mensagem e "Já exite um grupo com esse nome nessa matéria" logo abaixo do campo nome;



* Criar um grupo chamado <img src=x onerror=alert(1)>: um grupo com esse nome é criado sem problemas, visto que não é inserido na página usando innerHTML.



================================================================================



Necessidade do X-Total-Count:

* O X-Total-Count é usado para criar a variável total, importantíssima para a paginação do site, visto que é usada para calcular o número de páginas.

