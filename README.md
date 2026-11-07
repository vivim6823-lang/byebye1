# 🍔 API da Lanchonete

**Desenvolvedora:** [Seu nome]  
**Instituição:** Senac  
**Curso:** Análise e Desenvolvimento de Sistemas  
**Projeto:** Desafio Prático — Django REST Framework

---

## 1. Apresentação

A API da Lanchonete é um projeto que foi desenvolvido utilizando Python, Django e Django REST Framework.

O objetivo desse projeto é criar um sistema para uma lanchonete, onde seja possivel cadastrar produtos, categorias e areas de entrega. Também é possivel consultar os produtos, editar informações e excluir cadastros.

Além da API, o projeto possui uma página web onde é possivel visualizar o cardápio da lanchonete. Também foi desenvolvido um painel administrativo para facilitar o gerenciamento dos dados.

Durante o desenvolvimento, pude aprender mais sobre como funciona uma API e como utilizar o Django para criar um sistema.

---

## 2. Tecnologias utilizadas

| Tecnologia | Para que foi utilizada |
|---|---|
| **Python** | Linguagem utilizada para desenvolver o projeto. |
| **Django** | Foi utilizado para organizar o projeto, criar as páginas, configurar as rotas e trabalhar com o banco de dados. |
| **Django REST Framework** | Utilizado para criar a API e permitir o cadastro, consulta, edição e exclusão de informações. |
| **SQLite** | Banco de dados utilizado para guardar as informações do sistema. |
| **HTML** | Utilizado para criar a estrutura da página do cardápio. |
| **CSS** | Utilizado para deixar a página mais bonita e organizada, com cores e estilos. |
| **Requests** | Utilizado para fazer requisições para a API do IBGE. |
| **drf-spectacular** | Utilizado para gerar a documentação da API e disponibilizar o Swagger. |

---

## 3. Como rodar o projeto

Para executar o projeto é necessario ter o Python e o Git instalados no computador.

### 1. Clonar o repositório

```bash
git clone URL_DO_SEU_REPOSITORIO
```

Depois entre na pasta:

```bash
cd NOME_DA_PASTA
```

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

### 3. Ativar o ambiente virtual

No Windows:

```bash
.venv\Scripts\activate
```

No Linux:

```bash
source .venv/bin/activate
```

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Aplicar as migrações

```bash
python manage.py migrate
```

### 6. Criar um superusuário

```bash
python manage.py createsuperuser
```

### 7. Iniciar o servidor

```bash
python manage.py runserver
```

Depois disso, o projeto estará rodando localmente.

### Endereços do projeto

| Página | Endereço |
|---|---|
| Cardápio | http://127.0.0.1:8000/ |
| Painel Admin | http://127.0.0.1:8000/admin/ |
| API | http://127.0.0.1:8000/api/ |
| Swagger | http://127.0.0.1:8000/api/docs/ |
| Schema | http://127.0.0.1:8000/api/schema/ |

---

## 4. Explicação dos principais arquivos

### settings.py

Esse arquivo é responsavel pelas configurações principais do projeto. Nele ficam os aplicativos instalados, o banco de dados SQLite, as configurações de autenticação, permissões, paginação e documentação da API.

Também foi configurado para permitir que qualquer pessoa consulte os dados, mas para fazer alterações é necessario estar autenticado.

### urls.py

Esse arquivo serve para organizar os caminhos do projeto.

Ele direciona o endereço principal para a página do cardápio, também permite acessar o painel administrativo, a API, o login por token e a documentação Swagger.

As rotas da API utilizam o DefaultRouter, que ajuda a criar os caminhos de acesso para categorias, produtos e áreas de entrega.

### models.py

Nesse arquivo ficam os models, que representam as informações que serão guardadas no banco de dados.

Foram criados três models:

- **Categoria:** guarda o nome e a descrição das categorias.
- **Produto:** guarda o nome, preço, disponibilidade e categoria do produto.
- **AreaEntrega:** guarda o municipio, o código do IBGE e a taxa de entrega.

