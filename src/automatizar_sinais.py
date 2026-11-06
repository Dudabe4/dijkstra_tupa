"""V5 - Prepara Sinais-Dijkstra a partir da Database.

Nao altera o Dijkstra nem os modulos existentes. Por padrao, apenas simula.
Uso (na raiz do projeto):
    python -m src.automatizar_sinais
    python -m src.automatizar_sinais --aplicar

ATENCAO: --aplicar substitui A:D de Sinais-Dijkstra e atualiza H/I/M
na Database. Antes de usar, revise a simulacao e faca backup da planilha.
"""

import argparse
import re
import unicodedata
from collections import Counter

from src.google_sheets_nodes import ler_componentes_nos
from src.google_sheets_sinais import (
    atualizar_celulas_database,
    escrever_sinais_automatizados,
    ler_database,
)


CABECALHO_SINAIS = ["Sinal", "Origem", "Intermediário", "Destino"]

# Equivalencias confirmadas pela equipe. Nao modificam a planilha de cadastro.
ALIASES_COMPONENTES = {
    "APPS[1]": "APPS1",
    "APPS[2]": "APPS2",
    "INV L": "INV L1",
    "INV R": "INV R1",
}


def sinal_exige_roteamento_manual(tag):
    """CAN e SHUT sao sempre manuais, mesmo com origem/destino validos."""
    nome_sinal = str(tag or "").strip().split("_", 1)[0].upper()
    return "CAN" in nome_sinal or "SHUT" in nome_sinal


def normalizar_componente(texto):
    """Uniformiza espacos e caixa, inclusive 'ICU [B]' -> 'ICU[B]'."""
    texto = unicodedata.normalize("NFKC", str(texto or ""))
    texto = re.sub(r"\s+", " ", texto).strip().upper()
    return re.sub(r"\s+\[", "[", texto)


def preparar_cadastro(componentes_nos):
    """Indexa componentes; rejeita conflitos criados pela normalizacao."""
    indice = {}

    for componente, no in componentes_nos.items():
        chave = normalizar_componente(componente)

        if not chave:
            raise ValueError(
                "Existe um componente sem identificador no cadastro."
            )

        no = str(no).strip().upper()

        if chave in indice and indice[chave] != no:
            raise ValueError(
                f"Componente {chave!r} associado a nos diferentes: "
                f"{indice[chave]!r} e {no!r}."
            )

        indice[chave] = no

    for alias, componente in ALIASES_COMPONENTES.items():
        chave_alias = normalizar_componente(alias)
        chave_componente = normalizar_componente(componente)

        if chave_componente not in indice:
            raise ValueError(
                f"Alias {alias!r}: componente de referencia "
                f"{componente!r} nao encontrado no cadastro de nos."
            )

        no = indice[chave_componente]

        if chave_alias in indice and indice[chave_alias] != no:
            raise ValueError(
                f"Alias {alias!r} conflita com o cadastro de nos existente."
            )

        indice[chave_alias] = no

    return indice


def interpretar_tag(tag, indice_componentes):
    """Retorna (no_origem, no_destino, erro).

    Regras:
    - CAN/SHUT sao manuais (verificacao de seguranca).
    - Tags completas usam origem e destino normalmente.
    - CHASSI utiliza o no do outro componente.
    - Tags com apenas um componente identificado utilizam
      o mesmo no como origem e destino.
    - Componentes desconhecidos continuam manuais.
    """

    tag = str(tag or "").strip()

    # CAN e SHUT sempre devem ser manuais.
    if sinal_exige_roteamento_manual(tag):
        return None, None, (
            "sinal CAN/SHUT: roteamento manual obrigatorio"
        )

    partes = [parte.strip() for parte in tag.split("_")]

    # A tag deve conter o nome do sinal e o campo de origem.
    if len(partes) < 2 or not partes[0] or not partes[1]:
        return None, None, "tag sem sinal ou componente de origem"

    # Permite campos vazios adicionais no final:
    # SINAL_COMPONENTE_ e SINAL_COMPONENTE__
    if len(partes) > 3 and any(partes[3:]):
        return None, None, "tag fora do padrao SINAL_ORIGEM_DESTINO"

    origem = partes[1]
    destino = partes[2] if len(partes) >= 3 else ""

    origem_normalizada = normalizar_componente(origem)
    destino_normalizado = normalizar_componente(destino)

    # CHASSI em ambas as extremidades nao define um no.
    if origem_normalizada == "CHASSI" and destino_normalizado == "CHASSI":
        return None, None, "CHASSI nas duas extremidades; no indefinido"

    # Quando CHASSI aparece como origem, utiliza o no do destino.
    if origem_normalizada == "CHASSI":
        no = indice_componentes.get(destino_normalizado)

        if no is None:
            return None, None, (
                f"componente sem no cadastrado: {destino}"
            )

        return no, no, None

    # Verifica se o componente de origem existe.
    no_origem = indice_componentes.get(origem_normalizada)

    if no_origem is None:
        return None, None, (
            f"componente sem no cadastrado: {origem}"
        )

    # CHASSI ou destino vazio: origem e destino sao iguais.
    if not destino_normalizado or destino_normalizado == "CHASSI":
        return no_origem, no_origem, None

    # Caso normal: dois componentes definidos.
    no_destino = indice_componentes.get(destino_normalizado)

    if no_destino is None:
        return None, None, (
            f"componente sem no cadastrado: {destino}"
        )

    return no_origem, no_destino, None


