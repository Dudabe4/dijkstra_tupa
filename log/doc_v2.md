# DOCUMENTAÇÃO DA SEGUNDA IMPLEMENTAÇÃO DO ALGORITMO DE DIJKSTRA PARA O MAPA DO GLV

## 1. Visão geral

A V.2 evolui a primeira implementação do algoritmo de Dijkstra utilizada
para representar o mapa físico das conexões do sistema GLV de um carro
de Formula SAE Elétrica.

Na V.1, o grafo era cadastrado diretamente no código Python e o custo
utilizado pelo Dijkstra era somente o comprimento físico das conexões. A
V.2 mantém esse critério de custo, mas modifica a estrutura do projeto
para separar os dados do mapa da lógica do algoritmo.

A principal mudança é a utilização de uma Google Sheets como fonte dos
dados de conexões. O Python lê a planilha pela Google Sheets API,
transforma as linhas em um grafo e então executa o Dijkstra.

O fluxo passa a ser:

``` text
Google Sheets
     ↓
google_sheets.py
     ↓
construir_grafo.py
     ↓
grafo
     ↓
dijkstra.py
     ↓
main.py
     ↓
resultado
```

A V.2 também inclui modularização, validações, tratamento de duplicações
e comparação entre o grafo manual da V.1 e o grafo construído a partir
da planilha.

------------------------------------------------------------------------

## 2. Objetivos da V.2

-   Separar os dados do mapa da lógica do algoritmo.
-   Manter as conexões em uma Google Sheets.
-   Ler automaticamente a planilha pelo Python.
-   Construir o grafo automaticamente.
-   Criar conexões inversas para conexões bidirecionais.
-   Evitar duplicações.
-   Detectar duplicações com comprimentos conflitantes.
-   Validar nós, pesos e simetria.
-   Modularizar o projeto.
-   Manter o Dijkstra independente da origem dos dados.
-   Comparar o novo grafo com o grafo manual.
-   Preparar a estrutura para futuras melhorias do critério de custo.

------------------------------------------------------------------------

## 3. Relação entre as versões

### V.1 --- protótipo inicial

A primeira versão validou:

-   representação do mapa como grafo;
-   utilização de listas de adjacência;
-   Dijkstra;
-   pesos correspondentes a comprimentos;
-   entrada de origem e destino pelo terminal;
-   reconstrução do caminho;
-   apresentação do resultado.

O grafo era cadastrado diretamente no código.

### V.2 --- estruturação e entrada de dados

A segunda versão acrescenta:

-   correção e conferência do grafo;
-   modularização;
-   validações;
-   Google Sheets API;
-   leitura das conexões pela planilha;
-   construção automática do grafo;
-   inversas automáticas;
-   tratamento de duplicações;
-   comparação manual × planilha;
-   integração do Dijkstra com o novo fluxo.

O custo continua sendo somente:

``` text
custo = comprimento físico
```

------------------------------------------------------------------------

## 4. Estrutura atual do projeto

``` text
dijkstra/
├── src/
│   ├── main.py
│   ├── grafo.py
│   ├── dijkstra.py
│   ├── validacao.py
│   ├── teste_grafo.py
│   ├── google_sheets.py
│   └── construir_grafo.py
├── credentials/
│   └── credentials.json
├── log/
├── lib/
├── install/
└── .gitignore
```

### `main.py`

Responsável pelo fluxo principal:

1.  ler a planilha;
2.  construir o grafo;
3.  obter os nós válidos;
4.  receber origem e destino;
5.  validar as entradas;
6.  executar Dijkstra;
7.  apresentar o resultado.

### `grafo.py`

Mantém o grafo manual e os dados de componentes por nó. O grafo manual é
utilizado como referência para validação e comparação.

### `dijkstra.py`

Contém o algoritmo de Dijkstra. Ele recebe um grafo pronto e não depende
da Google Sheets.

### `validacao.py`

Contém as verificações de consistência e testes básicos do grafo e do
Dijkstra.

### `teste_grafo.py`

Responsável pela conferência entre o grafo manual e o grafo construído a
partir da Google Sheets. O arquivo organiza as conexões e verifica:

-   conexões que existem no manual, mas não na planilha;
-   conexões que existem na planilha, mas não no manual;
-   diferenças de comprimento entre os dois grafos.

O teste confirmou 87 conexões físicas únicas em ambos os grafos, sem
conexões perdidas e sem diferenças de comprimento.

### `google_sheets.py`

