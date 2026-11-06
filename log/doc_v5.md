# DOCUMENTAÇÃO DA VERSÃO 5 — AUTOMAÇÃO DO ROTEAMENTO DO CHICOTE GLV DO T11

## 1. Visão geral

A V.5 dá continuidade ao projeto de roteamento do chicote de baixa tensão (GLV/LV) do T11 da equipe TUPÃ Formula SAE Elétrica. As versões anteriores estabeleceram a representação do mapa físico por um grafo, a busca de caminhos pelo algoritmo de Dijkstra, as regras configuráveis de custo e o processamento de sinais. A V.5 concentra-se na integração desses recursos com os dados operacionais da Google Sheets, para reduzir o preenchimento manual e manter as informações calculadas sincronizadas.

O objetivo operacional é permitir que, após alterações nos dados de origem feitas pela equipe, seja possível executar um comando na raiz do projeto, recalcular os sinais elegíveis e atualizar as abas necessárias. O fluxo separa sinais de roteamento automático daqueles cujo tratamento deve permanecer manual, em especial os classificados como CAN e SHUT segundo as regras de identificação implementadas.

A V.5 não substitui o Dijkstra da V.4: utiliza o roteador existente e acrescenta leitura, classificação, preparação de alterações, sincronização, backups e verificações. O sistema continua calculando caminhos com base no grafo e nas regras cadastradas; não valida sozinho a instalação física e elétrica no carro.

Esta documentação utiliza a árvore de arquivos fornecida, o comportamento observado nas execuções compartilhadas e o conteúdo disponível de `src/automatizacao_v5.py` e da integração V5. Para módulos cujo código integral não foi fornecido nesta etapa, são descritas as responsabilidades e interfaces conhecidas, sem presumir detalhes internos não verificados.

------------------------------------------------------------------------

## 2. Objetivos da V.5

- Ler a `Database` como fonte dos sinais e de seus dados originais.
- Consultar a planilha de componentes e nós (`Nós-Dijkstra`) para associar componentes aos nós do grafo.
- Interpretar as tags dos sinais e separar os casos automáticos dos manuais, com atenção a CAN e SHUT.
- Preservar os dados manuais, sem substituir seus caminhos por rotas automáticas.
- Construir e validar o grafo a partir das conexões e configurações atuais.
- Calcular os caminhos e as distâncias físicas dos sinais automáticos pelo roteador V4.
- Preparar alterações nas colunas `H`, `I`, `L`, `M` e `N` da `Database`.
- Sincronizar as abas `Sinais-Dijkstra` e `Resultados-Dijkstra`.
- Evitar escritas quando as informações já estão atualizadas.
- Exibir previamente as alterações, solicitar confirmação, criar backups e verificar a escrita.
- Oferecer um fluxo unificado por `src/automatizacao_v5.py` e `executar++.sh`.
- Manter a execução tradicional da V4 disponível por `src/main.py` e `executar.sh`.

------------------------------------------------------------------------

## 3. Evolução entre as versões

### V.1 — protótipo

Representação do mapa como grafo e implementação inicial do Dijkstra, com entrada de origem e destino e reconstrução do caminho.

### V.2 — dados externos

Leitura de conexões na Google Sheets, construção automática do grafo e validações de nós, pesos e simetria.

### V.3 — critérios de roteamento

Inclusão do fator de preferência pelo caminho principal, penalização por utilização acumulada e penalizações direcionais do hoop. Separação entre custo de decisão e distância física.

### V.4 — modularização e processamento em lote

Organização em `configs/`, `src/` e `testes/`; separação dos módulos de Google Sheets; roteamento manual e automático pelo menu; criação de `executar.sh`.

### V.5 — integração com a Database e sincronização

Automação da associação entre sinais, componentes e nós; classificação dos sinais manuais; cálculo das rotas automáticas; preparação e atualização das colunas de saída; sincronização de duas abas auxiliares; auditoria; e criação de um coordenador único com verificações antes e depois das escritas.

------------------------------------------------------------------------

## 4. Estrutura de pastas da V.5

A estrutura informada, omitindo `__pycache__/` e arquivos `.pyc` gerados automaticamente, é:

```text
.
├── configs/
│   ├── __init__.py
│   ├── configs.py
│   └── terminal.py
├── credentials/
│   └── credentials.json
├── executar++.sh
├── executar.sh
├── log/
│   ├── doc_v1.md
│   ├── doc_v2.md
│   ├── doc_v3.md
│   ├── doc_v4.md
│   └── doc_v5.md                 # esta documentação
├── README.md
├── relatorios/
│   └── auditoria_v5/
│       ├── 01_divergencias_origem_destino.csv
│       ├── 02_todos_os_sinais.csv
│       ├── 03_todas_as_alteracoes.csv
│       └── 04_alertas.csv
├── src/
│   ├── __init__.py
│   ├── atualizar_database.py
│   ├── auditoria_v5.py
│   ├── automatizacao_v5.py
│   ├── automatizar_sinais.py
│   ├── construir_grafo.py
│   ├── dijkstra.py
│   ├── google_sheets_nodes.py
│   ├── google_sheets_sinais.py
│   ├── grafo.py
│   ├── integracao_v5.py
│   ├── main.py
│   ├── roteamento_sinais.py
│   ├── sincronizar_resultados_v5.py
│   ├── sincronizar_sinais_v5.py
│   └── validacao.py
└── testes/
    ├── teste_atualizar_database.py
    ├── teste_automatizar_sinais.py
    ├── teste_configs.py
    ├── teste_google_sheets_sinais.py
    ├── teste_grafo.py
    ├── teste_integracao_v5.py
    └── teste_roteamento_sinais.py
```

Os arquivos V4 permanecem no projeto. A automação V5 é uma camada adicional e não exige substituir o menu anterior. A árvore mostra a existência dos arquivos, mas não comprova, isoladamente, o comportamento de cada função.

------------------------------------------------------------------------

## 5. Visão geral da arquitetura

O funcionamento da V5 pode ser dividido em seis grupos:

1. **Entradas externas:** `Database`, cadastro de componentes/nós, conexões do mapa e configurações do algoritmo.
2. **Preparação:** leitura, interpretação de tags, associação de componentes a nós e classificação dos registros.
3. **Roteamento:** construção e validação do grafo e processamento dos sinais automáticos com Dijkstra.
4. **Planejamento:** geração das linhas de sinais/resultados e da lista de células da `Database` que precisam mudar.
5. **Persistência:** comparação das abas, backups, escritas e verificações.
6. **Execução e auditoria:** comando unificado, relatórios, testes e documentação.

O fluxo lógico é:

```text
Database + Nós-Dijkstra + mapa/configurações
                    |
                    v
        integracao_v5.py
        - ler e classificar sinais
        - identificar nós
        - validar grafo
        - calcular Dijkstra
        - preparar alterações
                    |
                    v
        automatizacao_v5.py
        - comparar estado atual
        - detectar pendências
        - confirmar alterações
        - revalidar dados
        - criar backups
                    |
          +---------+---------+
          |         |         |
          v         v         v
     Sinais-    Resultados-  Database
     Dijkstra   Dijkstra    H/I/L/M/N
          |         |         |
          +---------+---------+
                    |
                    v
           verificar escritas
```

------------------------------------------------------------------------

## 6. Entradas da Google Sheets

A V5 depende de três conjuntos principais de dados: os registros dos sinais da `Database`, o cadastro de componentes e nós e as conexões/configurações usadas para construir o grafo.

A `Database` é a fonte dos registros que precisam ser analisados. A associação entre componentes e nós é obtida pelo módulo `google_sheets_nodes.py`, por meio da função conhecida `ler_componentes_nos()`. O mesmo módulo fornece `ler_planilha()` para os dados do mapa e das configurações.

Os dados são consultados novamente quando a automação precisa conferir se alguém modificou as fontes durante a execução. A leitura não significa que todo registro será roteado: antes disso, ele passa por classificação e validação.

------------------------------------------------------------------------

## 7. Componentes e nós — `Nós-Dijkstra`

A V5 utiliza o cadastro de componentes e nós para determinar os pontos de origem e destino dos sinais elegíveis. Isso evita depender exclusivamente do preenchimento manual dos nós em cada linha da `Database`.

A função `ler_componentes_nos()` é utilizada pela integração e também pela automação central para conferir a estabilidade dos dados. Caso o cadastro seja alterado, uma nova execução deve recalcular as associações e as rotas dependentes delas.

A associação automática pressupõe que os identificadores dos componentes estejam consistentes com os registros da `Database`. Componentes não encontrados, ambiguidades ou nós inválidos devem ser tratados como problemas de dados, não resolvidos por escolhas arbitrárias.

