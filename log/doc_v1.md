# DOCUMENTAÇÃO DA PRIMEIRA IMPLEMENTAÇÃO DO ALGORITMO DE DIJKSTRA PARA O MAPA DO GLV


## 1. Visão geral do projeto

O objetivo desta primeira implementação é desenvolver uma ferramenta capaz de representar o mapa físico das conexões do sistema GLV de um carro de Formula SAE Elétrica e encontrar o caminho de menor custo entre dois pontos desse mapa.

A ideia central é transformar o mapa físico do chicote, dos componentes e das conexões elétricas em uma estrutura matemática chamada grafo. Nesse grafo:

- Cada nó representa um ponto de conexão, componente ou região do sistema.
- Cada aresta representa uma conexão entre dois nós.
- Cada peso representa o custo de percorrer aquela conexão.
Na versão atual, o custo considerado é o comprimento físico da conexão, medido em milímetros. Portanto, o programa procura o caminho que conecta a origem ao destino utilizando o menor comprimento total possível.

A implementação foi feita em Python e, nesta primeira versão, o grafo está cadastrado diretamente no código. O programa recebe os nós de origem e destino pelo terminal, executa o algoritmo de Dijkstra e mostra o caminho encontrado juntamente com o comprimento total.

Essa versão foi pensada como uma base funcional para validar a lógica do algoritmo antes de adicionar características mais específicas do sistema real, como restrições elétricas, caminhos proibidos, conexões unidirecionais, tipos de sinal, componentes obrigatórios e leitura automática de arquivos.


## 2. Objetivo da primeira versão

A primeira versão possui os seguintes objetivos:

- Representar o mapa do GLV em um grafo.
- Associar cada conexão a um comprimento físico.
- Permitir que o usuário informe dois nós.
- Verificar se os nós informados existem.
- Calcular o caminho de menor custo entre eles.
- Mostrar a sequência de nós percorrida.
- Mostrar o comprimento total do caminho.
- Tratar situações especiais, como origem igual ao destino e ausência de caminho.
- Manter o código organizado em funções para facilitar futuras modificações.

A implementação ainda não pretende resolver todas as regras reais do projeto elétrico. Ela representa uma primeira aproximação matemática do problema.

## 3. Fundamentação teórica

### 3.1. O que é um grafo

Um grafo é uma estrutura matemática utilizada para representar objetos e as relações entre eles.

Um grafo é formado principalmente por:

- Vértices ou nós: representam os elementos do sistema.
- Arestas ou conexões: representam as relações entre os nós.
- Pesos: representam algum custo associado às arestas. No contexto do GLV, podemos interpretar esses elementos da seguinte forma:
- Um nó pode representar um componente, uma conexão, uma emenda ou um ponto de passagem.
- Uma aresta representa um trecho físico do chicote entre dois nós.
- O peso da aresta representa o comprimento desse trecho.

Por exemplo, se existe uma conexão entre os nós A1 e E1 com comprimento de 250 mm, essa relação pode ser representada como:

A1 → E1, peso = 250 mm

Caso a conexão também possa ser percorrida no sentido contrário, temos:

A1 → E1, peso = 250 mm

E1 → A1, peso = 250 mm

### 3.2. Grafo ponderado

O grafo utilizado é ponderado, pois cada conexão possui um valor numérico associado.

Esse valor é o peso da aresta. Na primeira versão, esse peso corresponde ao comprimento físico da conexão em milímetros.

Se um caminho possui três trechos:

A → B com 100 mm

B → C com 250 mm

C → D com 150 mm

O custo total desse caminho é:

100 + 250 + 150 = 500 mm

O algoritmo de Dijkstra utiliza esses pesos para comparar diferentes caminhos e encontrar aquele cujo custo total é menor.

### 3.3. Grafo direcionado e não direcionado

Um grafo pode ser:

- Direcionado: uma conexão pode existir em apenas um sentido.
- Não direcionado: uma conexão pode ser percorrida nos dois sentidos.

Na implementação atual, as conexões foram cadastradas considerando que os nós podem ir e voltar. Por isso, uma conexão entre dois nós normalmente aparece nas duas direções dentro do dicionário do grafo.

Por exemplo:

grafo = {

   "A1": [("E1", 250)],

   "E1": [("A1", 250)]

}

Isso significa que existe uma conexão de A1 para E1 e também de E1 para A1.

Essa escolha foi feita como uma simplificação inicial. Entretanto, ela ainda precisa ser confirmada com o responsável pelo projeto, pois no sistema real podem existir situações em que:

- Uma conexão só pode ser utilizada em um sentido.
- Um caminho de alimentação não deve ser tratado como retorno.
- Determinados sinais não podem circular livremente.
- Alguns componentes podem impedir a passagem em determinada direção.

Portanto, a bidirecionalidade atual é uma hipótese de modelagem, e não necessariamente uma regra definitiva do sistema GLV.

### 3.4. Caminho em um grafo

Um caminho é uma sequência de nós conectados por arestas.

Por exemplo:

A1 → E1 → I1 → Y1 → K1

Esse caminho representa uma sequência de conexões físicas entre A1 e K1.

O comprimento total do caminho é obtido somando os pesos de todas as arestas utilizadas.

### 3.5. Caminho de menor custo

Entre dois nós, podem existir vários caminhos possíveis.

Por exemplo, para sair de A1 e chegar a S2, o programa pode encontrar diferentes alternativas:

Caminho 1:

A1 → E1 → I1 → Y1 → K1 → K3 → K2 → Q2 → S2

Caminho 2:

A1 → B1 → C1 → D1 → S1 → S2

Caminho 3:

A1 → F1 → G1 → H1 → L1 → W1 → S2

Cada caminho possui um comprimento total diferente. O objetivo do algoritmo é encontrar o caminho com a menor soma de pesos.

### 3.6. Algoritmo de Dijkstra

O algoritmo de Dijkstra é um algoritmo clássico utilizado para encontrar o caminho de menor custo entre um nó de origem e os demais nós de um grafo ponderado.

Ele funciona corretamente quando os pesos das arestas são não negativos.

