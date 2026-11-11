
-- ESTOM - SEMANA 04
-- Politicas de leitura com Row Level Security

-- Usuarios: consultar apenas o proprio perfil
CREATE POLICY "usuarios_select_own"
ON public.usuarios
FOR SELECT
TO authenticated
USING (id = (SELECT auth.uid()));

-- Produtos: consultar apenas os proprios produtos
CREATE POLICY "produtos_select_own"
ON public.produtos
FOR SELECT
TO authenticated
USING (usuario_id = (SELECT auth.uid()));

-- Historico: consultar apenas historicos dos proprios produtos
CREATE POLICY "historico_select_own"
ON public.historico_precos
FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1
        FROM public.produtos p
        WHERE p.id = historico_precos.produto_id
          AND p.usuario_id = (SELECT auth.uid())
    )
);

-- Notificacoes: consultar apenas notificacoes dos proprios produtos
CREATE POLICY "notificacoes_select_own"
ON public.notificacoes
FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1
        FROM public.produtos p
        WHERE p.id = notificacoes.produto_id
          AND p.usuario_id = (SELECT auth.uid())
    )
);
