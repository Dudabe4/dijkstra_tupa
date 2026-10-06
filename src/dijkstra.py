import heapq


def normalizar_aresta(no1, no2):
    """
    Normaliza uma aresta física para permitir comparação
    independentemente da direção.
    """
    return tuple(sorted([no1, no2]))


def obter_arestas_caminho_principal(configuracoes):
    """
    Constrói o conjunto de arestas pertencentes ao caminho principal.

    O caminho principal é considerado bidirecional.
    """
    arestas_principais = set()
    caminho = configuracoes.caminho_principal

    for i in range(len(caminho) - 1):
        aresta = normalizar_aresta(caminho[i], caminho[i + 1])
        arestas_principais.add(aresta)

    return arestas_principais


def calcular_custo(
    no_atual,
    vizinho,
    comprimento,
    configuracoes,
    utilizacao,
    arestas_caminho_principal
):
    """
    Calcula o custo utilizado pelo Dijkstra para decidir a rota.

    O custo não representa a distância física.
    Ele incorpora:
        - fator do caminho principal;
        - penalização por utilização do destino;
        - penalização de entrada no hoop.
    """

    # ---------------------------------------------------------
    # 1. Fator do caminho principal
    # ---------------------------------------------------------

    aresta = normalizar_aresta(no_atual, vizinho)

    if aresta in arestas_caminho_principal:
        fator_principal = configuracoes.fator_caminho_principal
    else:
        fator_principal = 1.0

    custo = comprimento * fator_principal

    # ---------------------------------------------------------
    # 2. Penalização por utilização do nó de destino
    # ---------------------------------------------------------

    quantidade_utilizacao = utilizacao.get(vizinho, 0)

    custo += (
        quantidade_utilizacao
        * configuracoes.penalizacao_utilizacao
    )

    # ---------------------------------------------------------
    # 3. Penalização de entrada no hoop
    # ---------------------------------------------------------
    #
    # Aqui a direção importa.
    #
    # Exemplo:
    #     L2 -> U2
    #
    # pode ser penalizado, enquanto:
    #
    #     U2 -> L2
    #
    # não é penalizado.
    # ---------------------------------------------------------

    aresta_direcional = (no_atual, vizinho)

    if aresta_direcional in configuracoes.arestas_penalizadas:
        custo += configuracoes.penalizacao_entrada_hoop

    return custo


def dijkstra(
    grafo,
    origem,
    destino,
    configuracoes,
    utilizacao=None
):
    """
    Encontra o caminho de menor custo entre origem e destino.

    Retorna:
        caminho
        custo_dijkstra
        distancia_fisica

    Onde:

        custo_dijkstra:
            valor utilizado pelo algoritmo para escolher a rota.

        distancia_fisica:
            soma dos comprimentos físicos das arestas da rota.
            Não recebe nenhuma penalização.
    """

    if utilizacao is None:
        utilizacao = {}

    # ---------------------------------------------------------
    # Validações básicas
    # ---------------------------------------------------------

    if origem not in grafo:
        raise ValueError(
            f"Origem '{origem}' não existe no grafo."
        )

    if destino not in grafo:
        raise ValueError(
            f"Destino '{destino}' não existe no grafo."
        )

    if origem == destino:
        return [origem], 0.0, 0.0

    # ---------------------------------------------------------
    # Arestas do caminho principal
    # ---------------------------------------------------------

    arestas_caminho_principal = (
        obter_arestas_caminho_principal(configuracoes)
    )

    # ---------------------------------------------------------
    # Estruturas do Dijkstra
    # ---------------------------------------------------------

    custos = {
        no: float("inf")
        for no in grafo
    }

    distancias_fisicas = {
        no: float("inf")
        for no in grafo
    }

    predecessores = {
        no: None
        for no in grafo
    }

    fila_prioridade = []

    # Origem
    custos[origem] = 0.0
    distancias_fisicas[origem] = 0.0

    heapq.heappush(
        fila_prioridade,
        (0.0, origem)
    )

    # ---------------------------------------------------------
    # Algoritmo de Dijkstra
    # ---------------------------------------------------------

    while fila_prioridade:

        custo_atual, no_atual = heapq.heappop(
            fila_prioridade
        )

        # Entrada antiga da fila
        if custo_atual > custos[no_atual]:
            continue

        # Chegamos ao destino
        if no_atual == destino:
            break

        # -----------------------------------------------------
        # Analisa os vizinhos
        # -----------------------------------------------------

        for vizinho, comprimento in grafo[no_atual]:

            if comprimento < 0:
                raise ValueError(
                    f"Comprimento negativo encontrado em "
                    f"{no_atual} -> {vizinho}."
                )

            # -------------------------------------------------
            # Custo usado pelo Dijkstra
            # -------------------------------------------------

            custo_aresta = calcular_custo(
                no_atual,
                vizinho,
                comprimento,
                configuracoes,
                utilizacao,
                arestas_caminho_principal
            )

            novo_custo = (
                custo_atual
                + custo_aresta
            )

            # -------------------------------------------------
            # Distância física real
            # -------------------------------------------------

            nova_distancia_fisica = (
                distancias_fisicas[no_atual]
                + comprimento
            )

            # -------------------------------------------------
            # Relaxamento
            # -------------------------------------------------

            if novo_custo < custos[vizinho]:

                custos[vizinho] = novo_custo

                distancias_fisicas[vizinho] = (
                    nova_distancia_fisica
                )

                predecessores[vizinho] = no_atual

                heapq.heappush(
                    fila_prioridade,
                    (novo_custo, vizinho)
                )

    # ---------------------------------------------------------
    # Verifica se existe caminho
    # ---------------------------------------------------------

    if custos[destino] == float("inf"):
        return None, float("inf"), float("inf")

    # ---------------------------------------------------------
    # Reconstrói o caminho
    # ---------------------------------------------------------

    caminho = []

    no_atual = destino

    while no_atual is not None:

        caminho.append(no_atual)

        no_atual = predecessores[no_atual]

    caminho.reverse()

    # ---------------------------------------------------------
    # Resultado
    # ---------------------------------------------------------

    return (
        caminho,
        custos[destino],
        distancias_fisicas[destino]
    )