Responsável pela autenticação e leitura dos dados da Google Sheets.

### `construir_grafo.py`

Converte as linhas da planilha em uma lista de adjacência utilizada pelo
Dijkstra.

------------------------------------------------------------------------

## 5. Separação entre dados e algoritmo

Um dos principais objetivos da V.2 é separar:

### Dados

-   quais nós existem;
-   quais conexões existem;
-   quais são os comprimentos;
-   quais conexões devem ser consideradas.

### Algoritmo

-   como encontrar o menor caminho.

Assim, alterar uma distância ou uma conexão na planilha não exige editar
`dijkstra.py`.

A arquitetura passa a ser:

``` text
dados → construção do grafo → algoritmo
```

em vez de manter os dados diretamente dentro da lógica principal.

------------------------------------------------------------------------

## 6. Google Sheets como fonte de dados

A aba de conexões possui a estrutura básica:

``` text
origem | destino | comprimento
```

Exemplo:

``` text
A1 | E1 | 402.81
E1 | I1 | 208.62
I1 | Y1 | 415.85
Y1 | K1 | 343.59
```

Cada linha representa uma conexão física.

O comprimento é informado em milímetros.

A planilha deve cadastrar cada conexão física uma vez. A conexão inversa
é criada automaticamente pelo Python quando a conexão é tratada como
bidirecional.

------------------------------------------------------------------------

## 7. Configuração da Google Sheets API

Para permitir que o Python leia a planilha, foi configurada uma conta de
serviço no Google Cloud.

O processo envolveu:

1.  criação do projeto;
2.  habilitação da Google Sheets API;
3.  criação da conta de serviço;
4.  criação da chave JSON;
5.  armazenamento das credenciais no projeto;
6.  compartilhamento da planilha com a conta de serviço.

O arquivo de credenciais utilizado é:

``` text
credentials/credentials.json
```

Esse arquivo contém informações privadas e não deve ser enviado ao
GitHub.

------------------------------------------------------------------------

## 8. Proteção das credenciais

O `.gitignore` deve conter:

``` gitignore
credentials/
token.json
__pycache__/
```

Assim, as credenciais não são adicionadas ao repositório.

A autenticação utilizada pela V.2 possui permissão de leitura da
planilha:

``` text
https://www.googleapis.com/auth/spreadsheets.readonly
```

------------------------------------------------------------------------

## 9. Leitura da planilha

A função `ler_planilha()` acessa a aba configurada e lê as colunas:

``` text
A:C
```

O resultado possui estrutura semelhante a:

``` python
[
    ["origem", "destino", "comprimento"],
    ["A1", "E1", "402.81"],
    ["E1", "I1", "208.62"],
    ["I1", "Y1", "415.85"],
    ["Y1", "K1", "343.59"]
]
```

O teste realizado confirmou que:

-   a autenticação funciona;
-   a planilha pode ser acessada;
-   os valores são recebidos pelo Python.

------------------------------------------------------------------------

## 10. Construção automática do grafo

O módulo `construir_grafo.py` transforma os dados da planilha em uma
estrutura de lista de adjacência.

Uma linha:

``` text
A1 | E1 | 402.81
```

gera:

``` python
"A1": [("E1", 402.81)]
"E1": [("A1", 402.81)]
```

O Dijkstra continua recebendo a mesma estrutura conceitual utilizada na
V.1.

A diferença é que o grafo é construído automaticamente.

------------------------------------------------------------------------

## 11. Criação automática das conexões inversas

Como a modelagem atual considera as conexões bidirecionais, uma única
linha da planilha:

``` text
A1 | E1 | 402.81
```

gera:

``` text
A1 → E1 = 402.81
E1 → A1 = 402.81
```

Não é necessário cadastrar as duas direções.

Essa regra reduz duplicações e diminui a possibilidade de esquecer uma
das direções.

A bidirecionalidade continua sendo uma hipótese de modelagem. Caso uma
conexão seja confirmada como unidirecional no sistema físico, essa regra
deverá ser alterada.

------------------------------------------------------------------------

## 12. Tratamento de duplicações

A V.2 identifica quando uma mesma conexão física aparece mais de uma
vez.

Exemplo:

``` text
A1 | E1 | 402.81
A1 | E1 | 402.81
```

ou:

``` text
A1 | E1 | 402.81
E1 | A1 | 402.81
```

As duas situações representam a mesma conexão física.

Quando o comprimento é igual, a duplicação é ignorada.