No caso deste projeto, isso faz sentido porque um comprimento físico não pode ser negativo. Uma conexão pode ter comprimento zero em um caso especial de modelagem, mas não deve possuir comprimento negativo.

A ideia principal do algoritmo é:

- Considerar inicialmente que a distância até todos os nós é infinita.
- Definir a distância da origem como zero.
- Escolher o nó ainda não processado com menor distância conhecida.
- Verificar seus vizinhos.
- Tentar melhorar as distâncias conhecidas até esses vizinhos.
- Repetir o processo até encontrar o destino ou até não existirem mais nós alcançáveis.

Esse processo é chamado de relaxamento das arestas.

### 3.7. Relaxamento de uma aresta

Suponha que o algoritmo esteja no nó A e exista uma conexão até B com peso 100.

Se a distância conhecida até A é 300, então o caminho passando por A até B teria custo:

300 + 100 = 400

Se a distância anteriormente conhecida até B era 500, o algoritmo atualiza essa distância para 400, pois encontrou um caminho melhor.

Esse processo pode ser descrito por:

nova_distancia = distancia_atual + peso_da_aresta

Se:

nova_distancia < distancia_conhecida

então a distância conhecida é atualizada.

Além da distância, também é armazenado o nó anterior utilizado para chegar ao vizinho. Isso permite reconstruir o caminho depois que o algoritmo termina.


## 4. Estrutura geral do código

O código foi organizado em algumas partes principais:

- Importação da biblioteca necessária.
- Dicionário com os componentes associados aos nós.
- Dicionário que representa o grafo.
- Função dijkstra.
- Função mostrar_resultado.
- Função main.
- Bloco de execução principal.

Essa organização evita que toda a lógica fique concentrada em um único bloco de código e facilita futuras alterações.

## 5. Importação da biblioteca heapq

O código começa com:

import heapq

A biblioteca heapq fornece uma implementação de fila de prioridade baseada em heap.

Uma fila de prioridade é uma estrutura em que o elemento com menor prioridade numérica é retirado primeiro.

No algoritmo de Dijkstra, precisamos sempre escolher o nó cuja distância conhecida até a origem é a menor entre os nós ainda não processados.

Por isso, a fila armazena elementos no formato:

(distancia, no)

Por exemplo:

(0, "A1")

(250, "E1")

(500, "B1")

Quando esses elementos são retirados da fila, o menor valor de distância é escolhido primeiro.

O uso de heapq torna essa seleção mais eficiente do que procurar manualmente, a cada etapa, o menor valor em uma lista.


## 6. Dicionário de componentes por nó

O código possui uma estrutura chamada componentes_por_no.
Ela associa cada nó aos componentes ou elementos relacionados a ele.

A ideia é separar duas informações diferentes:

- O grafo representa as conexões e os comprimentos.
- O dicionário de componentes representa quais componentes estão associados a cada nó. Essa separação é importante porque um nó não precisa ser apenas um componente. Ele pode representar, por exemplo:
- Um ponto de conexão.
- Uma emenda.
- Um terminal.
- Uma região do chicote.
- Um componente físico.
- Um ponto de passagem entre diferentes trechos.

A estrutura também pode ser útil futuramente para mostrar informações mais detalhadas sobre o caminho encontrado.

Por exemplo, em vez de mostrar somente:

A1 → E1 → I1 → Y1

O programa poderia mostrar:

A1 → E1 → I1 → Y1

Componentes envolvidos:

componente associado a A1;

componente associado a E1;

componente associado a I1;

componente associado a Y1.

Na versão atual, essa informação está cadastrada, mas ainda não é utilizada diretamente no cálculo do Dijkstra. Ela funciona como uma base para futuras funcionalidades de detalhamento dos resultados.

## 7. Representação do grafo

O grafo foi representado por um dicionário Python.

A estrutura geral é:

grafo = {

   "A1": [("E1", 250), ("F1", 370.94)],

   "E1": [("A1", 250), ("I1", 300)],

   ...

}

Cada chave do dicionário representa um nó.

O valor associado a cada chave é uma lista de vizinhos. Cada vizinho é representado por uma tupla contendo:
O nome do nó vizinho.
O peso da conexão até esse vizinho.

Por exemplo:

"A1": [("E1", 250), ("F1", 370.94)]

significa que o nó A1 possui duas conexões:

- A1 até E1, com comprimento de 250 mm.
- A1 até F1, com comprimento de 370,94 mm.

Essa forma de representação é chamada de lista de adjacência.

### 7.1. Por que foi utilizada uma lista de adjacência

Existem diferentes formas de representar um grafo. Algumas possibilidades são:

- Matriz de adjacência.
- Lista de adjacência.
- Lista de arestas.

A lista de adjacência foi escolhida porque é simples e eficiente para o tipo de problema atual.

Ela permite acessar rapidamente os vizinhos de um nó sem precisar percorrer todas as conexões do grafo.

Por exemplo, para descobrir as conexões de A1, basta acessar:

grafo["A1"]

Isso retorna a lista de vizinhos de A1.

Essa estrutura também facilita a utilização do Dijkstra, pois o algoritmo precisa justamente percorrer os vizinhos do nó que está sendo processado.

### 7.2. Exemplo de leitura do grafo

Considere:

grafo = {

   "A1": [("E1", 250), ("F1", 370.94)],

   "E1": [("A1", 250), ("I1", 400)]

}

Nesse exemplo:

- A1 está conectado a E1.
- A1 está conectado a F1.
- E1 está conectado a A1.
- E1 está conectado a I1.

O peso de cada conexão está indicado na segunda posição da tupla.


## 8. Função dijkstra

A função principal do algoritmo possui a seguinte estrutura conceitual:

def dijkstra(grafo, origem, destino):

Ela recebe três argumentos:

- grafo: estrutura que contém os nós, vizinhos e pesos.
- origem: nó a partir do qual o caminho será calculado.
- destino: nó até o qual se deseja chegar.

A função retorna, quando existe um caminho:

- A distância total mínima.
- A sequência de nós que compõe o caminho.

