import argparse
from datetime import datetime
from decimal import Decimal, InvalidOperation

from src.integracao_v5 import executar
from src.google_sheets_sinais import (
    ABA_RESULTADOS,
    SPREADSHEET_ID,
    conectar_google_sheets,
)


CABECALHO = [
    "Sinal",
    "Origem",
    "Intermediário",
    "Destino",
    "Distância Física (mm)",
    "Custo Dijkstra",
    "Caminho",
    "Status",
    "Detalhes",
]


def gerar_linhas_resultados(plano):
    """Converte os resultados da V5 para a planilha."""
    sinais = plano["sinais"]
    resultados = plano["resultados"]

    if len(sinais) != len(resultados):
        raise ValueError("Quantidade de resultados inconsistente.")

    linhas = [CABECALHO.copy()]

    for sinal, resultado in zip(sinais, resultados):
        for campo in ("sinal", "origem", "intermediario", "destino"):
            if sinal[campo] != resultado.get(campo):
                raise ValueError(
                    f"Resultado inconsistente: {sinal['sinal']}"
                )

        if resultado.get("status") != "OK":
            raise ValueError(
                f"Roteamento nao concluido: {sinal['sinal']}"
            )

        caminho = resultado.get("caminho")
        distancia = resultado.get("distancia_fisica")
        custo = resultado.get("custo_dijkstra")

        if not isinstance(caminho, (list, tuple)) or not caminho:
            raise ValueError(
                f"Caminho invalido: {sinal['sinal']}"
            )

        if distancia is None or custo is None:
            raise ValueError(
                f"Distancia ou custo ausente: {sinal['sinal']}"
            )

        linhas.append([
            sinal["sinal"],
            sinal["origem"],
            sinal["intermediario"],
            sinal["destino"],
            float(distancia),
            float(custo),
            " -> ".join(str(no) for no in caminho),
            resultado["status"],
            resultado.get("detalhes", "") or "",
        ])

    return linhas


def ler_resultados(servico):
    """Le A:I sem formatacao numerica brasileira."""
    resposta = servico.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{ABA_RESULTADOS}'!A:I",
        valueRenderOption="UNFORMATTED_VALUE",
    ).execute()

    return resposta.get("values", [])


def normalizar(linhas):
    """Normaliza linhas para comparar conteudos."""
    saida = []

    for linha in linhas:
        valores = list(linha[:9])

        while valores and valores[-1] == "":
            valores.pop()

        saida.append(valores)

    while saida and not saida[-1]:
        saida.pop()

    return saida


def numero_igual(a, b):
    try:
        return Decimal(str(a)) == Decimal(str(b))
    except (InvalidOperation, ValueError):
        return False


def linhas_iguais(atuais, novas):
    """Compara cabecalhos como texto e dados numericos corretamente."""
    atuais = normalizar(atuais)
    novas = normalizar(novas)

    if len(atuais) != len(novas):
        return False

    for numero_linha, (atual, novo) in enumerate(
        zip(atuais, novas), start=1
    ):
        atual = atual + [""] * (9 - len(atual))
        novo = novo + [""] * (9 - len(novo))

        for indice, (a, b) in enumerate(zip(atual, novo)):

            # Cabecalho: todas as colunas sao texto.
            if numero_linha == 1:
                if str(a) != str(b):
                    return False
                continue

            # Distancia fisica e custo Dijkstra.
            if indice in (4, 5) and a != "" and b != "":
                if not numero_igual(a, b):
                    return False

            # Demais colunas.
            elif str(a) != str(b):
                return False

    return True



def criar_backup(servico):
    """Cria copia integral da aba de resultados."""
    resposta = servico.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        fields="sheets(properties(sheetId,title))",
    ).execute()

    origem = next(
        (
            aba["properties"]
            for aba in resposta.get("sheets", [])
            if aba["properties"]["title"] == ABA_RESULTADOS
        ),
        None,
    )

    if origem is None:
        raise ValueError("Aba Resultados-Dijkstra nao encontrada.")

    nome = (
        "Resultados-BACKUP-"
        + datetime.now().strftime("%Y%m%d-%H%M%S")
    )

    copia = servico.spreadsheets().sheets().copyTo(
        spreadsheetId=SPREADSHEET_ID,
        sheetId=origem["sheetId"],
        body={"destinationSpreadsheetId": SPREADSHEET_ID},
    ).execute()

    servico.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "requests": [{
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": copia["sheetId"],
                        "title": nome,
                    },
                    "fields": "title",
                }
            }]
        },
    ).execute()

    print(f"Backup criado: {nome}")
    return nome