Regra:

``` text
mesma conexão + mesmo comprimento
→ ignora duplicação
```

------------------------------------------------------------------------

## 13. Duplicações com valores conflitantes

Uma situação diferente ocorre quando a mesma conexão possui comprimentos
diferentes:

``` text
A1 | E1 | 402.81
E1 | A1 | 405.00
```

Nesse caso, o programa não escolhe automaticamente um dos valores.

A construção do grafo gera erro informando que a mesma conexão possui
comprimentos conflitantes.

Regra:

``` text
mesma conexão + comprimento diferente
→ erro
```

Isso evita esconder possíveis erros do mapa físico.

------------------------------------------------------------------------

## 14. Conversão dos comprimentos

Os valores da planilha são convertidos para números:

``` python
comprimento = float(linha[2])
```

Isso é necessário para que o Dijkstra possa somar os pesos.

Por exemplo:

``` text
"402.81"
```

é convertido para:

``` text
402.81
```

como número.

Os pesos continuam sendo expressos em milímetros.

------------------------------------------------------------------------

## 15. Validação dos nós

Foi criada uma validação para verificar se todos os vizinhos de cada nó
realmente existem no grafo.

Exemplo de erro:

``` text
A1 → Z9
```

quando `Z9` não foi cadastrado.

A validação evita que erros de digitação ou cadastro permaneçam
escondidos.

------------------------------------------------------------------------

## 16. Validação dos pesos

Também foi criada uma validação para pesos negativos.

``` python
if comprimento < 0:
```

Comprimentos físicos negativos não são válidos e também violam a
condição necessária para o uso do Dijkstra.

Caso apareça um peso negativo, a validação informa o problema.

------------------------------------------------------------------------

## 17. Validação de simetria

Como as conexões atuais são consideradas bidirecionais, foi criada uma
validação para conferir se:

``` text
A1 → E1 = 402.81
```

possui também:

``` text
E1 → A1 = 402.81
```

A validação identifica:

-   conexão sem inversa;
-   inversa com comprimento diferente;
-   inconsistências no cadastro.

Essa verificação deve ser interpretada de acordo com a hipótese de
bidirecionalidade. Uma conexão realmente unidirecional não deve ser
alterada apenas para passar no teste.

------------------------------------------------------------------------

## 18. Testes do Dijkstra

A implementação atual possui testes básicos para garantir que a mudança
de arquitetura não quebrou o algoritmo.

São considerados casos como:

-   caminho entre dois nós;
-   origem igual ao destino;
-   existência de caminho;
-   execução do Dijkstra sobre o grafo manual.

O arquivo `validacao.py` reúne essas verificações. Atualmente, os testes
básicos incluem `A1 → A2` e `A1 → A1`.

Ainda falta ampliar esses testes para representar melhor diferentes
situações de caminho e confirmar de forma mais abrangente as distâncias
calculadas.

------------------------------------------------------------------------

## 19. Comparação do grafo manual com a planilha

Uma etapa fundamental foi comparar:

``` text
grafo manual da V.1
```

com:

``` text
grafo construído automaticamente pela planilha
```

O resultado da comparação foi:

``` text
Conexões no grafo manual:    87
Conexões na planilha:        87

OK: Os dois grafos são idênticos.
Nenhuma conexão foi perdida.
Nenhum comprimento está diferente.
```

Portanto, a migração preservou as conexões e os comprimentos utilizados
anteriormente.

------------------------------------------------------------------------

## 20. Quantidade de conexões

Foram identificadas:

``` text
87 conexões físicas únicas
```

Como o programa representa as conexões bidirecionais nas duas direções,
isso corresponde a:

``` text
174 entradas direcionadas
```

As 174 entradas não representam 174 conexões físicas diferentes. Cada
conexão física possui duas representações no grafo.

------------------------------------------------------------------------

## 21. Conexões ainda não confirmadas

Algumas conexões existentes nas observações do mapa permaneceram fora do
grafo por não estarem confirmadas.

Entre os exemplos estão:

``` text
B1 ↔ D1
D1 ↔ J1
H1 ↔ L1
I1 ↔ J1
K1 ↔ P1
N1 ↔ R1
S1 ↔ S3
R1 ↔ T1
M2 ↔ L2
U3 ↔ L2
```

Também existe a observação sobre `Y2`, que não está presente no
dicionário atual.

Essas conexões não foram adicionadas automaticamente. A confirmação deve
vir do mapa físico real.

