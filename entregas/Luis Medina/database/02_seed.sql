
-- ==================================================
-- ESTOM - SEMANA 04
-- Dados ficticios para testes
-- ==================================================

DO $$
DECLARE
    v_email TEXT := 'luis.medi1820@gmail.com';
    v_usuario_id UUID;
BEGIN
    -- 1. Localizar a conta de teste no Supabase Auth
    SELECT id
    INTO v_usuario_id
    FROM auth.users
    WHERE email = v_email;

    IF v_usuario_id IS NULL THEN
        RAISE EXCEPTION
            'Conta de teste nao encontrada em auth.users. Verifique o email.';
    END IF;

    -- 2. Criar o perfil, caso ainda nao exista
    INSERT INTO public.usuarios (id, nome, email)
    SELECT id, 'Usuário Teste', email
    FROM auth.users
    WHERE id = v_usuario_id
    ON CONFLICT (id) DO NOTHING;

    -- 3. Inserir produtos somente se a URL ainda nao existir
    INSERT INTO public.produtos (
        usuario_id,
        nome,
        preco_atual,
        url,
        imagem,
        preco_maximo,
        ultima_atualizacao
    )
    SELECT
        v_usuario_id,
        dados.nome,
        dados.preco_atual,
        dados.url,
        NULL,
        dados.preco_maximo,
        NOW()
    FROM (
        VALUES
            ('Monitor', 829.90, 'https://www.mercadolivre.com.br/monitor-exemplo', 800.00),
            ('Apple AirPods 4', 1190.90, 'https://www.mercadolivre.com.br/airpods-exemplo', 1250.00),
            ('PlayStation 5 Slim', 3299.00, 'https://www.mercadolivre.com.br/ps5-exemplo', NULL)
    ) AS dados(nome, preco_atual, url, preco_maximo)
    WHERE NOT EXISTS (
        SELECT 1
        FROM public.produtos p
        WHERE p.usuario_id = v_usuario_id
          AND p.url = dados.url
    );

    -- 4. Criar historico somente para produtos sem historico
    INSERT INTO public.historico_precos (
        produto_id,
        preco,
        data_consulta
    )
    SELECT
        p.id,
        dados.preco,
        NOW() - dados.dias_atras * INTERVAL '1 day'
    FROM public.produtos p
    CROSS JOIN LATERAL (
        VALUES
            (p.preco_atual + 100, 2),
            (p.preco_atual + 50, 1),
            (p.preco_atual, 0)
    ) AS dados(preco, dias_atras)
    WHERE p.usuario_id = v_usuario_id
      AND p.url IN (
          'https://www.mercadolivre.com.br/monitor-exemplo',
          'https://www.mercadolivre.com.br/airpods-exemplo',
          'https://www.mercadolivre.com.br/ps5-exemplo'
      )
      AND p.preco_atual IS NOT NULL
      AND NOT EXISTS (
          SELECT 1
          FROM public.historico_precos h
          WHERE h.produto_id = p.id
      );

    -- 5. Criar a notificacao de teste se ainda nao existir
    INSERT INTO public.notificacoes (
        produto_id,
        preco_notificado,
        status
    )
    SELECT
        p.id,
        p.preco_atual,
        'enviada'
    FROM public.produtos p
    WHERE p.usuario_id = v_usuario_id
      AND p.url = 'https://www.mercadolivre.com.br/airpods-exemplo'
      AND p.preco_atual IS NOT NULL
      AND NOT EXISTS (
          SELECT 1
          FROM public.notificacoes n
          WHERE n.produto_id = p.id
            AND n.status = 'enviada'
      );

END $$;