A nomenclatura exata das colunas de `Nós-Dijkstra` e as regras de desempate devem ser conferidas no código de leitura e na planilha vigente.

------------------------------------------------------------------------

## 8. Identificação e classificação dos sinais

A V5 analisa os registros e as tags dos sinais para decidir quais podem seguir para o roteamento automático e quais exigem tratamento manual. O tratamento de CAN e SHUT tem prioridade como regra de classificação, para evitar que uma rota calculada automaticamente substitua uma decisão manual específica desses circuitos.

O resultado do processamento é separado, na estrutura `plano_sinais`, em conjuntos de sinais automáticos, manuais e ignorados. O resumo apresentado no terminal informa a quantidade de cada grupo.

É importante não confundir **prioridade de identificação** com **prioridade de roteamento**. Neste contexto, CAN e SHUT recebem atenção na classificação para serem preservados; isso não significa que o Dijkstra esteja calculando automaticamente um caminho preferencial para eles.

As expressões exatas usadas para reconhecer as tags e os motivos para ignorar registros devem ser consultados em `src/automatizar_sinais.py` e nos testes correspondentes. Não se deve presumir que toda ocorrência textual de CAN ou SHUT seja classificada da mesma maneira sem verificar as regras implementadas.

------------------------------------------------------------------------

## 9. Caminhos manuais de CAN e SHUT

Os registros classificados como manuais não entram no mesmo fluxo de substituição de rotas automáticas. O objetivo é preservar as escolhas existentes na `Database`, em vez de recalculá-las e sobrescrevê-las.

Esse comportamento é importante porque a rota física de circuitos específicos pode depender de restrições elétricas, de segurança ou de montagem não representadas no custo do Dijkstra.

**Limite da implementação:** preservar 54 registros manuais, como ocorreu na última execução observada, não comprova que todos tenham caminhos e distâncias preenchidos ou fisicamente corretos. A conferência dos registros manuais permanece uma atividade específica da equipe.

------------------------------------------------------------------------

## 10. Preparação de origem e destino

Para os sinais automáticos, a integração combina os dados originais da `Database` com o cadastro de componentes/nós para obter os pontos usados no roteamento. As alterações previstas para origem e destino são incluídas no plano de atualização da `Database`.

As colunas envolvidas na automação são `H`, `I`, `L`, `M` e `N`. Na estrutura atual, `L` é usada para caminho, `M` para status e `N` para distância; `H` e `I` participam do preenchimento de origem/destino conforme o esquema do projeto.

O planejamento deve comparar os valores calculados com os existentes e incluir apenas alterações necessárias. Isso permite executar a V5 novamente sem reescrever células que já possuem o valor esperado.

------------------------------------------------------------------------

## 11. Construção e validação do grafo

A V5 reaproveita a infraestrutura de grafo da V4. A função `executar(aplicar=False)`, de `src/integracao_v5.py`, carrega os dados do mapa, constrói o grafo e executa as validações antes de calcular rotas.

As verificações conhecidas incluem:

- consistência dos nós referenciados;
- validade dos pesos;
- simetria das conexões, conforme a hipótese bidirecional do modelo.

Se forem encontrados erros impeditivos, a integração interrompe o cálculo em vez de produzir um plano de escrita baseado em um grafo inválido.

A validação é **estrutural**. Ela não confirma que a ligação física realmente existe no carro ou que atende a todas as restrições elétricas e mecânicas do chicote.

------------------------------------------------------------------------

## 12. Dijkstra e regras de custo herdadas

A V5 não introduz um novo algoritmo de caminho mínimo. Ela utiliza a implementação existente de Dijkstra e as regras configuráveis herdadas das versões anteriores:

- preferência pelo caminho principal por meio de um fator de custo;
- penalização por utilização acumulada de nós;
- penalizações direcionais de entrada do hoop;
- distinção entre custo de decisão e distância física.

A forma conceitual documentada na V4 é:

```text
custo_da_aresta = comprimento_fisico × fator_aplicavel
                 + penalizacao_por_utilizacao
                 + penalizacao_direcional
```

A distância física é a soma dos comprimentos originais das arestas percorridas. Ela não deve incorporar as penalizações do custo de decisão.

Os valores históricos `0,2`, `100` e `5000` pertencem aos registros de versões anteriores; não devem ser apresentados como os parâmetros atuais sem consultar a configuração vigente. A ordem de processamento também pode influenciar as rotas quando existe utilização acumulada.

