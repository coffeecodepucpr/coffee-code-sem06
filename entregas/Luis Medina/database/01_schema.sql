
-- ==================================================
-- ESTOM - SEMANA 04
-- Estrutura do banco de dados PostgreSQL
-- ==================================================

-- 1. Usuarios
CREATE TABLE public.usuarios (
    id UUID PRIMARY KEY
        REFERENCES auth.users(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

-- 2. Produtos monitorados
CREATE TABLE public.produtos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL
        REFERENCES public.usuarios(id) ON DELETE CASCADE,
    nome VARCHAR(150) NOT NULL,
    preco_atual NUMERIC(10,2)
        CHECK (preco_atual >= 0),
    url TEXT NOT NULL,
    imagem TEXT,
    preco_maximo NUMERIC(10,2)
        CHECK (preco_maximo > 0),
    ultima_atualizacao TIMESTAMPTZ
);

-- 3. Historico de precos
CREATE TABLE public.historico_precos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    produto_id UUID NOT NULL
        REFERENCES public.produtos(id) ON DELETE CASCADE,
    preco NUMERIC(10,2) NOT NULL
        CHECK (preco >= 0),
    data_consulta TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Notificacoes
CREATE TABLE public.notificacoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    produto_id UUID NOT NULL
        REFERENCES public.produtos(id) ON DELETE CASCADE,
    preco_notificado NUMERIC(10,2) NOT NULL
        CHECK (preco_notificado >= 0),
    data_tentativa TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'pendente'
        CHECK (status IN ('pendente', 'enviada', 'falhou'))
);

-- Habilitar Row Level Security
ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.produtos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.historico_precos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notificacoes ENABLE ROW LEVEL SECURITY;
