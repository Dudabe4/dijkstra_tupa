# DOCUMENTAÇÃO DA TERCEIRA IMPLEMENTAÇÃO DO ALGORITMO DE DIJKSTRA PARA O MAPA DO GLV

## 1. Visão geral

A V.3 evolui a implementação do algoritmo de Dijkstra utilizada para representar o mapa físico das conexões do sistema GLV de um carro de Formula SAE Elétrica.

A V.1 validou a representação do mapa como grafo e o Dijkstra básico. A V.2 separou os dados do mapa da lógica do algoritmo e passou a utilizar uma Google Sheets como fonte dos dados. A V.3 mantém essa estrutura e acrescenta um critério de roteamento configurável, considerando distância, prioridade do caminho principal, utilização acumulada dos nós e penalização direcional de entrada do main hoop.

Fluxo atual:

```text
Google Sheets
     ↓
google_sheets.py
     ↓
configurações + dados físicos
     ↓
configs.py / construir_grafo.py
     ↓
grafo + regras de custo
     ↓
validacao.py
     ↓
dijkstra.py
     ↓
main.py
     ↓
resultado + atualização da utilização
```

A V.3 é considerada finalizada quanto ao escopo funcional desenvolvido nesta etapa. As abas intermediária/final, a atualização pelo mapa oficial do chassi e a organização definitiva do workspace ficam para as próximas melhorias.

------------------------------------------------------------------------

## 2. Objetivos da V.3

- Implementar custo de roteamento configurável.
- Considerar a utilização acumulada dos nós.
- Fazer a utilização influenciar as próximas rotas.
- Priorizar o caminho principal por fator configurável.
- Penalizar entradas específicas do hoop.
- Manter custo de decisão separado da distância física.
- Manter configurações fora do código principal.
- Permitir alterações dos parâmetros pela Google Sheets.
- Manter penalizações direcionais.
- Validar o grafo antes do roteamento.
- Testar o fluxo completo.
- Preparar a estrutura para futuras restrições físicas e elétricas.

------------------------------------------------------------------------

## 3. Relação entre as versões

### V.1 --- protótipo inicial

A V.1 validou:

- representação do mapa como grafo;
- listas de adjacência;
- Dijkstra;
- pesos como comprimentos;
- origem e destino pelo terminal;
- reconstrução do caminho;
- apresentação do resultado.

O grafo era cadastrado diretamente no Python.

### V.2 --- estruturação e entrada de dados

A V.2 acrescentou:

- revisão do grafo;
- modularização;
- validações;
- Google Sheets API;
- leitura das conexões pela planilha;
- construção automática do grafo;
- inversas automáticas;
- tratamento de duplicações;
- comparação manual × planilha;
- integração do Dijkstra com o novo fluxo.

O custo ainda era:

```text
custo = comprimento físico
```

### V.3 --- custo configurável e utilização

A V.3 acrescenta:

- parâmetros de roteamento na Google Sheets;
- fator do caminho principal;
- penalização por utilização;
- contabilização acumulada;
- penalização direcional de entrada do hoop;
- separação entre custo ponderado e distância física;
- validação integrada;
- testes de múltiplas rotas;
- configuração do caminho principal sem codificá-lo diretamente no Dijkstra.

------------------------------------------------------------------------

## 4. Estrutura atual do projeto

```text
dijkstra/
├── src/
│   ├── main.py
│   ├── grafo.py
│   ├── dijkstra.py
│   ├── validacao.py
│   ├── teste_grafo.py
│   ├── google_sheets.py
│   ├── construir_grafo.py
│   └── configs.py
├── credentials/
│   └── credentials.json
└── .gitignore
```

### `main.py`

Coordena:

1. leitura da planilha;
2. carregamento das configurações;
3. construção do grafo;
4. validação;
5. entrada de origem e destino;
6. Dijkstra;
7. atualização da utilização;
8. apresentação do resultado.

### `grafo.py`

Mantém o grafo manual utilizado como referência para comparação.

### `dijkstra.py`

Contém o Dijkstra e as funções auxiliares de cálculo de custo. Não depende diretamente da Google Sheets.

### `validacao.py`

Contém verificações de nós, pesos, simetria e testes básicos.

### `teste_grafo.py`

Compara o grafo manual com o grafo construído pela planilha.

### `google_sheets.py`

Lê:

- parâmetros;
- caminho principal;
- arestas penalizadas;
- conexões físicas.

### `construir_grafo.py`