Quando não existe caminho, a função retorna uma indicação de que o destino é inalcançável.


## 9. Validação dos nós de origem e destino

A primeira etapa da função verifica se os nós informados existem no grafo.

A lógica é equivalente a:

if origem not in grafo or destino not in grafo:

   ...

Essa verificação evita que o programa tente executar o algoritmo com um nó que não foi cadastrado.

Por exemplo, se o usuário informar:

origem = "A1"

destino = "Z9"

e Z9 não existir no dicionário, o programa não deve tentar procurar seus vizinhos.

Essa validação é importante porque evita erros de acesso ao dicionário e também fornece uma resposta mais clara ao usuário.


## 10. Tratamento do caso origem igual ao destino

O código também trata o caso em que o nó de origem é igual ao nó de destino.

Por exemplo:

origem = "A1"

destino = "A1"

Nesse caso, não é necessário percorrer nenhuma conexão. O caminho já está completo.

A distância mínima é:

0 mm

E o caminho é:

A1

Esse tratamento também evita que o algoritmo execute etapas desnecessárias.

## 11. Inicialização das distâncias

O algoritmo cria um dicionário chamado distancias.

Ele armazena a menor distância conhecida entre a origem e cada nó.

Inicialmente, todas as distâncias são consideradas infinitas:

distancias = {no: float("inf") for no in grafo}

O valor:

float("inf")

representa infinito positivo em Python.

Isso significa que, inicialmente, o algoritmo considera que ainda não conhece nenhum caminho até aquele nó.

Depois, a distância da origem é definida como zero:

distancias[origem] = 0

Por exemplo, se o grafo possui os nós A1, E1, I1 e S2, a inicialização seria conceitualmente:

distancias = {

   "A1": infinito,

   "E1": infinito,

   "I1": infinito,

   "S2": infinito

}

Depois da definição da origem:

distancias = {

   "A1": 0,

   "E1": infinito,

   "I1": infinito,

   "S2": infinito

}

Isso representa que o custo para sair da origem e chegar à própria origem é zero.


## 12. Dicionário de predecessores

Além das distâncias, o código cria um dicionário chamado predecessores.

Ele armazena o nó anterior utilizado para alcançar cada nó pelo melhor caminho conhecido.

Por exemplo:

predecessores["I1"] = "E1"

significa que, no melhor caminho conhecido até I1, o nó anterior é E1.

Essa estrutura é necessária porque o algoritmo não deve retornar apenas o comprimento total. Ele também precisa informar quais nós formam o caminho.

Sem o dicionário de predecessores, seria possível descobrir a distância mínima, mas não seria simples reconstruir a sequência de conexões utilizada.

Inicialmente, os predecessores são definidos como None:

predecessores = {no: None for no in grafo}

### 12.1. Exemplo de atualização dos predecessores

Suponha que o algoritmo encontre o seguinte caminho:

A1 → E1 → I1

Nesse caso, os predecessores serão:

predecessores["E1"] = "A1"

predecessores["I1"] = "E1"

Quando o algoritmo chegar ao destino, ele poderá voltar pelos predecessores:

I1 → E1 → A1

Depois, basta inverter a sequência para obter:

A1 → E1 → I1

## 13. Inicialização da fila de prioridade

A fila de prioridade é criada com a distância da origem:

fila = [(0, origem)]

A estrutura inicial contém apenas:

(0, "A1")

Isso significa que o nó A1 possui distância conhecida igual a zero e deve ser processado primeiro.

A fila será atualizada durante a execução sempre que o algoritmo encontrar um caminho melhor para algum vizinho.


## 14. Laço principal do algoritmo

O processamento principal ocorre dentro de um laço que continua enquanto houver elementos na fila de prioridade.

A lógica geral é:

while fila:

   ...

Enquanto a fila não estiver vazia, ainda existem nós que podem ser processados.

A cada repetição, o algoritmo retira da fila o elemento com menor distância conhecida.


## 15. Retirada do nó com menor distância

A operação:

distancia_atual, no_atual = heapq.heappop(fila)

retira da fila o elemento de menor valor.

Por exemplo, se a fila contém:

[(250, "E1"), (500, "F1"), (700, "I1")]

o primeiro elemento retirado será:

(250, "E1")

Isso significa que E1 é o nó com menor distância conhecida naquele momento.

A variável distancia_atual armazena a distância até o nó atual.

A variável no_atual armazena o nome do nó que será processado.


## 16. Descarte de entradas antigas da fila

Durante o algoritmo, um mesmo nó pode ser inserido várias vezes na fila.

Isso acontece porque o algoritmo pode encontrar inicialmente um caminho de custo maior e, posteriormente, descobrir um caminho melhor.

Por exemplo:

- Primeiro, o nó E1 é encontrado com distância 500.
- Depois, é encontrado um caminho melhor até E1 com distância 300.

Nesse caso, a fila pode conter:

(500, "E1")

(300, "E1")

Quando o elemento de distância 300 for retirado, ele será processado normalmente.

Quando o elemento de distância 500 for retirado depois, ele estará desatualizado. O código verifica isso comparando a distância retirada com a distância atualmente registrada:

if distancia_atual > distancias[no_atual]:

   continue

Se a distância retirada for maior do que a distância conhecida, o algoritmo ignora essa entrada e passa para a próxima.

Essa verificação evita processamentos desnecessários e mantém o algoritmo eficiente.


## 17. Encerramento antecipado ao encontrar o destino

O código verifica se o nó atual é o destino:

if no_atual == destino:

   break

Quando o nó de destino é retirado da fila de prioridade, significa que sua menor distância foi encontrada.

Como o Dijkstra processa os nós em ordem crescente de distância, não é necessário continuar explorando o restante do grafo depois desse momento.

Essa interrupção reduz o tempo de execução, principalmente quando o destino está relativamente próximo da origem.


## 18. Percorrendo os vizinhos do nó atual

Depois de selecionar o nó atual, o algoritmo percorre todos os seus vizinhos.

A estrutura utilizada é equivalente a:

for vizinho, peso in grafo[no_atual]:

Cada elemento da lista contém:

