from grafo import grafo
from dijkstra import dijkstra


def validar_nos(grafo):
    """
    Verifica se todos os nos utilizados nas arestas
    existem no dicionario principal do grafo.
    """

    erros = []

    for no, arestas in grafo.items():

        for vizinho, comprimento in arestas:

            if vizinho not in grafo:
                erros.append(
                    f"O no '{no}' possui uma conexao com "
                    f"'{vizinho}', mas '{vizinho}' nao existe no grafo."
                )

    return erros


def validar_pesos(grafo):
    """
    Verifica se existem pesos negativos nas arestas do grafo.
    """

    erros = []

    for no, arestas in grafo.items():

        for vizinho, comprimento in arestas:

            if comprimento < 0:
                erros.append(
                    f"A conexao '{no}' -> '{vizinho}' possui "
                    f"peso negativo: {comprimento}."
                )

    return erros


def validar_simetria(grafo):
    """
    Verifica se as conexoes do grafo possuem o mesmo peso
    nos dois sentidos.

    Exemplo esperado:

        A1 -> E1 = 402.81
        E1 -> A1 = 402.81
    """

    erros = []

    for no, arestas in grafo.items():

        for vizinho, comprimento in arestas:

            conexao_inversa = False

            for destino, peso in grafo.get(vizinho, []):

                if destino == no:

                    if peso == comprimento:
                        conexao_inversa = True

                    else:
                        erros.append(
                            f"A conexao '{no}' -> '{vizinho}' "
                            f"possui peso {comprimento}, mas a "
                            f"conexao inversa possui peso {peso}."
                        )

                    break

            if not conexao_inversa:
                erros.append(
                    f"A conexao '{no}' -> '{vizinho}' "
                    f"nao possui conexao inversa."
                )

    return erros


def testar_dijkstra():
    """
    Executa alguns testes basicos do algoritmo de Dijkstra.
    """

    erros = []

    # Teste 1:
    # origem e destino diferentes.
    caminho, distancia = dijkstra(
        grafo,
        "A1",
        "A2"
    )

    if caminho is None:
        erros.append(
            "Falha no teste A1 -> A2: nenhum caminho encontrado."
        )

    # Teste 2:
    # origem e destino iguais.
    caminho, distancia = dijkstra(
        grafo,
        "A1",
        "A1"
    )

    if caminho != ["A1"] or distancia != 0:
        erros.append(
            "Falha no teste A1 -> A1."
        )

    return erros


def executar_validacoes():
    """
    Executa todas as validacoes do projeto.
    """

    print("========== VALIDACAO ==========")

    erros = []

    erros.extend(validar_nos(grafo))
    erros.extend(validar_pesos(grafo))
    erros.extend(validar_simetria(grafo))
    erros.extend(testar_dijkstra())

    if not erros:
        print("Todas as validacoes foram aprovadas.")

    else:
        print("Foram encontrados problemas:")

        for erro in erros:
            print(f"- {erro}")

    print("================================")


if __name__ == "__main__":
    executar_validacoes()