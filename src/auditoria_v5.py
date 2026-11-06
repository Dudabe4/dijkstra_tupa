import csv
import math
from collections import Counter
from datetime import datetime
from pathlib import Path

from src.integracao_v5 import executar
from src.google_sheets_nodes import ler_planilha


PASTA = Path("relatorios/auditoria_v5")

COLUNAS = {
    "H": 7,
    "I": 8,
    "L": 11,
    "M": 12,
    "N": 13,
}


def salvar_csv(nome, linhas, campos):
    PASTA.mkdir(parents=True, exist_ok=True)
    caminho = PASTA / nome

    with caminho.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos,
            delimiter=";"
        )
        escritor.writeheader()
        escritor.writerows(linhas)

    print(f"Arquivo gerado: {caminho}")
    return caminho


def texto(valor):
    if valor is None:
        return ""
    return str(valor).strip()


def valores_registro(registro):
    valores = list(registro.get("valores", []))
    return valores + [""] * max(0, 14 - len(valores))


def criar_indice_arestas(grafo):
    indice = {}

    for origem, vizinhos in grafo.items():
        for destino, comprimento in vizinhos:
            chave = (origem, destino)

            if chave in indice:
                if indice[chave] != comprimento:
                    raise ValueError(
                        f"Arestas duplicadas com pesos diferentes: {chave}"
                    )

            indice[chave] = comprimento

    return indice


def conferir_distancia(caminho, distancia, arestas):
    if not isinstance(caminho, (list, tuple)) or not caminho:
        return "CAMINHO INVALIDO", ""

    if not isinstance(distancia, (int, float)):
        return "DISTANCIA INVALIDA", ""

    if not math.isfinite(distancia):
        return "DISTANCIA INVALIDA", ""

    soma = 0.0

    for origem, destino in zip(caminho, caminho[1:]):
        chave = (origem, destino)

        if chave not in arestas:
            return f"ARESTA INEXISTENTE: {origem} -> {destino}", ""

        soma += arestas[chave]

    if not math.isclose(soma, distancia, rel_tol=1e-9, abs_tol=1e-6):
        return "DISTANCIA DIVERGENTE", soma

    return "OK", soma