------------------------------------------------------------------------

## 22. Integração do `main.py`

O fluxo do `main.py` passou a ser:

``` text
ler planilha
     ↓
construir grafo
     ↓
obter nós válidos
     ↓
receber origem
     ↓
receber destino
     ↓
validar
     ↓
executar Dijkstra
     ↓
mostrar resultado
```

Conceitualmente:

``` python
dados = ler_planilha()
grafo = construir_grafo(dados)

nos_validos = set(grafo.keys())

origem = input(...).strip().upper()
destino = input(...).strip().upper()

caminho, distancia = dijkstra(
    grafo,
    origem,
    destino
)
```

------------------------------------------------------------------------

## 23. Validação das entradas

As entradas continuam sendo normalizadas com:

``` python
.strip().upper()
```

Assim:

``` text
" a1 "
```

torna-se:

``` text
"A1"
```

Depois disso, o programa verifica:

``` python
origem in nos_validos
destino in nos_validos
```

Os nós válidos agora são obtidos diretamente do grafo construído a
partir da planilha.

------------------------------------------------------------------------

## 24. Separação das responsabilidades

A V.2 deixa cada etapa responsável por uma tarefa.

### `google_sheets.py`

``` text
Google Sheets → dados
```

### `construir_grafo.py`

``` text
dados → grafo
```

### `dijkstra.py`

``` text
grafo + origem + destino → caminho + distância
```

### `main.py`

``` text
coordena o fluxo
```

### `validacao.py`

``` text
verifica consistência
```

Essa separação facilita a manutenção e permite alterar uma etapa sem
precisar modificar todas as outras.

------------------------------------------------------------------------

## 25. Fluxo completo

``` text
                    GOOGLE SHEETS
                         │
                         ▼
                google_sheets.py
                         │
                         ▼
               dados das conexões
                         │
                         ▼
               construir_grafo.py
                         │
                         ▼
                       GRAFO
                         │
                         ▼
                    dijkstra.py
                         │
                         ▼
                caminho + distância
                         │
                         ▼
                      main.py
                         │
                         ▼
                    RESULTADO
```

As validações são executadas para conferir a consistência da estrutura.

------------------------------------------------------------------------

## 26. Critério de custo da V.2

O critério de otimização continua sendo:

``` text
custo = soma dos comprimentos das conexões
```

Por exemplo:

``` text
A → B = 100 mm
B → C = 200 mm
C → D = 150 mm
```

resulta em:

``` text
custo total = 100 + 200 + 150
            = 450 mm
```

O Dijkstra continua escolhendo o caminho cuja soma dos comprimentos seja
menor.

A quantidade de vezes que um nó foi utilizado ainda não influencia o
cálculo.

------------------------------------------------------------------------

## 27. O que a V.2 já consegue fazer

A V.2 já consegue:

-   ler conexões da Google Sheets;
-   construir o grafo automaticamente;
-   criar inversas;
-   converter comprimentos;
-   tratar duplicações;
-   detectar comprimentos conflitantes;
-   validar nós;
-   validar pesos;
-   validar simetria;
-   executar Dijkstra;
-   receber origem e destino;
-   normalizar entradas;
-   encontrar o menor caminho por distância;
-   apresentar o caminho;
-   apresentar o comprimento total;
-   comparar o grafo manual com o grafo da planilha.

------------------------------------------------------------------------

## 28. O que foi validado

A implementação foi testada em etapas:

### Google Sheets

Foi confirmado que o Python consegue ler:

``` text
origem
destino
comprimento
```

diretamente da planilha.

### Construção do grafo

Foi confirmado que as linhas são convertidas corretamente em conexões.

### Inversas

Foi confirmado que as conexões inversas são criadas automaticamente.

### Duplicações

Foi implementado tratamento para evitar conexões repetidas.

### Comparação

O grafo manual e o grafo da planilha apresentaram:

``` text
87 conexões físicas
```

sem perda ou alteração de comprimento.

### Dijkstra

Foi confirmado que o algoritmo continua funcionando sobre o grafo
construído automaticamente.

------------------------------------------------------------------------

## 29. Melhorias que ainda faltam

A estrutura principal já está funcionando, mas ainda existem melhorias
antes de considerar esta etapa completamente fechada.

### 29.1 Ampliar os testes do Dijkstra

Adicionar casos de teste com diferentes origens e destinos para
conferir:

- caminhos existentes;
- caminhos alternativos;
- distâncias calculadas;
- origem igual ao destino;
- situações sem caminho, quando aplicável.

O objetivo é testar o comportamento do algoritmo com mais de um caso
simples.

### 29.2 Melhorar a validação da entrada da planilha

A leitura atual deve ser reforçada para identificar dados inválidos
antes da construção do grafo, como:

- linha sem origem;
- linha sem destino;
- linha sem comprimento;
- comprimento que não pode ser convertido para `float`;
- valores vazios;
- registros incompletos.

Isso evita que um erro de preenchimento da planilha apareça somente mais
adiante durante o cálculo.

### 29.3 Separar claramente as funções dos testes

A organização dos arquivos deve permanecer:

```text
 teste_grafo.py
 → compara grafo manual × grafo da planilha

 validacao.py
 → verifica integridade do grafo e executa testes do Dijkstra
```

Assim, a comparação dos dados e a validação do funcionamento do
algoritmo ficam separadas.

### 29.4 Fazer um teste completo do fluxo atual

O fluxo completo deve ser testado de ponta a ponta:

```text
Google Sheets
     ↓
ler_planilha()
     ↓
construir_grafo()
     ↓
validações
     ↓
Dijkstra
     ↓
resultado
```

A ideia é confirmar que todas as etapas continuam funcionando juntas,
não somente de forma isolada.

### 29.5 Implementação do custo de utilização

- Definir e implementar o novo custo do caminho, considerando **distância + quantidade de passagens pelos nós**.
- Adaptar o Dijkstra para trabalhar com esse novo critério.
- Manter também o cálculo usando **somente distância**, para poder comparar os dois resultados.

### 29.6 Registro e contabilização dos caminhos

- Registrar o caminho escolhido para cada sinal.
- Contabilizar quantas vezes cada nó é utilizado pelos diferentes sinais.
- Usar essa quantidade como parte do custo nas próximas rotas.
- Testar a sequência de cálculo para garantir que a utilização acumulada esteja sendo considerada corretamente.

### 29.7 Teste do Dijkstra por distância

- Criar uma **aba intermediária na Google Sheets** para testar os caminhos usando somente distância.
- Conferir os resultados antes de adicionar o custo de utilização.
- Usar essa etapa como referência para comparar os caminhos antes e depois da nova lógica.

### 29.8 Geração da saída final

- Criar uma aba final de resultados na Google Sheets.
- Para cada sinal, apresentar:
  - sinal;
  - origem;
  - destino;
  - caminho considerando **distância + utilização**;
  - comprimento;
  - componente de origem;
  - componente de destino;
  - caminho considerando **somente distância**.
- Assim, será possível comparar diretamente o caminho escolhido pelos dois critérios.

------------------------------------------------------------------------

## 30. Limitações da V.2

A implementação atual ainda não resolve:

-   custo de utilização dos nós;
-   roteamento específico por tipo de sinal;
-   nós obrigatórios;
-   nós proibidos;
-   restrições elétricas;
-   restrições de segurança;
-   custos de conectores;
-   custos de emendas;
-   interferência;
-   manutenção;
-   visualização gráfica do caminho;
-   geração automática da planilha final.

Esses pontos dependem de definições futuras do projeto.

------------------------------------------------------------------------

## 31. Bidirecionalidade

A modelagem atual considera as conexões como bidirecionais.

Isso significa que:

``` text
A1 → E1
```

implica:

``` text
E1 → A1
```

Essa hipótese foi mantida para a V.2 porque corresponde à estrutura
atual do mapa.

Entretanto, ela ainda deve ser confirmada para todos os casos do sistema
real.

Se forem identificadas conexões que só podem ser percorridas em um
sentido, será necessário modificar a forma de construção do grafo.

------------------------------------------------------------------------

## 32. Dependência do mapa físico do T11

A qualidade do resultado depende diretamente dos dados físicos
utilizados.

O programa não determina sozinho quais conexões existem no carro.

As informações da planilha precisam representar o mapa real do T11.

Por isso, determinadas partes do projeto podem precisar aguardar a
finalização do mapa de sinais para que:

-   conexões;
-   distâncias;
-   caminhos;
-   componentes;
-   possibilidades de roteamento

estejam definidos.

------------------------------------------------------------------------

## 33. Por que a V.2 foi uma etapa necessária

A implementação da V.2 envolveu:

