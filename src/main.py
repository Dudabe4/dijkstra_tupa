import heapq

# Grafo do sistema GLV.
#
# Cada chave representa um no.
# Cada elemento da lista representa uma aresta:
# (no_destino, comprimento)
#
# Os comprimentos devem estar todos na mesma unidade,
# por exemplo, milimetros.


# Dicionario que associa cada no aos componentes do sistema
# GLV presentes ou conectados naquele ponto.
#
# A chave representa o nome do no.
# O valor e uma lista contendo os componentes associados a ele.
#
# Essa estrutura e utilizada para identificar quais componentes
# estao relacionados a cada no do grafo. Ela e independente
# da estrutura utilizada para armazenar as conexoes e os pesos
# das arestas.
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


# Dicionario que representa o grafo do sistema GLV.
#
# Cada chave corresponde ao nome de um no.
#
# O valor associado a cada chave e uma lista de tuplas.
# Cada tupla representa uma aresta que conecta o no atual
# a outro no do grafo.
#
# Formato de cada aresta:
#
#     (no_destino, comprimento)
#
# O primeiro elemento da tupla indica o no conectado.
# O segundo elemento indica o peso da aresta, que neste caso
# representa o comprimento fisico da conexao entre os dois nos.
#
# Como as conexoes foram cadastradas nos dois sentidos,
# o grafo e tratado como nao direcionado:
#
#     A -> B
#     B -> A
#
# Isso significa que o algoritmo pode percorrer a conexao
# em qualquer uma das duas direcoes.
#
# Todos os comprimentos devem estar na mesma unidade.
# Neste projeto, os valores estao representados em milimetros.