Também foram criadas algumas regras, como não permitir preços negativos e não repetir o código IBGE.

### serializers.py

Os serializers são responsaveis por transformar os dados em JSON para que a API consiga enviar e receber informações.

Também fazem algumas validações. Por exemplo, no cadastro de produtos não é permitido colocar um preço negativo.

No cadastro de áreas de entrega, o sistema consulta o IBGE para verificar se o código do municipio existe.

### views.py

Nesse arquivo ficam as funções e classes que controlam o funcionamento das páginas e da API.

Ele permite realizar as operações de cadastro, consulta, edição e exclusão. Também possui a busca e o filtro de produtos, além da consulta de municipios pelo IBGE.

### admin.py

Esse arquivo configura o painel administrativo do Django.

Nele é possivel gerenciar os produtos, categorias e áreas de entrega. Também foram adicionados filtros, pesquisa pelo nome dos produtos e uma opção para marcar vários produtos como indisponiveis.

### tests.py

Esse arquivo contém os testes automatizados do projeto.

Os testes servem para verificar se as funcionalidades estão funcionando corretamente, como os cadastros, validações, permissões, filtros, painel administrativo e integração com o IBGE.

---

## 5. Conceitos utilizados

**O que é uma API REST?**

É uma forma de fazer sistemas diferentes se comunicarem. Por exemplo, um aplicativo pode utilizar uma API para buscar os produtos de uma lanchonete.

**O que é um Model?**

É uma estrutura que representa os dados que serão salvos no banco de dados. No nosso projeto temos Categoria, Produto e AreaEntrega.

**O que é um Serializer?**

É o responsável por transformar os dados em JSON e também verificar se as informações recebidas estão corretas antes de salvar.

**O que é um ViewSet?**

É uma classe que organiza as ações da API, como cadastrar, listar, editar e excluir informações.

**O que é um Router?**

É utilizado para criar e organizar automaticamente as rotas da API, facilitando o acesso aos ViewSets.

**O que é CRUD?**

CRUD significa Create, Read, Update e Delete. São as quatro operações principais de um sistema: criar, consultar, atualizar e excluir informações.

**O que é JSON?**

É um formato utilizado para organizar e enviar informações entre sistemas. Ele utiliza chaves e valores para representar os dados.

**O que é autenticação por token?**

É uma forma de verificar se o usuário tem autorização para realizar determinadas ações. O usuário recebe um token e utiliza ele nas requisições que precisam de autenticação.

**Qual a diferença entre GET, POST, PUT, PATCH e DELETE?**

- GET: utilizado para consultar informações.
- POST: utilizado para cadastrar informações.
- PUT: utilizado para atualizar um registro.
- PATCH: utilizado para atualizar apenas algumas informações.
- DELETE: utilizado para excluir um registro.

---

## 6. Endpoints da API

Os endpoints são os caminhos utilizados para acessar as funcionalidades da API.

| Endpoint | Método | Função |
|---|---|---|
| `/api/categorias/` | GET | Listar categorias |
| `/api/categorias/` | POST | Cadastrar categoria |
| `/api/categorias/{id}/` | GET | Consultar uma categoria |
| `/api/categorias/{id}/` | PUT/PATCH | Editar categoria |
| `/api/categorias/{id}/` | DELETE | Excluir categoria |
| `/api/categorias/{id}/produtos/` | GET | Mostrar produtos de uma categoria |
| `/api/produtos/` | GET | Listar produtos |
| `/api/produtos/` | POST | Cadastrar produto |
| `/api/produtos/{id}/` | GET | Consultar produto |
| `/api/produtos/{id}/` | PUT/PATCH | Editar produto |
| `/api/produtos/{id}/` | DELETE | Excluir produto |
| `/api/areas-entrega/` | GET | Listar áreas de entrega |
| `/api/areas-entrega/` | POST | Cadastrar área de entrega |
| `/api/municipios/?uf=PE` | GET | Consultar municipios pelo IBGE |

### Filtros e pesquisas