def auditar(plano, registros, grafo):
    registros_por_linha = {
        registro["linha_planilha"]: registro
        for registro in registros
    }

    if len(registros_por_linha) != len(registros):
        raise ValueError("Existem linhas duplicadas nos registros.")

    alteracoes = plano["atualizacoes_database"]
    por_celula = {}

    for alteracao in alteracoes:
        linha = alteracao["linha_planilha"]
        coluna = alteracao["coluna"]
        chave = (linha, coluna)

        if coluna not in COLUNAS:
            raise ValueError(f"Coluna nao autorizada: {coluna}")

        if chave in por_celula:
            raise ValueError(f"Atualizacao duplicada: {coluna}{linha}")

        if linha not in registros_por_linha:
            raise ValueError(f"Linha inexistente: {linha}")

        por_celula[chave] = alteracao["valor"]

    automaticos = plano["plano_sinais"]["automaticos"]
    manuais = plano["plano_sinais"]["manuais"]
    resultados = plano["resultados"]

    if len(automaticos) != len(resultados):
        raise ValueError("Quantidade de resultados inconsistente.")

    arestas = criar_indice_arestas(grafo)

    divergencias = []
    relatorio_sinais = []
    relatorio_alteracoes = []
    alertas = []

    # 1. Todas as alteracoes previstas, incluindo valores anteriores.
    for alteracao in alteracoes:
        linha = alteracao["linha_planilha"]
        coluna = alteracao["coluna"]
        registro = registros_por_linha[linha]
        valores = valores_registro(registro)

        anterior = valores[COLUNAS[coluna]]
        novo = alteracao["valor"]

        relatorio_alteracoes.append({
            "linha": linha,
            "tag": registro["tag_via"],
            "celula": f"{coluna}{linha}",
            "coluna": coluna,
            "valor_atual": anterior,
            "valor_proposto": novo,
        })

    # 2. Divergencias de H/I: destacar TODAS, inclusive vazios.
    for item in automaticos:
        linha = item["linha_planilha"]
        registro = registros_por_linha[linha]
        valores = valores_registro(registro)

        for coluna, indice, campo in (
            ("H", 7, "origem"),
            ("I", 8, "destino"),
        ):
            atual = texto(valores[indice])
            calculado = texto(item[campo])

            if atual.upper() != calculado.upper():
                divergencias.append({
                    "linha": linha,
                    "tag": item["tag_via"],
                    "coluna": coluna,
                    "tipo": (
                        "CELULA VAZIA"
                        if not atual
                        else "NO DIFERENTE"
                    ),
                    "no_atual": atual,
                    "no_calculado": calculado,
                    "outra_extremidade_atual": (
                        texto(valores[8])
                        if coluna == "H"
                        else texto(valores[7])
                    ),
                    "outra_extremidade_calculada": (
                        item["destino"]
                        if coluna == "H"
                        else item["origem"]
                    ),
                    "decisao": "CONFERIR",
                })

    # 3. Rotas automaticas e respectivas distancias.
    for item, resultado in zip(automaticos, resultados):
        linha = item["linha_planilha"]
        registro = registros_por_linha[linha]
        valores = valores_registro(registro)

        caminho = resultado.get("caminho")
        distancia = resultado.get("distancia_fisica")

        problemas = []

        if resultado.get("sinal") != item["tag_via"]:
            problemas.append("TAG DIVERGENTE")

        if resultado.get("origem") != item["origem"]:
            problemas.append("ORIGEM DO RESULTADO DIVERGENTE")

        if resultado.get("destino") != item["destino"]:
            problemas.append("DESTINO DO RESULTADO DIVERGENTE")

        if resultado.get("status") != "OK":
            problemas.append("STATUS NAO OK")

        if not isinstance(caminho, (list, tuple)) or not caminho:
            problemas.append("CAMINHO INVALIDO")
            caminho_texto = ""
        else:
            caminho_texto = " -> ".join(map(str, caminho))

            if caminho[0] != item["origem"]:
                problemas.append("INICIO DO CAMINHO DIVERGENTE")

            if caminho[-1] != item["destino"]:
                problemas.append("FIM DO CAMINHO DIVERGENTE")

        status_distancia, soma = conferir_distancia(
            caminho, distancia, arestas
        )

        if status_distancia != "OK":
            problemas.append(status_distancia)

        if problemas:
            alertas.append({
                "linha": linha,
                "tag": item["tag_via"],
                "problemas": " | ".join(problemas),
            })

        relatorio_sinais.append({
            "linha": linha,
            "tag": item["tag_via"],
            "tipo": "automatico",
            "origem_atual": valores[7],
            "origem_calculada": item["origem"],
            "destino_atual": valores[8],
            "destino_calculado": item["destino"],
            "caminho_atual": valores[11],
            "caminho_calculado": caminho_texto,
            "distancia_atual_mm": valores[13],
            "distancia_calculada_mm": distancia,
            "soma_arestas_mm": soma,
            "status": resultado.get("status"),
            "auditoria": " | ".join(problemas) if problemas else "OK",
        })

    # 4. Conferir preservacao dos manuais.
    for item in manuais:
        linha = item["linha_planilha"]
        registro = registros_por_linha[linha]
        valores = valores_registro(registro)

        alteracoes_manuais = [
            coluna
            for coluna in ("H", "I", "L", "N")
            if (linha, coluna) in por_celula
        ]

        status = (
            "ALTERACAO INDEVIDA: " + ", ".join(alteracoes_manuais)
            if alteracoes_manuais
            else "PRESERVADO"
        )

        if alteracoes_manuais:
            alertas.append({
                "linha": linha,
                "tag": item["tag_via"],
                "problemas": status,
            })

        relatorio_sinais.append({
            "linha": linha,
            "tag": item["tag_via"],
            "tipo": "manual",
            "origem_atual": valores[7],
            "origem_calculada": "",
            "destino_atual": valores[8],
            "destino_calculado": "",
            "caminho_atual": valores[11],
            "caminho_calculado": "",
            "distancia_atual_mm": valores[13],
            "distancia_calculada_mm": "",
            "soma_arestas_mm": "",
            "status": "manual",
            "auditoria": status,
        })

    relatorio_sinais.sort(key=lambda x: x["linha"])
    divergencias.sort(key=lambda x: (x["linha"], x["coluna"]))
    relatorio_alteracoes.sort(
        key=lambda x: (x["linha"], x["coluna"])
    )

    return {
        "divergencias": divergencias,
        "sinais": relatorio_sinais,
        "alteracoes": relatorio_alteracoes,
        "alertas": alertas,
    }


