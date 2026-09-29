from grafo import grafo as grafo_manual
from google_sheets import ler_planilha
from construir_grafo import construir_grafo


def organizar_grafo(grafo):
    """
    Converte o grafo para um formato padronizado,
    facilitando a comparação entre os dois grafos.
    """

    conexoes = {}

    for origem, arestas in grafo.items():
        for destino, comprimento in arestas:

            # Como o grafo é bidirecional, guardamos
            # apenas uma vez cada conexão.
            conexao = tuple(sorted([origem, destino]))

            conexoes[conexao] = comprimento

    return conexoes


def comparar_grafos(grafo_manual, grafo_planilha):
    """
    Compara o grafo manual com o grafo construído
    a partir da planilha.
    """

    manual = organizar_grafo(grafo_manual)
    planilha = organizar_grafo(grafo_planilha)

    erros = []

    # Verifica conexões que estão no manual,
    # mas não estão na planilha.
    for conexao in manual:

        if conexao not in planilha:
            erros.append(
                f"FALTA NA PLANILHA: "
                f"{conexao[0]} -> {conexao[1]} "
                f"({manual[conexao]:.2f} mm)"
            )

    # Verifica conexões que estão na planilha,
    # mas não estão no manual.
    for conexao in planilha:

        if conexao not in manual:
            erros.append(
                f"NAO EXISTE NO MANUAL: "
                f"{conexao[0]} -> {conexao[1]} "
                f"({planilha[conexao]:.2f} mm)"
            )

    # Verifica se os comprimentos são diferentes.
    for conexao in manual:

        if conexao in planilha:

            comprimento_manual = manual[conexao]
            comprimento_planilha = planilha[conexao]

            if comprimento_manual != comprimento_planilha:
                erros.append(
                    f"COMPRIMENTO DIFERENTE: "
                    f"{conexao[0]} -> {conexao[1]} | "
                    f"manual = {comprimento_manual:.2f} mm | "
                    f"planilha = {comprimento_planilha:.2f} mm"
                )

    return erros, manual, planilha


def main():

    print("========== CONFERENCIA DO GRAFO ==========")

    # Lê a planilha
    dados = ler_planilha()

    # Constrói o grafo automaticamente
    grafo_planilha = construir_grafo(dados)

    # Compara os dois grafos
    erros, manual, planilha = comparar_grafos(
        grafo_manual,
        grafo_planilha
    )

    print(f"\nConexoes no grafo manual:    {len(manual)}")
    print(f"Conexoes na planilha:        {len(planilha)}")

    if not erros:

        print("\nOK: Os dois grafos sao identicos.")
        print("Nenhuma conexao foi perdida.")
        print("Nenhum comprimento esta diferente.")

    else:

        print("\nFORAM ENCONTRADAS DIFERENCAS:")

        for erro in erros:
            print(f"- {erro}")

    print("===========================================")


if __name__ == "__main__":
    main()