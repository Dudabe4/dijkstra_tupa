from google_sheets import ler_planilha
from construir_grafo import construir_grafo
from dijkstra import dijkstra



def mostrar_resultado(caminho, distancia):
    """
    Exibe o resultado do caminho mínimo.
    """

    if caminho is None:
        print("\nNenhum caminho encontrado.")
        return

    print("\n========== RESULTADO ==========")
    print(f"Caminho: {' -> '.join(caminho)}")
    print(f"Comprimento total: {distancia:.2f} mm")
    print("===============================")


def main():

    # Leitura da Google Sheets
    dados = ler_planilha()

    # Construção automática do grafo
    grafo = construir_grafo(dados)

    # Nós disponíveis no grafo
    nos_validos = set(grafo.keys())

    print("========== DIJKSTRA ==========")

    origem = input("Digite o nó de origem: ").strip().upper()
    destino = input("Digite o nó de destino: ").strip().upper()

    # Verificação dos nós
    if origem not in nos_validos:
        print(f"\nErro: o nó '{origem}' não existe no grafo.")
        return

    if destino not in nos_validos:
        print(f"\nErro: o nó '{destino}' não existe no grafo.")
        return

    # Execução do Dijkstra
    caminho, distancia = dijkstra(
        grafo,
        origem,
        destino
    )

    # Exibição do resultado
    mostrar_resultado(caminho, distancia)


if __name__ == "__main__":
    main()