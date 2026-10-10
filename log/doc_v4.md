# DOCUMENTAÇÃO DA VERSÃO 4 — ROTEAMENTO DO CHICOTE GLV DO T11

## 1. Visão geral

A V.4 dá continuidade ao projeto de roteamento do chicote de baixa tensão (GLV/LV) do carro T11 da Formula SAE Elétrica. O sistema representa os pontos do mapa como nós de um grafo, as conexões físicas como arestas e os comprimentos como pesos físicos. O algoritmo de Dijkstra encontra caminhos de menor custo segundo as regras de roteamento configuradas.

A evolução da V.4 não se limita ao algoritmo. O projeto foi reorganizado em pastas com responsabilidades mais específicas, a leitura de dados da Google Sheets foi dividida entre conexões/configurações e sinais, foi separado o processamento de roteamento dos sinais, foi criada uma pasta de testes e foi acrescentado um script de execução. A pasta `configs/` também concentra a configuração do algoritmo e os recursos de apresentação do terminal.

A V.4 preserva as decisões centrais da V.3:
- dados físicos separados do algoritmo;
- parâmetros de roteamento configuráveis;
- fator de prioridade do caminho principal;
- penalização pela utilização acumulada dos nós;
- penalizações direcionais de entrada do hoop;
- custo de decisão separado da distância física.

Além disso, a aplicação passa a organizar o fluxo de uso em roteamento manual e processamento automático de sinais, com geração de resultados destinados à planilha.

Esta documentação descreve a estrutura informada para a V.4 e o comportamento discutido ao longo da implementação. Quando a árvore de arquivos permite identificar a existência de um módulo, mas não confirma seu conteúdo interno, a responsabilidade é descrita como função esperada e indicada para conferência no código.

------------------------------------------------------------------------

## 2. Objetivos da V.4

Os objetivos desta etapa são:

- preservar o Dijkstra e as regras de custo da V.3;
- separar melhor os arquivos por responsabilidade;
- separar a leitura das conexões e configurações da leitura dos sinais;
- concentrar as configurações do algoritmo em `configs/`;
- concentrar recursos de terminal em `configs/terminal.py`;
- separar o processamento automático dos sinais do fluxo principal;
- manter `main.py` como coordenador da aplicação;
- oferecer roteamento manual entre origem e destino;
- permitir um nó intermediário opcional em consultas manuais;
- processar sinais cadastrados na Google Sheets em lote;
- organizar os resultados para gravação na aba `Resultados`;
- executar validações estruturais antes de permitir o roteamento;
- criar testes separados para configuração, grafo, integração com sinais e processamento de rotas;
- facilitar a execução por meio de `executar.sh`;
- manter documentação versionada em `log/doc_v1.md`, `log/doc_v2.md` e `log/doc_v3.md`;
- deixar explícitas as diferenças entre validação estrutural do grafo e validação física/elétrica do chicote.

------------------------------------------------------------------------

## 3. Evolução entre as versões

### V.1 — protótipo inicial

A V.1 validou a representação do mapa como grafo, a lista de adjacência, o Dijkstra básico, a entrada de origem e destino no terminal e a reconstrução do caminho. O grafo era cadastrado diretamente no código e o peso correspondia ao comprimento físico da conexão.

### V.2 — dados externos e construção automática

A V.2 separou os dados do mapa da lógica do algoritmo. A Google Sheets passou a ser a fonte das conexões; o grafo era construído automaticamente, as conexões inversas eram geradas quando a hipótese bidirecional se aplicava e foram organizadas validações para nós, pesos e simetria. Também foi comparado o grafo manual com o grafo vindo da planilha.

### V.3 — custo configurável e utilização

A V.3 acrescentou o fator do caminho principal, a penalização por utilização acumulada dos nós e a penalização direcional de entrada do hoop. O custo passou a representar uma métrica de decisão, enquanto a distância física continuou sendo calculada com os comprimentos originais.

### V.4 — organização do projeto e processamento de sinais

A V.4 avança em duas frentes.

**Organização do código:**
- criação/uso de `configs/` para configuração e terminal;
- separação da leitura de conexões/configurações e da leitura de sinais;
- módulo dedicado ao roteamento dos sinais;
- pasta `testes/` com testes por responsabilidade;
- script `executar.sh`;
- documentação das versões anteriores na pasta `log/`.

**Fluxo da aplicação:**
- menu com modo manual e modo automático;
- intermediário opcional no roteamento manual;
- validações reunidas antes de continuar;
- processamento em lote dos sinais;
- preparação de uma tabela de resultados e gravação na planilha;
- mensagens de terminal mais organizadas.

A organização não muda o objetivo matemático do Dijkstra. Ela torna o sistema mais modular, testável e preparado para evoluir.

------------------------------------------------------------------------

## 4. Estrutura de pastas da V.4

A árvore informada para a V.4 é:

```text
.
├── configs
│   ├── configs.py
│   ├── __init__.py
│   ├── __pycache__/
│   └── terminal.py
├── credentials
│   └── credentials.json
├── executar.sh
├── log
│   ├── doc_v1.md
│   ├── doc_v2.md
│   └── doc_v3.md
├── README.md
├── src
│   ├── construir_grafo.py
│   ├── dijkstra.py
│   ├── google_sheets_nodes.py
│   ├── google_sheets_sinais.py
│   ├── grafo.py
│   ├── __init__.py
│   ├── main.py
│   ├── __pycache__/
│   ├── roteamento_sinais.py
│   └── validacao.py
└── testes
    ├── teste_configs.py
    ├── teste_google_sheets_sinais.py
    ├── teste_grafo.py
    └── teste_roteamento_sinais.py
```

