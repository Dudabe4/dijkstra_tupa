from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


# Caminho do arquivo de credenciais
BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = BASE_DIR / "credentials" / "credentials.json"

# ID da Google Planilha
SPREADSHEET_ID = "1zeMWMU6evxUITpNCUEt6Yy7V97lBqIgllDI-EFSUrSg"

# Nome da aba da planilha
SHEET_NAME = "Nós-Dijkstra"

# Permissão utilizada neste primeiro teste:
# somente leitura.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]


def conectar_google_sheets():
    """
    Cria a conexão autenticada com a Google Sheets API.
    """

    credenciais = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES
    )

    servico = build(
        "sheets",
        "v4",
        credentials=credenciais
    )

    return servico


def ler_planilha():
    """
    Lê a planilha e separa as configurações dos dados do grafo.

    Retorna:
        configuracoes: dados de configuração da planilha.
        dados_grafo: linhas da tabela física do grafo.
    """

    servico = conectar_google_sheets()

    intervalo = f"{SHEET_NAME}"

    resultado = (
        servico.spreadsheets()
        .values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=intervalo
        )
        .execute()
    )

    valores = resultado.get("values", [])

    configuracoes = {
        "parametros": {},
        "caminho_principal": [],
        "arestas_penalizadas": []
    }

    dados_grafo = []

    secao = None

    for linha in valores:

        if not linha:
            continue

        primeira_celula = linha[0].strip() if linha[0] else ""

        # Cabeçalho da tabela física do grafo
        if (
            len(linha) >= 3
            and primeira_celula == "no"
            and linha[1].strip() == "vizinho"
            and linha[2].strip() == "comprimento"
        ):
            secao = "grafo"
            continue

        # Identificação do caminho principal
        if primeira_celula == "caminho principal":
            secao = "caminho_principal"
            continue

        # Identificação das arestas penalizadas
        if primeira_celula == "arestas com penalizacao":
            secao = "arestas_penalizadas"
            continue

        # Linhas da tabela física
        if secao == "grafo":
            if len(linha) >= 3:
                dados_grafo.append(linha[:3])

            continue

        # Caminho principal
        if secao == "caminho_principal":
            for no in linha:
                if no.strip():
                    configuracoes["caminho_principal"].append(no.strip())

            continue

        # Arestas penalizadas
        if secao == "arestas_penalizadas":
            for aresta in linha:
                if aresta.strip():
                    configuracoes["arestas_penalizadas"].append(
                        aresta.strip()
                    )

            continue

        # Parâmetros de configuração
        if (
            len(linha) >= 2
            and linha[0].strip()
            and linha[1].strip()
        ):
            nome = linha[0].strip()
            valor = linha[1].strip()

            if nome == "Configuração" and valor == "Valor":
                continue

            configuracoes["parametros"][nome] = valor

    return configuracoes, dados_grafo


def main():

    configuracoes, dados_grafo = ler_planilha()

    print("========== CONFIGURAÇÕES ==========")

    print("Parâmetros:")
    for nome, valor in configuracoes["parametros"].items():
        print(f"{nome}: {valor}")

    print("\nCaminho principal:")
    print(configuracoes["caminho_principal"])

    print("\nArestas penalizadas:")
    print(configuracoes["arestas_penalizadas"])

    print("\n========== DADOS DO GRAFO ==========")

    for linha in dados_grafo:
        print(linha)

    print("====================================")


if __name__ == "__main__":
    main()