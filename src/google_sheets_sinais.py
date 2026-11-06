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
ABA_DATABASE = "Database"

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


def ler_database():
    """Le A:N da Database, preservando a linha real de cada registro.

    Retorna uma lista de dicionarios com 'linha_planilha' (linha 2 em diante)
    e os valores originais das colunas A:N em 'valores'. Nao escreve dados.
    A leitura usa valores formatados, como a leitura original de sinais.
    """
    servico = conectar_google_sheets()
    resposta = (
        servico.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{ABA_DATABASE}'!A:N"
        ).execute()
    )
    linhas = resposta.get("values", [])
    if not linhas:
        raise ValueError("A aba 'Database' esta vazia.")

    registros = []
    for numero_linha, linha in enumerate(linhas[1:], start=2):
        if not any(str(celula).strip() for celula in linha):
            continue
        valores = list(linha[:14]) + [""] * max(0, 14 - len(linha))

        tag_via = valores[4] if len(valores) > 4 else ""

        if tag_via.strip().casefold() == "tag da via":
            continue

        registros.append({
            "linha_planilha": numero_linha,
            "valores": valores,
            "tag_via": str(valores[4]).strip(),  # Coluna E
        })
    return registros


def escrever_sinais_automatizados(linhas_sinais, *, confirmar_substituicao=False):
    """Substitui A:D de Sinais-Dijkstra somente com confirmacao explicita.

    'linhas_sinais' deve incluir o cabecalho e as linhas na ordem
    Sinal | Origem | Intermediário | Destino.
    Esta operacao nao altera outras abas nem colunas fora de A:D.
    """
    if not confirmar_substituicao:
        raise ValueError(
            "Escrita bloqueada: passe confirmar_substituicao=True "
            "apos revisar os sinais gerados."
        )
    if not linhas_sinais or any(len(linha) != 4 for linha in linhas_sinais):
        raise ValueError("Informe linhas de quatro colunas, incluindo cabecalho.")
    if [str(v).strip().casefold() for v in linhas_sinais[0]] != [
        "sinal", "origem", "intermediário", "destino"
    ]:
        raise ValueError("Cabecalho invalido para Sinais-Dijkstra.")

    servico = conectar_google_sheets()
    servico.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{ABA_SINAIS}'!A:D"
    ).execute()
    servico.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{ABA_SINAIS}'!A1",
        valueInputOption="RAW",
        body={"values": linhas_sinais}
    ).execute()


def atualizar_celulas_database(atualizacoes, *, confirmar_escrita=False):
    """Atualiza apenas celulas indicadas da Database via batchUpdate.

    Exemplo: [{"linha_planilha": 5, "coluna": "H", "valor": "L1"}].
    Colunas permitidas: H, I, L, M e N. Nenhuma outra celula e alterada.
    A decisao de preservar valores manuais cabe ao modulo chamador,
    que deve consultar 'ler_database' antes de montar as atualizacoes.
    """
    if not confirmar_escrita:
        raise ValueError(
            "Escrita bloqueada: passe confirmar_escrita=True "
            "apos revisar as atualizacoes."
        )
    colunas_permitidas = {"H", "I", "L", "M", "N"}
    dados = []
    enderecos = set()
    for item in atualizacoes:
        linha = item["linha_planilha"]
        coluna = str(item["coluna"]).strip().upper()
        if not isinstance(linha, int) or isinstance(linha, bool) or linha < 2:
            raise ValueError(f"Linha invalida: {linha!r}")
        if coluna not in colunas_permitidas:
            raise ValueError(f"Coluna nao autorizada: {coluna!r}")
        endereco = f"'{ABA_DATABASE}'!{coluna}{linha}"
        if endereco in enderecos:
            raise ValueError(f"Atualizacao duplicada: {endereco}")
        enderecos.add(endereco)
        dados.append({"range": endereco, "values": [[item["valor"]]]})

    if not dados:
        return

    servico = conectar_google_sheets()
    servico.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"valueInputOption": "RAW", "data": dados}
    ).execute()

def criar_backup_database():
    """Duplica a aba Database antes de modificar seus dados."""
    from datetime import datetime

    servico = conectar_google_sheets()
    planilha = servico.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        fields="sheets(properties(sheetId,title))"
    ).execute()

    abas = planilha.get("sheets", [])
    origem = next(
        (
            aba["properties"]
            for aba in abas
            if aba["properties"]["title"] == ABA_DATABASE
        ),
        None
    )

    if origem is None:
        raise ValueError("Aba Database nao encontrada.")

    nome_backup = (
        "Database-BACKUP-TX-"
        + datetime.now().strftime("%Y%m%d-%H%M%S")
    )

    copia = servico.spreadsheets().sheets().copyTo(
        spreadsheetId=SPREADSHEET_ID,
        sheetId=origem["sheetId"],
        body={"destinationSpreadsheetId": SPREADSHEET_ID}
    ).execute()

    novo_id = copia["sheetId"]

    servico.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "requests": [{
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": novo_id,
                        "title": nome_backup
                    },
                    "fields": "title"
                }
            }]
        }
    ).execute()

    print(f"Backup criado: {nome_backup}")
    return nome_backup