Os diretórios `__pycache__/` e os arquivos `.pyc` são artefatos gerados pelo Python. Eles não são módulos-fonte nem parte da arquitetura lógica do sistema. A árvore acima foi organizada para mostrar onde aparecem, mas a documentação e o controle de versão devem se concentrar nos arquivos `.py`, `.md` e no script de execução.

A árvore também mostra que não existe mais um único arquivo chamado `google_sheets.py` na pasta `src/`: a integração foi dividida entre `google_sheets_nodes.py` e `google_sheets_sinais.py`. Da mesma forma, as configurações aparecem sob `configs/`, em vez de estarem representadas apenas por um `configs.py` diretamente em `src/`.

------------------------------------------------------------------------

## 5. Visão geral da arquitetura

A arquitetura lógica pode ser entendida como cinco grupos.

### 5.1. Entrada e persistência de dados

- `src/google_sheets_nodes.py`: módulo dedicado à leitura de dados do mapa e/ou das configurações associadas aos nós e conexões. O contrato exato de retorno deve ser confirmado no código.
- `src/google_sheets_sinais.py`: módulo dedicado à leitura dos sinais da planilha e, conforme a implementação, à escrita dos resultados. Deve-se conferir no arquivo se leitura e escrita estão ambas implementadas nele ou se a escrita é delegada.
- `credentials/credentials.json`: credenciais para autenticação com o serviço Google; é um arquivo sensível, não documentação pública.

### 5.2. Construção e representação do grafo

- `src/grafo.py`: contém a representação de referência do grafo manual e/ou dados auxiliares do mapa.
- `src/construir_grafo.py`: transforma registros de conexões em lista de adjacência, tratando conexões inversas e duplicações conforme as regras adotadas.

### 5.3. Algoritmo e regras

- `src/dijkstra.py`: implementa a busca de caminho mínimo por custo.
- `configs/configs.py`: concentra a interpretação/organização das configurações de roteamento.
- `src/validacao.py`: verifica consistência estrutural do grafo antes do cálculo.

### 5.4. Aplicação e sinais

- `src/roteamento_sinais.py`: separa o processamento das rotas associadas aos sinais da interação do menu.
- `src/main.py`: coordena carregamento, validação, menu e encaminhamento para o modo manual ou automático.

### 5.5. Apresentação, execução e testes

- `configs/terminal.py`: concentra recursos de apresentação do terminal, como cores, estilos ou funções de mensagem, de acordo com a implementação do módulo.
- `executar.sh`: ponto de entrada por shell para iniciar a aplicação; o comando exato deve ser confirmado lendo o script.
- `testes/`: contém os testes divididos por responsabilidade.
- `README.md`: instruções de uso e apresentação rápida do projeto.
- `log/doc_v1.md`, `log/doc_v2.md` e `log/doc_v3.md`: registro das documentações das versões anteriores.

------------------------------------------------------------------------

## 6. Por que a organização foi alterada

Na V.3, a estrutura documentada era mais concentrada em `src/` e possuía um único módulo `google_sheets.py`. A evolução exigiu tratar dois conjuntos de dados diferentes: o mapa/configuração do grafo e os sinais que precisam ser roteados.

Separar esses módulos evita que toda a integração com a planilha fique em um único arquivo. Também facilita testar a leitura de sinais sem precisar testar ao mesmo tempo a construção do grafo, e permite testar o processamento de rotas com dados preparados.

A pasta `configs/` reúne recursos transversais que não são o próprio algoritmo:
- `configs.py` trata as configurações;
- `terminal.py` trata a apresentação no terminal.

A pasta `testes/` reúne testes fora do código de execução normal. Isso reduz a mistura entre lógica da aplicação e verificações usadas durante o desenvolvimento.

O script `executar.sh` cria um ponto de entrada fácil de repetir, desde que seja executado no ambiente correto e tenha permissões adequadas.

------------------------------------------------------------------------

## 7. Responsabilidade de `configs/configs.py`

O módulo `configs/configs.py` é o local da V.4 destinado à configuração do algoritmo. Ele substitui a localização anterior documentada para `configs.py`, que aparecia junto aos módulos de `src/`.

A configuração do roteamento pode incluir:
- fator do caminho principal;
- penalização por utilização;
- penalização de entrada do hoop;
- sequência de nós do caminho principal;
- lista de arestas direcionadas penalizadas.

Na V.3, os valores históricos de teste eram:

```text
fator caminho principal = 0,2
penalização por utilização = 100
penalização entrada hoop = 5000
```

Esses valores são referências históricas, não garantia de que a Google Sheets esteja atualmente com os mesmos números. A fonte efetiva é a planilha e a conversão realizada pelo módulo de configurações.

A configuração deve transformar os valores lidos em tipos consistentes, por exemplo, números para parâmetros numéricos e estruturas de sequência para caminhos e arestas. O nome da classe, os nomes dos atributos e as validações exatas precisam seguir o código real; não devem ser presumidos apenas a partir do nome do arquivo.

### Por que separar configuração do algoritmo?

O Dijkstra não deve precisar conhecer a API da Google Sheets. Ele deve receber o grafo e os parâmetros já preparados. Assim, é possível mudar parâmetros ou a origem dos dados sem reescrever o algoritmo de busca.

------------------------------------------------------------------------

## 8. Responsabilidade de `configs/terminal.py`

A árvore da V.4 inclui `configs/terminal.py`, que separa a apresentação do terminal da lógica de roteamento.

Esse módulo é o local adequado para concentrar, conforme o código implementado:
- códigos ANSI de cores;
- constantes para estilos de mensagens;
- função para restaurar a formatação;
- helpers para títulos, informações, avisos, sucessos e erros.