- vizinho: nó conectado ao nó atual.
- peso: comprimento da conexão entre o nó atual e o vizinho.

Por exemplo, se:

grafo["A1"] = [

   ("E1", 250),

   ("F1", 370.94)

]

o laço processará primeiro uma conexão e depois a outra.


## 19. Verificação de pesos negativos

O código verifica se o peso de uma conexão é negativo:

if peso < 0:

   raise ValueError(...)

Essa verificação é importante porque o algoritmo de Dijkstra pressupõe que todos os pesos sejam maiores ou iguais a zero.

No contexto físico do projeto, comprimentos negativos não fazem sentido. Portanto, se um comprimento negativo aparecer no cadastro, isso provavelmente indica um erro de preenchimento ou modelagem.

Em vez de continuar com um dado inválido, o programa interrompe a execução e informa o problema.


## 20. Cálculo da nova distância

Para cada vizinho, o algoritmo calcula:

nova_distancia = distancia_atual + peso

Esse valor representa o custo de chegar ao vizinho passando pelo nó atual.

Por exemplo, se:

- A distância até o nó atual é 500 mm.
- A conexão até o vizinho possui 200 mm.

Então:

nova_distancia = 500 + 200

nova_distancia = 700 mm


## 21. Comparação com a distância conhecida

Depois de calcular a nova distância, o algoritmo verifica se ela é menor que a distância já registrada para o vizinho:

if nova_distancia < distancias[vizinho]:

Se a nova distância for menor, significa que foi encontrado um caminho melhor.

Nesse caso, o código atualiza:

- A distância do vizinho.
- O predecessor do vizinho.
- A fila de prioridade.


## 22. Atualização da distância

Quando um caminho melhor é encontrado, o código faz:

distancias[vizinho] = nova_distancia

Isso substitui o valor anterior pelo novo custo mínimo conhecido.

Por exemplo, se anteriormente:

distancias["I1"] = 900

e o algoritmo encontra um caminho com custo 750, a atualização será:

distancias["I1"] = 750


## 23. Atualização do predecessor

Junto com a distância, o código registra de onde o vizinho foi alcançado:

predecessores[vizinho] = no_atual

Por exemplo:

predecessores["I1"] = "E1"

Isso indica que o melhor caminho conhecido até I1 passa por E1.

Esse registro será utilizado posteriormente para reconstruir o caminho completo.


## 24. Inserção na fila de prioridade

Depois de atualizar a distância, o novo par é inserido na fila:

heapq.heappush(fila, (nova_distancia, vizinho))

Assim, o vizinho será processado posteriormente na ordem correta de distância.

A fila pode conter diferentes nós e também diferentes versões de distância para o mesmo nó. Por isso, a verificação de entradas antigas explicada anteriormente é necessária.

## 25. Exemplo simplificado de execução

Considere o seguinte grafo:

A → B, peso 100

A → C, peso 300

B → C, peso 50

C → D, peso 200

B → D, peso 500

Deseja-se encontrar o menor caminho de A até D.

Inicialmente:

distancias[A] = 0

distancias[B] = infinito

distancias[C] = infinito

distancias[D] = infinito

Fila:

(0, A)

O algoritmo processa A.

A partir de A:

- Até B: 0 + 100 = 100.
- Até C: 0 + 300 = 300.

Atualizações:

distancias[B] = 100

distancias[C] = 300

Fila:

(100, B)

(300, C)

O algoritmo processa B.

A partir de B:

- Até C: 100 + 50 = 150. Como 150 é menor que 300, a distância de C é atualizada.
- Até D: 100 + 500 = 600.

Atualizações:

distancias[C] = 150

distancias[D] = 600

Fila:

(150, C)

(300, C)

(600, D)

O algoritmo processa C com distância 150.

A partir de C:

- Até D: 150 + 200 = 350.

Como 350 é menor que 600, a distância de D é atualizada.

Agora:

distancias[D] = 350

O predecessor de D será C.

Quando D for retirado da fila, o algoritmo encerra.

O caminho reconstruído será:

A → B → C → D

Comprimento total:

100 + 50 + 200 = 350


## 26. Reconstrução do caminho

Depois que o algoritmo encontra o destino, o código reconstrói o caminho utilizando o dicionário de predecessores.

A reconstrução começa pelo destino.

Suponha que:

destino = "S2"

e os predecessores sejam:

predecessores["S2"] = "Q2"

predecessores["Q2"] = "K2"

predecessores["K2"] = "K3"

predecessores["K3"] = "K1"

predecessores["K1"] = "Y1"

predecessores["Y1"] = "I1"

predecessores["I1"] = "E1"

predecessores["E1"] = "A1"

predecessores["A1"] = None

O algoritmo começa com:

caminho = ["S2"]

Depois, volta para o predecessor de S2:

caminho = ["S2", "Q2"]

Em seguida:

caminho = ["S2", "Q2", "K2"]

Esse processo continua até chegar à origem.

A sequência obtida inicialmente estará invertida:

S2 → Q2 → K2 → K3 → K1 → Y1 → I1 → E1 → A1

Por isso, o código utiliza uma operação de inversão, obtendo:

A1 → E1 → I1 → Y1 → K1 → K3 → K2 → Q2 → S2


## 27. Tratamento de destino inalcançável

Pode acontecer de o destino existir no grafo, mas não existir nenhum caminho entre ele e a origem.

Por exemplo, um nó pode estar isolado:

grafo["Z1"] = []

Nesse caso, o nó Z1 existe, mas não possui conexões.

O algoritmo processará todos os nós alcançáveis a partir da origem. Quando não houver mais elementos na fila, ele concluirá que o destino não pode ser alcançado.

A função então retorna uma indicação de que não existe caminho.

Esse tratamento é diferente do caso em que o nó não existe:

- Nó inexistente: erro de cadastro ou entrada inválida.
- Nó existente, mas inalcançável: o nó está cadastrado, porém não há conexão possível com a origem.


## 28. Retorno da função dijkstra

Quando existe um caminho, a função retorna informações equivalentes a:

distancia_total, caminho

Por exemplo:

2849.07, [
   "A1",
   "E1",
   "I1",
   "Y1",
   "K1",
   "K3",
   "K2",
   "Q2",
   "S2"
]

A distância total representa a soma dos pesos de todas as conexões utilizadas.

O caminho representa a sequência ordenada de nós desde a origem até o destino.


## 29. Função mostrar_resultado

A função mostrar_resultado foi criada para separar a apresentação dos resultados da lógica do algoritmo.

Essa separação é importante porque a função dijkstra deve se concentrar no cálculo. Ela não precisa saber como o resultado será exibido na tela.

A função de apresentação recebe as informações calculadas e mostra:

- A origem.
- O destino.
- O caminho encontrado.
- O comprimento total.
- Uma mensagem adequada caso não exista caminho.

Por exemplo, um resultado pode ser apresentado como:

Caminho encontrado:

A1 -> E1 -> I1 -> Y1 -> K1 -> K3 -> K2 -> Q2 -> S2

Comprimento total:

2849.07 mm

Essa organização facilita futuras alterações na interface. No futuro, o resultado poderia ser:

- Mostrado no terminal.
- Salvo em um arquivo.
- Exportado para CSV.
- Apresentado em uma interface gráfica.
- Utilizado por outro programa.


## 30. Formatação do comprimento

O comprimento total é apresentado com duas casas decimais.
Isso é feito porque os comprimentos cadastrados podem possuir valores decimais, como:

370.94 mm

A apresentação com duas casas decimais padroniza o resultado e evita que o terminal mostre uma quantidade excessiva de casas.

Por exemplo:

2849.07 mm

em vez de:

2849.0699999999997 mm

Essa formatação melhora a leitura sem alterar a lógica do cálculo.


## 31. Função main

A função main concentra a execução principal do programa.

Ela é responsável por:

Mostrar instruções ao usuário.

Receber a origem.

Receber o destino.

Normalizar as entradas.

Verificar se os nós existem.

Chamar a função dijkstra.

Mostrar o resultado.

A utilização de uma função main evita que toda a execução fique espalhada pelo arquivo.


## 32. Entrada dos nós pelo terminal

O programa recebe os nós utilizando input.

A lógica é equivalente a:

origem = input("Digite o nó de origem: ")

destino = input("Digite o nó de destino: ")

Assim, o usuário pode executar o programa e informar, por exemplo:

A1

S2

O programa então procura o menor caminho entre esses dois nós.


## 33. Normalização das entradas

Depois de receber os valores, o código utiliza:

.strip().upper()

Esses métodos têm duas funções.

O método strip() remove espaços desnecessários no início e no final da entrada.

Por exemplo:

" A1 "

é convertido para:

"A1"

O método upper() converte letras minúsculas em maiúsculas.

Por exemplo:

"a1"

é convertido para:

"A1"

Isso é importante porque os nós foram cadastrados utilizando letras maiúsculas. Dessa forma, o usuário pode digitar:

a1

A1

a1

e o programa tratará essas entradas como o mesmo nó.


## 34. Validação das entradas na função main

Antes de executar o algoritmo, a função main verifica se os nós informados existem no grafo.

Essa validação evita chamadas desnecessárias ao algoritmo e permite mostrar uma mensagem mais clara ao usuário.

Por exemplo:

Nó de origem inválido.

ou:

Nó de destino inválido.

Essa etapa também evita erros causados por nomes digitados incorretamente.


## 35. Chamada do algoritmo

Depois de validar as entradas, a função main chama:

dijkstra(grafo, origem, destino)

O grafo cadastrado é passado como argumento junto com os nós escolhidos pelo usuário.

O resultado retornado pelo algoritmo é então encaminhado para a função mostrar_resultado.

A separação entre entrada, processamento e saída deixa o programa mais organizado:

Entrada:

   main recebe origem e destino.

Processamento:

   dijkstra calcula o caminho mínimo.

Saída:

   mostrar_resultado apresenta o resultado.


## 36. Bloco de execução principal

O código termina com:

if name == "main":

   main()

Essa estrutura é utilizada em Python para garantir que a função main seja executada automaticamente quando o arquivo for executado diretamente.

Por exemplo:

python dijkstra.py

Nesse caso, o programa inicia a execução da main.

Por outro lado, se esse arquivo for importado por outro arquivo Python, a main não será executada automaticamente.

Isso é importante porque permite reutilizar as funções em outros módulos no futuro.


## 37. Fluxo completo de execução

O funcionamento completo do programa pode ser descrito da seguinte forma:

O Python importa a biblioteca heapq.

O programa carrega o dicionário de componentes.

O programa carrega o grafo com seus nós e conexões.

A função main é executada.

O usuário informa o nó de origem.

O usuário informa o nó de destino.

As entradas são removidos espaços extras e convertidas para maiúsculas.

O programa verifica se os nós existem.

A função dijkstra é chamada.

As distâncias são inicializadas como infinito.

A distância da origem é definida como zero.

O predecessor de cada nó é inicializado como None.

A origem é inserida na fila de prioridade.

O algoritmo retira o nó de menor distância da fila.

O algoritmo verifica seus vizinhos.

Para cada vizinho, calcula uma possível nova distância.

Se a nova distância for menor, o algoritmo atualiza a distância e o predecessor.

O vizinho atualizado é inserido na fila.

O processo continua até que o destino seja encontrado ou não existam mais nós alcançáveis.

O caminho é reconstruído utilizando os predecessores.

O comprimento total e o caminho são retornados.

A função mostrar_resultado apresenta o resultado.


## 38. Exemplo real de resultado

Em um dos testes realizados, foi solicitada a rota de A1 até S2.

O algoritmo encontrou:

A1 → E1 → I1 → Y1 → K1 → K3 → K2 → Q2 → S2

O comprimento total calculado foi:

2849.07 mm

Isso significa que, considerando o grafo cadastrado e os pesos utilizados, esse foi o caminho de menor comprimento encontrado entre A1 e S2.

Outro teste foi realizado entre A2 e S2.

O caminho encontrado foi:

A2 → A1 → E1 → I1 → Y1 → K1 → K3 → K2 → Q2 → S2

