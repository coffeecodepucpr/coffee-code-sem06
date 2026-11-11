# Dicionário de Dados — Estom

## 1. Tabela `usuarios`

Armazena os dados de perfil dos usuários do Estom. As credenciais de autenticação são gerenciadas pelo Supabase Auth.

| Campo | Tipo | Restrições | Descrição |
|---|---|---|---|
| `usuario_id` | UUID | FK, NOT NULL, ON DELETE CASCADE | Usuário proprietário do produto. Referencia `usuarios.id`; o produto é removido quando o usuário é excluído. |
| `nome` | VARCHAR(100) | NOT NULL | Nome do usuário. |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | E-mail do perfil. |

## 2. Tabela `produtos`

Armazena os produtos monitorados por cada usuário.

| Campo | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | UUID | PK, NOT NULL, DEFAULT `gen_random_uuid()` | Identificador único do produto, gerado automaticamente. |
| `usuario_id` | UUID | FK, NOT NULL | Usuário proprietário do produto. |
| `nome` | VARCHAR(150) | NOT NULL | Nome do produto. |
| `preco_atual` | NUMERIC(10,2) | CHECK >= 0 | Preço atual registrado. |
| `url` | TEXT | NOT NULL | Endereço do produto no Mercado Livre. |
| `imagem` | TEXT | Opcional | Endereço da imagem do produto. |
| `preco_maximo` | NUMERIC(10,2) | CHECK > 0 | Preço máximo desejado pelo usuário. |
| `ultima_atualizacao` | TIMESTAMPTZ | Opcional | Data e hora da última atualização do produto. |

## 3. Tabela `historico_precos`

Armazena os registros de preços observados ao longo do tempo.

| Campo | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | UUID | PK, NOT NULL | Identificador único do registro histórico. |
| `produto_id` | UUID | FK, NOT NULL | Produto ao qual o registro pertence. |
| `preco` | NUMERIC(10,2) | NOT NULL, CHECK >= 0 | Preço registrado na consulta. |
| `data_consulta` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Data e hora do registro. |

## 4. Tabela `notificacoes`

Registra as tentativas de notificação relacionadas aos produtos monitorados.

| Campo | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | UUID | PK, NOT NULL | Identificador único da notificação. |
| `produto_id` | UUID | FK, NOT NULL | Produto relacionado à notificação. |
| `preco_notificado` | NUMERIC(10,2) | NOT NULL, CHECK >= 0 | Preço associado à notificação. |
| `data_tentativa` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Data e hora da tentativa. |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'pendente', CHECK | Situação da notificação: `pendente`, `enviada` ou `falhou`. |

## 5. Relacionamentos

- `usuarios.id` é chave primária e chave estrangeira para `auth.users.id`.
- `produtos.usuario_id` referencia `usuarios.id`.
- `historico_precos.produto_id` referencia `produtos.id`.
- `notificacoes.produto_id` referencia `produtos.id`.

As relações entre usuários e produtos, produtos e histórico, e produtos e notificações são de um para muitos (1:N).