A existência do arquivo confirma a separação estrutural, mas os nomes exatos das constantes e funções precisam ser lidos diretamente no módulo. Não se deve importar nomes que não existam nele.

A apresentação colorida pode distinguir, por exemplo:
- títulos e divisórias;
- informações de carregamento;
- sucesso da validação;
- avisos de entrada;
- erros e exceções;
- custo e distância apresentados ao usuário.

As cores não devem alterar dados, custos, caminhos ou decisões do algoritmo. O programa precisa continuar inteligível mesmo em um terminal que não renderize cores ANSI.

### Relação com `main.py`

O objetivo da separação é que `main.py` use os recursos de terminal, em vez de duplicar sequências de cores por todo o código. A forma concreta de importação deve ser confirmada no código atual.

------------------------------------------------------------------------

## 9. Responsabilidade de `src/google_sheets_nodes.py`

Este módulo separa a integração relacionada ao mapa físico — nós, conexões e os dados necessários à construção do grafo — do módulo dedicado aos sinais.

Na arquitetura anterior, `google_sheets.py` fazia a leitura das configurações e das conexões físicas. Na V.4, o nome `google_sheets_nodes.py` indica a especialização da leitura associada ao grafo. A função exata que retorna as conexões e a forma como as configurações são obtidas devem ser conferidas no arquivo atual.

A leitura do mapa precisa fornecer dados suficientes para que `construir_grafo.py` crie a lista de adjacência. Em termos conceituais, um registro de conexão possui:

```text
origem | destino | comprimento
```

Exemplo ilustrativo:

```text
A1 | E1 | 402.81
E1 | I1 | 208.62
```

O comprimento é tratado como medida física, historicamente em milímetros. A planilha deve ser a fonte atualizada do mapa; dados de exemplo não substituem a conferência dos registros reais.

A autenticação utiliza o arquivo em `credentials/credentials.json`, conforme o caminho configurado no código. O módulo deve tratar erros de acesso e dados incompletos de modo que a aplicação não continue como se tivesse carregado o mapa completo.

------------------------------------------------------------------------

## 10. Responsabilidade de `src/google_sheets_sinais.py`

Este módulo separa a integração com a planilha que contém os sinais a serem roteados.

O processamento automático precisa identificar, para cada sinal, os dados necessários para determinar uma rota, como o sinal e os nós de origem/destino conforme o esquema usado no projeto. A estrutura exata das colunas não deve ser inferida apenas pelo nome do arquivo; deve ser documentada a partir do código e da planilha atual.

O módulo pode fornecer funções para:
- ler os registros da aba de sinais;
- interpretar ou normalizar valores vindos da planilha;
- escrever os resultados na aba de saída, se essa responsabilidade estiver implementada nele.

É necessário conferir qual função realiza a escrita e se a aba de saída é chamada `Resultados`. O fluxo discutido para a V.4 prevê gravar uma tabela de resultados, mas o nome das colunas, a política de sobrescrita e o destino final precisam ser confirmados no código vigente.

Separar esse módulo de `google_sheets_nodes.py` deixa mais claro que o mapa físico e a lista de sinais são entradas diferentes, mesmo que estejam na mesma planilha ou no mesmo arquivo de planilha do Google.

------------------------------------------------------------------------

## 11. Credenciais e segurança

A árvore contém:

```text
credentials/
└── credentials.json
```

Esse arquivo é utilizado para autenticação, mas contém dados sensíveis. Ele não deve ser copiado para documentação pública, enviado em mensagens, nem incluído no repositório remoto.

O `.gitignore` deve excluir a pasta `credentials/`, além de arquivos gerados como `__pycache__/` e `*.pyc`. Também é importante verificar se o arquivo de credenciais já foi versionado em algum momento; adicioná-lo ao `.gitignore` não remove automaticamente uma versão que já esteja sob controle de versão.

O caminho usado pelo código para encontrar as credenciais precisa ser compatível com o diretório de execução escolhido pelo `executar.sh`. Um script executado a partir de outra pasta pode mudar a resolução de caminhos relativos, por isso o caminho deve ser testado em uma execução real.

------------------------------------------------------------------------

## 12. Responsabilidade de `src/construir_grafo.py`

O módulo transforma os registros de conexões físicas em uma estrutura que o Dijkstra consegue percorrer.

A representação típica é uma lista de adjacência:

```python
grafo = {
    "A1": [("E1", 402.81)],
    "E1": [("A1", 402.81), ("I1", 208.62)],
    "I1": [("E1", 208.62)]
}
```

O exemplo é ilustrativo. O grafo efetivo é construído com os registros atuais da planilha.

### Conexões inversas

Quando o modelo trata uma conexão como bidirecional, um registro de `A1` para `E1` também resulta na conexão inversa `E1` para `A1`. Essa regra é uma hipótese do modelo físico e precisa ser confirmada contra o mapa oficial.

### Duplicações

A regra documentada na V.3 era:
- mesma conexão com mesmo comprimento: ignorar a repetição;
- mesma conexão com comprimentos conflitantes: sinalizar erro.

A construção do grafo deve preservar essa distinção, sem escolher arbitrariamente um dos comprimentos conflitantes.

### Penalizações direcionais

A criação de arestas inversas físicas não deve fazer com que penalizações direcionais de hoop sejam aplicadas automaticamente nos dois sentidos. A direção de uma penalização é uma regra de custo separada da existência física da conexão.

------------------------------------------------------------------------

## 13. Responsabilidade de `src/grafo.py`

`grafo.py` fazia parte da arquitetura anterior como local do grafo manual usado para comparação e/ou como referência dos nós e dados do mapa.

