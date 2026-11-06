import argparse
import sys
from pathlib import Path

from src.automatizar_sinais import preparar_automatizacao
from src.atualizar_database import preparar_atualizacoes_database
from src.google_sheets_nodes import ler_componentes_nos, ler_planilha
from src.google_sheets_sinais import ler_database, atualizar_celulas_database, criar_backup_database

from decimal import Decimal, InvalidOperation

def configurar_ipv4():
    """Forca IPv4 sem instalar o patch mais de uma vez."""
    import socket

    if getattr(socket.getaddrinfo, "_tupa_ipv4", False):
        return

    original = socket.getaddrinfo

    def somente_ipv4(host, port, family=0, type=0, proto=0, flags=0):
        return original(
            host, port, socket.AF_INET, type, proto, flags
        )

    somente_ipv4._tupa_ipv4 = True
    socket.getaddrinfo = somente_ipv4

def carregar_roteador_v4():
    """Importa a V4 sem exigir alteracoes nos imports antigos de seus modulos."""
    pasta_src = str(Path(__file__).resolve().parent)
    if pasta_src not in sys.path:
        sys.path.insert(0, pasta_src)

    from roteamento_sinais import processar_sinais
    from construir_grafo import construir_grafo
    from configs.configs import Configuracoes

    return processar_sinais, construir_grafo, Configuracoes


def preparar_entradas(plano_sinais):
    """Cria os sinais no formato da V4, preservando ordem e linha original."""
    automaticos = plano_sinais["automaticos"]
    linhas = plano_sinais["linhas_sinais"]

    if len(linhas) != len(automaticos) + 1:
        raise ValueError(
            "Quantidade de linhas geradas difere dos sinais automaticos."
        )

    sinais = []
    vistas = set()

    for posicao, item in enumerate(automaticos, start=2):
        linha = item["linha_planilha"]

        if linha in vistas:
            raise ValueError(f"Linha original duplicada: {linha}")

        vistas.add(linha)

        if item.get("linha_sinais") != posicao:
            raise ValueError(
                f"Ordem de Sinais-Dijkstra inconsistente na linha {linha}."
            )

        tag, origem, intermediario, destino = linhas[posicao - 1]

        if (
            tag != item["tag_via"]
            or origem != item["origem"]
            or destino != item["destino"]
            or intermediario != "-"
        ):
            raise ValueError(
                f"Sinal gerado nao corresponde a Database na linha {linha}."
            )

        sinais.append({
            "sinal": tag,
            "origem": origem,
            "intermediario": intermediario,
            "destino": destino,
            "linha_planilha": posicao,
        })

    return sinais


def associar_resultados(plano_sinais, sinais, resultados):
    """Associa por posicao e confere identidade; nunca procura apenas por tag."""
    if len(resultados) != len(sinais):
        raise ValueError(
            f"Lote incompleto: {len(resultados)} resultados "
            f"para {len(sinais)} sinais."
        )

    associados = []
    falhas = []

    for indice, (item, sinal, resultado) in enumerate(
        zip(plano_sinais["automaticos"], sinais, resultados),
        start=1
    ):
        if not isinstance(resultado, dict):
            raise ValueError(
                f"Resultado {indice} nao e dicionario."
            )

        for campo in ("sinal", "origem", "intermediario", "destino"):
            if resultado.get(campo) != sinal[campo]:
                raise ValueError(
                    f"Resultado {indice}: campo {campo} "
                    f"nao confere com a entrada."
                )

        if resultado.get("status") != "OK":
            falhas.append((
                item["linha_planilha"],
                item["tag_via"],
                resultado.get("detalhes", "")
            ))

        associados.append({
            "linha_planilha": item["linha_planilha"],
            "tag_via": item["tag_via"],
            "status": resultado.get("status"),
            "caminho": resultado.get("caminho"),
            "distancia_fisica": resultado.get("distancia_fisica"),
        })

    if falhas:
        exemplos = "; ".join(
            f"linha {linha}: {tag} ({motivo})"
            for linha, tag, motivo in falhas[:8]
        )

        raise ValueError(
            f"{len(falhas)} roteamento(s) falharam. "
            f"Escrita bloqueada. {exemplos}"
        )

    return associados


def preparar_integracao(
    registros,
    componentes_nos,
    grafo,
    configuracoes,
    processar_sinais
):
    """Calcula e prepara alteracoes, sem escrever nas planilhas."""
    plano_sinais = preparar_automatizacao(
        registros, componentes_nos
    )

    sinais = preparar_entradas(plano_sinais)

    if not sinais:
        raise ValueError(
            "Nenhum sinal automatico encontrado; nada sera escrito."
        )

    resultados, utilizacao = processar_sinais(
        sinais, grafo, configuracoes
    )

    associados = associar_resultados(
        plano_sinais, sinais, resultados
    )

    plano_resultados = preparar_atualizacoes_database(
        registros, associados
    )

    # Combina H/I e marcacoes manuais com L/M/N.
    atualizacoes = (
        plano_sinais["atualizacoes_database"]
        + plano_resultados["atualizacoes_database"]
    )

    enderecos = set()

    for item in atualizacoes:
        endereco = (
            item["linha_planilha"],
            item["coluna"]
        )

        if endereco in enderecos:
            raise ValueError(
                f"Atualizacao duplicada: {endereco}"
            )

        enderecos.add(endereco)

    return {
        "sinais": sinais,
        "resultados": resultados,
        "utilizacao": utilizacao,
        "plano_sinais": plano_sinais,
        "plano_resultados": plano_resultados,
        "atualizacoes_database": atualizacoes,
    }


