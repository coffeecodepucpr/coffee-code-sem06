
-- ==================================================
-- ESTOM - SEMANA 04
-- Consultas SQL
-- ==================================================

-- 1. JOIN: historico com nome do produto
SELECT
    p.nome AS produto,
    h.preco,
    h.data_consulta
FROM public.historico_precos h
JOIN public.produtos p
    ON h.produto_id = p.id
ORDER BY p.nome, h.data_consulta;

-- 2. GROUP BY: quantidade e media de precos
SELECT
    p.nome AS produto,
    COUNT(h.id) AS total_consultas,
    ROUND(AVG(h.preco), 2) AS preco_medio
FROM public.produtos p
JOIN public.historico_precos h
    ON h.produto_id = p.id
GROUP BY p.id, p.nome
ORDER BY p.nome;

-- 3. LEFT JOIN: produtos com ou sem notificacoes
SELECT
    p.nome AS produto,
    p.preco_atual,
    n.status AS status_notificacao
FROM public.produtos p
LEFT JOIN public.notificacoes n
    ON n.produto_id = p.id
ORDER BY p.nome;