Na V.4, o arquivo permanece na estrutura. A sua função concreta deve ser verificada antes de concluir que ainda é uma fonte usada em execução normal. Se estiver presente apenas para comparação ou testes, essa distinção deve ser mantida: o grafo manual de referência não deve ser confundido com o grafo construído a partir da planilha atual.

A comparação entre um grafo de referência e o grafo vindo da planilha foi útil na V.2 para verificar se as conexões físicas e os comprimentos tinham sido transferidos sem perdas. Quando o mapa oficial for atualizado, qualquer referência manual precisa ser atualizada ou claramente identificada como histórica.

------------------------------------------------------------------------

## 14. Responsabilidade de `src/dijkstra.py`

Este módulo implementa o algoritmo de busca. Ele recebe o grafo já construído e as informações necessárias ao custo; não deve depender diretamente da interface da Google Sheets.

O Dijkstra mantém, conceitualmente:
- menor custo de decisão conhecido para cada nó;
- distância física acumulada separadamente;
- predecessores para reconstruir o caminho;
- fila de prioridade para expandir primeiro o estado de menor custo.

A versão anterior utiliza uma fila de prioridade baseada em `heapq`. Para um grafo com lista de adjacência e heap, a complexidade típica é:

```text
O((V + E) log V)
```

onde `V` é o número de nós e `E` o número de arestas direcionadas.

O algoritmo exige pesos de decisão não negativos. Pesos físicos negativos devem ser rejeitados antes do cálculo. Se forem adicionadas regras futuras, elas não podem introduzir custos negativos sem uma mudança fundamentada do algoritmo.

------------------------------------------------------------------------

## 15. Custo de decisão versus distância física

A V.3 introduziu uma distinção que deve ser preservada na V.4.

### Custo de decisão

É o valor utilizado para comparar caminhos. A regra conceitual documentada foi:

```text
C_aresta =
    D_aresta × F_principal
    + U_destino × P_utilização
    + P_hoop
```

Em que:
- `D_aresta` é o comprimento físico original;
- `F_principal` é o fator aplicável ao caminho principal;
- `U_destino` é a utilização acumulada do nó de destino;
- `P_utilização` é a penalização por utilização;
- `P_hoop` é a penalização aplicada quando a aresta direcionada está configurada.

Para as arestas fora do caminho principal, a documentação anterior descreveu o fator físico padrão como `1,0`; para as arestas do caminho principal, os testes usaram `0,2`. A fórmula exata deve ser conferida na função de custo real.

### Distância física

É a soma dos comprimentos físicos originais das arestas percorridas. Não deve receber o fator do caminho principal nem as penalizações.

Portanto:

```text
custo_dijkstra ≠ necessariamente distância_fisica
```

Uma rota pode ser fisicamente curta e ter custo alto por atravessar uma aresta penalizada. O custo é uma métrica de decisão; a distância física é uma medida do comprimento do caminho no mapa.

------------------------------------------------------------------------

## 16. Caminho principal e parâmetros históricos

O caminho principal registrado na V.3 era:

```text
E2 → H2 → G2 → G3 → G1 → H1 → I1 → Y1 → K1 → K3 → K2 → L2 → V2 → V1 → N1
```

Os parâmetros de teste registrados eram:

```text
fator caminho principal = 0,2
penalização por utilização = 100
penalização entrada hoop = 5000
```

As arestas direcionadas penalizadas registradas eram:

```text
L1 → U1
L2 → U2
V1 → U1
V2 → U2
```

Esses dados são referências históricas da V.3, não garantia de que a planilha atual contenha os mesmos valores.

### Direcionalidade do hoop

Cadastrar `L2 → U2` como penalizada não implica penalizar `U2 → L2`. A penalização não deve ser espelhada automaticamente, mesmo quando a conexão física correspondente é bidirecional.

### Efeito do fator

O fator do caminho principal reduz ou modifica o custo usado para decidir a rota, mas não altera a distância física real. Ele é uma preferência de roteamento, não uma garantia de que o caminho principal sempre será selecionado.

------------------------------------------------------------------------

## 17. Utilização acumulada dos nós

A V.3 contabiliza os nós visitados por uma rota para que o uso anterior possa influenciar rotas futuras. A regra registrada incrementa todos os nós do caminho, exceto a origem.

Para:

```text
A → B → C → D
```

são incrementados `B`, `C` e `D`.

A justificativa é que a penalização é aplicada à entrada no nó de destino de cada aresta. O algoritmo consulta a utilização do vizinho/destino e adiciona o custo correspondente.

O contador é estado do processamento: para reproduzir resultados, é necessário saber quando é inicializado, quando é atualizado e se é compartilhado entre consultas. A V.3 demonstrou acumulação entre rotas na mesma execução. A V.4 possui fluxos manual e automático separados, por isso o escopo do contador deve ser confirmado em cada modo.

------------------------------------------------------------------------

## 18. Penalização de entrada do hoop

A penalização do hoop é uma regra direcional configurável. Nas configurações históricas, as arestas penalizadas eram `L1 → U1`, `L2 → U2`, `V1 → U1` e `V2 → U2`.

A penalização é adicionada ao custo de decisão ao atravessar uma aresta configurada no sentido indicado. Ela não muda o comprimento físico cadastrado.

Uma penalização alta não proíbe uma conexão: se não houver alternativa de menor custo, o algoritmo ainda pode escolhê-la. Caso uma conexão seja fisicamente proibida, deve ser removida do conjunto de arestas permitidas ou tratada por uma restrição explícita, em vez de depender apenas de uma penalização finita.

------------------------------------------------------------------------

## 19. Responsabilidade de `src/validacao.py`

O módulo reúne verificações de integridade antes de executar o roteamento. Na arquitetura anterior, as validações cobriam:
- consistência dos nós referenciados;
- validade dos pesos;
- simetria das conexões quando o grafo é considerado bidirecional.