grafo = {
    # No A1 conectado aos nos E1, F1, A2 e B1.
    "A1": [
        ("E1", 402.81),
        ("F1", 370.94),
        ("A2", 310.00),
        ("B1", 310.00),
    ],

    # No A2 conectado somente ao no A1.
    "A2": [
        ("A1", 310.00),
    ],

    # No B1 conectado aos nos C1 e A1.
    "B1": [
        ("C1", 189.61),
        ("A1", 310.00),
    ],

    # No C1 conectado aos nos E1 e B1.
    "C1": [
        ("E1", 191.16),
        ("B1", 189.61),
    ],

    # No D1 conectado aos nos D2 e E1.
    "D1": [
        ("D2", 355.14),
        ("E1", 159.09),
    ],

    # No D2 conectado somente ao no D1.
    "D2": [
        ("D1", 355.14),
    ],

    # No E1 possui conexoes com diversos nos do grafo.
    # Ele funciona como um dos principais pontos de ligacao
    # entre diferentes regioes do sistema.
    "E1": [
        ("C1", 191.16),
        ("H1", 395.92),
        ("A1", 402.81),
        ("F1", 331.04),
        ("G1", 576.64),
        ("I1", 352.29),
        ("D1", 159.09),
    ],

    # No E2 conectado somente ao no H2.
    "E2": [
        ("H2", 395.92),
    ],

    # No F1 conectado aos nos E1, G1 e A1.
    "F1": [
        ("E1", 331.04),
        ("G1", 370.94),
        ("A1", 370.94),
    ],

    # No G1 conectado aos nos H1, G3, E1 e F1.
    "G1": [
        ("H1", 278.73),
        ("G3", 213.73),
        ("E1", 576.64),
        ("F1", 370.94),
    ],

    # No G2 conectado aos nos H2 e G3.
    "G2": [
        ("H2", 278.73),
        ("G3", 213.73),
    ],

    # No G3 conecta as regioes associadas aos nos G1 e G2.
    "G3": [
        ("G1", 213.73),
        ("G2", 213.73),
    ],

    # No H1 conectado aos nos E1, G1 e I1.
    "H1": [
        ("E1", 395.92),
        ("G1", 278.73),
        ("I1", 208.62),
    ],

    # No H2 conectado aos nos E2 e G2.
    "H2": [
        ("E2", 395.92),
        ("G2", 278.73),
    ],

    # No I1 conectado aos nos H1, Y1, L1, E1 e K1.
    "I1": [
        ("H1", 208.62),
        ("Y1", 415.85),
        ("L1", 827.50),
        ("E1", 352.29),
        ("K1", 813.27),
    ],

    # No J1 conectado aos nos E1 e K1.
    "J1": [
        ("E1", 374.66),
        ("K1", 810.90),
    ],

    # No K1 conectado aos nos K3, L1, Y1, I1, J1 e M1.
    "K1": [
        ("K3", 326.64),
        ("L1", 331.60),
        ("Y1", 343.59),
        ("I1", 813.27),
        ("J1", 810.90),
        ("M1", 333.21),
    ],

    # No K2 conectado aos nos K3, L2 e Q2.
    "K2": [
        ("K3", 326.64),
        ("L2", 331.60),
        ("Q2", 416.47),
    ],

    # No K3 conecta os nos K1 e K2.
    "K3": [
        ("K1", 326.64),
        ("K2", 326.64),
    ],

    # No L1 conectado aos nos V1, G1, I1, K1, N1, U1 e L2.
    "L1": [
        ("V1", 609.91),
        ("G1", 870.76),
        ("I1", 827.50),
        ("K1", 331.60),
        ("N1", 462.27),
        ("U1", 946.75),
        ("L2", 774.26),
    ],

    # No L2 conectado aos nos W2, U2, M2, K2, L1 e V2.
    "L2": [
        ("W2", 204.62),
        ("U2", 946.75),
        ("M2", 349.96),
        ("K2", 331.60),
        ("L1", 774.26),
        ("V2", 609.91),
    ],

    # No M1 conectado somente ao no K1.
    "M1": [
        ("K1", 333.21),
    ],

    # No M2 conectado aos nos L2 e P2.
    "M2": [
        ("L2", 349.96),
        ("P2", 139.51),
    ],

    # No N1 conectado aos nos V1, T1, M1, P1, N2 e L1.
    "N1": [
        ("V1", 186.73),
        ("T1", 225.35),
        ("M1", 171.03),
        ("P1", 154.96),
        ("N2", 712.25),
        ("L1", 462.27),
    ],

    # No N2 conectado aos nos N1 e V2.
    "N2": [
        ("N1", 712.25),
        ("V2", 186.73),
    ],

    # No P1 conectado somente ao no N1.
    "P1": [
        ("N1", 154.96),
    ],

    # No P2 conectado aos nos M2 e R2.
    "P2": [
        ("M2", 139.51),
        ("R2", 132.57),
    ],

    # No Q2 conectado aos nos S2 e K2.
    "Q2": [
        ("S2", 264.78),
        ("K2", 416.47),
    ],

    # No R1 conectado somente ao no S1.
    "R1": [
        ("S1", 131.10),
    ],

    # No R2 conectado aos nos P2 e S2.
    "R2": [
        ("P2", 132.57),
        ("S2", 130.77),
    ],

    # No S1 conectado somente ao no R1.
    "S1": [
        ("R1", 131.10),
    ],

    # No S2 conectado aos nos T2, Q2 e R2.
    # Este no tambem esta associado ao componente "24V BAT".
    "S2": [
        ("T2", 176.01),
        ("Q2", 264.78),
        ("R2", 130.77),
    ],

    # No S3 conectado somente ao no S2.
    "S3": [
        ("S2", 75.79),
    ],

    # No T1 conectado aos nos N1 e V1.
    "T1": [
        ("N1", 225.35),
        ("V1", 124.38),
    ],

    # No T2 conectado aos nos V2 e S2.
    "T2": [
        ("V2", 124.38),
        ("S2", 176.01),
    ],

    # No U1 conectado aos nos V1, U2 e L1.
    "U1": [
        ("V1", 1114.48),
        ("U2", 246.75),
        ("L1", 946.75),
    ],

    # No U2 conectado aos nos U3, U1 e L2.
    "U2": [
        ("U3", 123.38),
        ("U1", 246.75),
        ("L2", 946.75),
    ],

    # No U3 conectado aos nos U1 e L2.
    "U3": [
        ("U1", 123.38),
        ("L2", 996.79),
    ],

    # No V1 conectado aos nos N1, V2, T1, U1 e L1.
    "V1": [
        ("N1", 186.73),
        ("V2", 664.85),
        ("T1", 124.38),
        ("U1", 1114.48),
        ("L1", 609.91),
    ],

    # No V2 conectado aos nos V1, T2, N2 e L2.
    "V2": [
        ("V1", 664.85),
        ("T2", 124.38),
        ("N2", 186.73),
        ("L2", 609.91),
    ],

    # No W2 conectado aos nos L2 e M2.
    "W2": [
        ("L2", 204.62),
        ("M2", 143.89),
    ],

    # No Y1 conectado aos nos I1 e K1.
    "Y1": [
        ("I1", 415.85),
        ("K1", 343.59),
    ],
}


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

    # Verifica se o no de origem esta cadastrado no grafo.
    # Essa verificacao evita tentar acessar um no inexistente
    # durante a execucao do algoritmo.
    if origem not in grafo:
        raise ValueError(f"O no de origem '{origem}' nao existe no grafo.")

    # Verifica se o no de destino esta cadastrado no grafo.
    if destino not in grafo:
        raise ValueError(f"O no de destino '{destino}' nao existe no grafo.")

    # Se a origem e o destino forem iguais, o caminho nao
    # precisa percorrer nenhuma aresta.
    #
    # Nesse caso, o caminho e formado apenas pelo proprio no
    # e o custo total e igual a zero.
    if origem == destino:
        return [origem], 0

    # Dicionario que armazena a menor distancia conhecida
    # entre a origem e cada no do grafo.
    #
    # Inicialmente, todos os nos recebem distancia infinita,
    # pois ainda nao foi encontrado nenhum caminho ate eles.
    #
    # A distancia da origem sera definida como zero mais abaixo.
    distancias = {
        no: float("inf")
        for no in grafo
    }

    # Dicionario que armazena o predecessor de cada no.
    #
    # O predecessor e o no imediatamente anterior no caminho
    # de menor custo encontrado ate determinado no.
    #
    # Essa estrutura permite reconstruir o caminho completo
    # depois que o algoritmo termina.
    predecessores = {
        no: None
        for no in grafo
    }

    # Fila de prioridade utilizada para escolher o proximo
    # no a ser processado.
    #
    # Cada elemento da fila possui o formato:
    #
    #     (distancia_acumulada, no_atual)
    #
    # O heap garante que o elemento com menor distancia
    # acumulada seja retirado primeiro.
    fila_prioridade = []

    # A distancia da origem ate ela mesma e zero, pois
    # nenhum deslocamento e necessario para chegar ao no inicial.
    distancias[origem] = 0

    # Insere a origem na fila de prioridade com distancia zero.
    #
    # heapq.heappush() insere um elemento no heap mantendo
    # sua propriedade de fila de prioridade.
    heapq.heappush(
        fila_prioridade,
        (0, origem)
    )

    # O algoritmo continua enquanto houver nos aguardando
    # processamento na fila de prioridade.
    while fila_prioridade:

        # Retira da fila o no com a menor distancia acumulada
        # conhecida ate o momento.
        #
        # distancia_atual representa o custo para chegar ao no.
        # no_atual representa o no que sera analisado.
        distancia_atual, no_atual = heapq.heappop(
            fila_prioridade
        )

        # Ignora uma entrada antiga da fila.
        #
        # Durante o algoritmo, um mesmo no pode ser inserido
        # varias vezes na fila, caso sejam encontrados caminhos
        # cada vez menores ate ele.
        #
        # Se a distancia retirada da fila for maior que a menor
        # distancia atualmente registrada, significa que essa
        # entrada esta desatualizada e nao precisa ser processada.
        if distancia_atual > distancias[no_atual]:
            continue

        # Se o no atual ja e o destino, podemos encerrar.
        #
        # Como a fila de prioridade sempre retira primeiro o no
        # com menor distancia conhecida, quando o destino e
        # retirado com sua menor distancia, o menor caminho
        # ate ele ja foi encontrado.
        if no_atual == destino:
            break

        # Percorre todas as arestas que saem do no atual.
        #
        # Cada vizinho representa um no conectado ao no atual.
        # O comprimento representa o peso da aresta, ou seja,
        # o custo para percorrer essa conexao.
        for vizinho, comprimento in grafo[no_atual]:

            # O algoritmo de Dijkstra exige pesos nao negativos.
            #
            # Como os pesos representam comprimentos fisicos,
            # normalmente todos devem ser maiores ou iguais a zero.
            #
            # Caso seja encontrado um peso negativo, a execucao
            # e interrompida com uma mensagem de erro.
            if comprimento < 0:
                raise ValueError(
                    "O algoritmo de Dijkstra nao aceita "
                    "pesos negativos."
                )

            # Calcula o custo de chegar ao vizinho passando
            # pelo no atual.
            #
            # Esse valor e formado pela distancia ja acumulada
            # ate o no atual somada ao comprimento da nova aresta.
            nova_distancia = (
                distancia_atual + comprimento
            )

            # Relaxamento da aresta.
            #
            # Verifica se o caminho passando pelo no atual
            # e menor que o melhor caminho conhecido anteriormente
            # ate o vizinho.
            #
            # Se for menor, atualiza:
            # - a menor distancia ate o vizinho;
            # - o predecessor do vizinho;
            # - a fila de prioridade, para que o vizinho
            #   seja processado com sua nova distancia.
            if nova_distancia < distancias[vizinho]:

                # Registra a nova menor distancia encontrada.
                distancias[vizinho] = nova_distancia

                # Registra o no atual como predecessor do vizinho.
                # Isso permite reconstruir o caminho posteriormente.
                predecessores[vizinho] = no_atual

                # Insere o vizinho na fila com sua nova distancia.
                #
                # Nao e necessario remover a entrada antiga da fila.
                # Ela sera ignorada posteriormente caso esteja
                # desatualizada, conforme a verificacao feita
                # no inicio do while.
                heapq.heappush(
                    fila_prioridade,
                    (nova_distancia, vizinho)
                )

    # Se a distancia do destino continua infinita, nenhuma
    # rota foi encontrada entre a origem e o destino.
    #
    # Nesse caso, retorna None para o caminho e infinito
    # para a distancia total.
    if distancias[destino] == float("inf"):
        return None, float("inf")

    # Inicia a reconstrução do caminho a partir do destino.
    #
    # O dicionario predecessores permite voltar de cada no
    # para o no anterior, ate chegar novamente a origem.
    caminho = []
    no_atual = destino

    # Continua enquanto houver um no valido para adicionar.
    #
    # O predecessor da origem e None, pois ela e o inicio
    # do caminho e nao possui um no anterior.
    while no_atual is not None:

        # Adiciona o no atual ao caminho.
        caminho.append(no_atual)

        # Avanca para o predecessor do no atual.
        no_atual = predecessores[no_atual]

    # A reconstrução foi feita do destino para a origem.
    # Por isso, a lista precisa ser invertida para apresentar
    # o caminho na ordem correta de percurso.
    caminho.reverse()

    # Retorna o caminho encontrado e a menor distancia total.
    return caminho, distancias[destino]