def main():
    print("\nExecutando roteamento em modo somente leitura...")
    plano = executar(aplicar=False)

    # Releitura para conferir os valores reais da Database.
    from src.google_sheets_sinais import ler_database
    registros = ler_database()

    # A leitura adicional tambem permite verificar se os dados
    # nao mudaram durante a simulacao.
    _, dados_grafo = ler_planilha()

    from src.integracao_v5 import carregar_roteador_v4
    _, construir_grafo, _ = carregar_roteador_v4()
    grafo = construir_grafo(dados_grafo)

    # Nao produzir relatorio potencialmente incorreto
    # se a planilha tiver mudado durante a execucao.
    from src.google_sheets_nodes import ler_componentes_nos
    from src.automatizar_sinais import preparar_automatizacao

    plano_atual = preparar_automatizacao(
        registros, ler_componentes_nos()
    )

    if plano_atual != plano["plano_sinais"]:
        raise ValueError(
            "Database ou cadastro de nos mudou durante a auditoria. "
            "Execute novamente."
        )

    auditoria = auditar(plano, registros, grafo)

    salvar_csv(
        "01_divergencias_origem_destino.csv",
        auditoria["divergencias"],
        [
            "linha", "tag", "coluna", "tipo",
            "no_atual", "no_calculado",
            "outra_extremidade_atual",
            "outra_extremidade_calculada", "decisao"
        ]
    )

    salvar_csv(
        "02_todos_os_sinais.csv",
        auditoria["sinais"],
        [
            "linha", "tag", "tipo",
            "origem_atual", "origem_calculada",
            "destino_atual", "destino_calculado",
            "caminho_atual", "caminho_calculado",
            "distancia_atual_mm", "distancia_calculada_mm",
            "soma_arestas_mm", "status", "auditoria"
        ]
    )

    salvar_csv(
        "03_todas_as_alteracoes.csv",
        auditoria["alteracoes"],
        [
            "linha", "tag", "celula", "coluna",
            "valor_atual", "valor_proposto"
        ]
    )

    salvar_csv(
        "04_alertas.csv",
        auditoria["alertas"],
        ["linha", "tag", "problemas"]
    )

    divergencias = auditoria["divergencias"]
    contagem = Counter(x["coluna"] for x in divergencias)

    print("\n========== AUDITORIA V5 ==========")
    print("Data:", datetime.now().strftime("%d/%m/%Y %H:%M"))
    print("Sinais automaticos:", len(plano["resultados"]))
    print("Sinais manuais:", len(plano["plano_sinais"]["manuais"]))
    print("Alteracoes previstas:", len(auditoria["alteracoes"]))
    print("Divergencias em H:", contagem["H"])
    print("Divergencias em I:", contagem["I"])
    print(
        "Linhas com divergencia H/I:",
        len({x["linha"] for x in divergencias})
    )
    print("Alertas de rota/distancia:", len(auditoria["alertas"]))

    print("\nDIVERGENCIAS DE ORIGEM E DESTINO:")
    if not divergencias:
        print("Nenhuma divergencia encontrada.")

    for item in divergencias:
        print(
            f"  {item['coluna']}{item['linha']} | "
            f"{item['tag']} | "
            f"{item['tipo']} | "
            f"ATUAL: {item['no_atual'] or '(vazio)'} | "
            f"CALCULADO: {item['no_calculado']}"
        )

    print("\nALERTAS:")
    if not auditoria["alertas"]:
        print("Nenhum alerta de rota ou distancia.")

    for alerta in auditoria["alertas"]:
        print(
            f"  Linha {alerta['linha']} | "
            f"{alerta['tag']} | {alerta['problemas']}"
        )

    print("\nNenhuma celula foi modificada.")
    if divergencias:
        print(
            "ATENCAO: H/I possuem divergencias. "
            "NAO EXECUTE --aplicar antes de revisar."
        )

    print("================================\n")


if __name__ == "__main__":
    main()