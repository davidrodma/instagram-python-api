# Instagram Python API

API REST em **Python (Flask) + MongoDB** construída sobre a biblioteca [instagrapi](https://github.com/subzeroid/instagrapi) para:

- **Extrair dados públicos** do Instagram (perfis, posts, seguidores, curtidas, comentários, stories, hashtags);
- **Executar ações** com contas próprias (seguir, curtir, comentar, ver stories, curtir comentários, editar perfil);
- **Gerenciar um pool de contas, proxies e sessões**, com rodízio automático e desativação de contas/proxies problemáticos.

> [!WARNING]
> Este projeto não tem nenhuma relação com o Instagram ou a Meta. Automatizar ações no Instagram pode violar os [Termos de Uso](https://help.instagram.com/581066165581870) da plataforma e levar ao bloqueio das contas utilizadas. Ao extrair dados de terceiros, respeite a LGPD/GDPR. Use por sua conta e risco e, de preferência, com contas criadas para esse fim (nunca com sua conta pessoal).

## Sumário

- [Como funciona](#como-funciona)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Primeiros passos](#primeiros-passos)
- [Convenções da API](#convenções-da-api)
- [Referência de endpoints](#referência-de-endpoints)
  - [CRUD dos cadastros](#1-crud-dos-cadastros)
  - [Instagram — Scrape (extração)](#2-instagram--scrape-extração)
  - [Instagram — Profile](#3-instagram--profile)
  - [Instagram — Worker (ações)](#4-instagram--worker-ações)
  - [Instagram — Boost](#5-instagram--boost)
  - [Teste](#6-teste)
- [Configurações dinâmicas (`/config`)](#configurações-dinâmicas-config)
- [Tratamento automático de erros](#tratamento-automático-de-erros)
- [Coleção do Insomnia](#coleção-do-insomnia)

## Como funciona

```mermaid
flowchart LR
    C[Seu sistema / Insomnia / curl] -- "Authorization: Bearer SECRET_KEY" --> A[Flask API<br>/api]
    A --> S[Services]
    S --> I[instagrapi] --> IG[(Instagram)]
    S --> M[(MongoDB)]
    I -. proxy .-> IG
```

O projeto trabalha com **três tipos de conta do Instagram**, cada um guardado em uma coleção do MongoDB:

| Tipo | Coleção | Para que serve | Como é escolhida |
| --- | --- | --- | --- |
| **Profile** | `profiles` | Contas "extratoras", usadas nas rotas de **scrape** e em `seen-stories-action` | Aleatoriamente, entre as ativas (`status: 1`) |
| **Worker** | `workers` | Contas que executam **ações** (seguir, curtir, comentar...) | Você informa qual, em `username_action` |
| **Boost** | `boosts` | Contas de **clientes** do seu sistema, associadas via `/instagram/boost/save` | Você informa qual, em `username_action` |

Além delas existem os cadastros de apoio:

- **Proxies** (`proxies`): proxies sorteados no login de acordo com o `type`;
- **Cookies** (`cookies`): sessões do instagrapi salvas após cada login, reaproveitadas para não precisar logar de novo (menos risco de *challenge*);
- **Config** (`configs`): parâmetros que mudam o comportamento da API em tempo de execução (veja [Configurações dinâmicas](#configurações-dinâmicas-config));
- **Nationality Names** (`nationalitynames`): banco de nomes e sobrenomes por nacionalidade, usado para gerar nomes de perfil.

As coleções são criadas automaticamente pelo MongoDB na primeira gravação.

## Estrutura do projeto

```text
.
├── main.py                       # Ponto de entrada (Flask, porta 5011 por padrão)
├── requirements.txt
├── .env.developer                # Modelo de variáveis de ambiente
├── _resources/
│   └── Insomnia_2024-03-26.json  # Coleção com todas as requisições da API
└── app/
    ├── common/
    │   ├── routes/config/routes.py        # Todas as rotas da API
    │   ├── routes/middlewares/            # Autenticação por token
    │   ├── routes/services/route_service.py # Gera as rotas CRUD padrão
    │   └── utilities/                     # Criptografia, logs, paginação, imagens...
    ├── database/repositories/             # Acesso ao MongoDB (pymongo)
    └── modules/
        ├── instagram/                     # Scrape e ações no Instagram (instagrapi)
        ├── profile/  worker/  boost/      # Contas
        ├── proxy/  cookie/  config/       # Apoio
        └── nationality_name/              # Gerador de nomes/perfis
```

Cada módulo segue o padrão `controllers → services → repositories → models`, com validação de entrada via DTOs do [Pydantic](https://docs.pydantic.dev/).

## Requisitos

- **Python 3.10, 3.11 ou 3.12** (recomendado 3.11). O Python 3.13 ainda não é suportado, porque o `instagrapi 2.0.3` exige o `pydantic 2.5.3`, que não tem versão para 3.13.
- **MongoDB** 5 ou superior (local, Docker ou Atlas). Não precisa de *replica set*.
- **Contas do Instagram** para extração e/ou ações e, opcionalmente, **proxies** (recomendado).

## Instalação

### 1. Clone o repositório e crie um ambiente virtual

```bash
git clone https://github.com/davidrodma/instagram-python-api.git
cd instagram-python-api
python -m venv venv
```

Ative o ambiente virtual:

```bash
# Linux / macOS
source venv/bin/activate
```

```bash
# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

A aplicação lê o arquivo **`.env`** na raiz do projeto. Use o `.env.developer` como modelo:

```bash
cp .env.developer .env
```

| Variável | Obrigatória | Descrição |
| --- | --- | --- |
| `DATABASE_URL` | Sim | String de conexão do MongoDB. Ex.: `mongodb://localhost:27017/` |
| `DATABASE_NAME` | Sim | Nome do banco. Ex.: `instagram_api` |
| `SECRET_KEY` | Sim | Token que os clientes devem enviar no cabeçalho `Authorization` |
| `SECRET_ENCRYPTION` | Sim | Chave AES usada pelo utilitário de criptografia. **Precisa ter exatamente 16, 24 ou 32 caracteres** |

Exemplo de `.env`:

```env
DATABASE_URL="mongodb://localhost:27017/"
DATABASE_NAME="instagram_api"
SECRET_KEY='troque-por-um-token-forte'
SECRET_ENCRYPTION='0123456789abcdef0123456789abcdef'
```

Para gerar valores aleatórios (o comando abaixo gera 32 caracteres, que servem para as duas chaves):

```bash
python -c "import secrets; print(secrets.token_hex(16))"
```

> [!IMPORTANT]
> Nunca faça commit do `.env`. Ele já está no `.gitignore`.

### 4. Suba o MongoDB

Se você já tem o MongoDB instalado, basta deixá-lo rodando. Para subir rapidamente com Docker:

```bash
docker run -d --name mongo -p 27017:27017 mongo:7
```

### 5. Inicie a API

```bash
python main.py
```

A API sobe em `http://localhost:5011` e todas as rotas ficam sob o prefixo **`/api`**. Também é possível escolher a porta `5012` ou `5013` (outros valores são ignorados), o que permite rodar mais de uma instância ao mesmo tempo:

```bash
python main.py 5012
```

> [!NOTE]
> O `main.py` usa o servidor de desenvolvimento do Flask com `debug=True`. Não exponha essa instância diretamente na internet. Em produção, use um servidor WSGI (como gunicorn ou waitress) apontando para `main:app`, com **um único processo**, já que as sessões logadas ficam em cache na memória.

## Primeiros passos

Os exemplos abaixo usam `curl` e consideram `SECRET_KEY=troque-por-um-token-forte`.

**1. Teste se a API está de pé** (não depende do Instagram):

```bash
curl http://localhost:5011/api/nationality-names/generate-simple-profile -H "Authorization: Bearer troque-por-um-token-forte"
```

```json
{"username": "k3x9...", "password": "aB3$...", "full_name": "John Doe", "birth": {"day": 12, "month": 5, "year": 1990}}
```

**2. Cadastre pelo menos uma conta extratora (profile):**

```bash
curl -X POST http://localhost:5011/api/profiles -H "Authorization: Bearer troque-por-um-token-forte" -H "Content-Type: application/json" -d '{"username": "my_scraper_account", "password": "your_password"}'
```

**3. (Opcional, recomendado) Cadastre um proxy para extração:**

```bash
curl -X POST http://localhost:5011/api/proxies -H "Authorization: Bearer troque-por-um-token-forte" -H "Content-Type: application/json" -d '{"url": "http://user:password@proxy.example.com:8080", "type": "extract"}'
```

**4. Consulte um perfil público:**

```bash
curl -X GET http://localhost:5011/api/instagram/scrape/user-info -H "Authorization: Bearer troque-por-um-token-forte" -H "Content-Type: application/json" -d '{"username": "instagram"}'
```

Na primeira chamada a API faz login com a conta extratora e salva a sessão na coleção `cookies`. As próximas chamadas reaproveitam essa sessão.

## Convenções da API

### Autenticação

Todas as rotas exigem o cabeçalho:

```http
Authorization: Bearer <SECRET_KEY>
```

| Situação | Status | Resposta |
| --- | --- | --- |
| Cabeçalho ausente | `401` | `{"error": "Token not provided"}` |
| Token diferente do `SECRET_KEY` | `401` | `{"error": "Invalid Token"}` |

### Parâmetros vão no corpo JSON, inclusive nos `GET`

Todas as rotas (**inclusive as `GET`**) recebem os parâmetros como JSON no corpo da requisição, com `Content-Type: application/json`. Ferramentas como curl, Insomnia, Postman, `requests` (Python) e axios enviam corpo em `GET` sem problema. O `fetch` dos navegadores não envia, então chame a API a partir do seu backend.

Exemplo em Python:

```python
import requests

API = "http://localhost:5011/api"
HEADERS = {"Authorization": "Bearer troque-por-um-token-forte"}

user = requests.get(f"{API}/instagram/scrape/user-info", json={"username": "instagram"}, headers=HEADERS).json()
print(user["username"], user["follower_count"])
```

Exemplo em JavaScript (Node.js + axios):

```js
const { data } = await axios.get("http://localhost:5011/api/instagram/scrape/user-info", {
  headers: { Authorization: "Bearer troque-por-um-token-forte" },
  data: { username: "instagram" },
});
```

### Respostas de erro

| Status | Quando | Formato |
| --- | --- | --- |
| `400` | Erro durante o processamento (inclui corpo inválido nas rotas do Instagram) | `{"error": "mensagem"}` |
| `404` | Registro não encontrado (busca por id) | `{"error": "Record not found"}` |
| `422` | Corpo inválido no `POST`/`PUT` dos cadastros (validação do Pydantic) | `{"error": "...", "errors": [...], "error_count": 1}` |

O corpo das respostas é sempre JSON, mas algumas rotas o enviam com `Content-Type: text/html`. Se o seu cliente HTTP decidir o parse pelo cabeçalho, converta o texto da resposta com um parse de JSON.

> [!TIP]
> Várias rotas do Instagram respondem **`200` com um campo `error`** quando o problema é do alvo e não da requisição: perfil privado (`"is_private": true`), link inexistente (`"error_link": true`), stories expirados etc. **Sempre verifique se a resposta contém `error`.**

### Identificadores do Instagram

| Campo | O que é | Exemplo |
| --- | --- | --- |
| `username` | Nome de usuário, sem `@` | `instagram` |
| `id` / `pk` (usuário) | ID numérico do usuário | `25025320` |
| `url` | Link de um post | `https://www.instagram.com/p/POST_CODE/` |
| `id` / `pk` / `media_id` (post) | ID numérico da mídia. Use `/instagram/scrape/media-id` para obtê-lo a partir da URL | `1234567890123456789` |

### Imagens em base64

Muitas respostas incluem `image_base64` (ou `imageBase64`, `image_target`, `image_action`): a foto de perfil ou miniatura do post em 150x150, como *data URI*, pronta para usar em um `<img src="...">`.

## Referência de endpoints

Base URL: `http://localhost:5011/api`

### 1. CRUD dos cadastros

Os módulos `proxies`, `cookies`, `config`, `nationality-names`, `profiles`, `workers` e `boosts` têm as mesmas 6 rotas:

| Método | Rota | Corpo | Resposta |
| --- | --- | --- | --- |
| `GET` | `/{modulo}` | `{"page": 1, "limit": 100}` (opcional) | `{"total", "page", "pages", "limit", "list": [...]}` |
| `GET` | `/{modulo}/{id}` | — | O registro, ou `404` |
| `POST` | `/{modulo}` | Campos do registro | `{"id": "..."}` |
| `PUT` | `/{modulo}/{id}` | Campos a alterar | `{"message": "1 records successfully updated!", "success": true}` |
| `PATCH` | `/{modulo}/status` | `{"ids": ["id1", "id2"], "status": 0}` | `{"message": "...", "success": true}` |
| `DELETE` | `/{modulo}` | `{"ids": ["id1", "id2"]}` | `{"message": "...", "success": true}` |

- `{id}` é o `_id` do MongoDB (ex.: `65f1a2b3c4d5e6f708192a3b`).
- A paginação também pode ir na query string, desde que você envie os dois parâmetros: `?page=2&limit=50`.
- `status`: `1` = ativo, `0` = desativado. Só registros ativos são usados pela API.
- `ids` aceita uma lista ou um único id em string.
- No `PUT`, apenas os campos enviados são alterados, mas alguns módulos exigem certos campos mesmo na edição (indicado abaixo).
- Os contadores (`countError`, `countSuccess`, `countFewMinutes`, `countChallenge`, `countUsed`...) e as datas (`disabledAt`, `fewMinutesAt`, `expireAt`...) são mantidos automaticamente pela API.

#### Proxies — `/proxies`

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `url` | string | Sim (também no `PUT`) | `http://usuario:senha@host:porta` (aceita `https://` e `socks5://`) |
| `type` | string | Sim (também no `PUT`) | Em que fluxo o proxy é usado (veja abaixo) |
| `status` | int | Não (padrão `1`) | `1` ativo, `0` desativado |

Valores de `type`:

| `type` | Usado em |
| --- | --- |
| `extract` | Login das contas extratoras (scrape) |
| `worker` | Login dos workers |
| `worker-action` | Troca de proxy dos workers após o login, se `change-proxy-action = 1` |
| `boost` | Login dos boosts |
| `boost-action` | Troca de proxy dos boosts após o login, se `change-proxy-action = 1` |
| `buy-proxy` | Proxy fixo/comprado para uma conta: se ele cair, a conta é desativada em vez de trocar de proxy |
| `test`, `website-view` | Uso livre |

Rotas extras:

| Método | Rota | Corpo | Descrição |
| --- | --- | --- | --- |
| `POST` | `/proxies/create-many` | `[{"url": "...", "type": "extract"}, ...]` | Cadastra vários de uma vez. Retorna `{"ids": [...]}` |
| `GET` | `/proxies/test-proxy` | `{"proxy": "http://user:password@proxy.example.com:8080"}` | Compara o IP com e sem o proxy. Retorna `{"success", "before_ip", "after_ip"}` |

#### Profiles — `/profiles` (contas extratoras)

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `username` | string | Sim (também no `PUT`) | Usuário do Instagram |
| `password` | string | Sim no `POST` | Senha do Instagram |
| `status` | int | Não (padrão `1`) | |
| `groupType`, `provider` | string | Não | Campos livres para você organizar as contas |

Ao cadastrar um `username` que já existe, o registro anterior é substituído. Rota extra: `POST /profiles/create-many` com uma lista de objetos.

#### Workers — `/workers` (contas de ação)

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `username` | string | Sim (também no `PUT`) | Usuário do Instagram |
| `password` | string | Sim no `POST` | Senha do Instagram |
| `proxy` | string | Não | URL de um proxy fixo, `random` (sorteia e grava um proxy `worker`) ou vazio |
| `nationality` | string | Não | Código do país (ex.: `BR`). Usado para sortear proxies desse país |
| `typeProxy`, `countryProxy` | string | Não | Informações do proxy da conta |
| `groupType`, `provider`, `info` | string | Não | Campos livres |
| `price`, `costSms` | float | Não | Campos livres (custo da conta) |
| `isCreate` | bool | Não | Se `true`, aplica a config `which-proxy-type-to-use-after-create-worker` |

Rotas extras:

| Método | Rota | Corpo | Descrição |
| --- | --- | --- | --- |
| `POST` | `/workers/create-many` | `[{"username": "...", "password": "..."}, ...]` | Cadastra vários de uma vez |
| `POST` | `/workers/disable` | `{"username": "my_worker_account", "reason": "manual"}` | Desativa a conta e retorna o registro atualizado |

#### Boosts — `/boosts` (contas de clientes)

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `username` | string | Sim (também no `PUT`) | Usuário do Instagram |
| `password` | string | Sim no `POST` | Senha do Instagram |
| `accountId` | string | Sim (também no `PUT`) | ID do cliente **no seu sistema** |
| `socialId` | string | Não | ID numérico (pk) do perfil no Instagram |
| `proxy` | string | Não | URL fixa, `random` ou vazio |
| `countryCode` | string | Não (padrão `BR`) | País usado para sortear proxies |

> Para cadastrar um cliente, prefira [`POST /instagram/boost/save`](#5-instagram--boost), que valida o login antes de salvar.

Rotas extras:

| Método | Rota | Corpo | Descrição |
| --- | --- | --- | --- |
| `POST` | `/boosts/disable` | `{"username": "my_boost_account", "reason": "manual"}` | Desativa pelo username |
| `POST` | `/boosts/disable-by-social-id` | `{"socialId": "1234567890", "reason": "manual"}` | Desativa pelo pk do Instagram |
| `POST` | `/boosts/active-by-social-id` | `{"socialId": "1234567890"}` | Reativa e zera os contadores de erro |

#### Cookies — `/cookies` (sessões salvas)

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `username` | string | Sim no `POST` | Dono da sessão |
| `state` | string | Sim | JSON (em texto) com as configurações de sessão do instagrapi |
| `pk` | string | Não | ID numérico da conta |

As sessões são criadas e atualizadas automaticamente a cada login. Na prática, você só vai usar este módulo para listar sessões ou **apagar uma sessão para forçar um novo login** com usuário e senha.

#### Config — `/config`

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `name` | string | Sim no `POST` | Chave da configuração (veja a [lista de chaves](#configurações-dinâmicas-config)) |
| `title` | string | Sim no `POST` | Título legível |
| `description` | string | Sim no `POST` | Descrição |
| `type` | string | Sim no `POST` | Tipo do campo, para uso em painéis (ex.: `text`) |
| `value` | string | Não | Valor da configuração |
| `jsonOptions`, `classAdd` | string | Não | Campos livres, para uso em painéis |
| `status` | int | Não (padrão `1`) | A configuração só tem efeito com `status: 1` e `value` preenchido |

#### Nationality Names — `/nationality-names`

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `romanName` | string | Sim (também no `PUT`) | Nome em alfabeto latino (usado para gerar o username) |
| `nativeName` | string | Não | Nome no alfabeto original (ex.: japonês), usado no nome de exibição |
| `gender` | string | Não | `male` ou `female` (para `type: name`) |
| `nationality` | string | Sim (também no `PUT`) | Código do país, ex.: `BR`, `JP`, `KR` |
| `type` | string | Sim (também no `PUT`) | `name` (nome) ou `lastname` (sobrenome) |

Rotas extras:

| Método | Rota | Corpo | Resposta |
| --- | --- | --- | --- |
| `GET` | `/nationality-names/generate-name` | `{"gender": "female", "nationality": "BR"}` | `{"username": "maria_silvaxy", "full_name": "Maria Silva ✨"}`. Sorteia nome e sobrenome cadastrados para esse gênero e país, por isso precisa de nomes cadastrados |
| `GET` | `/nationality-names/generate-simple-profile` | — | `{"username", "password", "full_name", "birth": {"day", "month", "year"}}`. Gerado com Faker, não depende do banco |

### 2. Instagram — Scrape (extração)

Todas as rotas abaixo são `GET`, ficam em `/instagram/scrape/...` e usam uma **conta extratora** (`profiles`) sorteada, com um proxy do tipo `extract` quando houver. Se a conta falhar, a API tenta de novo com outra (até 3 vezes) e registra o erro na conta.

| Rota | Corpo (JSON) | Retorno |
| --- | --- | --- |
| `/user-info` | `{"username": "instagram"}` | Dados completos do perfil (`pk`, `username`, `full_name`, `biography`, `follower_count`, `following_count`, `media_count`, `is_private`, `profile_pic_url`...) e `image_base64` |
| `/user-info-by-id` | `{"id": "25025320"}` | Igual ao `user-info` |
| `/user-recent-posts` | `{"username": "instagram", "max": 5}` | `{"total_recent_posts", "posts": [...], "user"}` |
| `/user-last-post` | `{"username": "instagram"}` | `{"total_recent_posts", "post", "last_post", "user"}` |
| `/user-info-and-last-post` | `{"username": "instagram"}` | Igual ao `user-last-post` |
| `/media-url-info` | `{"url": "https://www.instagram.com/p/POST_CODE/"}` | Dados do post (`pk`, `code`, `like_count`, `comment_count`, `caption_text`, `user`...) e `image_base64` |
| `/media-id-info` | `{"id": "1234567890123456789"}` | Igual ao `media-url-info` |
| `/media-id` | `{"url": "https://www.instagram.com/p/POST_CODE/"}` | `{"pk": "1234567890123456789"}`. Calculado a partir da URL, sem login |
| `/followers` | `{"username": "instagram", "max": 10, "only_username": true}` | `{"count", "next_max_id", "username_action", "list": [...]}` |
| `/followers-in-profile` | `{"username_target": "instagram", "username_action": "some_follower"}` | Verifica se `username_action` segue o alvo: `{"is_follower", "id_action", "id_target", "follower_count_target", "change_username", ...}` |
| `/recent-post-likers` | `{"id": "1234567890123456789"}` ou `{"url": "..."}` | `{"media_id", "total", "likers": [...]}` |
| `/recent-post-likers-by-url` | `{"url": "https://www.instagram.com/p/POST_CODE/"}` | Igual ao anterior |
| `/likers-in-post` | `{"url": "...", "usernames_action": ["some_liker"]}` | Verifica se os usernames curtiram o post: `{"is_liker", "likers": [{"username", "id", "is_liker"}], "total", ...}` |
| `/likers-in-post-by-id` | `{"media_id": "...", "ids_likers_action": ["9876543210"]}` | Igual ao anterior, usando o id do post e ids de usuários |
| `/post-comments` | `{"url": "...", "max": 50}` | `{"count", "next_max_id", "list": [...], "username_action"}` |
| `/post-comments-by-id` | `{"id": "1234567890123456789", "max": 50}` | Igual ao anterior |
| `/comments-in-post` | `{"media_id": "...", "usernames_action": "some_commenter"}` | Verifica se o usuário comentou: `{"is_comment", "username_comment", "comments": [{"id", "username", "is_comment", "comment_id", "comment_like_count", "text"}], ...}` |
| `/user-commented-in-post` | `{"media_id": "...", "username_comment": "some_commenter"}` | Igual ao `comments-in-post` |
| `/comment-in-last-post` | `{"username": "instagram", "text": "123456"}` | Verifica se `username` comentou o texto `text` (sem diferenciar maiúsculas de minúsculas) no **próprio último post**, ou no post `media_id`. Útil para confirmar a posse de um perfil. Retorna `{"is_comment", "post_id", "post_code", "post_image", "total_comments", ...}` |
| `/user-recent-stories` | `{"username": "instagram", "max": 5}` | `{"total_recent_stories", "stories": [...], "user"}` |
| `/posts-by-tag` | `{"tag": "travel", "tab": "recent", "max": 27}` | `{"count", "next_max_id", "list": [...], "username_action"}` |
| `/extract-biographies` | `{"username": "instagram", "quantity": 3, "min_char": 20}` | Coleta biografias de perfis da rede do alvo (contas seguidas pelos seguidores dele): `{"count", "followers": [{"pk", "username", "full_name", "biography"}]}` |

Parâmetros opcionais mais usados:

| Parâmetro | Rotas | Descrição |
| --- | --- | --- |
| `id` / `pk` | `user-recent-posts`, `user-last-post`, `followers`, `recent-post-likers`, `post-comments`, `user-recent-stories` | Use o id no lugar do `username`/`url` (evita uma consulta extra) |
| `max` | várias | Quantidade máxima de itens. Padrões: posts `60`, seguidores `200`, comentários `20`, stories `20`, hashtag `27` |
| `return_with_next_max_id` + `next_max_id` | `user-recent-posts`, `followers` | Paginação: envie `return_with_next_max_id: true` e, nas próximas chamadas, o `next_max_id` recebido |
| `next_max_id` | `post-comments`, `posts-by-tag` | Paginação (essas rotas sempre retornam `next_max_id`) |
| `query` | `followers` | Busca seguidores por nome em vez de listar todos |
| `only_username` | `followers` | Retorna apenas a lista de usernames |
| `only_text` | `post-comments` | Retorna apenas a lista de textos dos comentários |
| `tab` | `posts-by-tag` | `recent` (padrão) ou `top` |
| `media_id` | `user-recent-stories` | Busca um story específico |
| `return_image_base64` | `followers-in-profile` | Inclui a foto do alvo em `image_target` |

> [!NOTE]
> Em posts com 1000 curtidas ou mais, o Instagram não devolve a lista completa. Nesses casos, e quando o post oculta as curtidas, `likers-in-post` e `likers-in-post-by-id` consideram `is_liker: true`.

### 3. Instagram — Profile

| Método | Rota | Corpo | Descrição |
| --- | --- | --- | --- |
| `POST` | `/instagram/profile/seen-stories-action` | `{"username": "instagram", "max": 1}` | Uma conta extratora sorteada visualiza os stories do alvo. Retorna `{"success", "count", "stories"}`. Aceita também `pk` e `media_id` |

### 4. Instagram — Worker (ações)

Rotas `POST` em `/instagram/worker/...`. A conta informada em `username_action` precisa estar cadastrada em `/workers` com `status: 1`. A API faz o login (reaproveitando a sessão salva), escolhe o proxy e executa a ação.

| Rota | Corpo | Campo de sucesso |
| --- | --- | --- |
| `/follower-action` | `{"username_action": "my_worker_account", "username_target": "instagram"}` | `is_follower` |
| `/like-action` | `{"username_action": "my_worker_account", "url_target": "https://www.instagram.com/p/POST_CODE/"}` | `is_liker` |
| `/comment-action` | `{"username_action": "my_worker_account", "url_target": "...", "text": "Great post! 🔥"}` | `is_comment` |
| `/story-action` | `{"username_action": "my_worker_account", "username_target": "instagram", "max": 5}` | `is_story` |
| `/like-comment-action` | `{"username_action": "my_worker_account", "url_target": "...", "username_comment": "some_commenter"}` | `is_liker` |

- No lugar de `username_target`/`url_target` você pode enviar o id em `id_target`, o que poupa uma consulta.
- Em `like-comment-action`, informe o comentário por `comment_id` **ou** pelo autor (`username_comment` ou `user_id_comment`) junto com o post (`url_target` ou `id_target`).

Exemplo de resposta de sucesso:

```json
{
  "username_action": "my_worker_account",
  "username_target": "instagram",
  "id_target": "25025320",
  "is_follower": true,
  "already_exists": false,
  "worker": {"_id": "65f1a2b3c4d5e6f708192a3b", "username": "my_worker_account", "status": 1, "noteError": ""}
}
```

Em caso de falha a resposta vem com `error`. Se `error_link: true`, o alvo não existe ou o link é inválido. `max_limit: true` (só no follow) indica que a conta atingiu o limite de pessoas seguidas. O objeto `worker` mostra se a conta foi desativada por causa do erro.

#### Editar perfil — `POST /instagram/worker/edit-instagram`

Faz login na conta (ou usa o cadastro de `workers`, se existir) e altera apenas os campos enviados que forem diferentes dos atuais.

```json
{
  "username": "my_worker_account",
  "password": "your_password",
  "new_username": "auto",
  "new_password": "",
  "gender": "female",
  "nationality": "BR",
  "first_name": "Maria Silva",
  "biography": "Example biography",
  "external_url": "https://example.com",
  "visibility": "public",
  "album": "avatars",
  "filename": "photo1.jpg",
  "posts_album": "posts",
  "posts_quantity": 3,
  "proxy": "worker"
}
```

| Campo | Descrição |
| --- | --- |
| `username`, `password` | Obrigatórios. Credenciais atuais da conta |
| `session_id` | Opcional. Faz login pelo `sessionid` de um navegador em vez da senha (quando a conta não está em `workers`) |
| `new_username` | Novo username. Com `"auto"`, gera um nome a partir de `gender` + `nationality` (via `nationality-names`) ou, sem `gender`, um nome aleatório |
| `new_password` | Nova senha. Com `"auto"`, gera uma senha aleatória |
| `first_name`, `biography`, `external_url`, `email`, `phone_number` | Dados do perfil |
| `visibility` | `public` ou `private` |
| `album` + `filename` | Troca a foto de perfil pelo arquivo `../public/galleries/<album>/<filename>` |
| `posts_album` + `posts_quantity` | Publica imagens aleatórias de `../public/galleries/<posts_album>/` até a conta ter `posts_quantity` posts |
| `proxy` | URL de um proxy ou um tipo cadastrado (`worker`, `boost`, `extract`, `test`) para sortear |

> Os caminhos de imagens são relativos à pasta **de onde você executa** o `main.py`. Ou seja, a pasta `public/` deve ficar ao lado da pasta do projeto.

Retorno: `{"success": true, "imageBase64", "new_username", "new_password", "first_name", "proxy"}` ou `{"error": "..."}`. Se a conta estiver em `workers`, o novo username/senha também são gravados lá.

### 5. Instagram — Boost

#### Associar uma conta — `POST /instagram/boost/save`

Faz login com as credenciais (até 3 tentativas, sorteando proxies do tipo `boost`). Se der certo, cria ou atualiza o registro em `/boosts` usando o `accountId` como chave.

```json
{
  "username": "my_boost_account",
  "password": "your_password",
  "accountId": "1",
  "socialId": "1234567890",
  "proxy": "random",
  "status": 1,
  "countryCode": "BR"
}
```

| Campo | Obrigatório | Descrição |
| --- | --- | --- |
| `username`, `password` | Sim | Credenciais do Instagram |
| `accountId` | Sim | ID do cliente no seu sistema |
| `socialId` | Sim | ID numérico (pk) do perfil no Instagram |
| `proxy` | Não (padrão `random`) | URL fixa ou `random` |
| `countryCode` | Não | País usado para sortear proxies |

Se o login falhar, o retorno traz uma mensagem pronta para mostrar ao usuário final:

```json
{
  "error": "boost.first_login_boost.login_custom: ...",
  "message_user": "A senha informada parece não estar correta. Por favor, confira e insira novamente.",
  "attempt": true
}
```

#### Ações

As mesmas ações do Worker, em `/instagram/boost/...`, usando contas cadastradas em `/boosts`:

`/follower-action`, `/like-action`, `/comment-action`, `/story-action`, `/like-comment-action`

Os corpos são iguais aos do Worker. A única diferença no retorno é que os dados da conta vêm na chave `boost` em vez de `worker`.

### 6. Teste

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/my-test` | Criptografa e descriptografa um texto com a `SECRET_ENCRYPTION`. Útil para validar a chave: retorna `{"encrypt", "decrypt"}` |

## Configurações dinâmicas (`/config`)

Cadastre estas chaves em `/config` (campo `name`) para ajustar o comportamento sem reiniciar a API. Uma configuração só tem efeito com `status: 1` e `value` preenchido.

| `name` | Exemplo de `value` | Efeito |
| --- | --- | --- |
| `allow-only-proxy` | `1` | Se `1`, nenhum login é feito sem proxy (a requisição falha quando não houver proxy disponível) |
| `change-proxy-action` | `1` | Se `1`, workers/boosts trocam para um proxy `worker-action`/`boost-action` depois do login |
| `change-proxy-action-error` | `1` | Se `1`, erros de ação também marcam o proxy para troca |
| `proxy-fixed` | `,1,` | Posições `extract,worker,boost`. Posição preenchida = a conta mantém o proxy fixo em vez de sortear outro após erros |
| `limit-proxy-few-minutes` | `5,3` | Desativa o proxy após N erros seguidos de "wait a few minutes"/429: 1º valor para extração, 2º para worker/boost |
| `disable-few-minutes` | `5,3,3` | Desativa a conta após N erros seguidos de "wait a few minutes"/429: profile, worker, boost |
| `disable-challenge-login` | `2` | Desativa o worker/boost após N *challenges* no login |
| `disable-challenge-action` | `3` | Desativa o worker/boost após N *challenges* durante ações |
| `which-proxy-type-to-use-after-create-worker` | `worker` | Valor gravado em `typeProxy` ao criar um worker com `isCreate: true` |
| `delay-random-upload-post` | `5,20` | Intervalo (em segundos) sorteado entre uploads de posts no `edit-instagram` |

Exemplo:

```bash
curl -X POST http://localhost:5011/api/config -H "Authorization: Bearer troque-por-um-token-forte" -H "Content-Type: application/json" -d '{"name": "allow-only-proxy", "title": "Allow only proxy", "description": "Never log in without a proxy", "type": "text", "value": "1"}'
```

## Tratamento automático de erros

A cada login ou ação, a API analisa a mensagem de erro do Instagram e atualiza a conta e o proxy usados:

| Erro do Instagram | O que a API faz |
| --- | --- |
| `429` / "Please wait a few minutes" | Incrementa `countFewMinutes` da conta e do proxy. Ao atingir o limite configurado, desativa |
| Erro de conexão com o proxy | Registra o erro no proxy e, se a conta não usar proxy fixo, sorteia outro na próxima vez |
| `challenge_required` / `checkpoint_required` | Workers/boosts: incrementa `countChallenge` e desativa ao atingir `disable-challenge-*`. Profiles: desativa |
| `login_required` (sessão expirada) | Limpa a sessão salva e faz um novo login com usuário e senha |
| Senha incorreta, conta desativada ou excluída, `feedback_required` | Desativa a conta (`status: 0`) e grava o motivo em `noteError` |
| Bloqueio temporário ("block will expire on AAAA-MM-DD") | Desativa e preenche `expireAt` com a data de liberação |

Para reativar contas ou proxies, use `PATCH /{modulo}/status` com `"status": 1` (ou `/boosts/active-by-social-id` para boosts). O campo `noteError` de cada registro mostra o último erro.

## Coleção do Insomnia

O arquivo [`_resources/Insomnia_2024-03-26.json`](_resources/Insomnia_2024-03-26.json) tem **todas as requisições da API** prontas, com exemplos de corpo.

1. No [Insomnia](https://insomnia.rest/), vá em **Import** e selecione o arquivo;
2. Em **Base Environment**, ajuste as variáveis:

```json
{
  "api": "http://localhost:5011/api",
  "token": "troque-por-um-token-forte"
}
```

3. Substitua os valores de exemplo (`my_worker_account`, `POST_CODE`, ids...) pelos seus.

## Autor

- [David Rodma](https://github.com/davidrodma/)
