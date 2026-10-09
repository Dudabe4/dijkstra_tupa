from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


# ---------------------------------------------------------
# CONFIGURACAO
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = BASE_DIR / "credentials" / "credentials.json"

# Mantem a mesma planilha utilizada pelo modulo google_sheets.py.
SPREADSHEET_ID = "1zeMWMU6evxUITpNCUEt6Yy7V97lBqIgllDI-EFSUrSg"

ABA_SINAIS = "Sinais-Dijkstra"
ABA_RESULTADOS = "Resultados-Dijkstra"

# Permite ler a entrada e escrever os resultados.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


# ---------------------------------------------------------
# CONEXAO
# ---------------------------------------------------------

def conectar_google_sheets():
    """Cria a conexao autenticada com a Google Sheets API."""

    credenciais = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES
    )

    return build(
        "sheets",
        "v4",
        credentials=credenciais
    )


# ---------------------------------------------------------
# LEITURA DOS SINAIS
# ---------------------------------------------------------

def ler_sinais():
    """
    Le os sinais da aba Sinais.

    Colunas esperadas:
        Sinal | Origem | Intermediario | Destino

    O campo Intermediario pode conter '-' quando nao
    houver um no intermediario obrigatorio.

    Retorna uma lista de dicionarios.
    """

    servico = conectar_google_sheets()

    resposta = (
        servico.spreadsheets()
        .values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{ABA_SINAIS}!A:D"
        )
        .execute()
    )

    linhas = resposta.get("values", [])

    if not linhas:
        raise ValueError(
            f"A aba '{ABA_SINAIS}' esta vazia."
        )

    cabecalho = [
        celula.strip().casefold()
        for celula in linhas[0]
    ]

    cabecalho_esperado = [
        "sinal",
        "origem",
        "intermediário",
        "destino"
    ]

    if cabecalho[:4] != cabecalho_esperado:
        raise ValueError(
            "Cabecalho invalido na aba Sinais. "
            "Use: Sinal | Origem | Intermediário | Destino."
        )

    sinais = []

    for numero_linha, linha in enumerate(linhas[1:], start=2):

        # Ignora linhas completamente vazias.
        if not any(celula.strip() for celula in linha):
            continue

        # Preserva a linha para que um registro incompleto
        # possa ser identificado sem interromper o lote.
        valores = linha + [""] * (4 - len(linha))

        sinal = {
            "sinal": valores[0].strip() or f"Linha {numero_linha}",
            "origem": valores[1].strip().upper(),
            "intermediario": valores[2].strip().upper(),
            "destino": valores[3].strip().upper(),
            "linha_planilha": numero_linha
        }

        if len(linha) < 4 or not all(
            valores[i].strip() for i in range(4)
        ):
            sinal["erro_entrada"] = (
                "Preencha Sinal, Origem, Intermediário e Destino. "
                "Use '-' quando nao houver intermediario."
            )

        sinais.append(sinal)

    return sinais


# ---------------------------------------------------------
# ESCRITA DOS RESULTADOS
# ---------------------------------------------------------

def escrever_resultados(resultados):
    """
    Substitui o conteudo da aba Resultados.

    Cada resultado deve ser uma lista de valores.
    A primeira linha deve conter os cabecalhos.

    Esta funcao nao altera a aba Sinais nem a aba do grafo.
    """

    if not resultados:
        raise ValueError(
            "Nao ha resultados para escrever."
        )

    servico = conectar_google_sheets()

    # Limpa exclusivamente a aba de resultados.
    (
        servico.spreadsheets()
        .values()
        .clear(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{ABA_RESULTADOS}!A:Z"
        )
        .execute()
    )

    # Escreve os novos resultados a partir de A1.
    (
        servico.spreadsheets()
        .values()
        .update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{ABA_RESULTADOS}!A1",
            valueInputOption="RAW",
            body={"values": resultados}
        )
        .execute()
    )
