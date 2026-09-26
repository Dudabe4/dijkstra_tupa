from grafo import grafo, componentes_por_no
from dijkstra import dijkstra


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