Converte as conexões físicas em lista de adjacência e cria as inversas das conexões bidirecionais.

### `configs.py`

Converte as configurações da planilha para os tipos usados pelo algoritmo e normaliza as arestas direcionais penalizadas.

------------------------------------------------------------------------

## 5. Separação entre dados, configurações e algoritmo

A V.3 mantém três responsabilidades:

### Dados físicos

- nós;
- conexões;
- comprimentos;
- conectividade do mapa.

### Configurações

- fator do caminho principal;
- penalização por utilização;
- penalização de entrada do hoop;
- caminho principal;
- arestas penalizadas.

### Algoritmo

- encontrar o caminho de menor custo segundo as regras configuradas.

Arquitetura:

```text
dados físicos → construção do grafo
configurações → regras de custo
grafo + regras → Dijkstra
```

Alterar uma conexão, comprimento ou parâmetro não exige alterar a lógica do Dijkstra.

------------------------------------------------------------------------

## 6. Google Sheets

A planilha contém as configurações e as conexões físicas.

Seção de parâmetros:

```text
Configuração | Valor

fator caminho principal | 0,2
penalização por utilização | 100
penalização entrada hoop | 5000
```

Seção do caminho principal:

```text
E2 | H2 | G2 | G3 | G1 | H1 | I1 | Y1 | K1 | K3 | K2 | L2 | V2 | V1 | N1
```

Seção de arestas penalizadas:

```text
L1,U1
L2,U2
V1,U1
V2,U2
```

Seção do grafo:

```text
no | vizinho | comprimento
```

A leitura identifica essas seções e não mistura configurações com conexões físicas.

------------------------------------------------------------------------

## 7. Leitura e configuração

`ler_planilha()` retorna:

```python
configuracoes_brutas, dados_grafo = ler_planilha()
```

As configurações possuem:

```python
{
    "parametros": {},
    "caminho_principal": [],
    "arestas_penalizadas": []
}
```

A classe `Configuracoes` converte valores como `0,2`, `100` e `5000` para `float`, mantém o caminho como lista e transforma as arestas penalizadas em tuplas direcionadas.

------------------------------------------------------------------------

## 8. Conexões físicas e duplicações

A planilha cadastra uma conexão física uma vez. Como o modelo atual considera essas conexões bidirecionais:

```text
A1 | E1 | 402.81
```

gera:

```text
A1 → E1 = 402.81
E1 → A1 = 402.81
```

A mesma conexão é normalizada internamente para detectar duplicações.

Regra:

```text
mesma conexão + mesmo comprimento
→ ignora duplicação
```

Se houver comprimentos conflitantes:

```text
mesma conexão + comprimento diferente
→ erro
```

O programa não escolhe automaticamente um dos valores.

------------------------------------------------------------------------

## 9. Grafo atual

O grafo utilizado nos testes possui:

```text
87 conexões físicas únicas
```

Como cada conexão física bidirecional é representada nas duas direções:

```text
174 entradas direcionadas
```

As 174 entradas são representações das 87 conexões físicas, não 174 conexões físicas diferentes.

------------------------------------------------------------------------

## 10. Validações

Antes da execução normal do roteamento, o `main.py` chama:

```python
validar_nos(grafo)
validar_pesos(grafo)
validar_simetria(grafo)
```

### Nós

Verifica a consistência dos vizinhos existentes no grafo.

### Pesos

Verifica pesos físicos inválidos, especialmente negativos.

### Simetria

Verifica as inversas das conexões quando a modelagem é bidirecional.

O fluxo passa a ser:

```text
leitura → construção → validação → Dijkstra
```

------------------------------------------------------------------------

## 11. Novo critério de custo

A principal mudança da V.3 é o custo usado para escolher a rota.

Conceitualmente:

```text
C_aresta =
    D_aresta × F_principal
    +
    U_destino × P_utilização
    +
    P_hoop
```

Onde:

- `D_aresta` = comprimento físico original;
- `F_principal` = fator do caminho principal;
- `U_destino` = quantidade de utilizações do nó de destino;
- `P_utilização` = penalização por utilização;
- `P_hoop` = penalização de entrada, somente quando a aresta direcionada estiver configurada.

O custo é usado para decidir a rota.

------------------------------------------------------------------------

## 12. Separação entre custo e distância física

A V.3 mantém duas informações:

### `custo_dijkstra`

Valor utilizado para escolher o caminho.

Pode incluir:

- fator do caminho principal;
- utilização;
- penalização de entrada do hoop.

### `distancia_fisica`

Soma dos comprimentos físicos originais.

Portanto:

```text
custo_dijkstra ≠ necessariamente distância física
```

Essa separação é obrigatória para interpretar corretamente os resultados.

------------------------------------------------------------------------

## 13. Caminho principal

O caminho principal configurado é:

```text
E2 → H2 → G2 → G3 → G1 → H1 → I1 → Y1 → K1 → K3 → K2 → L2 → V2 → V1 → N1
```

Os trechos são tratados como bidirecionais para o fator de prioridade:

```text
E2 ↔ H2
H2 ↔ G2
G2 ↔ G3
G3 ↔ G1
G1 ↔ H1
H1 ↔ I1
I1 ↔ Y1
Y1 ↔ K1
K1 ↔ K3
K3 ↔ K2
K2 ↔ L2
L2 ↔ V2
V2 ↔ V1
V1 ↔ N1
```

O algoritmo constrói automaticamente as arestas do caminho a partir da sequência da planilha.

------------------------------------------------------------------------

## 14. Fator do caminho principal

No teste realizado:

```text
fator caminho principal = 0,2
```

Para uma aresta do caminho principal:

```text
custo físico ajustado = comprimento × 0,2
```

Para uma aresta fora dele:

```text
custo físico ajustado = comprimento × 1,0
```

O fator não modifica o comprimento físico real.

Ele altera somente o custo utilizado para a decisão.

------------------------------------------------------------------------

## 15. Utilização acumulada

A V.3 introduz a quantidade de vezes que os nós já foram utilizados.

Depois de uma rota ser encontrada, os nós percorridos, exceto a origem, são contabilizados.

Para:

```text
A → B → C → D
```

a atualização é:

```text
B += 1
C += 1
D += 1
```

A origem não é contabilizada porque a penalização é aplicada ao entrar no nó de destino de cada aresta.

------------------------------------------------------------------------

## 16. Penalização por utilização

Ao analisar:

```text
no_atual → vizinho
```

o algoritmo consulta:

```python
utilizacao.get(vizinho, 0)
```

O custo adicional é:

```text
utilização do destino × penalização por utilização
```

Assim, quanto mais um nó já foi utilizado, maior fica o custo de entrar nele.

A utilização permanece acumulada entre as solicitações executadas na mesma execução do programa.

------------------------------------------------------------------------

## 17. Entrada do hoop

A V.3 implementa penalização somente para entradas configuradas do hoop.

Arestas atuais:

```text
L1 → U1
L2 → U2
V1 → U1
V2 → U2
```

Elas são direcionais.

Portanto, cadastrar:

```text
L2 → U2
```

não implica penalizar:

```text
U2 → L2
```

A penalização não é aplicada automaticamente para:

- sair do hoop;
- movimentar-se internamente;
- utilizar U3 internamente.

Somente as arestas configuradas recebem a penalização.

------------------------------------------------------------------------

## 18. Cálculo de uma aresta

Para cada vizinho, o algoritmo:

1. verifica se a aresta pertence ao caminho principal;
2. aplica o fator correspondente;
3. consulta a utilização do nó de destino;
4. adiciona a penalização de utilização;
5. verifica a aresta direcionada de hoop;
6. adiciona a penalização de hoop quando aplicável;
7. retorna o custo final da aresta.

O comprimento original permanece disponível para a distância física.

------------------------------------------------------------------------

## 19. Estruturas do Dijkstra

A V.3 utiliza:

### `custos`

Menor custo de roteamento conhecido.

### `distancias_fisicas`

Soma dos comprimentos físicos do caminho.

### `predecessores`

Nó anterior utilizado para reconstruir o caminho.

### `fila_prioridade`

Fila baseada em `heapq`, ordenada pelo custo de roteamento.

A estrutura básica do Dijkstra permanece a mesma, mas o peso de decisão agora é configurável.

------------------------------------------------------------------------

## 20. Casos básicos mantidos

O algoritmo continua tratando:

### Origem inexistente

Gera erro informando que o nó não existe.

### Destino inexistente

Gera erro informando que o nó não existe.

### Origem igual ao destino

Retorna:

```text
caminho = [origem]
custo = 0
distância física = 0
```

### Destino inalcançável

Retorna indicação de ausência de caminho.

### Peso negativo

Gera erro, pois comprimentos negativos não são válidos e violam a condição necessária para Dijkstra.

