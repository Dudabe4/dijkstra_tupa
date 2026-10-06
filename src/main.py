from google_sheets import ler_planilha
from configs import Configuracoes
from construir_grafo import construir_grafo
from dijkstra import dijkstra
from validacao import validar_nos, validar_pesos, validar_simetria


def atualizar_utilizacao(utilizacao, caminho):
    """
    Atualiza a quantidade de utilizações dos nós
    depois que uma rota é encontrada.

    A origem não é contabilizada, pois a penalização
    é aplicada ao entrar no nó de destino de cada aresta.
    """

    for no in caminho[1:]:
        utilizacao[no] = utilizacao.get(no, 0) + 1


def main():

    print("\n========================================")
    print("           ROTEAMENTO DIJKSTRA")
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

    print("\nValidando grafo...")

    validar_nos(grafo)
    validar_pesos(grafo)
    validar_simetria(grafo)

    print("Grafo validado com sucesso.")

    print(f"Nós no grafo: {len(grafo)}")
    print(f"Conexões físicas: {len(dados_grafo)}")

    # ---------------------------------------------------------
    # 3. Mostrar configurações
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
    # 4. Dicionário de utilização
    # ---------------------------------------------------------

    utilizacao = {}

    # ---------------------------------------------------------
    # 5. Loop para entrada das rotas
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
        # 6. Executar Dijkstra
        # -----------------------------------------------------

        caminho, custo_dijkstra, distancia_fisica = dijkstra(
            grafo,
            origem,
            destino,
            configuracoes,
            utilizacao
        )

        # -----------------------------------------------------
        # 7. Mostrar resultado
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

            caminho_principal = configuracoes.caminho_principal

            if (
                caminho == caminho_principal
                or caminho == caminho_principal[::-1]
            ):
                print(" -> ".join(caminho) + " (caminho principal)")
            else:
                print(" -> ".join(caminho))

            print(
                f"\nDistância física: "
                f"{distancia_fisica:.2f} mm"
            )

            print(
                f"Custo utilizado pelo Dijkstra: "
                f"{custo_dijkstra:.2f}"
            )

            # -----------------------------------------------
            # 8. Atualizar utilização dos nós
            # -----------------------------------------------

            atualizar_utilizacao(
                utilizacao,
                caminho
            )

            print("\nUtilização dos nós:")

            for no, quantidade in utilizacao.items():
                print(f"{no}: {quantidade}")

        print("----------------------------------------")


if __name__ == "__main__":
    main()