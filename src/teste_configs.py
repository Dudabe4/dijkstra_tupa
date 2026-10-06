from google_sheets import ler_planilha
from configs import Configuracoes


def main():

    configuracoes_brutas, dados_grafo = ler_planilha()

    config = Configuracoes(configuracoes_brutas)

    print("\n========== CONFIGURAÇÕES ==========")

    print("\nParâmetros:")
    print(
        f"Fator caminho principal: "
        f"{config.fator_caminho_principal}"
    )

    print(
        f"Penalização por utilização: "
        f"{config.penalizacao_utilizacao}"
    )

    print(
        f"Penalização entrada hoop: "
        f"{config.penalizacao_entrada_hoop}"
    )

    print("\nCaminho principal:")
    print(config.caminho_principal)

    print("\nArestas penalizadas:")
    for aresta in config.arestas_penalizadas:
        print(aresta)

    print("\nQuantidade de conexões do grafo:")
    print(len(dados_grafo))

    print("\n===================================")


if __name__ == "__main__":
    main()