------------------------------------------------------------------------

## 13. Responsabilidade de `src/integracao_v5.py`

Este módulo integra as entradas da planilha ao roteador da V4 e prepara os dados que serão sincronizados. A função principal conhecida é:

```python
executar(aplicar=False)
```

No modo de simulação, a função lê a `Database`, consulta os componentes/nós e o mapa, constrói e valida o grafo, prepara os sinais, calcula os resultados e mostra um resumo sem escrever na planilha.

O dicionário retornado contém, entre outros elementos utilizados pela automação:

- `plano_sinais`, incluindo `linhas_sinais`, `manuais` e `ignorados`;
- `resultados`, com os resultados de roteamento;
- `atualizacoes_database`, com as alterações planejadas nas células.

O módulo também disponibiliza `configurar_ipv4()`, usado para contornar problemas de resolução/conexão observados no ambiente, e `converter_numero()`, empregado na interpretação de números com formatos de localidade diferentes.

O modo `executar(aplicar=True)` possui seu próprio fluxo de escrita da `Database`. Para a operação unificada, a entrada recomendada é `automatizacao_v5.py`, que chama a integração inicialmente em modo de simulação e coordena as três abas.

------------------------------------------------------------------------

## 14. Responsabilidade de `src/automatizar_sinais.py`

O arquivo concentra a lógica específica de automação e classificação dos sinais, separando-a do coordenador geral. Sua existência e os testes associados constam da árvore do projeto.

Seu papel na arquitetura é permitir que os registros sejam analisados antes do roteamento, distinguindo sinais automáticos, manuais e ignorados. A implementação exata das regras de tag, campos obrigatórios e tratamento de ambiguidades deve ser conferida no código atual.

Essa separação facilita alterar uma regra de identificação sem modificar o algoritmo de Dijkstra.

------------------------------------------------------------------------

## 15. Responsabilidade de `src/atualizar_database.py`

Este módulo participa da preparação e/ou tratamento das atualizações da `Database`, com testes próprios em `teste_atualizar_database.py`. A escrita efetiva usada pelo coordenador V5 é chamada por `atualizar_celulas_database()`, disponibilizada em `src/google_sheets_sinais.py`.

A atualização deve manter a separação entre dados originais fornecidos pela equipe e campos calculados pela automação. O fluxo unificado atua nas colunas `H`, `I`, `L`, `M` e `N` conforme o plano preparado, e não substitui indiscriminadamente toda a aba.

------------------------------------------------------------------------

## 16. Aba `Sinais-Dijkstra`

A aba `Sinais-Dijkstra` é a representação tabular dos sinais automáticos preparados para roteamento. Na V5, a sincronização trabalha com a faixa `A:D`.

O módulo `src/sincronizar_sinais_v5.py` fornece as funções conhecidas `ler_linhas_aba()`, `normalizar_linhas()` e `criar_backup_aba()`. A gravação é realizada por `escrever_sinais_automatizados()`, disponível em `src/google_sheets_sinais.py`.

Antes de escrever, a automação compara as linhas existentes com as linhas geradas. Se forem equivalentes após normalização, a aba é considerada sincronizada e não precisa ser substituída. Quando existe diferença, a atualização é planejada e passa pelas etapas de confirmação, backup e conferência.

A sincronização da aba de sinais não significa que os registros manuais sejam roteados automaticamente.

------------------------------------------------------------------------

## 17. Aba `Resultados-Dijkstra`

A aba `Resultados-Dijkstra` armazena os resultados calculados para os sinais automáticos. A faixa de sincronização da V5 é `A:I`.

O módulo `src/sincronizar_resultados_v5.py` fornece `gerar_linhas_resultados()`, `ler_resultados()`, `linhas_iguais()` e a rotina de backup. A comparação considera a estrutura da tabela e os campos numéricos conforme a lógica implementada.

Quando a escrita é necessária, o coordenador limpa a faixa `A:I`, escreve a nova tabela a partir de `A1` e relê a aba para conferir a correspondência. Essa substituição deve ser tratada com cuidado: não se devem inserir manualmente dados que precisam ser preservados dentro da faixa gerenciada pela automação.

------------------------------------------------------------------------

## 18. Atualização da `Database`

