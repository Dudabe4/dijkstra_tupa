from dijkstra import dijkstra


def atualizar_utilizacao(utilizacao, caminho):
    """
    Atualiza a utilizacao dos nos de uma rota completa.
    A origem nao e contabilizada.
    """

    for no in caminho[1:]:
        utilizacao[no] = utilizacao.get(no, 0) + 1


def executar_trecho(
    grafo,
    origem,
    destino,
    configuracoes,
    utilizacao
):
    """
    Executa Dijkstra para um trecho da rota.
    Retorna caminho, custo e distancia fisica.
    """

    caminho, custo, distancia = dijkstra(
        grafo,
        origem,
        destino,
        configuracoes,
        utilizacao
    )

    if caminho is None:
        raise ValueError(
            f"Nao existe caminho entre {origem} e {destino}."
        )

    return caminho, custo, distancia


def rotear_sinal(sinal, grafo, configuracoes, utilizacao):
    """
    Calcula a rota de um sinal, com ou sem intermediario.

    A utilizacao so e atualizada depois que a rota completa
    e encontrada com sucesso.
    """

    nome = sinal["sinal"]
    origem = sinal["origem"]
    intermediario = sinal["intermediario"]
    destino = sinal["destino"]

    resultado = {
        "sinal": nome,
        "origem": origem,
        "intermediario": intermediario,
        "destino": destino,
        "distancia_fisica": None,
        "custo_dijkstra": None,
        "caminho": None,
        "status": "ERRO",
        "detalhes": ""
    }

    # Erro de preenchimento detectado na leitura da planilha.
    if "erro_entrada" in sinal:
        resultado["detalhes"] = sinal["erro_entrada"]
        return resultado

    try:
        # Caso 1: nao existe intermediario obrigatorio.
        if intermediario == "-":

            caminho, custo, distancia = executar_trecho(
                grafo,
                origem,
                destino,
                configuracoes,
                utilizacao
            )

        # Caso 2: a rota precisa passar pelo intermediario.
        else:

            caminho_1, custo_1, distancia_1 = executar_trecho(
                grafo,
                origem,
                intermediario,
                configuracoes,
                utilizacao
            )

            caminho_2, custo_2, distancia_2 = executar_trecho(
                grafo,
                intermediario,
                destino,
                configuracoes,
                utilizacao
            )

            # O intermediario aparece apenas uma vez.
            caminho = caminho_1 + caminho_2[1:]

            custo = custo_1 + custo_2
            distancia = distancia_1 + distancia_2

        # Atualiza a utilizacao uma unica vez por sinal.
        atualizar_utilizacao(utilizacao, caminho)

        resultado.update({
            "distancia_fisica": distancia,
            "custo_dijkstra": custo,
            "caminho": caminho,
            "status": "OK",
            "detalhes": ""
        })

    except (ValueError, KeyError, TypeError) as erro:
        # O erro deste sinal nao interrompe os demais.
        resultado["detalhes"] = str(erro)

    return resultado


def processar_sinais(sinais, grafo, configuracoes):
    """
    Processa os sinais na ordem em que aparecem na planilha.

    A utilizacao comeca em zero para cada lote automatico
    e se acumula entre os sinais processados.

    Retorna:
        resultados: lista de resultados individuais
        utilizacao: utilizacao acumulada dos nos
    """

    utilizacao = {}
    resultados = []

    for sinal in sinais:
        resultado = rotear_sinal(
            sinal,
            grafo,
            configuracoes,
            utilizacao
        )

        resultados.append(resultado)

    return resultados, utilizacao


def resultados_para_planilha(resultados):
    """
    Converte os resultados para uma tabela compativel
    com escrever_resultados() de google_sheets_sinais.py.
    """

    tabela = [[
        "Sinal",
        "Origem",
        "Intermediario",
        "Destino",
        "Distancia fisica (mm)",
        "Custo Dijkstra",
        "Caminho",
        "Status",
        "Detalhes"
    ]]

    for resultado in resultados:

        caminho = resultado["caminho"]

        if caminho:
            caminho_texto = " -> ".join(caminho)
        else:
            caminho_texto = "-"

        distancia = resultado["distancia_fisica"]
        custo = resultado["custo_dijkstra"]

        tabela.append([
            resultado["sinal"],
            resultado["origem"],
            resultado["intermediario"],
            resultado["destino"],
            round(distancia, 2) if distancia is not None else "",
            round(custo, 2) if custo is not None else "",
            caminho_texto,
            resultado["status"],
            resultado["detalhes"]
        ])

    return tabela