------------------------------------------------------------------------

## 21. Teste da primeira rota

Configuração:

```text
fator caminho principal = 0,2
penalização por utilização = 100
penalização entrada hoop = 5000
```

Solicitação:

```text
E2 → N1
```

Resultado:

```text
E2 → H2 → G2 → G3 → G1 → H1 → I1 → Y1 → K1 → K3 → K2 → L2 → V2 → V1 → N1
```

Distância física:

```text
4795,27 mm
```

Custo Dijkstra:

```text
959,05
```

Na primeira execução não havia utilização acumulada.

------------------------------------------------------------------------

## 22. Teste da segunda rota

A mesma solicitação:

```text
E2 → N1
```

foi executada novamente.

Resultado:

```text
E2 → I2 → L2 → V2 → V1 → N1
```

Distância física:

```text
2641,28 mm
```

Custo Dijkstra:

```text
1872,09
```

A mudança demonstra que a utilização acumulada passou a influenciar a decisão.

------------------------------------------------------------------------

## 23. Teste da terceira rota

A mesma solicitação foi executada uma terceira vez.

Resultado:

```text
E2 → H2 → G2 → G3 → G1 → H1 → I1 → Y1 → K1 → M1 → N1
```

Distância física:

```text
2853,14 mm
```

Custo Dijkstra:

```text
1974,02
```

O resultado reforçou que a utilização é acumulada e interfere nas rotas seguintes.

------------------------------------------------------------------------

## 24. Interpretação dos testes

Os testes demonstraram:

```text
1ª rota → caminho principal
2ª rota → alternativa
3ª rota → nova alternativa
```

Portanto, a V.3 deixou de procurar simplesmente o caminho fisicamente mais curto.

Ela procura o caminho de menor custo segundo as prioridades configuradas.

Isso confirma o funcionamento da penalização por utilização.

------------------------------------------------------------------------

## 25. Calibração da penalização por utilização

O valor utilizado no teste:

```text
100
```

teve influência significativa.

Na segunda execução, ele foi suficiente para fazer o algoritmo abandonar partes do caminho principal já utilizadas.

Isso não caracteriza necessariamente erro. Significa que a magnitude da penalização precisa ser calibrada de acordo com a prioridade física desejada.

Valores como:

```text
5
10
20
50
100
```

podem ser comparados futuramente.

A escolha definitiva depende do objetivo real do roteamento.

------------------------------------------------------------------------

## 26. Estado do mapa físico

A V.3 utiliza o mapa disponível durante esta etapa.

As 87 conexões físicas utilizadas nos testes não devem ser tratadas como o mapa oficial definitivo do T11.

Quando o gerente do chassi fornecer o mapa oficialmente definido, deverão ser revisados:

- nós;
- conexões;
- distâncias;
- componentes;
- bidirecionalidade;
- possíveis conexões unidirecionais;
- caminho principal;
- entradas do hoop;
- possibilidades de roteamento.

Depois disso, todo o fluxo deverá ser testado novamente.

------------------------------------------------------------------------

## 27. Bidirecionalidade

As conexões físicas atuais são modeladas como bidirecionais.

Assim:

```text
A1 → E1
```

implica:

```text
E1 → A1
```

Essa hipótese ainda deve ser confirmada no mapa oficial.

Se forem encontradas conexões fisicamente unidirecionais, a construção do grafo deverá ser modificada para representar essa restrição.

As penalizações de hoop são uma exceção importante: elas possuem direção própria e não devem ser normalizadas como arestas físicas bidirecionais.

------------------------------------------------------------------------

## 28. O que a V.3 já consegue fazer

- ler conexões da Google Sheets;
- ler parâmetros de roteamento;
- ler o caminho principal;
- ler arestas direcionais penalizadas;
- construir o grafo automaticamente;
- criar inversas;
- tratar duplicações;
- detectar comprimentos conflitantes;
- validar nós;
- validar pesos;
- validar simetria;
- normalizar origem e destino;
- executar Dijkstra;
- priorizar o caminho principal;
- aplicar fator configurável;
- contabilizar utilização;
- aplicar penalização por utilização;
- acumular utilização entre rotas;
- aplicar penalização direcional de entrada do hoop;
- reconstruir caminhos;
- informar distância física;
- informar custo Dijkstra;
- tratar ausência de caminho;
- tratar origem igual ao destino;
- manter dados, configurações e algoritmo separados.

------------------------------------------------------------------------