A `Database` concentra os registros originais e os campos de integração do roteamento. A V5 prepara atualizações pontuais em `H`, `I`, `L`, `M` e `N`, em vez de substituir a tabela inteira.

O coordenador consulta `plano['atualizacoes_database']` para decidir se há células pendentes. Quando há escrita, chama `atualizar_celulas_database(..., confirmar_escrita=True)` e depois relê a `Database` para comparar os valores esperados.

A verificação da coluna `N` utiliza conversão numérica e comparação com precisão de duas casas decimais, tolerando diferenças de representação numérica decorrentes da localidade. Para as demais colunas verificadas, a comparação é textual após remoção de espaços nas extremidades.

O programa não deve alterar caminhos manuais apenas porque um novo caminho automático seria possível.

------------------------------------------------------------------------

## 19. Responsabilidade de `src/automatizacao_v5.py`

Este arquivo é o coordenador do fluxo completo. Sua função principal é:

```python
automatizar(aplicar=False)
```

Ele não reimplementa o Dijkstra: chama `executar(aplicar=False)` para produzir o plano e depois organiza a sincronização.

O fluxo observado no código é:

1. configurar o acesso IPv4 e conectar à Google Sheets;
2. calcular o plano V5 sem escrita;
3. gerar as linhas de `Sinais-Dijkstra` e `Resultados-Dijkstra`;
4. verificar a consistência das quantidades;
5. ler o estado atual das três abas e das fontes;
6. comparar os dados atuais com os calculados;
7. exibir quais abas precisam de atualização;
8. encerrar sem escrita se tudo estiver sincronizado;
9. se a escrita foi solicitada, pedir confirmação explícita;
10. reler entradas e destinos e recalcular o plano para revalidação;
11. criar os backups necessários antes da primeira escrita;
12. escrever cada aba necessária e verificar seu conteúdo.

O arquivo contém a estrutura `Estado`, que agrupa o plano, as tabelas atuais e novas, os dados de entrada e os indicadores de pendência.

------------------------------------------------------------------------

## 20. Simulação e aplicação

A execução padrão é uma **simulação**, sem modificações na Google Sheets:

```bash
python -m src.automatizacao_v5
```

Para habilitar a escrita, o comando disponível é:

```bash
python -m src.automatizacao_v5 --aplicar
```

Mesmo com `--aplicar`, o coordenador não escreve imediatamente. Primeiro apresenta as abas que serão modificadas e solicita que a pessoa digite exatamente:

```text
APLICAR V5
```

Uma resposta diferente cancela a operação. Se nenhuma alteração estiver pendente, o programa termina sem solicitar confirmação e sem escrever.

A simulação deve ser a primeira etapa para diagnosticar problemas sem modificar dados compartilhados.

------------------------------------------------------------------------

## 21. Comando unificado — `executar++.sh`

O arquivo `executar++.sh` foi criado na raiz para simplificar a rotina de uso da equipe. A intenção é que, após mudanças nas linhas originais da `Database` ou em outros dados de entrada, o usuário não precise executar manualmente cada módulo de sincronização.

O comando previsto é:

```bash
cd ~/Desktop/Tupa/dijkstra
./executar++.sh
```

Na primeira utilização, pode ser necessário habilitar a execução:

```bash
chmod +x 'executar++.sh'
```

O script deve encaminhar a operação ao coordenador `src.automatizacao_v5`, utilizando o ambiente Python configurado. A execução com permissão de escrita continua sujeita à confirmação de segurança implementada no Python.

**Estado de validação:** o comando Python de simulação já foi executado com sucesso. Não foi apresentado, até esta documentação, um log de execução de ponta a ponta do `executar++.sh`; portanto, a integração do shell ainda precisa ser conferida no ambiente local. O conteúdo integral do `.sh` também deve ser revisado para registrar seu comportamento exato.

------------------------------------------------------------------------

## 22. Diferença entre `executar.sh` e `executar++.sh`

| Arquivo | Finalidade |
|---|---|
| `executar.sh` | Entrada tradicional da aplicação V4, com menu de roteamento manual e automático. |
| `executar++.sh` | Entrada operacional planejada para a automação V5, com recálculo e sincronização das abas. |

O primeiro é útil para consultas manuais e para o fluxo histórico. O segundo deve ser o comando de rotina após atualizações dos dados pela equipe, depois de validado integralmente.

A V5 não exige apagar `main.py` nem os módulos da V4.

------------------------------------------------------------------------