def sincronizar(*, aplicar=False):
    # Reutiliza a integracao V5 sem escrever.
    plano = executar(aplicar=False)
    linhas_novas = gerar_linhas_resultados(plano)

    servico = conectar_google_sheets()
    linhas_atuais = ler_resultados(servico)

    iguais = linhas_iguais(linhas_atuais, linhas_novas)

    print("\n========== SINCRONIZACAO DE RESULTADOS ==========")
    print("Resultados calculados:", len(linhas_novas) - 1)
    print("Linhas atuais:", max(0, len(linhas_atuais) - 1))
    print("Sincronizados:", "SIM" if iguais else "NAO")

    print("\nPrimeiros resultados:")
    for linha in linhas_novas[1:6]:
        print(
            f"{linha[0]} | {linha[6]} | "
            f"{linha[4]} mm | {linha[7]}"
        )

    if iguais:
        print("\nNenhuma alteracao necessaria.")
        return

    if not aplicar:
        print("\nSIMULACAO: nenhuma escrita realizada.")
        return

    print(
        "\nATENCAO: as colunas A:I de Resultados-Dijkstra "
        "serao substituidas."
    )

    if input("Digite SINCRONIZAR para confirmar: ").strip() != "SINCRONIZAR":
        print("Operacao cancelada.")
        return

    # Confere se a aba foi modificada durante a simulacao.
    if ler_resultados(servico) != linhas_atuais:
        raise ValueError(
            "Resultados-Dijkstra mudou. Operacao cancelada."
        )

    # Confere se os calculos continuam iguais.
    novo_plano = executar(aplicar=False)
    novas_linhas_conferidas = gerar_linhas_resultados(novo_plano)

    if not linhas_iguais(novas_linhas_conferidas, linhas_novas):
        print("\nDIVERGENCIAS ENTRE AS DUAS EXECUCOES:")

        nomes_colunas = CABECALHO

        if len(novas_linhas_conferidas) != len(linhas_novas):
            print(
                "Quantidade de linhas:",
                len(linhas_novas),
                "->",
                len(novas_linhas_conferidas),
            )

        for numero, (antiga, nova) in enumerate(
            zip(linhas_novas, novas_linhas_conferidas),
            start=1,
        ):
            for indice, (a, b) in enumerate(zip(antiga, nova)):
                if indice in (4, 5):
                    diferente = not numero_igual(a, b)
                else:
                    diferente = str(a) != str(b)

                if diferente:
                    print(
                        f"Linha {numero}, coluna {nomes_colunas[indice]}:"
                    )
                    print(f"  Primeira execucao: {a!r}")
                    print(f"  Segunda execucao: {b!r}")

        raise ValueError(
            "Resultados mudaram durante a simulacao. "
            "Operacao cancelada."
        )

    # Verifica se as duas outras abas continuam sincronizadas.
    if novo_plano["atualizacoes_database"]:
        raise ValueError(
            "Database possui alteracoes pendentes. "
            "Operacao cancelada."
        )

    from src.sincronizar_sinais_v5 import (
        ler_linhas_aba,
        normalizar_linhas,
    )

    sinais_atuais = ler_linhas_aba(servico)
    sinais_esperados = novo_plano["plano_sinais"]["linhas_sinais"]

    if (
        normalizar_linhas(sinais_atuais)
        != normalizar_linhas(sinais_esperados)
    ):
        raise ValueError(
            "Sinais-Dijkstra nao esta sincronizada. "
            "Operacao cancelada."
        )

    criar_backup(servico)

    # Substitui somente os valores A:I.
    servico.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{ABA_RESULTADOS}'!A:I",
    ).execute()

    servico.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{ABA_RESULTADOS}'!A1",
        valueInputOption="RAW",
        body={"values": linhas_novas},
    ).execute()

    gravadas = ler_resultados(servico)

    if not linhas_iguais(gravadas, linhas_novas):
        raise RuntimeError(
            "Escrita realizada, mas a conferencia encontrou "
            "divergencias. Verifique o backup antes de repetir."
        )

    print(
        "\nSUCESSO: Resultados-Dijkstra sincronizada "
        "e conferida."
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aplicar", action="store_true")
    args = parser.parse_args()

    sincronizar(aplicar=args.aplicar)


if __name__ == "__main__":
    main()