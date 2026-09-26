import heapq


def dijkstra(grafo, origem, destino):
    """
    # dijkstra

    Encontra o caminho de menor custo entre origem e destino.

    O algoritmo de Dijkstra calcula o menor custo acumulado
    para chegar da origem ate cada no do grafo. Neste projeto,
    o custo representa o comprimento total das conexoes
    percorridas em milimetros.

    O algoritmo utiliza uma fila de prioridade para sempre
    processar primeiro o no que possui a menor distancia
    conhecida ate o momento.

    Args:
        grafo: dicionario com os nos e suas arestas.
               Cada aresta possui o formato:
               (no_destino, comprimento)

        origem: no inicial do caminho.

        destino: no final do caminho.

    Returns:
        caminho: lista de nos do caminho encontrado, na ordem
                 em que devem ser percorridos.

        distancia_total: custo total do caminho encontrado.

    Caso nao exista caminho entre origem e destino, retorna:
        (None, float("inf"))
    """

    if origem not in grafo:
        raise ValueError(f"O no de origem '{origem}' nao existe no grafo.")

    if destino not in grafo:
        raise ValueError(f"O no de destino '{destino}' nao existe no grafo.")

    if origem == destino:
        return [origem], 0


    distancias = {
        no: float("inf")
        for no in grafo
    }

    predecessores = {
        no: None
        for no in grafo
    }

    fila_prioridade = []
    distancias[origem] = 0

    heapq.heappush(
        fila_prioridade,
        (0, origem)
    )


    while fila_prioridade:

        distancia_atual, no_atual = heapq.heappop(
            fila_prioridade
        )

        if distancia_atual > distancias[no_atual]:
            continue

        if no_atual == destino:
            break


        for vizinho, comprimento in grafo[no_atual]:

            if comprimento < 0:
                raise ValueError(
                    "O algoritmo de Dijkstra nao aceita "
                    "pesos negativos."
                )

            nova_distancia = (
                distancia_atual + comprimento
            )

            if nova_distancia < distancias[vizinho]:

                distancias[vizinho] = nova_distancia

                predecessores[vizinho] = no_atual

                heapq.heappush(
                    fila_prioridade,
                    (nova_distancia, vizinho)
                )

 
    if distancias[destino] == float("inf"):
        return None, float("inf")


    caminho = []
    no_atual = destino


    while no_atual is not None:

        caminho.append(no_atual)

        no_atual = predecessores[no_atual]


    caminho.reverse()

    return caminho, distancias[destino]