Para mostrar apenas os produtos disponiveis:

```text
/api/produtos/?disponivel=true
```

Para mostrar os produtos indisponiveis:

```text
/api/produtos/?disponivel=false
```

Para pesquisar um produto pelo nome:

```text
/api/produtos/?search=bacon
```

Também foi adicionada a paginação, que mostra 10 itens por página.

### Exemplo de cadastro de categoria

```json
{
  "nome": "Lanches",
  "descricao": "Lanches da lanchonete"
}
```

### Exemplo de cadastro de produto

```json
{
  "nome": "Hambúrguer",
  "preco": "25.00",
  "disponivel": true,
  "categoria": 1
}
```

O número da categoria precisa ser de uma categoria que já esteja cadastrada no banco de dados.

### Autenticação

Para conseguir um token, é necessario acessar:

```text
/api/token/
```

Nas requisições que precisam de autenticação, o token deve ser enviado no cabeçalho:

```text
Authorization: Token SEU_TOKEN
```

---

## 7. Django Admin

O Django Admin é o painel administrativo do projeto. Ele permite organizar e gerenciar as informações sem precisar fazer tudo diretamente pelo código.

Para acessar, basta entrar no endereço:

```text
http://127.0.0.1:8000/admin/
```

É necessario utilizar o usuário e a senha criados pelo comando `createsuperuser`.

No painel é possivel:

- Cadastrar e editar categorias.
- Cadastrar e editar produtos.
- Gerenciar as áreas de entrega.
- Filtrar produtos por categoria e disponibilidade.
- Pesquisar produtos pelo nome.
- Alterar a disponibilidade dos produtos diretamente na listagem.
- Editar produtos dentro da tela de categorias.
- Marcar vários produtos como indisponiveis de uma vez.

### Prints do painel

Coloque aqui as imagens do seu painel administrativo:

![Painel administrativo](docs/img/admin.png)

![Categorias](docs/img/categorias.png)

![Produtos](docs/img/produtos.png)

---

## 8. Prints do projeto

Nessa parte devem ser colocadas imagens mostrando o funcionamento do projeto.

Algumas imagens que podem ser adicionadas:

- Página inicial do cardápio.
- Lista de categorias.
- Lista de produtos.
- Cadastro de produtos.
- Filtro de disponibilidade.
- Documentação Swagger.
- Consulta de municipios pelo IBGE.
- Painel administrativo.

As imagens podem ficar organizadas dentro da pasta `docs/img/`.

Exemplo:

![Cardápio](docs/img/cardapio.png)

![Swagger](docs/img/swagger.png)

![Consulta de municípios](docs/img/municipios.png)

---

## 9. Dificuldades e aprendizados

Durante o desenvolvimento do projeto tive algumas dificuldades, principalmente para entender como as partes do Django funcionam juntas.

No começo foi um pouco complicado entender a diferença entre models, serializers e views, mas com o desenvolvimento fui conseguindo compreender melhor a função de cada um.

Também aprendi mais sobre como criar rotas, fazer validações, trabalhar com o banco de dados e testar as funcionalidades da API.

Uma parte que achei interessante foi a integração com o IBGE, porque foi possivel utilizar informações de outro serviço dentro do nosso próprio projeto.

No geral, o projeto me ajudou a praticar os conteúdos estudados e entender melhor como funciona o desenvolvimento de uma API.

---

## 10. Perguntas-chave

### 1. O que é uma API e por que ela é útil para a lanchonete?

Uma API é uma forma de permitir que sistemas diferentes se comuniquem. Ela é útil para a lanchonete porque permite que outros sistemas consultem os produtos, categorias e informações de entrega sem precisar acessar diretamente o banco de dados.

### 2. O que significa REST? Cite duas características.

REST é um estilo utilizado para organizar APIs. Duas características são o uso dos métodos HTTP, como GET e POST, e a utilização de URLs para acessar os recursos do sistema.

### 3. Qual a diferença entre Django e Django REST Framework?