def mostrar_resumo(plano):
    sinais = plano["plano_sinais"]

    print("\n========== SIMULACAO COMPLETA V5 ==========")
    print("Sinais automaticos roteados:", len(plano["resultados"]))
    print("Sinais manuais preservados:", len(sinais["manuais"]))
    print("Linhas ignoradas:", len(sinais["ignorados"]))
    print(
        "Celulas H/I/L/M/N a atualizar:",
        len(plano["atualizacoes_database"])
    )

    for item in plano["atualizacoes_database"][:30]:
        print(
            f"  {item['coluna']}{item['linha_planilha']} "
            f"= {item['valor']}"
        )

    if len(plano["atualizacoes_database"]) > 30:
        print("  ... demais alteracoes omitidas")

    print("Nenhuma escrita realizada na simulacao.")
    print("=========================================\n")

def converter_numero(valor):
    """Converte numeros do Python e do formato brasileiro."""
    texto = str(valor).strip().replace(" ", "")

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    try:
        return Decimal(texto)
    except InvalidOperation:
        raise ValueError(f"Numero invalido: {valor!r}")


def executar(*, aplicar=False):
    """Le dados reais, calcula e simula. Escrita somente apos confirmacao."""

    configurar_ipv4()

    registros = ler_database()
    componentes_nos = ler_componentes_nos()

    configuracoes_brutas, dados_grafo = ler_planilha()

    processar_sinais, construir_grafo, Configuracoes = (
        carregar_roteador_v4()
    )

    grafo = construir_grafo(dados_grafo)

    from validacao import (
        validar_nos,
        validar_pesos,
        validar_simetria
    )

    erros = (
        validar_nos(grafo)
        + validar_pesos(grafo)
        + validar_simetria(grafo)
    )

    if erros:
        raise ValueError(
            "Grafo invalido: "
            + "; ".join(str(erro) for erro in erros)
        )

    plano = preparar_integracao(
        registros,
        componentes_nos,
        grafo,
        Configuracoes(configuracoes_brutas),
        processar_sinais
    )

    mostrar_resumo(plano)

    if not aplicar:
        return plano

    if not plano["atualizacoes_database"]:
        print("Nenhuma alteracao necessaria.")
        return plano

    # Confere se os dados utilizados para calcular
    # as rotas continuam iguais.
    if ler_database() != registros:
        raise ValueError(
            "Database mudou durante a simulacao. "
            "Escrita cancelada."
        )

    if ler_componentes_nos() != componentes_nos:
        raise ValueError(
            "Cadastro de componentes mudou. "
            "Escrita cancelada."
        )

    if ler_planilha() != (configuracoes_brutas, dados_grafo):
        raise ValueError(
            "Configuracoes ou grafo mudaram. "
            "Escrita cancelada."
        )

    print(
        "\nATENCAO: serao atualizadas "
        f"{len(plano['atualizacoes_database'])} celulas "
        "nas colunas H/I/L/M/N da Database."
    )

    if input("Digite APLICAR para confirmar: ").strip() != "APLICAR":
        print("Operacao cancelada.")
        return plano

    # Reconfere imediatamente antes do backup e da escrita.
    if (
        ler_database() != registros
        or ler_componentes_nos() != componentes_nos
        or ler_planilha() != (configuracoes_brutas, dados_grafo)
    ):
        raise ValueError(
            "Dados de origem mudaram antes da escrita. "
            "Operacao cancelada."
        )

    # Backup obrigatorio antes de modificar a Database.
    criar_backup_database()

    atualizar_celulas_database(
        plano["atualizacoes_database"],
        confirmar_escrita=True
    )

    # Confere os valores efetivamente gravados.
    registros_depois = ler_database()
    por_linha = {
        registro["linha_planilha"]: registro
        for registro in registros_depois
    }

    indices = {"H": 7, "I": 8, "L": 11, "M": 12, "N": 13}
    divergencias = []

    for item in plano["atualizacoes_database"]:
        linha = item["linha_planilha"]
        coluna = item["coluna"]
        esperado = str(item["valor"]).strip()

        registro = por_linha.get(linha)
        if registro is None:
            divergencias.append(f"{coluna}{linha}: linha ausente")
            continue

        encontrado = str(
            registro["valores"][indices[coluna]]
        ).strip()

        if coluna == "N":
            try:
                iguais = (
                    converter_numero(encontrado)
                    == converter_numero(esperado)
                )
            except ValueError:
                iguais = False
        else:
            iguais = encontrado == esperado

        if not iguais:
            divergencias.append(
                f"{coluna}{linha}: esperado {esperado!r}, "
                f"encontrado {encontrado!r}"
            )

    if divergencias:
        raise RuntimeError(
            "Escrita enviada, mas a verificacao encontrou "
            f"{len(divergencias)} divergencias:\n"
            + "\n".join(divergencias[:20])
        )

    print(
        "\nSUCESSO: todas as celulas atualizadas "
        "foram conferidas no Google Sheets."
    )

    return plano


def main():
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--aplicar",
        action="store_true",
        help="Habilita escrita apos confirmacao digitada."
    )

    args = parser.parse_args()
    executar(aplicar=args.aplicar)


if __name__ == "__main__":
    main()