## 29. O que foi validado

### Google Sheets

Leitura confirmada de:

```text
parâmetros
caminho principal
arestas penalizadas
conexões físicas
```

### Construção

As conexões físicas são convertidas corretamente para lista de adjacência.

### Duplicações

Conexões repetidas são tratadas e comprimentos conflitantes geram erro.

### Validações

O grafo é validado antes do roteamento.

### Dijkstra

Executa sobre o grafo gerado automaticamente.

### Utilização

A utilização acumulada altera as rotas seguintes.

### Caminho principal

O fator configurado influencia o custo.

### Hoop

A penalização direcional está implementada.

### Distância física

Permanece separada do custo ponderado.

### Fluxo completo

O fluxo validado é:

```text
Google Sheets
→ leitura
→ configurações
→ construção
→ validação
→ Dijkstra
→ atualização da utilização
→ resultado
```

------------------------------------------------------------------------

## 30. Funcionalidades que ficam para as próximas melhorias

Estas funcionalidades foram previstas, mas não são necessárias para considerar a V.3 funcionalmente finalizada.

### 30.1. Aba intermediária por distância

Ainda não foi criada a aba específica para registrar caminhos usando somente distância.

Ela servirá futuramente como referência para comparar:

```text
menor distância física
```

e:

```text
menor custo considerando as regras da V.3
```

### 30.2. Aba final de resultados

Ainda não foi criada a geração automática da aba final.

A estrutura planejada deverá permitir registrar, por sinal:

- sinal;
- origem;
- destino;
- caminho considerando distância + utilização;
- comprimento;
- componente de origem;
- componente de destino;
- caminho considerando somente distância.

### 30.3. Roteamento automático por sinais

O programa ainda recebe origem e destino pelo terminal.

O processamento automático de todos os sinais será implementado posteriormente.

### 30.4. Restrições de caminho

Ainda não foram implementados:

- nós obrigatórios;
- nós proibidos;
- conexões proibidas;
- regiões obrigatórias;
- restrições por tipo de sinal.

### 30.5. Restrições elétricas e físicas

Ainda não foram incorporados critérios como:

- corrente;
- tipo de sinal;
- separação;
- interferência eletromagnética;
- segurança;
- manutenção;
- confiabilidade;
- montagem.

### 30.6. Custos adicionais

Ainda não foram implementados custos de:

- conectores;
- emendas;
- outros critérios físicos.

### 30.7. Visualização

Ainda não existe visualização gráfica do grafo ou do caminho.

------------------------------------------------------------------------

## 31. Organização futura do workspace

A estrutura atual já está modularizada, mas a organização definitiva em pastas será feita posteriormente.

Uma possível organização futura é:

```text
src/
testes/
config/
docs/
credentials/
```

A estrutura exata será definida quando a implementação estiver mais estável.

Após mover arquivos, será necessário revisar:

- imports;
- caminhos;
- execução;
- testes;
- `.gitignore`;
- documentação.

Essa etapa será feita depois das melhorias funcionais para evitar retrabalho.

------------------------------------------------------------------------

## 32. Atualização futura pelo mapa oficial

Quando o gerente do chassi enviar o mapa oficial:

1. atualizar nós;
2. atualizar conexões;
3. atualizar comprimentos;
4. atualizar componentes;
5. confirmar bidirecionalidade;
6. cadastrar eventuais conexões unidirecionais;
7. atualizar caminho principal;
8. atualizar entradas do hoop;
9. executar validações;
10. repetir os testes de roteamento.

A partir dessa etapa, os resultados poderão ser avaliados sobre o mapa oficial do T11.

------------------------------------------------------------------------

## 33. Separação entre decisão e resultado físico

A V.3 deve manter permanentemente a distinção:

```text
custo de decisão
```

versus:

```text
distância física
```

O custo pode incluir:

```text
distância ajustada
+
utilização
+
penalizações
```

A distância física continua sendo:

```text
soma dos comprimentos originais
```

Isso permite analisar por que determinado caminho foi escolhido sem perder a informação física real do chicote.

------------------------------------------------------------------------

## 34. Limitações da V.3

As principais limitações atuais são:

- o mapa físico ainda não é o mapa oficial definitivo;
- os valores de penalização ainda precisam de calibração;
- o processamento automático de sinais ainda não existe;
- restrições elétricas e mecânicas ainda não estão incorporadas;
- conectores e emendas ainda não possuem custos;
- não há exportação automática para a aba final;
- não há visualização gráfica;
- a organização definitiva do workspace ainda será feita.