Django é um framework utilizado para desenvolver aplicações web. Já o Django REST Framework é uma ferramenta que funciona junto com o Django e facilita a criação de APIs, permitindo trabalhar com serializers, viewsets e autenticação.

### 4. O que é um ambiente virtual e por que utilizá-lo?

É um ambiente separado onde ficam instaladas as bibliotecas utilizadas no projeto. Ele é importante porque evita misturar as dependências de projetos diferentes.

### 5. O que é um Model? O que acontece com makemigrations e migrate?

Model é uma classe que representa os dados que serão armazenados no banco de dados.

O `makemigrations` identifica as mudanças feitas nos models e cria os arquivos de migração. O `migrate` aplica essas mudanças no banco de dados.

### 6. Para que serve o ForeignKey e o related_name?

O ForeignKey serve para criar uma relação entre dois models. No nosso projeto, ele relaciona um produto com uma categoria.

O related_name define um nome para acessar os objetos relacionados. No nosso caso, podemos utilizar `categoria.produtos` para acessar os produtos de uma categoria.

### 7. Qual on_delete foi escolhido? O que acontece quando uma categoria é excluída?

Foi escolhido o `PROTECT`. Ele impede que uma categoria seja excluída enquanto ainda existirem produtos relacionados a ela. Assim evitamos perder a relação entre os produtos e suas categorias.

### 8. O que é um Serializer?

É responsável por transformar os dados do sistema em JSON e também validar as informações que chegam pela API antes de salvar no banco de dados.

### 9. Qual a diferença entre serializar e desserializar?

Serializar é transformar os dados do sistema em um formato que pode ser enviado pela API, como JSON.

Desserializar é receber os dados enviados pelo usuário e transformar essas informações para que o sistema consiga validar e utilizar.

### 10. O que é JSON?

JSON é um formato utilizado para organizar e transmitir informações entre sistemas. Ele organiza os dados através de chaves e valores.

### 11. O que é um ViewSet? Quais ações o ModelViewSet disponibiliza?

ViewSet é uma classe que organiza as ações de uma API. O ModelViewSet disponibiliza ações como listar, consultar, cadastrar, atualizar e excluir registros.

### 12. O que o Router faz?

O Router cria automaticamente as rotas necessárias para acessar as funcionalidades dos ViewSets. Isso facilita a organização da API e evita escrever todas as URLs manualmente.

### 13. Explique GET, POST, PUT, PATCH e DELETE.

- GET serve para consultar informações.
- POST serve para cadastrar novos registros.
- PUT serve para atualizar um registro.
- PATCH serve para atualizar apenas alguns campos.
- DELETE serve para excluir um registro.

### 14. O que significam os códigos HTTP 200, 201, 204, 400 e 404?

- **200:** significa que a requisição foi realizada com sucesso.
- **201:** significa que um novo registro foi criado.
- **204:** significa que a operação deu certo, mas não existe conteúdo para retornar.
- **400:** significa que os dados enviados estão incorretos ou são inválidos.
- **404:** significa que o conteúdo solicitado não foi encontrado.

### 15. Onde foi colocada a validação do preço?

A validação foi colocada no serializer de Produto, utilizando o método `validate_preco`. Ele verifica o valor recebido e impede que um preço negativo seja cadastrado.

### 16. Qual a diferença entre Django Admin e API?

O Django Admin é um painel visual que permite administrar os dados do sistema. Já a API permite que outros sistemas acessem essas informações através de requisições.

### 17. Um produto cadastrado pelo Admin aparece na API? Por quê?

Sim, porque tanto o Admin quanto a API utilizam o mesmo banco de dados. Então, quando um produto é cadastrado pelo painel, ele também fica disponível para consulta na API.

### 18. Para que servem list_display, list_filter e search_fields?

- `list_display` define quais informações aparecem na listagem do painel.
- `list_filter` permite filtrar os registros.
- `search_fields` permite pesquisar informações através de determinados campos.

### 19. Por que venv e db.sqlite3 não devem ir para o GitHub?

