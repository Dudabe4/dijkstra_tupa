import heapq


# Grafo do sistema GLV.
#
# Cada chave representa um no.
# Cada elemento da lista representa uma aresta:
# (no_destino, comprimento)
#
# Os comprimentos devem estar todos na mesma unidade,
# por exemplo, milimetros.

componentes_por_no = {
    "L2": [
        "PNLAT[A]",
        "PNLAT[B]",
        "INV R1",
    ],

    "L1": [
        "INV L1",
        "ICU",
        "MSD",
        "SENSOR[A]",
    ],

    "N1": [
        "ENERGM",
        "SENSOR[G]",
    ],

    "N2": [
        "SENSOR[H]",
    ],

    "K3": [
        "PDM",
        "IMU",
    ],

    "C1": [
        "DCU[A]",
        "DCU[B]",
    ],

    "G2": [
        "STARTBU",
        "PUSHBP",
    ],

    "H1": [
        "PNPIL",
        "TORADEX",
    ],

    "U2": [
        "PUSHBR",
    ],

    "U1": [
        "PUSHBL",
    ],

    "S2": [
        "24V BAT",
    ],

    "Y1": [
        "INERSW",
    ],

    "B1": [
        "BOTS",
        "APPS1",
        "APPS2",
    ],

    "U3": [
        "RML",
        "SSI",
    ],

    "T2": [
        "BRKLIGHT",
    ],

    "W2": [
        "BUZZER",
        "PACK[A]",
        "PACK[B]",
    ],

    "G1": [
        "POTDIR",
    ],

    "K1": [
        "BRAKE B",
        "BRAKE F",
        "MIC",
    ],

    "G3": [
        "SENSOR[B]",
        "DISPLAY",
    ],

    "E1": [
        "SENSOR[C]",
    ],

    "E2": [
        "SENSOR[D]",
    ],

    "V1": [
        "SENSOR[E]",
        "SENSOR[I]",
    ],

    "V2": [
        "SENSOR[F]",
        "SENSOR[J]",
    ],
}

grafo = {
    "A1": [
        ("E1", 402.81),
        ("F1", 370.94),
        ("A2", 310.00),
        ("B1", 310.00),
    ],

    "A2": [
        ("A1", 310.00),
    ],

    "B1": [
        ("C1", 189.61),
        ("A1", 310.00),
    ],

    "C1": [
        ("E1", 191.16),
        ("B1", 189.61),
    ],

    "D1": [
        ("D2", 355.14),
        ("E1", 159.09),
    ],

    "D2": [
        ("D1", 355.14),
    ],

    "E1": [
        ("C1", 191.16),
        ("H1", 395.92),
        ("A1", 402.81),
        ("F1", 331.04),
        ("G1", 576.64),
        ("I1", 352.29),
        ("D1", 159.09),
    ],

    "E2": [
        ("H2", 395.92),
    ],

    "F1": [
        ("E1", 331.04),
        ("G1", 370.94),
        ("A1", 370.94),
    ],

    "G1": [
        ("H1", 278.73),
        ("G3", 213.73),
        ("E1", 576.64),
        ("F1", 370.94),
    ],

    "G2": [
        ("H2", 278.73),
        ("G3", 213.73),
    ],

    "G3": [
        ("G1", 213.73),
        ("G2", 213.73),
    ],

    "H1": [
        ("E1", 395.92),
        ("G1", 278.73),
        ("I1", 208.62),
    ],

    "H2": [
        ("E2", 395.92),
        ("G2", 278.73),
    ],

    "I1": [
        ("H1", 208.62),
        ("Y1", 415.85),
        ("L1", 827.50),
        ("E1", 352.29),
        ("K1", 813.27),
    ],

    "J1": [
        ("E1", 374.66),
        ("K1", 810.90),
    ],

    "K1": [
        ("K3", 326.64),
        ("L1", 331.60),
        ("Y1", 343.59),
        ("I1", 813.27),
        ("J1", 810.90),
        ("M1", 333.21),
    ],

    "K2": [
        ("K3", 326.64),
        ("L2", 331.60),
        ("Q2", 416.47),
    ],

    "K3": [
        ("K1", 326.64),
        ("K2", 326.64),
    ],

    "L1": [
        ("V1", 609.91),
        ("G1", 870.76),
        ("I1", 827.50),
        ("K1", 331.60),
        ("N1", 462.27),
        ("U1", 946.75),
        ("L2", 774.26),
    ],

    "L2": [
        ("W2", 204.62),
        ("U2", 946.75),
        ("M2", 349.96),
        ("K2", 331.60),
        ("L1", 774.26),
        ("V2", 609.91),
    ],

    "M1": [
        ("K1", 333.21),
    ],

    "M2": [
        ("L2", 349.96),
        ("P2", 139.51),
    ],

    "N1": [
        ("V1", 186.73),
        ("T1", 225.35),
        ("M1", 171.03),
        ("P1", 154.96),
        ("N2", 712.25),
        ("L1", 462.27),
    ],

    "N2": [
        ("N1", 712.25),
        ("V2", 186.73),
    ],

    "P1": [
        ("N1", 154.96),
    ],

    "P2": [
        ("M2", 139.51),
        ("R2", 132.57),
    ],

    "Q2": [
        ("S2", 264.78),
        ("K2", 416.47),
    ],

    "R1": [
        ("S1", 131.10),
    ],

    "R2": [
        ("P2", 132.57),
        ("S2", 130.77),
    ],

    "S1": [
        ("R1", 131.10),
    ],

    "S2": [
        ("T2", 176.01),
        ("Q2", 264.78),
        ("R2", 130.77),
    ],

    "S3": [
        ("S2", 75.79),
    ],

    "T1": [
        ("N1", 225.35),
        ("V1", 124.38),
    ],

    "T2": [
        ("V2", 124.38),
        ("S2", 176.01),
    ],

    "U1": [
        ("V1", 1114.48),
        ("U2", 246.75),
        ("L1", 946.75),
    ],

    "U2": [
        ("U3", 123.38),
        ("U1", 246.75),
        ("L2", 946.75),
    ],

    "U3": [
        ("U1", 123.38),
        ("L2", 996.79),
    ],

    "V1": [
        ("N1", 186.73),
        ("V2", 664.85),
        ("T1", 124.38),
        ("U1", 1114.48),
        ("L1", 609.91),
    ],

    "V2": [
        ("V1", 664.85),
        ("T2", 124.38),
        ("N2", 186.73),
        ("L2", 609.91),
    ],

    "W2": [
        ("L2", 204.62),
        ("M2", 143.89),
    ],

    "Y1": [
        ("I1", 415.85),
        ("K1", 343.59),
    ],
}