-   revisão do grafo;
-   conferência das conexões;
-   conferência dos comprimentos;
-   reorganização do código;
-   criação de módulos;
-   criação das validações;
-   configuração da Google Sheets API;
-   criação da conta de serviço;
-   configuração das credenciais;
-   leitura da planilha;
-   construção automática do grafo;
-   tratamento de duplicações;
-   comparação dos grafos;
-   integração do Dijkstra.

A etapa foi necessária para criar uma base confiável antes da mudança do
critério de custo.

------------------------------------------------------------------------

## 34. Estado final da V.2

Ao final da V.2, o sistema possui:

``` text
Google Sheets
      ↓
leitura automática
      ↓
construção automática do grafo
      ↓
validação
      ↓
Dijkstra
      ↓
caminho mínimo por distância
```

O projeto deixou de depender do cadastro manual do grafo para sua
execução normal.

As conexões podem ser atualizadas na planilha, e o programa pode
reconstruir o grafo a partir desses dados.

------------------------------------------------------------------------

## 35. Estado atual e critérios para fechar esta etapa

A estrutura principal da V.2 está funcionando:

-   a Google Sheets está configurada;
-   as credenciais estão funcionando;
-   a leitura da planilha está funcionando;
-   o grafo está sendo construído automaticamente;
-   as inversas estão sendo geradas;
-   duplicações estão sendo tratadas;
-   o grafo manual foi comparado com o grafo da planilha;
-   o Dijkstra está executando sobre o grafo gerado.

Ainda faltam alguns testes, melhorias de robustez e etapas de
implementação antes de considerar esta etapa completamente fechada:

-   ampliar os testes do Dijkstra;
-   reforçar a validação da entrada da planilha;
-   manter separados os testes de `teste_grafo.py` e `validacao.py`;
-   executar um teste completo do fluxo;
-   implementar o custo de utilização;
-   registrar e contabilizar os caminhos utilizados;
-   criar e preencher a aba de teste dos caminhos por distância;
-   criar a aba final de resultados.

------------------------------------------------------------------------

## 36. Resumo técnico da V.2

``` text
ENTRADA
Google Sheets
    │
    └── origem
    └── destino
    └── comprimento
           │
           ▼
CONSTRUÇÃO
construir_grafo.py
    │
    ├── normaliza conexões
    ├── converte pesos
    ├── cria inversas
    └── trata duplicações
           │
           ▼
VALIDAÇÃO
validacao.py
    │
    ├── nós
    ├── pesos
    ├── simetria
    └── testes
           │
           ▼
PROCESSAMENTO
dijkstra.py
    │
    ├── menor distância
    ├── predecessores
    └── reconstrução
           │
           ▼
SAÍDA
main.py
    │
    ├── caminho
    └── comprimento total
```

------------------------------------------------------------------------

## 37. Conclusão

A V.2 representa a evolução da primeira implementação de um protótipo
com grafo cadastrado diretamente no código para uma estrutura mais
organizada, modular e atualizável.

A principal mudança foi separar os dados do mapa da lógica do algoritmo.
As conexões passam a ser mantidas em uma Google Sheets, lidas pelo
Python e transformadas automaticamente no grafo utilizado pelo Dijkstra.

Também foram implementados mecanismos de validação, criação automática
das conexões inversas, tratamento de duplicações e comparação entre o
grafo manual e o grafo construído a partir da planilha.

A conferência realizada encontrou:

``` text
87 conexões físicas únicas no grafo manual
87 conexões físicas únicas na planilha

Nenhuma conexão perdida.
Nenhum comprimento diferente.
```

O projeto possui atualmente os seguintes módulos:

``` text
main.py
grafo.py
dijkstra.py
validacao.py
teste_grafo.py
google_sheets.py
construir_grafo.py
```

O `teste_grafo.py` ficou responsável pela comparação entre as duas
fontes do grafo, enquanto o `validacao.py` concentra as verificações de
integridade e os testes básicos do Dijkstra.

O critério de custo continua sendo somente o comprimento físico das
conexões. Portanto, a implementação atual encontra o caminho de menor
distância a partir dos dados fornecidos pela planilha.

Antes de considerar esta etapa completamente fechada, ainda devem ser
realizados os testes e melhorias de robustez descritos na seção
"Melhorias que ainda faltam", principalmente a ampliação dos testes do
Dijkstra, a validação dos dados de entrada da planilha e o teste
completo do fluxo.

A estrutura atual permite que o mapa seja atualizado na planilha e que o
grafo seja reconstruído sem alterar a lógica central do algoritmo.