def mostrar_resultado(origem, destino, caminho, distancia_total):
    """
    # mostrar_resultado

    Exibe o resultado do algoritmo.

    A funcao recebe a origem, o destino, o caminho encontrado
    e a distancia total calculada pelo algoritmo de Dijkstra.

    Args:
        origem: no inicial do caminho.
    
        destino: no final do caminho.

        caminho: lista de nos do caminho encontrado, na ordem
                 em que devem ser percorridos.

        distancia_total: custo total do caminho encontrado.

    Returns:
        None: Sao apenas exibidas informacoes

    Caso exista um caminho, sao exibidos:
        - o no de origem;
        - o no de destino;
        - a sequencia de nos percorridos;
        - o comprimento total do caminho.

    Caso nenhum caminho seja encontrado, a funcao informa
    essa situacao e encerra a exibicao do resultado.
    """

    print()
    print("========== RESULTADO ==========")

    # Mostra o no utilizado como ponto inicial da busca.
    print(f"Origem: {origem}")

    # Mostra o no utilizado como destino da busca.
    print(f"Destino: {destino}")

    # Quando o algoritmo nao encontra um caminho, ele retorna
    # None para a variavel caminho.
    #
    # Nesse caso, nao e possivel exibir uma sequencia de nos,
    # portanto a funcao mostra uma mensagem informativa
    # e encerra sua execucao com return.
    if caminho is None:
        print("Nenhum caminho foi encontrado.")
        return

    # Informa que existe um caminho entre a origem e o destino.
    print("Caminho encontrado:")

    # A variavel caminho e uma lista contendo os nos na ordem
    # em que devem ser percorridos.
    #
    # O metodo join() transforma essa lista em uma unica string,
    # utilizando " -> " como separador entre os nos.
    #
    # Exemplo:
    # ["A1", "E1", "I1", "Y1"]
    #
    # sera exibido como:
    # A1 -> E1 -> I1 -> Y1
    print(" -> ".join(caminho))

    # Exibe o comprimento total do caminho encontrado.
    #
    # O formato :.2f limita a exibicao a duas casas decimais.
    # A unidade utilizada e o milimetro, conforme definido
    # na representacao do grafo.
    print(f"Comprimento total: {distancia_total:.2f} mm")

    print("================================")
    print()


