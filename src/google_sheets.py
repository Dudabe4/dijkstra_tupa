from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from construir_grafo import construir_grafo


# Caminho do arquivo de credenciais
BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = BASE_DIR / "credentials" / "credentials.json"

# ID da Google Planilha
SPREADSHEET_ID = "1pGlO6cT59_Fycrt_LUcETAkyXSqaHrbcN7-_RIA-k3E"

# Nome da aba da planilha
SHEET_NAME = "Página1"

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
    Lê os dados da planilha e retorna as linhas.
    """

    servico = conectar_google_sheets()

    intervalo = f"{SHEET_NAME}!A:C"

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

    return valores


def main():

    dados = ler_planilha()

    grafo = construir_grafo(dados)

    print("========== GRAFO ==========")

    for no, arestas in grafo.items():
        print(f"{no}: {arestas}")

    print("============================")


if __name__ == "__main__":
    main()