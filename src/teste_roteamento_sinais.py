from google_sheets import ler_planilha
from google_sheets_sinais import ler_sinais
from construir_grafo import construir_grafo
from configs import Configuracoes
from roteamento_sinais import (
    processar_sinais,
    resultados_para_planilha
)
from google_sheets_sinais import escrever_resultados


def main():
    print("Lendo configuracoes e grafo...")

    configuracoes_brutas, dados_grafo = ler_planilha()
    configuracoes = Configuracoes(configuracoes_brutas)
    grafo = construir_grafo(dados_grafo)

    print("Lendo sinais...")
    sinais = ler_sinais()

    print("Calculando rotas...\n")

    resultados, utilizacao = processar_sinais(
        sinais,
        grafo,
        configuracoes
    )

    for resultado in resultados:
        print("=" * 50)
        print(f"Sinal: {resultado['sinal']}")
        print(
            f"Rota: {resultado['origem']} -> "
            f"{resultado['destino']}"
        )
        print(f"Status: {resultado['status']}")

        if resultado["status"] == "OK":
            print("Caminho:", " -> ".join(resultado["caminho"]))
            print(
                f"Distancia fisica: "
                f"{resultado['distancia_fisica']:.2f} mm"
            )
            print(
                f"Custo Dijkstra: "
                f"{resultado['custo_dijkstra']:.2f}"
            )
        else:
            print("Erro:", resultado["detalhes"])

    print("\n========== UTILIZACAO ACUMULADA ==========")

    for no, quantidade in sorted(utilizacao.items()):
        print(f"{no}: {quantidade}")

    print("\n========== PREVIA DA PLANILHA ==========")

    tabela = resultados_para_planilha(resultados)
    escrever_resultados(tabela)

    print("\nResultados gravados na aba 'Resultados'.")


if __name__ == "__main__":
    main()