Uma validação estrutural deve responder se o grafo está internamente consistente segundo as hipóteses adotadas. Ela não comprova que os comprimentos correspondem ao carro nem que uma rota atende a todas as regras elétricas e mecânicas.

Na V.4, o fluxo principal foi discutido para reunir mensagens de erro e impedir a continuação normal se existirem erros impeditivos. Isso exige que as funções de validação retornem uma estrutura compatível com a agregação feita por `main.py`; se uma função apenas imprimir uma mensagem e retornar `None`, o fluxo precisa ser adaptado.

A presença de `validacao.py` na árvore confirma o módulo, mas os nomes exatos das funções e o tipo de retorno devem ser conferidos no arquivo executado.

------------------------------------------------------------------------

## 20. Responsabilidade de `src/roteamento_sinais.py`

A V.4 inclui `roteamento_sinais.py`, separando o processamento em lote dos sinais da interação principal.

A função lógica desse módulo é receber os sinais lidos, utilizar o grafo e as configurações para calcular as rotas e organizar o resultado de cada sinal. O nome exato das funções, os argumentos e o formato retornado devem ser documentados a partir do código atual, sem inferi-los apenas do nome do arquivo.

O processamento de sinais pode precisar:
- percorrer cada registro de sinal;
- identificar origem e destino;
- executar Dijkstra;
- atualizar a utilização de nós conforme a política do lote;
- guardar o caminho, o custo, a distância física e o estado;
- registrar erros individuais de sinais inválidos ou sem caminho.

Esses itens descrevem as responsabilidades que o módulo precisa atender para realizar o fluxo automático. A lista exata de campos e a política para falhas individuais dependem da implementação.

Separar o roteamento dos sinais de `main.py` deixa o arquivo principal mais simples e permite testar o processamento em lote sem simular toda a interação do menu.

------------------------------------------------------------------------

## 21. Responsabilidade de `src/main.py`

`main.py` é o coordenador da aplicação. Não precisa conter todos os detalhes da Google Sheets, da configuração, do Dijkstra ou do processamento de sinais; deve chamar os módulos especializados.

O fluxo discutido para a V.4 é:

1. carregar conexões e configurações;
2. construir o grafo;
3. executar as validações;
4. interromper a execução normal se houver erros impeditivos;
5. mostrar o menu;
6. encaminhar para roteamento manual ou automático;
7. apresentar mensagens e resultados;
8. tratar falhas de carregamento e processamento.

### Modo manual

Permite informar origem e destino, com intermediário opcional, calcula a rota e apresenta custo e distância física.

### Modo automático

Lê os sinais, chama o módulo de roteamento em lote, transforma os resultados em tabela e encaminha a gravação para a planilha.

### Tratamento de exceções

O tratamento de erros deve comunicar a etapa que falhou e evitar continuar com dados incompletos. Uma mensagem amigável não substitui o detalhe necessário para depuração.

------------------------------------------------------------------------

## 22. Roteamento manual sem intermediário

No modo manual, a pessoa informa origem e destino. As entradas são normalizadas, removendo espaços extras e convertendo letras para maiúsculas. Antes de chamar Dijkstra, é necessário confirmar que os nós existem.

A consulta retorna conceitualmente:

```text
caminho
custo de decisão
distância física
```

Os casos importantes incluem:
- rota existente;
- origem igual ao destino;
- nó inexistente;
- nós existentes sem conexão entre si;
- erro inesperado durante a chamada.

Origem igual ao destino deve resultar em um caminho contendo apenas aquele nó, com custo e distância física iguais a zero, desde que esse comportamento seja preservado pela implementação.

A ausência de caminho não é igual a um nó inexistente: no primeiro caso os nós podem ser válidos, mas não há uma sequência de arestas que os conecte.

------------------------------------------------------------------------

## 23. Roteamento manual com intermediário

A consulta manual pode aceitar um nó intermediário opcional. Nesse caso, o programa precisa calcular duas partes:

```text
origem → intermediário
intermediário → destino
```

Se qualquer parte não possuir caminho, a rota completa não deve ser apresentada como sucesso. Quando ambos os trechos são válidos, os caminhos podem ser concatenados removendo a primeira ocorrência do segundo trecho, pois ela é o intermediário já presente no fim do primeiro.

A soma dos custos e das distâncias deve corresponder aos dois trechos calculados. Não se deve misturar custo de decisão com distância física ao somar.

### Observação sobre a utilização

Se o custo depende da utilização acumulada, é relevante saber se o segundo trecho é calculado antes ou depois de contabilizar o primeiro. Calcular ambos com o mesmo estado de utilização pode produzir resultado diferente de atualizar temporariamente o contador entre os trechos. A regra correta deve ser definida no código e testada; não deve ser assumida pela documentação.

------------------------------------------------------------------------

## 24. Utilização no modo manual

O contador de utilização no modo manual deve ter um escopo bem definido. O comportamento discutido para a V.4 inicializa a utilização para uma sessão manual e acumula as rotas realizadas naquela sessão.

Isso significa que sair do modo manual e iniciar outra sessão pode zerar o contador, dependendo de onde o dicionário é inicializado. Não se deve descrever essa utilização como persistente entre execuções, salvo se houver gravação explícita em arquivo ou planilha.

Também é necessário definir se uma rota malsucedida altera ou não a utilização. A prática coerente é só contabilizar uma rota quando ela tiver sido calculada e aceita, mas o comportamento efetivo deve ser confirmado no código.

------------------------------------------------------------------------

## 25. Processamento automático dos sinais

O modo automático processa os sinais registrados na planilha sem exigir que a pessoa digite manualmente origem e destino para cada um.

O fluxo conceitual é:

```text
Google Sheets
     ↓
google_sheets_sinais.py
     ↓
lista de sinais
     ↓
roteamento_sinais.py
     ↓
resultados por sinal
     ↓
conversão para tabela
     ↓
gravação na planilha
```

O módulo de leitura deve retornar registros em formato compatível com o processador. O processador deve utilizar o grafo já construído e as configurações carregadas pelo fluxo principal.

É importante distinguir:
- quantidade de sinais lidos;
- quantidade de rotas calculadas com sucesso;
- quantidade de rotas sem caminho;
- quantidade de registros inválidos;
- quantidade de resultados efetivamente gravados.

Uma mensagem indicando que todos os sinais foram lidos não comprova que todas as rotas foram calculadas nem que todos os resultados foram gravados corretamente.

------------------------------------------------------------------------

## 26. Ordem dos sinais e reprodutibilidade

Quando a utilização acumulada influencia o custo, a ordem de processamento dos sinais pode alterar as rotas seguintes. Se cada rota atualiza o contador antes do próximo sinal, a execução em lote é sequencial e não equivale a calcular todos os sinais independentemente com utilização zerada.

Para permitir a reprodução dos resultados, a documentação e os testes devem registrar:
- a ordem em que os sinais são percorridos;
- quando o contador é inicializado;
- quais nós são incrementados;
- se uma rota malsucedida modifica o contador;
- se a utilização é reiniciada a cada lote;
- se a utilização do modo manual é independente da automática.

A política exata deve ser obtida de `roteamento_sinais.py`. A presença do módulo, por si só, não confirma todos esses detalhes.

------------------------------------------------------------------------

## 27. Tabela de resultados e aba `Resultados`

Depois do processamento automático, os dados calculados precisam ser convertidos para uma estrutura tabular e gravados na aba de saída prevista.

O fluxo discutido para a V.4 é:

```text
sinais lidos
    ↓
rotas calculadas
    ↓
resultados organizados em linhas/colunas
    ↓
escrita na aba Resultados
```

A documentação não fixa nomes de colunas que não foram confirmados no código. Ao revisar a função que converte os resultados, conferir pelo menos:
- identificador/nome do sinal;
- origem e destino, se forem colunas de saída;
- caminho;
- custo de decisão;
- distância física;
- estado ou mensagem de erro.

Essa lista é um roteiro de conferência, não uma declaração de que todas essas colunas já existem.

Depois de executar o processamento, abrir a planilha e confirmar que a aba correta foi atualizada, que as linhas correspondem aos resultados esperados e que a política de escrita (substituir conteúdo ou anexar) é a desejada.

------------------------------------------------------------------------

## 28. Responsabilidade de `executar.sh`

O script `executar.sh` fornece um ponto de entrada pelo terminal para iniciar o programa. Sua presença permite padronizar a execução, mas o comando exato não deve ser inventado sem ler o conteúdo do arquivo.

Ao revisar o script, conferir:
- se ele muda para o diretório raiz do projeto;
- se chama o interpretador Python esperado;
- se executa `src/main.py` como script ou como módulo;
- se ativa ou pressupõe um ambiente virtual;
- se propaga o código de saída em caso de erro;
- se possui permissão de execução.

A execução deve funcionar a partir do diretório documentado no `README.md`. Se o script usa caminhos relativos, é importante testar a execução a partir de outra pasta para garantir que as credenciais e os módulos sejam encontrados.

------------------------------------------------------------------------

## 29. Responsabilidade de `README.md`

O `README.md` é a entrada rápida do repositório. Ele deve explicar o propósito do projeto, os requisitos, a estrutura de pastas, a configuração de credenciais e como executar o programa.

A documentação detalhada da evolução continua em `log/doc_v1.md`, `log/doc_v2.md`, `log/doc_v3.md` e nesta documentação da V.4. O README não precisa repetir todos os detalhes do algoritmo, mas deve apontar para a documentação de versão adequada.

O README também deve refletir os nomes reais dos arquivos atuais. Se ainda mencionar `google_sheets.py` ou `configs.py` dentro de `src/` como se fossem os módulos atuais, deve ser atualizado para a nova estrutura.

------------------------------------------------------------------------

## 30. Histórico em `log/`

A pasta `log/` contém:
- `doc_v1.md`;
- `doc_v2.md`;
- `doc_v3.md`.

Esses arquivos registram a evolução histórica. Eles não devem ser sobrescritos pela V.4, pois cada documento explica o escopo da versão correspondente.

A documentação da V.4 deve continuar o histórico e descrever:
- o que foi herdado da V.3;
- o que foi reorganizado;
- quais módulos novos foram introduzidos;
- como o processamento automático se conecta à leitura e à escrita;
- o que foi testado;
- o que continua pendente.

O documento V.4 deve ser salvo no local escolhido para documentação de versões, de preferência mantendo a mesma convenção de nomes e o histórico do projeto.

------------------------------------------------------------------------

## 31. Testes disponíveis na V.4

A árvore informada contém quatro arquivos de teste:

```text
testes/
├── teste_configs.py
├── teste_google_sheets_sinais.py
├── teste_grafo.py
└── teste_roteamento_sinais.py
```

Os nomes indicam quatro áreas de teste. A existência dos arquivos não comprova que todos passam; isso só pode ser declarado após executar os testes no ambiente atual.

### `testes/teste_configs.py`

Destinado a testar a interpretação e a consistência das configurações. Conferir conversão de parâmetros, estrutura do caminho principal e representação das arestas penalizadas conforme o que estiver implementado no módulo de configuração.

### `testes/teste_google_sheets_sinais.py`

Destinado a testar a integração relacionada à leitura dos sinais. É importante distinguir testes que usam dados simulados de testes que acessam a Google Sheets real e dependem de credenciais e rede.