## 23. Comparação e idempotência

A automação compara as informações calculadas com os dados atuais antes de escrever. Isso permite executar o mesmo processo várias vezes sem alterar uma aba que já contém o resultado esperado.

A comparação ocorre em três níveis:

- `Database`: existência de atualizações planejadas em `H/I/L/M/N`;
- `Sinais-Dijkstra`: comparação das linhas normalizadas;
- `Resultados-Dijkstra`: comparação das linhas, incluindo tratamento apropriado dos campos numéricos.

A última simulação compartilhada apresentou:

```text
Sinais automaticos: 201
Sinais manuais preservados: 54
Linhas ignoradas: 20
Database: 0 celulas pendentes
Sinais-Dijkstra: SINCRONIZADA
Resultados-Dijkstra: SINCRONIZADA
SUCESSO: as tres abas ja estao sincronizadas.
```

Esse resultado confirma o comportamento sem escrita para o conjunto de dados observado naquele momento. Não garante que uma alteração futura terá sido corretamente aplicada até que o fluxo de escrita seja testado.

------------------------------------------------------------------------

## 24. Revalidação antes da escrita

Antes de iniciar backups e escritas, `automatizacao_v5.py` relê os dados de origem e as abas de destino para detectar alterações desde a leitura inicial. Em seguida, recalcula o plano V5 e compara as atualizações da `Database`, as linhas de sinais e os resultados esperados.

Se forem detectadas divergências, a execução é interrompida antes da escrita. A rotina também confere o estado de uma aba imediatamente antes de alterá-la.

Esse mecanismo reduz o risco de sobrescrever mudanças feitas por outra pessoa durante a execução, mas não oferece bloqueio exclusivo da planilha. Ainda existe uma janela entre a conferência e a escrita, porque a API não fornece uma transação atômica única para todo o processo.

------------------------------------------------------------------------

## 25. Backups e segurança das escritas

Quando existe alteração e a pessoa confirma a aplicação, a V5 cria backups das abas que serão modificadas **antes da primeira escrita**.

As rotinas conhecidas são:

- `criar_backup_aba()` para `Sinais-Dijkstra`;
- `criar_backup()` do módulo de resultados para `Resultados-Dijkstra`;
- `criar_backup_database()` para a `Database`.

Na execução anterior dos módulos individuais foram observados backups com nomes como `Sinais-BACKUP-...`, `Resultados-BACKUP-...` e `Database-BACKUP-TX-...`.

O coordenador escreve e verifica uma aba por vez. A ordem implementada é: `Sinais-Dijkstra`, `Resultados-Dijkstra` e `Database`, somente para as que precisarem de atualização.

**Importante:** o backup não implica restauração automática. Uma falha pode deixar parte das abas atualizada e outra parte no estado anterior. Nessa situação, a equipe deve conferir o erro e os backups antes de tentar aplicar novamente.

------------------------------------------------------------------------

## 26. Tratamento de erros e recuperação

O coordenador encerra com erro quando encontra inconsistências de quantidades, alterações inesperadas de dados, falhas de conexão, divergências após a escrita ou exceções dos módulos de integração.

Caso a escrita falhe, ele informa quais etapas foram confirmadas e avisa que a etapa com erro **pode ter sido parcialmente gravada**. Não se deve executar imediatamente outra atualização sem investigar o estado da planilha.

Procedimento recomendado:

1. não editar ou reexecutar a atualização até identificar a etapa que falhou;
2. conferir o resumo do terminal e as abas afetadas;
3. localizar os backups criados na execução;
4. comparar os dados atuais com os backups e decidir se é necessário restaurar;
5. corrigir o problema e executar uma simulação;
6. somente depois repetir a aplicação, se ainda houver pendências.

A restauração automática entre as três abas não está implementada no coordenador inspecionado.

------------------------------------------------------------------------

## 27. Auditoria V5

A árvore do projeto inclui `src/auditoria_v5.py` e quatro relatórios CSV em `relatorios/auditoria_v5/`:

```text
01_divergencias_origem_destino.csv
02_todos_os_sinais.csv
03_todas_as_alteracoes.csv
04_alertas.csv
```

Os nomes indicam uma organização destinada a examinar divergências, registros, alterações e alertas. O conteúdo efetivo e os critérios de geração desses relatórios precisam ser confirmados no módulo de auditoria e nos arquivos CSV.

