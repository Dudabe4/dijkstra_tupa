class Configuracoes:
    """
    Armazena as configurações utilizadas pelo algoritmo de roteamento.

    Os valores são lidos da Google Planilha e convertidos
    para os tipos adequados.
    """

    def __init__(self, dados):
        parametros = dados["parametros"]

        # Parâmetros de custo
        self.fator_caminho_principal = float(
            parametros["fator caminho principal"].replace(",", ".")
        )

        self.penalizacao_utilizacao = float(
            parametros["penalização por utilização"].replace(",", ".")
        )

        self.penalizacao_entrada_hoop = float(
            parametros["penalização entrada hoop"].replace(",", ".")
        )

        # Caminho principal
        self.caminho_principal = dados["caminho_principal"]

        # Arestas que recebem penalização ao serem utilizadas
        self.arestas_penalizadas = self._normalizar_arestas(
            dados["arestas_penalizadas"]
        )

    @staticmethod
    def _normalizar_arestas(arestas):
        """
        Converte as arestas da planilha para um formato padronizado.

        Exemplo:
            "L1,U1" -> ("L1", "U1")

        A ordem dos nós não importa.
        """

        arestas_normalizadas = set()

        for aresta in arestas:

            partes = aresta.split(",")

            if len(partes) != 2:
                raise ValueError(
                    f"Aresta inválida na configuração: {aresta}"
                )

            no1 = partes[0].strip().upper()
            no2 = partes[1].strip().upper()

            # Ordena os nós para que:
            # L1,U1 e U1,L1 sejam considerados a mesma aresta.
            aresta_normalizada = (no1, no2)

            arestas_normalizadas.add(
                aresta_normalizada
            )

        return arestas_normalizadas