### `testes/teste_grafo.py`

Destinado a testar a construção, estrutura ou consistência do grafo. A responsabilidade exata deve ser conferida no arquivo, especialmente se o teste ainda compara o grafo de referência com o grafo lido da planilha.

### `testes/teste_roteamento_sinais.py`

Destinado a testar o processamento de rotas associadas aos sinais. Deve verificar os casos válidos e inválidos cobertos pela implementação, o formato dos resultados e o efeito da utilização acumulada quando aplicável.

------------------------------------------------------------------------

## 32. Como interpretar os testes

Há três níveis distintos de teste:

### Teste unitário

Avalia uma função ou módulo isoladamente, normalmente com dados controlados. Por exemplo, verificar se uma configuração é convertida corretamente ou se um grafo pequeno produz o caminho esperado.

### Teste de integração

Verifica se módulos diferentes funcionam juntos. Por exemplo, se a leitura de sinais entrega a estrutura que `roteamento_sinais.py` espera.

### Teste de ponta a ponta

Executa o fluxo da aplicação: carregamento dos dados, construção e validação do grafo, escolha do modo, cálculo das rotas e gravação dos resultados.

Um teste que usa dados simulados pode ser útil sem acessar a planilha real. Contudo, ele não comprova que credenciais, permissões, nomes de abas e escrita na Google Sheets funcionam em produção.

Os resultados dos testes devem ser registrados com o comando utilizado, ambiente Python, resultado e eventuais dependências externas. Não declarar aprovação sem evidência de execução.

------------------------------------------------------------------------

## 33. Roteiro de testes de configuração

Conferir:
- se os parâmetros numéricos são lidos e convertidos corretamente;
- se valores ausentes ou inválidos são identificados;
- se o caminho principal permanece na ordem correta;
- se as arestas penalizadas preservam direção;
- se as configurações não são misturadas aos dados físicos do grafo;
- se o Dijkstra recebe os tipos esperados.

Os valores históricos `0,2`, `100` e `5000` podem ser utilizados como cenário de referência, desde que se reconheça que os valores atuais são os da fonte configurada.

------------------------------------------------------------------------

## 34. Roteiro de testes do grafo e da validação

Testar:
1. grafo válido;
2. vizinho inexistente;
3. peso inválido;
4. conexão duplicada com mesmo comprimento;
5. conexão duplicada com comprimento conflitante;
6. conexão sem inversa quando o modelo é bidirecional;
7. origem e destino válidos com caminho;
8. origem e destino válidos sem caminho;
9. construção a partir dos dados atuais da planilha;
10. comportamento do `main.py` quando a validação encontra erros.

Além de conferir as mensagens, verificar o fluxo de controle: erros impeditivos devem impedir que o menu de roteamento seja iniciado.

------------------------------------------------------------------------

## 35. Roteiro de testes do modo manual

Executar:
1. rota simples entre dois nós conectados;
2. origem igual ao destino;
3. origem inexistente;
4. destino inexistente;
5. destino inalcançável;
6. rota com intermediário válido;
7. intermediário que não pode ser alcançado pela origem;
8. intermediário alcançável sem caminho até o destino;
9. consultas repetidas para conferir utilização acumulada;
10. retorno ao menu;
11. entrada inválida no menu;
12. saída do modo manual pelo comando previsto.

Nos casos com intermediário, conferir se o nó aparece uma única vez na rota final e se custo e distância física são somados separadamente.

------------------------------------------------------------------------

## 36. Roteiro de testes do modo automático

Executar primeiro com um conjunto pequeno de sinais conhecido. Conferir:
- registros lidos;
- estrutura de cada sinal;
- origem e destino usados;
- caminho calculado;
- custo de decisão;
- distância física;
- estado de sucesso ou falha;
- efeito da ordem dos sinais;
- atualização do contador de utilização;
- tratamento de sinais incompletos;
- tratamento de nós inexistentes;
- tratamento de rotas sem caminho;
- conversão para tabela;
- gravação na aba correta;
- correspondência entre resultados calculados e gravados.

Depois, executar o lote completo. Comparar os totais antes e depois da escrita, sem assumir que uma mensagem de sucesso significa que todas as rotas foram fisicamente validadas.

------------------------------------------------------------------------

## 37. Testes de terminal e execução

Para `configs/terminal.py`, conferir se:
- as cores e estilos são consistentes;
- a formatação é restaurada depois de cada mensagem;
- erros são visualmente distinguíveis de sucessos;
- o terminal permanece compreensível sem suporte a ANSI;
- a camada de apresentação não modifica resultados.

Para `executar.sh`, conferir se:
- o script tem permissão de execução;
- o caminho para o projeto está correto;
- o Python e as dependências esperadas estão disponíveis;
- os imports funcionam no modo de execução utilizado;
- o carregamento das credenciais funciona;
- falhas de execução são propagadas de forma compreensível.

------------------------------------------------------------------------

## 38. Estatísticas históricas da V.3

Em uma execução automática anterior, foram observadas:
- 188 rotas com estado `OK`;
- distância física média de aproximadamente `1043,004 mm`;
- custo médio de aproximadamente `960,38`;
- sete rotas com custo acima de `5000`, associadas à penalização da aresta direcionada `L2 → U2`.

Esses números são históricos e não são resultados garantidos da V.4 atual. Alterações na organização dos módulos, nos sinais, na planilha, nas configurações e na ordem de processamento podem mudar os resultados.

O estado `OK` significa apenas que a rota foi tratada como sucesso pelas verificações da execução correspondente. Não prova que a rota é fisicamente instalável, eletricamente permitida ou aprovada pelo mapa oficial do T11.

