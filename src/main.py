from google_sheets_nodes import ler_planilha
from configs.configs import Configuracoes
from construir_grafo import construir_grafo
from dijkstra import dijkstra
from validacao import validar_nos, validar_pesos, validar_simetria

from google_sheets_sinais import ler_sinais, escrever_resultados
from roteamento_sinais import (
    processar_sinais,
    resultados_para_planilha
)

from configs.terminal import titulo, sucesso, aviso, error, info


def atualizar_utilizacao(utilizacao, caminho):
    """
    Atualiza a utilização dos nós após encontrar uma rota.
    A origem não é contabilizada.
    """
    for no in caminho[1:]:
        utilizacao[no] = utilizacao.get(no, 0) + 1


def executar_modo_manual(grafo, configuracoes):
    """
    Mantém o roteamento manual pelo terminal.
    Permite informar um nó intermediário opcional.
    A utilização acumula entre as consultas desta sessão.
    """
    utilizacao = {}

    while True:
        origem = input(
            "\nDigite o nó de origem (ou 'sair' para voltar ao menu): "
        ).strip().upper()

        if origem == "SAIR":
            break

        intermediario = input(
            "Digite o nó intermediário (ou Enter para nenhum): "
        ).strip().upper()

        if intermediario == "":
            intermediario = "-"

        destino = input(
            "Digite o nó de destino: "
        ).strip().upper()

        # Validar os nós informados
        if origem not in grafo:
            print(" ")
            error(f"Erro: a origem '{origem}' não existe no grafo.")
            continue

        if intermediario != "-" and intermediario not in grafo:
            print(" ")
            error(f"Erro: o nó intermediário ")
            error(f"'{intermediario}' não existe no grafo.")
            continue

        if destino not in grafo:
            print(" ")
            error(f"Erro: o destino '{destino}' não existe no grafo.")
            continue

        try:
            if intermediario == "-":
                # Roteamento normal: origem -> destino
                caminho, custo_dijkstra, distancia_fisica = dijkstra(
                    grafo,
                    origem,
                    destino,
                    configuracoes,
                    utilizacao
                )

            else:
                # Primeiro trecho: origem -> intermediário
                caminho_1, custo_1, distancia_1 = dijkstra(
                    grafo,
                    origem,
                    intermediario,
                    configuracoes,
                    utilizacao
                )

                if caminho_1 is None:
                    print(" ")
                    error(f"Não existe caminho entre {origem} ")
                    error(f"e {intermediario}.")
                    continue

                # Segundo trecho: intermediário -> destino
                caminho_2, custo_2, distancia_2 = dijkstra(
                    grafo,
                    intermediario,
                    destino,
                    configuracoes,
                    utilizacao
                )

                if caminho_2 is None:
                    print(" ")
                    error("Não existe caminho entre {intermediario} ")
                    error(f"e {destino}.")
                    continue

                # Unir os caminhos sem repetir o intermediário
                caminho = caminho_1 + caminho_2[1:]

                custo_dijkstra = custo_1 + custo_2
                distancia_fisica = distancia_1 + distancia_2

        except (ValueError, KeyError, TypeError) as erro:
            print(" ")
            error(f"Erro ao calcular a rota: {erro}")
            continue

        print(" ")
        titulo("-------------------------------------")
        titulo("           RESULTADO")
        titulo("-------------------------------------")
        print(" ")

        if caminho is None:
            print(" ")
            error(f"Não existe caminho entre {origem} e {destino}.")
            continue

        caminho_principal = configuracoes.caminho_principal

        if caminho == caminho_principal or caminho == caminho_principal[::-1]:
            sucesso(" -> ".join(caminho) + " (caminho principal)")
        else:
            sucesso(" -> ".join(caminho))

        print(" ")
        print(f"Distância física: {distancia_fisica:.2f} mm")
        print(f"Custo Dijkstra: {custo_dijkstra:.2f}")

        # Atualizar utilização após calcular a rota completa
        atualizar_utilizacao(utilizacao, caminho)

        print("\nUtilização dos nós:")
        for no, quantidade in utilizacao.items():
            print(f"{no}: {quantidade}")

        print("----------------------------------------")


def executar_modo_automatico(grafo, configuracoes):
    """
    Lê os sinais da planilha, calcula as rotas e grava os resultados.
    Os detalhes ficam somente na aba Resultados.
    """
    try:
        print("\nLendo sinais da aba 'Sinais'...")
        sinais = ler_sinais()

        sucesso(f"Quantidade de sinais lidos: {len(sinais)}")
        print(" ")
        print("Calculando rotas...")

        resultados, utilizacao = processar_sinais(
            sinais,
            grafo,
            configuracoes
        )

        tabela = resultados_para_planilha(resultados)

        print("Gravando resultados na aba 'Resultados'...")
        escrever_resultados(tabela)

        sucesso("Resultados gravados com sucesso!")

    except Exception as erro:
        print(" ")
        error("Não foi possível concluir o modo automático.")
        error(f"Erro: {erro}")


def main():
    print(" ")
    titulo("=====================================")
    titulo("        ROTEAMENTO DIJKSTRA")
    titulo("=====================================")

    print("\nLendo configurações e grafo...")

    configuracoes_brutas, dados_grafo = ler_planilha()
    configuracoes = Configuracoes(configuracoes_brutas)
    grafo = construir_grafo(dados_grafo)

    sucesso("Dados carregados com sucesso.")

    print("\nValidando grafo...")

    erros = []
    erros.extend(validar_nos(grafo))
    erros.extend(validar_pesos(grafo))
    erros.extend(validar_simetria(grafo))

    if erros:
        print(" ")
        error("Foram encontrados problemas no grafo:")

        for erro in erros:
            error(f"- {erro}")

        print("\nCorrija os problemas antes de continuar.")
        return

    sucesso("Todas as validações do grafo foram aprovadas.")
    print(" ")

    print(f"Nós no grafo: {len(grafo)}")
    print(f"Conexões físicas: {len(dados_grafo)}")

    print(" ")
    info("Configurações:")
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

    while True:
        print(" ")
        titulo("=====================================")
        titulo("               MENU")
        titulo("=====================================")
        print("1 - Roteamento manual")
        print("2 - Roteamento automático pela planilha")
        print("0 - Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            executar_modo_manual(grafo, configuracoes)

        elif opcao == "2":
            executar_modo_automatico(grafo, configuracoes)

        elif opcao == "0":
            print(" ")
            aviso("Programa encerrado.")
            break

        else:
            print(" ")
            error("Opção inválida. Escolha 1, 2 ou 0.")


if __name__ == "__main__":
    main()