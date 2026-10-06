from google_sheets import ler_planilha
from configs import Configuracoes
from construir_grafo import construir_grafo
from dijkstra import dijkstra


def main():

    print("\n========================================")
    print("       ROTEAMENTO DIJKSTRA - V.3")
    print("========================================")

    # ---------------------------------------------------------
    # 1. Ler dados da Google Planilha
    # ---------------------------------------------------------

    print("\nLendo dados da Google Planilha...")

    configuracoes_brutas, dados_grafo = ler_planilha()

    configuracoes = Configuracoes(configuracoes_brutas)

    # ---------------------------------------------------------
    # 2. Construir grafo físico
    # ---------------------------------------------------------

    grafo = construir_grafo(dados_grafo)

    print("Dados carregados com sucesso.")
    print(f"Nós no grafo: {len(grafo)}")
    print(f"Conexões físicas: {len(dados_grafo)}")

    # ---------------------------------------------------------
    # 3. Mostrar configurações utilizadas
    # ---------------------------------------------------------

    print("\nConfigurações:")
    print(
        f"Fator caminho principal: "
        f"{configuracoes.fator_caminho_principal}"
    )
    print(
        f"Penalização por utilização: "
        f"{configuracoes.penalizacao_utilizacao}"
    )
    print(
        f"Penalização entrada hoop: "
        f"{configuracoes.penalizacao_entrada_hoop}"
    )

    # ---------------------------------------------------------
    # 4. Entrada dos nós pelo usuário
    # ---------------------------------------------------------

    while True:

        origem = input(
            "\nDigite o nó de origem "
            "(ou 'sair' para encerrar): "
        ).strip().upper()

        if origem == "SAIR":
            print("\nPrograma encerrado.")
            break

        destino = input(
            "Digite o nó de destino: "
        ).strip().upper()

        # -----------------------------------------------------
        # Verifica se os nós existem
        # -----------------------------------------------------

        if origem not in grafo:
            print(
                f"\nErro: o nó de origem '{origem}' "
                f"não existe no grafo."
            )
            continue

        if destino not in grafo:
            print(
                f"\nErro: o nó de destino '{destino}' "
                f"não existe no grafo."
            )
            continue

        # -----------------------------------------------------
        # 5. Executar Dijkstra
        # -----------------------------------------------------

        # Nesta etapa ainda não estamos considerando
        # utilização anterior dos nós.
        utilizacao = {}

        caminho, custo_dijkstra, distancia_fisica = dijkstra(
            grafo,
            origem,
            destino,
            configuracoes,
            utilizacao
        )

        # -----------------------------------------------------
        # 6. Mostrar resultado
        # -----------------------------------------------------

        print("\n----------------------------------------")
        print("              RESULTADO")
        print("----------------------------------------")

        if caminho is None:

            print(
                f"\nNão existe caminho entre "
                f"{origem} e {destino}."
            )

        else:

            print("\nCaminho encontrado:")
            print(" -> ".join(caminho))

            print(
                f"\nDistância física: "
                f"{distancia_fisica:.2f} mm"
            )

            print(
                f"Custo utilizado pelo Dijkstra: "
                f"{custo_dijkstra:.2f}"
            )

        print("----------------------------------------")


if __name__ == "__main__":
    main()