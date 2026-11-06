import argparse
from datetime import datetime

from src.integracao_v5 import executar
from src.google_sheets_sinais import (
    ABA_SINAIS,
    SPREADSHEET_ID,
    conectar_google_sheets,
    escrever_sinais_automatizados,
)


def ler_linhas_aba(servico):
    resposta = servico.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{ABA_SINAIS}'!A:D",
    ).execute()

    return resposta.get("values", [])


def normalizar_linhas(linhas):
    """Remove somente celulas e linhas vazias finais."""
    normalizadas = []

    for linha in linhas:
        valores = [str(valor) for valor in linha[:4]]

        while valores and valores[-1] == "":
            valores.pop()

        normalizadas.append(valores)

    while normalizadas and not normalizadas[-1]:
        normalizadas.pop()

    return normalizadas


def criar_backup_aba(servico):
    """Duplica Sinais-Dijkstra antes de substitui-la."""
    resposta = servico.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        fields="sheets(properties(sheetId,title))",
    ).execute()

    origem = next(
        (
            aba["properties"]
            for aba in resposta.get("sheets", [])
            if aba["properties"]["title"] == ABA_SINAIS
        ),
        None,
    )

    if origem is None:
        raise ValueError("Aba Sinais-Dijkstra nao encontrada.")

    nome = (
        "Sinais-BACKUP-"
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


def sincronizar(*, aplicar=False):
    # Reutiliza o calculo completo da V5.
    # Esta chamada nao escreve nada.
    plano = executar(aplicar=False)

    linhas_novas = plano["plano_sinais"]["linhas_sinais"]

    automaticos = plano["plano_sinais"]["automaticos"]

    if len(linhas_novas) != len(automaticos) + 1:
        raise ValueError(
            "Quantidade de sinais inconsistente."
        )

    if not automaticos:
        raise ValueError("Nenhum sinal automatico encontrado.")

    servico = conectar_google_sheets()
    linhas_atuais = ler_linhas_aba(servico)

    iguais = (
        normalizar_linhas(linhas_atuais)
        == normalizar_linhas(linhas_novas)
    )

    print("\n========== SINCRONIZACAO DE SINAIS ==========")
    print("Sinais automaticos:", len(automaticos))
    print("Linhas atuais:", max(0, len(linhas_atuais) - 1))
    print("Linhas novas:", len(linhas_novas) - 1)
    print("Abas ja sincronizadas:", "SIM" if iguais else "NAO")

    print("\nPrimeiros sinais gerados:")
    for linha in linhas_novas[1:6]:
        print(" | ".join(str(valor) for valor in linha))

    if iguais:
        print("\nNenhuma alteracao necessaria.")
        return

    if not aplicar:
        print("\nSIMULACAO: nenhuma escrita realizada.")
        return

    print(
        "\nATENCAO: as colunas A:D de Sinais-Dijkstra "
        "serao substituidas pelos sinais automaticos."
    )

    if input("Digite SINCRONIZAR para confirmar: ").strip() != "SINCRONIZAR":
        print("Operacao cancelada.")
        return

    # Impede substituir uma aba modificada durante a simulacao.
    if ler_linhas_aba(servico) != linhas_atuais:
        raise ValueError(
            "Sinais-Dijkstra mudou durante a simulacao. "
            "Operacao cancelada."
        )

    # Confere novamente as entradas da V5.
    novo_plano = executar(aplicar=False)

    if (
        novo_plano["plano_sinais"]["linhas_sinais"] != linhas_novas
        or novo_plano["atualizacoes_database"]
        != plano["atualizacoes_database"]
    ):
        raise ValueError(
            "Os dados calculados mudaram. "
            "Operacao cancelada."
        )

    criar_backup_aba(servico)

    escrever_sinais_automatizados(
        linhas_novas,
        confirmar_substituicao=True,
    )

    linhas_gravadas = ler_linhas_aba(servico)

    if (
        normalizar_linhas(linhas_gravadas)
        != normalizar_linhas(linhas_novas)
    ):
        raise RuntimeError(
            "Escrita realizada, mas a verificacao encontrou "
            "divergencias. Nao repita a operacao antes de conferir."
        )

    print("\nSUCESSO: Sinais-Dijkstra sincronizada e conferida.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aplicar", action="store_true")
    args = parser.parse_args()

    sincronizar(aplicar=args.aplicar)


if __name__ == "__main__":
    main()