A auditoria é útil para revisar decisões da automação, mas não substitui os backups das abas nem a verificação de escrita feita pelo coordenador.

------------------------------------------------------------------------

## 28. Testes disponíveis

A árvore informada contém sete arquivos de teste:

```text
teste_atualizar_database.py
teste_automatizar_sinais.py
teste_configs.py
teste_google_sheets_sinais.py
teste_grafo.py
teste_integracao_v5.py
teste_roteamento_sinais.py
```

Na execução anterior compartilhada, **54 testes passaram** com o comando:

```bash
PYTHONPATH=.:src python -m unittest discover -s testes -p 'teste_*.py'
```

Esses testes dão evidência sobre os módulos cobertos, mas foram executados antes da criação do coordenador unificado. Não há, na árvore informada, um arquivo `teste_automatizacao_v5.py` que comprove os casos de confirmação, backups e falhas parciais do novo coordenador.

------------------------------------------------------------------------

## 29. Testes ainda necessários para o coordenador

Os cenários prioritários são:

1. todas as abas sincronizadas: nenhuma escrita;
2. somente `Sinais-Dijkstra` divergente;
3. somente `Resultados-Dijkstra` divergente;
4. somente `Database` divergente;
5. divergências simultâneas nas três abas;
6. cancelamento na confirmação;
7. mudança de dados de origem antes da escrita;
8. mudança de uma aba de destino antes da escrita;
9. falha ao criar um backup: nenhuma escrita iniciada;
10. falha ao escrever uma aba: mensagem de erro e identificação das etapas confirmadas;
11. divergência na conferência após a escrita;
12. tratamento de sinais manuais e ignorados;
13. preservação de colunas não gerenciadas;
14. execução do `executar++.sh` com o ambiente Python correto;
15. simulação e escrita em uma cópia da planilha, sem afetar a produção.

Os testes unitários devem utilizar dados controlados e simulações da API. O teste real de escrita deve ser realizado em uma cópia autorizada da planilha.

------------------------------------------------------------------------

## 30. Evidências de funcionamento observadas

O estado conhecido do projeto, com base nas execuções compartilhadas, é:

- 201 sinais classificados e roteados automaticamente;
- 54 sinais classificados como manuais e preservados;
- 20 linhas ignoradas;
- `Database` sem atualizações pendentes;
- `Sinais-Dijkstra` sincronizada;
- `Resultados-Dijkstra` sincronizada;
- 54 testes existentes aprovados;
- simulação integrada de `python -m src.automatizacao_v5` concluída com sucesso e sem escrita.

As sincronizações individuais das três abas já haviam sido executadas e conferidas anteriormente. Entretanto, a **escrita de ponta a ponta pelo coordenador unificado** ainda não foi demonstrada por uma execução com alterações pendentes.

------------------------------------------------------------------------

## 31. Limitações da V.5

- O sistema calcula rotas a partir do mapa e das regras configuradas; não comprova a viabilidade física, elétrica ou mecânica do chicote.
- Os caminhos manuais de CAN e SHUT são preservados, não automaticamente auditados quanto à correção física.
- A qualidade das rotas depende do cadastro de componentes, dos nós, das conexões e das tags dos sinais.
- Alterações nas configurações e na ordem dos sinais podem modificar o resultado do roteamento.
- A sincronização usa chamadas separadas à Google Sheets, sem transação atômica entre abas.
- Backups são criados, mas a restauração automática não faz parte do fluxo inspecionado.
- A detecção de mudanças concorrentes reduz riscos, mas não elimina todas as condições de corrida.
- Os testes existentes não comprovam todos os cenários do coordenador central.
- O script `executar++.sh` e o caminho de escrita integrada ainda exigem validação final no ambiente local.

------------------------------------------------------------------------

## 32. Credenciais e controle de versão

A pasta `credentials/` contém o arquivo de autenticação usado no acesso à Google Sheets. Esse arquivo não deve ser publicado no repositório nem incluído na documentação.

O `.gitignore` deve excluir credenciais e arquivos gerados pelo Python. Se uma credencial já tiver sido versionada ou exposta, ignorar o arquivo em novos commits não remove o segredo do histórico; a credencial deve ser revogada ou substituída conforme necessário.

A documentação e os relatórios podem ser versionados de acordo com a política da equipe, desde que não incluam segredos ou dados indevidamente expostos.

------------------------------------------------------------------------

## 33. Uso operacional recomendado