O comprimento total foi:

3159.07 mm

Nesse caso, o algoritmo identificou que o caminho de A2 até S2 passava primeiro por A1 e depois seguia pelo caminho mínimo encontrado anteriormente.


## 39. O que foi validado nos testes

Os testes realizados permitiram verificar diferentes aspectos da implementação.

### 39.1. Teste com origem e destino diferentes

Foi verificado se o programa conseguia encontrar um caminho entre dois nós conectados.
Esse é o caso principal de utilização do algoritmo.

### 39.2. Teste com caminhos alternativos

Foi observado que o algoritmo não escolhe necessariamente o caminho com menor número de nós.

Ele escolhe o caminho com menor soma de pesos.

Isso é importante porque um caminho com mais conexões pode ser fisicamente menor do que outro caminho com menos conexões.

### 39.3. Teste com origem igual ao destino

Foi considerado o caso em que o usuário informa o mesmo nó como origem e destino.

O resultado esperado é:

Caminho: o próprio nó.

Distância: 0 mm.

### 39.4. Teste com nó inexistente

Foi considerado o caso de entrada de um nó que não está cadastrado no grafo.

O programa deve informar que o nó é inválido, sem tentar executar o algoritmo.

### 39.5. Teste com destino inalcançável

Foi considerado o caso de um nó existente, mas sem conexão com a região do grafo alcançável a partir da origem.

O programa deve informar que não existe caminho entre a origem e o destino.


## 40. Por que o algoritmo não escolhe necessariamente o caminho com menos nós

É importante destacar que o Dijkstra não minimiza a quantidade de nós ou a quantidade de conexões.

Ele minimiza a soma dos pesos.

Considere dois caminhos:

Caminho A:

A → B → C

Pesos:

100 mm + 100 mm = 200 mm

Caminho B:

A → D → E → F → C

Pesos:

30 mm + 40 mm + 50 mm + 20 mm = 140 mm

Mesmo possuindo mais nós, o Caminho B é escolhido porque possui menor comprimento total.

No projeto GLV, isso é adequado para a primeira versão, pois o objetivo inicial é minimizar o comprimento físico do chicote.


## 41. Hipóteses adotadas na primeira versão

A implementação atual utiliza algumas hipóteses simplificadoras.

### 41.1. Todas as conexões são consideradas percorríveis

As conexões foram cadastradas em ambas as direções, considerando que é possível ir e voltar entre os nós.

Essa hipótese ainda precisa ser validada com as regras reais do sistema.

### 41.2. O único custo considerado é o comprimento

O peso de cada aresta representa somente o comprimento físico em milímetros.

Não são considerados, por enquanto:

- Quantidade de conectores.
- Quantidade de emendas.
- Tempo de montagem.
- Facilidade de manutenção.
- Interferência eletromagnética.
- Risco de falha.
- Tipo de sinal.
- Capacidade de corrente.
- Separação física entre cabos.
- Restrições de segurança.
- Necessidade de passar por determinados componentes.

### 41.3. Todos os nós são tratados de forma semelhante

O algoritmo atual não diferencia automaticamente:

- Alimentação.
- Retorno.
- Comunicação.
- Sinais digitais.
- Sinais analógicos.
- Sinais de segurança.

Essa diferenciação poderá ser implementada futuramente.

### 41.4. O grafo está cadastrado manualmente

Os nós e as conexões estão escritos diretamente no arquivo Python.

Isso é aceitável para uma primeira validação, mas não é a melhor solução para um sistema que precisará ser atualizado frequentemente.


## 42. Limitações atuais

Apesar de funcional, a implementação ainda possui algumas limitações.

### 42.1. Ausência de leitura automática de arquivos

Atualmente, para alterar uma conexão ou adicionar um nó, é necessário editar o código.

No futuro, seria interessante ler os dados de:

- CSV.
- Excel.
- Banco de dados.
- Arquivo de configuração.

Isso permitiria que o grafo fosse atualizado sem modificar diretamente a lógica do programa.

### 42.2. Ausência de validação completa do grafo

O código verifica pesos negativos durante a execução, mas ainda não realiza uma validação completa de todos os dados cadastrados.

Seria interessante verificar automaticamente:

- Se todos os pesos são numéricos.
- Se todos os pesos são não negativos.
- Se todos os vizinhos existem no grafo.
- Se existem conexões duplicadas.
- Se as conexões bidirecionais estão consistentes.
- Se existem nós isolados inesperados.
- Se existem nós cadastrados sem conexões.

### 42.3. Ausência de restrições de caminho

O algoritmo atual encontra o menor caminho considerando apenas os pesos.

Ele ainda não permite, por exemplo:

- Proibir a passagem por determinado nó.
- Exigir que o caminho passe por determinado componente.
- Impedir a utilização de uma conexão.
- Separar caminhos por tipo de sinal.
- Definir regiões obrigatórias do chicote.

### 42.4. Ausência de múltiplos critérios

O custo atual é apenas o comprimento físico.

Entretanto, no projeto real, o melhor caminho pode depender de vários fatores.

Por exemplo:

custo_total =

   comprimento +

   penalidade_por_emenda +

   penalidade_por_conector +

   penalidade_por_regiao +

   penalidade_por_interferencia


Essa abordagem ainda não foi implementada.

### 42.5. Ausência de visualização

O resultado é apresentado no terminal como uma sequência de nós.

Ainda não existe uma representação visual do grafo ou do caminho encontrado.

No futuro, seria possível gerar:

- Um desenho do grafo.
- Uma imagem do caminho.
- Um mapa sobre o desenho físico do chicote.
- Uma visualização interativa.


## 43. Possíveis melhorias na organização dos arquivos

Atualmente, o código está concentrado em um único arquivo. Isso é adequado para uma primeira versão, mas a organização pode ser melhorada conforme o projeto crescer.

Uma possível estrutura futura seria:

`main.py`

Responsável por:

- Entrada do usuário.
- Execução do programa.
- Apresentação dos resultados.

`dijkstra.py`

Responsável por:

- Implementação do algoritmo de Dijkstra.
- Funções auxiliares de cálculo.

`grafo.py`

Responsável por:

- Cadastro dos nós.
- Cadastro das conexões.
- Funções de manipulação do grafo.

`validacao.py`

Responsável por:

- Verificação da consistência do grafo.
- Verificação de nós e pesos.

`testes/`

Responsável por:

- Testes automatizados.

Essa separação não é obrigatória neste momento, mas pode facilitar a manutenção quando novas funcionalidades forem adicionadas.


## 44. Possível função para adicionar conexões

Uma melhoria futura seria criar uma função para cadastrar conexões sem precisar escrever manualmente as duas direções.

Por exemplo, uma função conceitual:

adicionar_conexao(grafo, origem, destino, peso, bidirecional=True)

Se bidirecional for True, a função adicionaria:

origem → destino

destino → origem

Se bidirecional for False, adicionaria somente:

origem → destino

Isso reduziria a chance de erros de cadastro e permitiria representar conexões direcionadas.


## 45. Possível validação de simetria

Como a primeira versão utiliza conexões bidirecionais, seria interessante verificar se o cadastro está consistente.

Por exemplo, se existe:

A1 → E1 com peso 250

deveria existir também:

E1 → A1 com peso 250

Uma função de validação poderia identificar situações como:

- A conexão existe em apenas uma direção.
- Os pesos são diferentes em cada direção.
- Um nó foi digitado incorretamente.
- Uma conexão foi esquecida no cadastro.

Essa verificação é importante porque uma inconsistência no grafo pode alterar o caminho encontrado pelo algoritmo.


## 46. Possível leitura de CSV

Uma futura versão poderia utilizar um arquivo CSV com colunas como:

origem,destino,comprimento,bidirecional

Exemplo:

A1,E1,250,True

A1,F1,370.94,True

E1,I1,400,True

O programa poderia ler esse arquivo e construir automaticamente o dicionário do grafo.

Essa abordagem teria algumas vantagens:

- Facilita a atualização dos dados.
- Permite que os dados sejam editados em planilhas.
- Evita alterar o código do algoritmo.
- Facilita o compartilhamento dos dados entre integrantes da equipe.


## 47. Possível leitura de Excel

Como os dados do projeto podem estar organizados em planilhas, também seria possível utilizar um arquivo Excel.

Uma planilha poderia conter:

- Nó de origem.
- Nó de destino.
- Comprimento.
- Tipo de conexão.
- Tipo de sinal.
- Componente associado.
- Sentido permitido.
- Região física.
- Observações.

A partir desses dados, o programa poderia construir um grafo mais completo e próximo da realidade do sistema.


## 48. Possibilidade de pesos mais complexos

Na primeira versão, o peso é apenas o comprimento físico.

Porém, o conceito de peso pode ser generalizado.

Por exemplo, uma conexão de 100 mm pode ser considerada pior que uma conexão de 120 mm se exigir uma emenda adicional ou passar por uma região de difícil montagem.

Nesse caso, o peso poderia ser calculado como:

peso = comprimento + penalidades

Por exemplo:

peso = 100 + 50

onde:

- 100 representa o comprimento.
- 50 representa uma penalidade associada a uma emenda.

Essa abordagem permite que o Dijkstra continue sendo utilizado, mas com um custo que representa melhor as necessidades do projeto.


## 49. Possibilidade de nós proibidos

Uma futura versão poderia receber uma lista de nós proibidos.

Por exemplo:

nos_proibidos = ["K3", "Q2"]

Durante o algoritmo, qualquer vizinho pertencente a essa lista seria ignorado.

Isso permitiria representar componentes ou regiões que não podem ser utilizados em determinado caminho.

Essa funcionalidade precisa ser implementada com cuidado, pois remover um nó pode tornar determinados destinos inalcançáveis.


## 50. Possibilidade de nós obrigatórios

Também poderia ser necessário exigir que um caminho passe por determinados nós.

Por exemplo:

origem = A1

destino = S2

nó obrigatório = I1

Uma forma simples de tratar isso seria dividir o problema em etapas:

Encontrar o caminho de A1 até I1.

Encontrar o caminho de I1 até S2.

Concatenar os dois caminhos.

Entretanto, em uma implementação mais completa, seria necessário verificar se a combinação realmente representa o melhor caminho que passa pelo nó obrigatório.


## 51. Possibilidade de restrições por tipo de sinal

No sistema GLV, diferentes sinais podem possuir regras diferentes.

Por exemplo:

- Alimentação.
- Retorno.
- Sinais digitais.
- Sinais analógicos.
- Comunicação.
- Circuitos de segurança.

Uma futura modelagem poderia associar um tipo de sinal a cada conexão ou a cada nó.

O algoritmo poderia então aceitar somente conexões compatíveis com o tipo de sinal solicitado.

Isso permitiria evitar caminhos que são fisicamente possíveis, mas eletricamente inadequados.


## 52. Possibilidade de conexões direcionadas

Se forem identificadas conexões que só podem ser utilizadas em um sentido, o grafo deverá ser representado como direcionado.

Nesse caso, uma conexão:

A1 → E1

não implicaria automaticamente na existência de:

E1 → A1

Essa mudança é simples na estrutura do grafo, mas precisa ser baseada nas regras reais do sistema.


## 53. Testes automatizados

Outra melhoria importante seria criar testes automatizados para verificar se o algoritmo continua funcionando após alterações.

Alguns testes importantes seriam:

- Caminho simples entre dois nós.
- Origem igual ao destino.
- Nó inexistente.
- Destino inalcançável.
- Grafo com diferentes caminhos possíveis.
- Grafo com pesos iguais.
- Grafo com peso zero.
- Grafo com peso negativo.
- Grafo com conexões direcionadas.
- Grafo com nós isolados.

Os testes automatizados evitam que uma alteração futura quebre alguma funcionalidade já implementada.


## 54. Separação entre dados e algoritmo

Um dos pontos mais importantes para a evolução do projeto é separar os dados do grafo da lógica do algoritmo.

Atualmente, ambos estão no mesmo arquivo, mas conceitualmente são coisas diferentes.