def dijkstra(grafo, origem, destino):
    """
    Encontra o caminho de menor custo entre origem e destino.

    Parametros:
        grafo: dicionario com os nos e suas arestas
        origem: no inicial
        destino: no final

    Retorna:
        caminho: lista de nos do caminho encontrado
        distancia_total: custo total do caminho
    """

    if origem not in grafo:
        raise ValueError(f"O no de origem '{origem}' nao existe no grafo.")

    if destino not in grafo:
        raise ValueError(f"O no de destino '{destino}' nao existe no grafo.")

    if origem == destino:
        return [origem], 0

    # Distancias conhecidas ate cada no.
    distancias = {
        no: float("inf")
        for no in grafo
    }

    # Predecessor de cada no no caminho encontrado.
    predecessores = {
        no: None
        for no in grafo
    }

    # Fila de prioridade.
    # Cada elemento possui:
    # (distancia_acumulada, no_atual)
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

        # Ignora uma entrada antiga da fila.
        if distancia_atual > distancias[no_atual]:
            continue

        # Se chegamos ao destino, podemos encerrar.
        if no_atual == destino:
            break

        # Analisa todos os vizinhos do no atual.
        for vizinho, comprimento in grafo[no_atual]:

            if comprimento < 0:
                raise ValueError(
                    "O algoritmo de Dijkstra nao aceita "
                    "pesos negativos."
                )

            nova_distancia = (
                distancia_atual + comprimento
            )

            # Relaxamento da aresta.
            if nova_distancia < distancias[vizinho]:

                distancias[vizinho] = nova_distancia

                predecessores[vizinho] = no_atual

                heapq.heappush(
                    fila_prioridade,
                    (nova_distancia, vizinho)
                )

    # Se o destino continua com distancia infinita,
    # nao existe caminho entre origem e destino.
    if distancias[destino] == float("inf"):
        return None, float("inf")

    # Reconstrucao do caminho, partindo do destino.
    caminho = []
    no_atual = destino

    while no_atual is not None:

        caminho.append(no_atual)

        no_atual = predecessores[no_atual]

    # O caminho foi reconstruido de tras para frente.
    caminho.reverse()

    return caminho, distancias[destino]


def mostrar_resultado(origem, destino, caminho, distancia_total):
    """
    Exibe o resultado do algoritmo.
    """

    print()
    print("========== RESULTADO ==========")
    print(f"Origem: {origem}")
    print(f"Destino: {destino}")

    if caminho is None:
        print("Nenhum caminho foi encontrado.")
        return

    print("Caminho encontrado:")
    print(" -> ".join(caminho))

    print(f"Comprimento total: {distancia_total:.2f} mm")
    print("================================")
    print()


def main():

    nos_validos = set(grafo.keys())


    print("========== DIJKSTRA ==========")
    origem = input("Digite o nó de origem: ").strip().upper()
    destino = input("Digite o nó de destino: ").strip().upper()


    if origem not in nos_validos:
        print(f"Erro: o nó de origem '{origem}' não existe no grafo.")

    elif destino not in nos_validos:
        print(f"Erro: o nó de destino '{destino}' não existe no grafo.")

    else:

        caminho, distancia_total = dijkstra(
            grafo,
            origem,
            destino
        )

        mostrar_resultado(
            origem,
            destino,
            caminho,
            distancia_total
        )


if __name__ == "__main__":
    main()