Essas limitações representam evolução futura e não impedem o fechamento funcional da V.3.

------------------------------------------------------------------------

## 35. Por que a V.3 foi uma etapa necessária

A V.2 criou uma base em que o mapa podia ser alterado sem modificar o algoritmo.

A V.3 utiliza essa base para representar uma parte mais realista do problema de roteamento.

A evolução foi:

```text
V.1
Dijkstra básico
     ↓
V.2
Google Sheets + grafo automático
     ↓
V.3
custo configurável + utilização + prioridades
```

A separação entre dados e algoritmo permitiu adicionar os novos critérios sem reconstruir o projeto.

------------------------------------------------------------------------

## 36. Considerações sobre Dijkstra

Dijkstra continua adequado porque:

- trabalha com pesos não negativos;
- encontra o menor custo;
- permite grafos direcionados ou não direcionados;
- permite pesos definidos por uma função de custo;
- permite reconstruir o caminho;
- é simples e suficiente para o tamanho atual do grafo.

A V.3 demonstra que o algoritmo pode utilizar custos que dependem da utilização acumulada, desde que os custos de cada execução sejam calculados antes das decisões correspondentes.

------------------------------------------------------------------------

## 37. Complexidade computacional

A implementação utiliza uma fila de prioridade baseada em heap.

Para:

```text
V = número de nós
E = número de arestas
```

a complexidade típica é:

```text
O((V + E) log V)
```

O tamanho atual do grafo é pequeno o suficiente para que o custo computacional seja baixo.

A utilização acumulada altera os pesos das arestas, mas não muda a estrutura fundamental do algoritmo.

------------------------------------------------------------------------

## 38. Estado final da V.3

A V.3 está funcionalmente finalizada dentro do escopo trabalhado.

O sistema possui:

```text
Google Sheets
      ↓
leitura dos dados
      ↓
leitura das configurações
      ↓
construção automática
      ↓
validação
      ↓
Dijkstra com custo configurável
      ↓
utilização acumulada
      ↓
resultado
```

O algoritmo agora combina, quando aplicável:

```text
distância
+
prioridade do caminho principal
+
utilização dos nós
+
penalização de entrada do hoop
```

sem misturar esses valores com a distância física real.

------------------------------------------------------------------------

## 39. Próximas etapas

### Etapa 1 --- planilhas

Implementar:

- aba intermediária por distância;
- aba final de resultados;
- processamento automático dos sinais;
- comparação entre distância e custo final.

### Etapa 2 --- mapa oficial

Quando o mapa for recebido:

- atualizar o grafo;
- conferir conexões;
- conferir distâncias;
- conferir nós;
- conferir componentes;
- confirmar bidirecionalidade;
- atualizar caminho principal;
- atualizar hoop.

### Etapa 3 --- testes

Após o mapa oficial:

- executar validações;
- testar múltiplas rotas;
- testar utilização acumulada;
- testar penalizações;
- conferir resultados físicos.

### Etapa 4 --- organização

- separar arquivos em pastas;
- ajustar imports;
- revisar caminhos;
- revisar testes;
- revisar `.gitignore`;
- revisar documentação.

### Etapa 5 --- fechamento do projeto

- executar teste completo;
- revisar resultados;
- atualizar documentação;
- organizar o repositório;
- realizar o commit correspondente.

------------------------------------------------------------------------

## 40. Resumo técnico da V.3

A V.3 implementa um sistema de roteamento baseado em Dijkstra no qual o grafo físico é obtido automaticamente de uma Google Sheets e o custo de cada conexão pode ser configurado externamente.

O sistema separa:

```text
dados físicos
```

de:

```text
regras de roteamento
```

e:

```text
algoritmo
```

O custo de decisão pode considerar:

```text
comprimento × fator do caminho principal
+
utilização do nó de destino × penalização
+
penalização direcional de entrada do hoop
```

Enquanto isso, a distância física continua sendo calculada independentemente.

Os testes realizados demonstraram:

```text
1ª rota → caminho principal
2ª rota → alternativa
3ª rota → nova alternativa
```

quando a utilização acumulada passa a influenciar o custo.

A V.3 está, portanto, encerrada como a versão funcional desta etapa. As próximas evoluções concentram-se nas planilhas de resultados, no mapa oficial do T11, nas restrições físicas/elétricas e na organização definitiva do workspace.
