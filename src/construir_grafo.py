def construir_grafo(dados):
    """
    Constrói um grafo a partir dos dados lidos da planilha.

    Cada linha deve possuir:
        origem, destino, comprimento

    Cada conexão física deve aparecer apenas uma vez
    na planilha. A conexão inversa é criada automaticamente.

    Duplicações com o mesmo comprimento são ignoradas.
    Duplicações com comprimentos diferentes geram erro.
    """

    grafo = {}

    # Guarda as conexões físicas já adicionadas.
    conexoes = {}

    # Ignora a primeira linha, que contém os cabeçalhos
    for numero_linha, linha in enumerate(dados[1:], start=2):

        # Ignora linhas vazias ou incompletas
        if len(linha) < 3:
            continue

        origem = linha[0].strip().upper()
        destino = linha[1].strip().upper()
        comprimento = float(linha[2])

        # A conexão é considerada igual nos dois sentidos.
        conexao = tuple(sorted([origem, destino]))

        # Verifica se a conexão já apareceu.
        if conexao in conexoes:

            comprimento_existente = conexoes[conexao]

            # Duplicação exata: simplesmente ignora.
            if comprimento == comprimento_existente:
                continue

            # Mesma conexão, mas comprimento diferente.
            raise ValueError(
                f"Conexao duplicada com comprimentos diferentes "
                f"na linha {numero_linha}: "
                f"{origem} <-> {destino}. "
                f"Valores encontrados: "
                f"{comprimento_existente} mm e {comprimento} mm."
            )

        # Registra a nova conexão física.
        conexoes[conexao] = comprimento

        # Cria os nós caso ainda não existam.
        if origem not in grafo:
            grafo[origem] = []

        if destino not in grafo:
            grafo[destino] = []

        # Adiciona a conexão nos dois sentidos.
        grafo[origem].append(
            (destino, comprimento)
        )

        grafo[destino].append(
            (origem, comprimento)
        )

    return grafo