Quando os gerentes atualizarem os dados de origem:

1. conferir se as alterações na `Database`, nos componentes e no mapa estão completas;
2. abrir o terminal na raiz do projeto;
3. executar o comando unificado, após sua validação final;
4. conferir as contagens de sinais automáticos, manuais e ignorados;
5. conferir quais abas serão alteradas;
6. autorizar a escrita somente quando os dados estiverem coerentes;
7. verificar o resultado final e os backups, se criados.

Enquanto o `executar++.sh` não estiver validado, a alternativa segura para conferência é:

```bash
python -m src.automatizacao_v5
```

O comando sem `--aplicar` não modifica a planilha. Não é necessário executar separadamente os sincronizadores quando o coordenador unificado estiver validado.

------------------------------------------------------------------------

## 34. Critérios de conclusão da V.5

A versão poderá ser considerada concluída para o fluxo operacional pretendido quando:

- a leitura de `Database`, componentes e grafo funcionar com dados atuais;
- a classificação de CAN/SHUT e demais sinais estiver revisada;
- os sinais manuais permanecerem preservados;
- o roteamento automático produzir caminhos e distâncias coerentes;
- as atualizações pontuais de `H/I/L/M/N` estiverem corretas;
- as duas abas auxiliares forem sincronizadas corretamente;
- uma execução sem alterações não realizar escrita;
- os backups forem criados antes das escritas;
- o coordenador for testado em casos de sucesso, cancelamento e falha;
- o `executar++.sh` funcionar como ponto único de entrada;
- o procedimento de recuperação estiver documentado;
- o README refletir os comandos atuais;
- os resultados forem conferidos com as restrições reais do T11.

A existência de um arquivo ou a aprovação de testes isolados não basta para marcar como concluído o fluxo de escrita integrada.

------------------------------------------------------------------------

## 35. Próximas etapas

### 35.1. Validar o comando único

Executar `./executar++.sh` no ambiente `ambiente_tupa` e confirmar que ele utiliza o módulo e o modo esperados. Verificar o comportamento quando não existem alterações pendentes.

### 35.2. Testar a aplicação em cópia da planilha

Preparar uma cópia autorizada, alterar registros controlados e verificar backups, atualização das três abas e conferência posterior. Não modificar a planilha de produção apenas para forçar um teste.

### 35.3. Criar testes do coordenador

Adicionar `testes/teste_automatizacao_v5.py` cobrindo comparação, confirmação, revalidação, backup, escrita e falhas parciais.

### 35.4. Conferir os caminhos manuais

Revisar os registros CAN e SHUT preservados e confirmar que os caminhos e as distâncias manuais necessários estão preenchidos e fisicamente corretos.

### 35.5. Finalizar documentação e README

Adicionar esta documentação em `log/doc_v5.md`, atualizar o `README.md` com os dois comandos de execução e registrar o procedimento de recuperação a partir dos backups.

------------------------------------------------------------------------

## 36. Resumo técnico da V.5

A V.5 transforma o processamento de sinais da V4 em um fluxo integrado com a Google Sheets. Os registros da `Database` são interpretados junto ao cadastro de componentes/nós, os sinais são classificados em automáticos, manuais e ignorados, e os automáticos são roteados usando o Dijkstra e as regras de custo existentes. A integração prepara os caminhos, distâncias e campos associados para atualização pontual da `Database` e gera as tabelas das abas `Sinais-Dijkstra` e `Resultados-Dijkstra`.

O coordenador `src/automatizacao_v5.py` compara o plano com o estado atual, evita escritas desnecessárias, exige confirmação quando há alterações, revalida os dados, cria backups e verifica cada escrita. O `executar++.sh` foi acrescentado como entrada operacional única, mantendo o `executar.sh` e o `main.py` da V4 para o uso tradicional.

Na última simulação observada, o sistema roteou 201 sinais automáticos, preservou 54 manuais, ignorou 20 registros e encontrou as três abas sincronizadas. Os 54 testes anteriores também passaram. Esses resultados confirmam o funcionamento do cálculo e da comparação no cenário observado, mas a escrita integrada pelo novo coordenador e o comando de shell ainda precisam ser validados com alterações controladas.

A V.5 reduz o trabalho repetitivo e melhora a rastreabilidade das atualizações. A aprovação final dos caminhos continua dependendo da conferência dos dados e das restrições físicas e elétricas do T11 pela equipe.