A pasta venv possui as bibliotecas instaladas no ambiente virtual e pode ocupar bastante espaço. Não é necessario enviar ela porque outra pessoa pode instalar as dependências pelo requirements.txt.

O arquivo db.sqlite3 contém o banco de dados local do projeto. Por isso, nesse projeto ele foi colocado no .gitignore para não ser enviado junto com o código.

### 20. Como um aplicativo de celular utilizaria essa API?

Um aplicativo poderia utilizar a API para mostrar os produtos, categorias e preços da lanchonete. Ele faria requisições para os endpoints e receberia as informações em JSON. Assim, o aplicativo conseguiria mostrar os dados para os usuários sem precisar acessar diretamente o banco de dados.

---

## 11. Integração com o IBGE

### Objetivo

Foi criada uma integração com a API do IBGE para consultar os municipios de um estado e verificar os códigos municipais utilizados no cadastro das áreas de entrega.

### API utilizada

```text
https://servicodados.ibge.gov.br/api/v1/localidades/estados/{UF}/municipios
```

### Como testar

Para consultar os municipios de Pernambuco:

```text
http://127.0.0.1:8000/api/municipios/?uf=PE
```

Para testar uma UF inválida:

```text
http://127.0.0.1:8000/api/municipios/?uf=XX
```

### Funcionalidades implementadas

- Consulta de municipios pelo estado.
- Retorno do nome e código IBGE dos municipios.
- Exibição da quantidade de municipios encontrados.
- Verificação de UF ausente ou inválida.
- Tratamento de erros quando o IBGE não responde.
- Utilização de timeout.
- Validação dos códigos IBGE no cadastro de áreas de entrega.

### Perguntas do extra

**E1. Qual a diferença entre sua API fornecer dados e consumir dados de outra API?**

Quando nossa API fornece dados, ela disponibiliza informações do próprio projeto para outros sistemas. Quando ela consome outra API, ela busca informações em um serviço externo.

No nosso projeto, fornecemos os dados da lanchonete e consumimos os dados do IBGE para consultar os municipios.

**E2. Por que é importante utilizar timeout ao chamar uma API externa?**

O timeout serve para definir um tempo limite para esperar a resposta de uma API. Isso é importante porque o serviço externo pode demorar para responder ou até ficar fora do ar. Assim, evitamos que nosso sistema fique esperando por muito tempo.

**E3. Por que transformar a resposta do IBGE antes de repassá-la ao cliente?**

Porque o IBGE pode retornar várias informações que não precisamos utilizar. Então transformamos a resposta para mostrar somente os dados importantes para nosso projeto, como o nome e o código do municipio.

**E4. O que acontece se o IBGE estiver fora do ar? Por que utilizar HTTP 503?**

Se o IBGE estiver fora do ar, nosso sistema não vai conseguir consultar os municipios naquele momento.

O código HTTP 503 indica que o serviço está temporariamente indisponível. Assim, quem estiver utilizando a API consegue entender que o problema é uma indisponibilidade temporária e pode tentar novamente depois.

### Prints da integração

Adicionar imagens mostrando:

- Código da integração com o IBGE.
- Consulta de uma UF válida.
- Consulta de uma UF inválida.
- Cadastro de áreas de entrega no Admin.
- Validação de um código IBGE inexistente.

---

## Considerações finais

Esse projeto foi uma oportunidade de colocar em prática os conhecimentos que estou aprendendo no curso de Análise e Desenvolvimento de Sistemas.

Durante o desenvolvimento consegui aprender mais sobre Python, Django, criação de APIs, banco de dados, validações e testes.

Também consegui entender melhor como funciona a comunicação entre sistemas através de uma API e como utilizar informações de serviços externos, como o IBGE.

Sei que ainda tenho muito para aprender, mas o projeto me ajudou a ter mais contato com a programação e entender melhor como funciona o desenvolvimento de um sistema.

---

**Projeto desenvolvido para o curso de Análise e Desenvolvimento de Sistemas — Senac.**