def main():
    """
    # Main 

    Funcao principal do programa.

    Responsavel por:
        - obter os nos validos do grafo;
        - exibir o cabecalho do programa;
        - receber a origem e o destino pelo terminal;
        - normalizar as entradas do usuario;
        - verificar se os nos informados existem;
        - executar o algoritmo de Dijkstra;
        - exibir o resultado encontrado.
    """

    # Cria um conjunto contendo todos os nos cadastrados
    # no grafo.
    #
    # O metodo keys() retorna as chaves do dicionario grafo,
    # que representam os nos existentes.
    #
    # O uso de um conjunto permite verificar rapidamente
    # se determinado no pertence ao conjunto de nos validos.
    nos_validos = set(grafo.keys())

    print("========== DIJKSTRA ==========")

    # Solicita ao usuario o no de origem.
    #
    # strip() remove espacos em branco no inicio e no final
    # da entrada.
    #
    # upper() converte a entrada para letras maiusculas,
    # permitindo que o usuario digite, por exemplo, "a1"
    # ou "A1" e ambos sejam interpretados como "A1".
    origem = input("Digite o nó de origem: ").strip().upper()

    # Solicita ao usuario o no de destino e aplica as mesmas
    # etapas de normalizacao utilizadas na origem.
    destino = input("Digite o nó de destino: ").strip().upper()

    # Verifica se o no de origem informado esta cadastrado
    # no conjunto de nos validos.
    #
    # Caso o no nao exista, exibe uma mensagem de erro.
    # O algoritmo nao e executado nessa situacao.
    if origem not in nos_validos:
        print(f"Erro: o nó de origem '{origem}' não existe no grafo.")

    # Caso a origem seja valida, verifica se o destino
    # tambem esta cadastrado no grafo.
    #
    # O uso de elif garante que somente uma das mensagens
    # de erro seja exibida nessa etapa.
    elif destino not in nos_validos:
        print(f"Erro: o nó de destino '{destino}' não existe no grafo.")

    # Se tanto a origem quanto o destino forem validos,
    # o programa pode executar o algoritmo.
    else:

        # Executa o algoritmo de Dijkstra utilizando:
        # - grafo: estrutura que representa os nos e as arestas;
        # - origem: no inicial informado pelo usuario;
        # - destino: no final informado pelo usuario.
        #
        # A funcao retorna:
        # - caminho: lista de nos que formam o menor caminho;
        # - distancia_total: comprimento total desse caminho.
        caminho, distancia_total = dijkstra(
            grafo,
            origem,
            destino
        )

        # Envia os dados encontrados para a funcao
        # mostrar_resultado(), responsavel por organizar
        # e exibir as informacoes no terminal.
        #
        # Essa separacao evita misturar a logica do algoritmo
        # com a parte de apresentacao dos resultados.
        mostrar_resultado(
            origem,
            destino,
            caminho,
            distancia_total
        )

if __name__ == "__main__":
    main()