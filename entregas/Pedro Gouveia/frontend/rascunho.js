const grupos = [
    {'nome':'Desenho Interpretativo', 'vagas':5},
    {'nome':'Escrita Criativa', 'vagas':4},
    {'nome':'OPSEC Básico', 'vagas':8},
    {'nome':'JS Iniciantes', 'vagas':3},
    {'nome':'Leitura Guiada', 'vagas':9}
];

const filtrados = grupos.filter((g) => g.vagas > 4);
const mapeados = grupos.map((g) => g.nome);

console.log(grupos);
console.log(filtrados);
console.log(mapeados);

const devolver = (grupo) => {
    for (let i = 0; i < grupo.length ; i++){
        console.log(`Grupo: ${grupo[i].nome} | Vagas: ${grupo[i].vagas}`)
    }
};

devolver(grupos);

const objTeste = {'nome':'gorfo','uwa':'gwa','numeros':67};
console.log(objTeste);
const objStr = JSON.stringify(objTeste)
console.log(objStr);
console.log(JSON.parse(objStr));

const param = new URLSearchParams({q: "a", limit: 3, offset: 1});
const url = `127.0.0.1:8000/grupos?${param}`;
console.log(url);

const grupos2 =  [
    {nome: "Redes", vagas: 0},
    {nome: "SQL", vagas: 3},
    {nome:"Cálculo", vagas: 5}
];
    
const retorno = grupos2.filter((g) => g.vagas>0).map((g) => g.nome);
console.log(retorno.join(', '));    