Os dados respondem:
- Quais nós existem?
- Quais conexões existem?
- Quais são os comprimentos?
- Quais componentes estão associados?

O algoritmo responde:
- Como encontrar o menor caminho?

Essa separação permite alterar completamente o mapa sem precisar modificar o Dijkstra.

Da mesma forma, seria possível utilizar o mesmo algoritmo para outros mapas ou outros sistemas.


## 55. O que a implementação já consegue fazer

A versão atual já consegue:

- Representar o mapa como um grafo ponderado.
- Associar conexões a comprimentos em milímetros.
- Trabalhar com conexões bidirecionais cadastradas nas duas direções.
- Receber origem e destino pelo terminal.
- Normalizar as entradas.
- Verificar se os nós existem.
- Tratar origem igual ao destino.
- Inicializar distâncias e predecessores.
- Utilizar uma fila de prioridade.
- Processar os nós em ordem crescente de distância.
- Ignorar entradas antigas da fila.
- Verificar pesos negativos.
- Atualizar distâncias menores.
- Registrar predecessores.
- Reconstruir o caminho.
- Informar quando não existe caminho.
- Mostrar o comprimento total com duas casas decimais.
- Manter a lógica do algoritmo separada da apresentação.

## 56. O que ainda não foi implementado

A versão atual ainda não possui:

- Leitura automática de CSV.
- Leitura automática de Excel.
- Interface gráfica.
- Visualização do grafo.
- Validação completa dos dados.
- Detecção automática de conexões duplicadas.
- Verificação automática de simetria.
- Restrições por tipo de sinal.
- Nós obrigatórios.
- Nós proibidos.
- Conexões unidirecionais configuráveis.
- Custos de conectores ou emendas.
- Critérios de confiabilidade.
- Exportação automática dos resultados.
- Testes automatizados organizados em arquivos próprios.

Esses itens não foram esquecidos. Eles fazem parte de uma possível evolução do projeto, mas foram deixados para depois para que a primeira versão pudesse validar a estrutura básica do grafo e o funcionamento do Dijkstra.


## 57. Considerações sobre a escolha de Dijkstra

O algoritmo de Dijkstra foi uma escolha adequada para esta primeira etapa porque:

- É relativamente simples de implementar.
- É bem conhecido e documentado.
- Funciona com pesos não negativos.
- Encontra o caminho mínimo.
- Pode trabalhar com grafos direcionados ou não direcionados.
- Pode ser adaptado para diferentes tipos de custo.
- É eficiente para grafos desse porte.
- Permite reconstruir o caminho completo.

Como o grafo atual possui poucas dezenas de nós, o custo computacional da implementação é baixo. Mesmo que o mapa cresça, a utilização de uma fila de prioridade torna a solução suficientemente eficiente para esse tipo de aplicação.


## 58. Complexidade computacional

Considerando uma implementação com lista de adjacência e fila de prioridade, a complexidade típica do Dijkstra é:

O((V + E) log V)

onde:

- V é o número de vértices ou nós.
- E é o número de arestas ou conexões.

No caso do projeto:

- V corresponde à quantidade de nós cadastrados.
- E corresponde à quantidade de conexões consideradas pelo algoritmo.

A fila de prioridade é responsável pelo fator log V, pois inserir e retirar elementos do heap possui esse custo aproximado.

Para o tamanho atual do grafo, essa complexidade não representa um problema prático.


## 59. Interpretação do resultado no contexto do GLV

O resultado atual deve ser interpretado como o menor caminho físico segundo o grafo cadastrado.

Isso significa que o programa responde à seguinte pergunta:

“Considerando os nós, as conexões e os comprimentos cadastrados, qual é o caminho de menor comprimento entre a origem e o destino?”

Ele ainda não responde necessariamente:

“Qual é o melhor caminho elétrico, mecânico ou construtivo para o projeto?”

Essa diferença é importante.

Um caminho pode ser o menor fisicamente, mas não ser o mais adequado devido a:

- Restrições elétricas.
- Necessidade de separação entre sinais.
- Dificuldade de montagem.
- Manutenção.
- Segurança.
- Quantidade de emendas.
- Disponibilidade de conectores.

Por isso, a primeira implementação deve ser vista como uma base matemática sobre a qual poderão ser adicionadas regras específicas do sistema.


## 60. Conclusão

A primeira implementação desenvolvida representa o mapa do GLV como um grafo ponderado e utiliza o algoritmo de Dijkstra para encontrar o caminho de menor comprimento entre dois nós.

O grafo foi representado por listas de adjacência, nas quais cada nó possui uma lista de vizinhos e os respectivos pesos. Os pesos correspondem aos comprimentos físicos das conexões em milímetros.

O algoritmo foi implementado utilizando uma fila de prioridade da biblioteca heapq. Durante a execução, são mantidas as menores distâncias conhecidas até cada nó e os respectivos predecessores. Quando uma distância menor é encontrada, ela é atualizada e o vizinho é inserido novamente na fila.

Ao final, o caminho é reconstruído a partir dos predecessores e apresentado ao usuário junto com o comprimento total.

Também foram incluídos tratamentos para nós inexistentes, origem igual ao destino, destinos inalcançáveis, pesos negativos e entradas com letras minúsculas ou espaços extras.

A implementação já constitui uma primeira versão funcional do problema e permite realizar consultas de menor caminho no grafo cadastrado. Entretanto, ela ainda utiliza algumas simplificações, principalmente a consideração de conexões bidirecionais e o uso exclusivo do comprimento físico como custo.

As próximas etapas devem ser definidas a partir das regras reais do sistema GLV. Entre as melhorias mais importantes estão a validação do grafo, a criação de testes automatizados, a separação dos arquivos, a leitura dos dados por CSV ou Excel e a inclusão de restrições relacionadas aos tipos de sinal, componentes proibidos ou obrigatórios e outros fatores de custo.

Assim, o projeto poderá evoluir de um algoritmo de menor caminho puramente geométrico para uma ferramenta mais completa de planejamento e análise das conexões do sistema GLV.