def preparar_automatizacao(registros, componentes_nos):
    """Monta um plano de escrita sem fazer chamadas de rede.

    Para tags invalidas, atualiza somente M='manual', preservando L/N.
    Para tags validas, atualiza H/I; nao altera L/M/N porque o
    roteamento ainda nao foi executado. A escrita de L/M/N e tarefa
    do futuro modulo atualizar_database.py.

    Retorna: linhas_sinais, atualizacoes_database, automaticos, manuais,
    ignorados. 'automaticos' preserva a linha original para a proxima etapa.
    """
    indice = preparar_cadastro(componentes_nos)

    linhas_sinais = [CABECALHO_SINAIS.copy()]
    atualizacoes = []
    automaticos = []
    manuais = []
    ignorados = []

    for registro in registros:
        linha = registro["linha_planilha"]
        tag = str(registro.get("tag_via", "") or "").strip()

        valores = list(registro.get("valores", []))
        valores += [""] * max(0, 14 - len(valores))

        # Linhas sem tag nao sao sinais; nao sobrescrever informacoes.
        if not tag or tag == "---":
            ignorados.append({
                "linha_planilha": linha,
                "tag_via": tag
            })
            continue

        if tag.casefold() == "tag da via":
            continue

        if sinal_exige_roteamento_manual(tag):
            origem, destino, erro = (
                None,
                None,
                "sinal CAN/SHUT: roteamento manual obrigatorio"
            )
        else:
            origem, destino, erro = interpretar_tag(tag, indice)

        if erro:
            manuais.append({
                "linha_planilha": linha,
                "tag_via": tag,
                "motivo": erro
            })

            if str(valores[12]).strip().casefold() != "manual":
                atualizacoes.append({
                    "linha_planilha": linha,
                    "coluna": "M",
                    "valor": "manual"
                })

            continue

        # O sinal e identificado pela tag completa para nao perder o
        # vinculo com o identificador eletrico existente na Database.
        linhas_sinais.append([
            tag,
            origem,
            "-",
            destino
        ])

        automaticos.append({
            "linha_planilha": linha,
            "tag_via": tag,
            "origem": origem,
            "destino": destino,
            "linha_sinais": len(linhas_sinais),
        })

        if str(valores[7]).strip().upper() != origem:
            atualizacoes.append({
                "linha_planilha": linha,
                "coluna": "H",
                "valor": origem
            })

        if str(valores[8]).strip().upper() != destino:
            atualizacoes.append({
                "linha_planilha": linha,
                "coluna": "I",
                "valor": destino
            })

        # Nao limpar 'manual' anterior sem ter um resultado de roteamento.

    return {
        "linhas_sinais": linhas_sinais,
        "atualizacoes_database": atualizacoes,
        "automaticos": automaticos,
        "manuais": manuais,
        "ignorados": ignorados,
    }


def mostrar_resumo(plano):
    print("\n========== SIMULACAO DA AUTOMATIZACAO ==========")

    print(f"Sinais validos preparados: {len(plano['automaticos'])}")
    print(f"Sinais para tratamento manual: {len(plano['manuais'])}")
    print(f"Linhas sem tag ignoradas: {len(plano['ignorados'])}")
    print(
        f"Celulas H/I/M a atualizar: "
        f"{len(plano['atualizacoes_database'])}"
    )

    repetidas = {
        tag: n
        for tag, n in Counter(
            item["tag_via"] for item in plano["automaticos"]
        ).items()
        if n > 1
    }

    if repetidas:
        print(
            f"ATENCAO: {len(repetidas)} tag(s) repetida(s) "
            "entre os sinais validos."
        )

        for tag, quantidade in repetidas.items():
            print(f"  {tag}: {quantidade} ocorrencias")

    print("\nExemplos de sinais validos:")

    for item in plano["automaticos"][:8]:
        print(
            f"  Database {item['linha_planilha']}: "
            f"{item['tag_via']} -> "
            f"{item['origem']} / {item['destino']}"
        )

    print("\nSinais classificados como manuais:")

    for item in plano["manuais"]:
        print(
            f"  Database {item['linha_planilha']}: "
            f"{item['tag_via']} | {item['motivo']}"
        )

    print("\nNenhuma celula foi alterada nesta simulacao.")
    print("===============================================\n")


def executar(*, aplicar=False):
    """Le dados reais; simula por padrao. --aplicar exige confirmacao."""
    registros = ler_database()
    componentes_nos = ler_componentes_nos()

    plano = preparar_automatizacao(registros, componentes_nos)
    mostrar_resumo(plano)

    if not aplicar:
        return plano

    if not plano["automaticos"]:
        raise ValueError(
            "Nenhum sinal valido: escrita cancelada."
        )

    print(
        "ATENCAO: sera substituido o intervalo A:D "
        "de Sinais-Dijkstra."
    )
    print(
        "Na Database, apenas as celulas H/I/M listadas "
        "serao alteradas."
    )
    print(
        "Os caminhos e distancias existentes (L/N) "
        "serao preservados."
    )

    resposta = input(
        "Digite APLICAR para confirmar: "
    ).strip()

    if resposta != "APLICAR":
        print("Operacao cancelada. Nenhuma escrita solicitada.")
        return plano

    # Escreve primeiro os sinais. Se falhar, nao atualiza a Database.
    # ATENCAO: as duas chamadas nao sao uma transacao atomica.
    escrever_sinais_automatizados(
        plano["linhas_sinais"],
        confirmar_substituicao=True
    )

    atualizar_celulas_database(
        plano["atualizacoes_database"],
        confirmar_escrita=True
    )

    print(
        "Sinais-Dijkstra e atualizacoes H/I/M "
        "enviados ao Google Sheets."
    )

    return plano


def main():
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--aplicar",
        action="store_true",
        help="Permite escrita somente apos confirmacao digitada."
    )

    args = parser.parse_args()
    executar(aplicar=args.aplicar)


if __name__ == "__main__":
    main()