------------------------------------------------------------------------

## 39. Estado do mapa físico e validação do T11

O mapa utilizado nas versões anteriores não deve ser tratado como mapa oficial definitivo sem confirmação. Quando o mapa oficial estiver disponível, revisar:
- nós;
- conexões;
- comprimentos;
- componentes;
- conexões bidirecionais e direcionais;
- caminho principal;
- entradas penalizadas do hoop;
- origem e destino de cada sinal;
- rotas permitidas e proibidas.

Depois da atualização, reconstruir o grafo, executar as validações e repetir os testes de configuração, grafo, roteamento manual e processamento automático.

A validação estrutural e a validação física/elétrica são diferentes. O código pode confirmar que um caminho existe no grafo e, ainda assim, o caminho estar incorreto no carro ou violar uma regra física não codificada.

------------------------------------------------------------------------

## 40. Limitações da V.4

A V.4 não deve ser apresentada como um sistema que já valida integralmente a instalação física do chicote. Permanecem dependentes de confirmação ou implementação:
- correspondência com o mapa oficial definitivo do T11;
- restrições elétricas e mecânicas completas;
- nós ou conexões obrigatórios e proibidos;
- critérios de interferência, segurança, montagem e manutenção;
- calibração dos parâmetros de custo;
- esquema final das colunas de saída;
- política de utilização entre consultas e entre modos;
- execução e registro dos testes no ambiente atual.

Essas limitações delimitam o que precisa ser verificado; não anulam o valor da modularização nem do processamento de rotas.

------------------------------------------------------------------------

## 41. Critérios de conclusão da V.4

A versão pode ser considerada fechada dentro do escopo atual quando:
- os imports correspondem à nova estrutura de pastas;
- o carregamento de conexões e configurações funciona;
- a leitura dos sinais funciona;
- o grafo é construído e validado antes do menu;
- erros impeditivos bloqueiam o roteamento;
- o modo manual funciona com e sem intermediário;
- a utilização segue a política definida;
- o modo automático processa os sinais esperados;
- a tabela contém as colunas corretas;
- os resultados são gravados na aba prevista;
- os quatro arquivos de teste são executados e seus resultados registrados;
- `executar.sh` inicia o programa no ambiente documentado;
- as credenciais não são expostas no repositório;
- `README.md` corresponde à estrutura atual;
- a documentação histórica é preservada;
- custo e distância física permanecem separados;
- os resultados são analisados contra o mapa vigente.

Um item não deve ser marcado como concluído apenas porque existe um arquivo com o nome esperado. A conclusão depende de execução ou revisão do conteúdo.

------------------------------------------------------------------------

## 42. Próximas etapas

### 42.1. Conferir os contratos entre módulos

- verificar quais funções cada módulo exporta;
- documentar argumentos e valores de retorno;
- revisar os imports após a reorganização;
- confirmar onde a escrita dos resultados está implementada;
- garantir que a estrutura dos sinais corresponda ao que o roteador espera.

### 42.2. Conferir execução e ambiente

- ler `executar.sh` e registrar o comando real;
- verificar dependências Python;
- testar a execução a partir do diretório previsto;
- testar a leitura de credenciais sem expô-las;
- revisar `.gitignore` para credenciais e arquivos gerados.

### 42.3. Fechar os testes

- executar `teste_configs.py`;
- executar `teste_google_sheets_sinais.py`;
- executar `teste_grafo.py`;
- executar `teste_roteamento_sinais.py`;
- separar testes unitários dos que dependem da internet;
- registrar falhas, correções e resultado final.

### 42.4. Validar os dados físicos

- atualizar o mapa pelo documento oficial;
- conferir as conexões e comprimentos;
- revisar o caminho principal;
- confirmar arestas penalizadas;
- repetir o processamento e analisar os resultados.

### 42.5. Fechar a documentação e o repositório

- atualizar o `README.md`;
- salvar a documentação da V.4 seguindo a convenção do projeto;
- preservar os documentos V.1–V.3;
- registrar o estado real dos testes;
- revisar alterações e fazer um commit descritivo.

------------------------------------------------------------------------

## 43. Resumo técnico da V.4

A V.4 evolui o sistema de roteamento do chicote GLV do T11 tanto na organização quanto no fluxo de uso. A estrutura deixa de concentrar todos os módulos em `src/`: as configurações e recursos de terminal ficam em `configs/`; a integração com Google Sheets é separada entre dados do mapa e sinais; o processamento dos sinais é separado em `roteamento_sinais.py`; e os testes ficam agrupados em `testes/`. O script `executar.sh`, o `README.md` e a pasta `log/` complementam a execução e a documentação do projeto.

A lógica de Dijkstra mantém as regras de custo da V.3: fator do caminho principal, utilização acumulada e penalização direcional de entrada do hoop. O custo de decisão continua separado da distância física.

O fluxo de aplicação prevê roteamento manual, com intermediário opcional, e roteamento automático dos sinais. O modo automático deve ler os sinais, calcular as rotas, organizar os resultados em tabela e gravá-los na planilha. A validação estrutural precisa ocorrer antes do roteamento, e a apresentação do terminal deve permanecer separada da lógica do algoritmo.

A árvore de arquivos confirma a organização dos módulos e dos testes, mas não comprova por si só que todos os fluxos passaram em execução. As funções exportadas, os nomes das colunas, o comando de `executar.sh`, a integração real com a planilha e os resultados dos testes precisam ser confirmados no código e no ambiente atuais.

Por fim, o sistema continua sendo uma ferramenta de roteamento baseada no grafo e nas regras configuradas. Ele não substitui a conferência do mapa oficial do T11 nem comprova sozinho a viabilidade física, mecânica ou elétrica de cada trajeto.