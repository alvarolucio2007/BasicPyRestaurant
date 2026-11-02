# BasicPyRestaurant
Sistema de gestão de restaurante desenvolvido com Python, Streamlit e MongoDB.

## Sumário

- [Visão geral](#visão-geral)
- [Diferenciais do projeto](#diferenciais-do-projeto)
- [Stack de tecnologias](#stack-de-tecnologias)
- [Arquitetura](#arquitetura)
  - [Estrutura do projeto](#estrutura-do-projeto)
- [Banco de dados](#banco-de-dados)
  - [Principais coleções](#principais-coleções)
  - [Índices](#índices)
- [Relatórios e agregações](#relatórios-e-agregações)
- [Como executar](#como-executar)
- [Decisões de projeto](#decisões-de-projeto)
- [Escopo e limitações](#escopo-e-limitações)
- [Licença](#licença)

---

## Visão geral
...

Sistema de gestão de restaurante desenvolvido com Python, Streamlit e MongoDB.

---

## Visão geral

O BasicPyRestaurant é uma aplicação web de gestão interna para restaurantes. Permite
cadastrar categorias do cardápio, gerenciar produtos e registrar pedidos com cálculo
automático de total e controle de status.

O projeto foi desenvolvido como trabalho da disciplina de Banco de Dados, com o
objetivo de demonstrar, na prática, a integração entre uma aplicação Python e o
MongoDB, aplicando uma separação em camadas inspirada em arquitetura hexagonal.

> **Nota de transparência:** o desenvolvimento contou com auxílio de ferramentas
> de IA para estruturação, refatoração e revisão de código. Todas as decisões de
> arquitetura, modelagem e regras de negócio foram discutidas, compreendidas e
> validadas durante o processo, e o código final foi lido e testado manualmente.

---

## Diferenciais do projeto

- **Arquitetura hexagonal (ports and adapters):** separação entre domínio, casos de
  uso (services) e adaptadores de infraestrutura (repositórios MongoDB e interface
  Streamlit).
- **Domínio puro:** as entidades (`Category`, `Product`, `Order`, `OrderItem`) não
  dependem de Streamlit, PyMongo ou qualquer framework externo, sendo representadas
  por `dataclasses` simples.
- **Camada de aplicação isolada da persistência:** os serviços de aplicação
  dependem de repositórios injetados, permitindo substituir o MongoDB por outra
  implementação sem alterar regras de negócio.
- **Hierarquia de exceções customizadas:** `CategoryNotFound`, `ProductNotFound`,
  `OrderNotFound`, `CategoryValidationError`, `ProductValidationError` e
  `OrderValidationError` são traduzidas na interface para mensagens amigáveis,
  eliminando a exposição de tracebacks ao usuário final.
- **Histórico de pedido imutável:** ao criar um pedido, o nome e o preço unitário
  de cada produto são congelados no `OrderItem`. Alterações posteriores no cadastro
  do produto não afetam pedidos já registrados.
- **Índices no MongoDB:** índices simples e compostos alinhados às consultas
  realizadas pela aplicação, cobrindo listagem por categoria, listagem de produtos
  disponíveis e filtros por status de pedido.
- **Interface com padrão de flash message:** o feedback de sucesso/erro é
  transmitido entre reruns do Streamlit via `st.session_state`, evitando que
  mensagens desapareçam antes de serem lidas pelo usuário.
- **Orquestração completa com Docker Compose:** banco de dados, MongoDB Express
  e aplicação Streamlit sobem com um único comando.
- **Modelo de dados documental com referência por ID:** categorias, produtos e
  pedidos são armazenados em coleções separadas, relacionadas por `category_id`
  e `product_id`.

---

## Stack de tecnologias

| Camada | Tecnologia |
| --- | --- |
| **Aplicação** | |
| Linguagem | Python 3.14.9 |
| Interface | Streamlit |
| Driver MongoDB | PyMongo |
| **Banco de dados** | |
| SGBD | MongoDB 9 |
| **Infraestrutura** | |
| Containerização | Docker e Docker Compose |
| Administração do banco |  Mongo Express |

---

## Arquitetura

O projeto segue os princípios da arquitetura hexagonal, com dependências fluindo
exclusivamente de fora para dentro:

```
┌─────────────────────────────────────────┐
│  Streamlit (adapter de entrada)         │
│  ────────────────────────────────────   │
│  Service (casos de uso)                 │
│  ────────────────────────────────────   │
│  Domain (entidades e regras)            │
└─────────────────────────────────────────┘
         ▲
         │  Adapter de saída (MongoDB)
```

Cada camada tem uma responsabilidade bem definida:

- **Domínio:** entidades representadas como dataclasses, sem dependências externas.
- **Aplicação (services):** validação de regras de negócio, orquestração de chamadas
  ao repositório e tradução de falhas de persistência em exceções de domínio.
- **Adaptadores:** implementações concretas de persistência (MongoDB) e de interface
  (Streamlit). São substituíveis por outras implementações desde que respeitem o
  contrato esperado pelos services.

### Estrutura do projeto

```
BasicPyRestaurant/
├── main.py                     # Entrypoint da aplicação
├── setup.py                    # Wiring: monta services com os repositórios
├── bootstrap.py                # Conexão MongoDB com @st.cache_resource e criação de índices
├── Dockerfile                  # Imagem do frontend Streamlit
├── docker-compose.yml          # Orquestração de MongoDB, Mongo Express e frontend
├── front/
│   └── streamlit.py            # Interface Streamlit (classe Streamlit)
├── domain/
│   ├── category.py             # Entidade Category
│   ├── product.py              # Entidade Product
│   └── order.py                # Entidades Order e OrderItem
├── service/
│   ├── category_service.py     # Casos de uso de categoria
│   ├── product_service.py      # Casos de uso de produto
│   └── order_service.py        # Casos de uso de pedido
├── mongodb/
│   ├── category_repository.py  # Repositório MongoDB de categoria
│   ├── product_repository.py   # Repositório MongoDB de produto
│   └── order_repository.py     # Repositório MongoDB de pedido
└── README.md
```

---

## Banco de dados

### SGBD

MongoDB 9, executado via Docker Compose. O projeto está configurado para uso
local; a string de conexão pode ser adaptada para o MongoDB Atlas em nuvem,
adicionando o parâmetro `tlsCAFile` (necessário para TLS).


### Principais coleções

O modelo segue uma abordagem documental, com coleções separadas por entidade e
relacionamentos referenciados por identificador.

| Coleção | Descrição |
| --- | --- |
| `categories` | Categorias do cardápio (nome e ordem de exibição) |
| `products` | Produtos do cardápio, referenciando uma categoria por `category_id` |
| `orders` | Pedidos, com lista embutida de `items` (histórico congelado) |

### Índices

| Coleção | Índice | Motivação |
| --- | --- | --- |
| `categories` | `{ name: 1 }` (único) | Evitar nomes duplicados |
| `categories` | `{ display_order: 1 }` | Ordenação padrão da listagem |
| `products` | `{ category_id: 1, name: 1 }` | Listagem por categoria com ordenação |
| `products` | `{ available: 1 }` | Filtro do cardápio (produtos disponíveis) |
| `orders` | `{ status: 1, created_at: 1 }` | Filtro por status com ordenação temporal |

### Estrutura dos documentos

**Pedido (`orders`)** — os itens são embutidos para garantir atomicidade e
preservar o histórico:

```json
{
  "_id": ObjectId("..."),
  "table_number": 5,
  "customer_name": "Maria Silva",
  "status": "pending",
  "total_amount": 79.80,
  "created_at": "2026-11-01T18:32:00Z",
  "items": [
    {
      "product_id": "6725a...",
      "product_name": "Pizza Margherita",
      "unit_price": 39.90,
      "quantity": 2,
      "subtotal": 79.80,
      "notes": "sem manjericão"
    }
  ]
}
```

## Relatórios e agregações

A aplicação expõe três relatórios via aggregation pipeline do MongoDB, consumidos
pela aba "📊 Reports" da interface. Os cálculos rodam no banco; o frontend só
exibe.

### Produtos mais vendidos

`$unwind` no array `items` → `$group` por `product_id` somando quantidade e
receita → `$sort` desc → `$limit` no top N → `$project` para remover o `_id`.

Equivalente MongoDB de um `GROUP BY` com `SUM`, com a diferença de que `$unwind`
é necessário porque os itens vivem embutidos no pedido.

### Receita por categoria

`$unwind` nos itens → `$group` por `product_id` → `$lookup` em `products` →
`$unwind` → `$group` por `category_id` → `$lookup` em `categories` → `$unwind` →
`$sort` → `$project`.

O `$lookup` usa a forma com `let`/`pipeline` e `$toObjectId` porque
`orders.items.product_id` é string, enquanto `products._id` é `ObjectId`.
A conversão resolve o mismatch sem mudar o modelo.

### Resumo por status

`$group` por `status` com `$sum: 1` (contagem), `$sum` (receita) e `$avg`
(ticket médio) → `$sort` desc → `$project` com `$round` para arredondar 2 casas.

Como `status` e `total_amount` estão no nível raiz do documento, não precisa de
`$unwind`.

### Limitações

- Sem filtro por período ou paginação.
- Pipelines fazem collection scan; para o volume de demonstração é irrelevante,
  mas em produção exigiria índices específicos.
- Sem cache dos resultados (recalculados a cada requisição).
- Sem exportação (CSV, PDF).

São demonstrações funcionais de aggregation, não um módulo de BI.

---

## Como executar

### Requisitos

- Docker e Docker Compose

### Opção 1 — Stack completa via Docker (recomendado)

```bash
git clone https://github.com/alvarolucio2007/BasicPyRestaurant.git
cd BasicPyRestaurant
docker compose up -d --build
```

Após o build (primeira execução leva alguns minutos), os serviços estarão em:

- **Aplicação:** `http://localhost:8501`
- **Mongo Express:** `http://localhost:8081`

O `docker-compose.yml` sobe o MongoDB com autenticação e volume persistente,
o Mongo Express para inspeção visual e a aplicação Streamlit containerizada.
O serviço de frontend só inicia após o MongoDB estar saudável (`healthcheck`).

### Opção 2 — Desenvolvimento local (hot reload)

Para desenvolver com hot reload do Streamlit, mantenha apenas o banco no Docker:

```bash
# 1. Ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 2. Sobe apenas o MongoDB
docker compose up -d mongo

# 3. Roda a aplicação localmente
streamlit run main.py --server.port 8501
```

Nesse modo, a `MONGO_URL` usada é a do fallback em `main.py`
(`localhost:27017`), já que o MongoDB está com a porta exposta ao host.

### Variáveis de ambiente

A string de conexão é lida de `MONGO_URL` (variável de ambiente) com fallback
para `localhost`. No modo Docker, o `docker-compose.yml` injeta a URL apontando
para o hostname interno `mongo`. No modo local, o fallback já atende.

---

## Decisões de projeto

### Arquitetura hexagonal

A separação entre domínio, aplicação e adaptadores foi adotada para isolar as
regras de negócio da infraestrutura. O domínio não conhece MongoDB nem Streamlit,
e os serviços dependem de repositórios injetados — o que torna trivial substituir
a camada de persistência por um repositório em memória em testes, por exemplo.

### Imutabilidade do histórico de pedidos

Ao criar um pedido, o nome e o preço de cada produto são copiados para o item do
pedido. Essa decisão evita que alterações futuras no cadastro de produto (reajuste
de preço, troca de nome ou remoção) corrompam pedidos já registrados. O histórico
permanece auditável e reflete o que o cliente efetivamente contratou.

### Cálculo do total no serviço

O `total_amount` de um pedido é calculado no `OrderService` a partir dos subtotais
dos itens (`sum(item.subtotal)`), nunca recebido da interface. Isso elimina a
possibilidade de o front-end enviar um valor divergente do que foi de fato pedido.

### Validação de ID e uso de `matched_count`

No `update` dos repositórios, o retorno é baseado em `matched_count` (documento
existe?) e não em `modified_count` (documento mudou?). Essa escolha garante que
salvar um formulário sem alterar nenhum campo não seja tratado como erro — o
registro existe e a operação foi bem-sucedida.

### Tratamento de IDs inválidos

A conversão `str → ObjectId` é encapsulada em um método estático `_oid` que trata
`InvalidId` e `TypeError`, retornando `None` em caso de entrada inválida. Sem essa
camada, um ID malformado dispararia `InvalidId` do PyMongo e interromperia a
requisição com um erro de baixo nível.

### Flash message no Streamlit

Como o Streamlit reexecuta o script a cada interação, mensagens de sucesso/erro
exibidas antes de um `st.rerun()` desaparecem antes de serem lidas. O padrão
adotado armazena a mensagem em `st.session_state` e a consome no início do próximo
rerun, garantindo que o usuário veja o feedback de cada ação.

### Cache de recursos

A conexão com o MongoDB é encapsulada em uma função decorada com
`@st.cache_resource`, garantindo que seja criada uma única vez por sessão e
reaproveitada entre reruns. Sem esse cache, cada clique na interface abriria uma
nova conexão com o banco.

### Índices alinhados às consultas

Cada índice foi criado em função de uma consulta real da aplicação. O índice
composto `{ category_id: 1, name: 1 }`, por exemplo, cobre simultaneamente o filtro
e a ordenação de `list_by_category`, evitando sort em memória.

### Injeção de dependências sem framework

Não há framework de DI no projeto. O `setup.py` atua como composition root: recebe
a `collection` do MongoDB, instancia cada repositório, injeta nos services e
devolve a classe `Streamlit` pronta para uso. Essa abordagem evita dependências
extras e mantém o fluxo de construção explícito e rastreável.

---

## Escopo e limitações

Este é um projeto acadêmico com escopo deliberadamente enxuto. Ficam fora do
escopo desta versão:

- Autenticação e controle de acesso de usuários.
- Testes automatizados.
- Deploy em ambiente de produção.
- Histórico de auditoria de alterações.
- Migrações versionadas do schema do MongoDB.

Essas extensões estão previstas como evolução natural do projeto.

---

## Licença

Este projeto está licenciado sob a MIT License. Consulte o arquivo `LICENSE` para mais detalhes.
