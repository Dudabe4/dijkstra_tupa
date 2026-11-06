import math
from src.google_sheets_sinais import atualizar_celulas_database
from src.automatizar_sinais import sinal_exige_roteamento_manual

from decimal import Decimal, InvalidOperation

def converter_distancia(valor):
    """Converte numeros comuns ou formatados no padrao brasileiro."""
    texto = str(valor).strip().replace(" ", "")

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    try:
        return Decimal(texto)
    except InvalidOperation:
        raise ValueError(f"Distancia invalida: {valor!r}")


def distancias_iguais(valor_atual, valor_calculado):
    """Compara distancias em milimetros com duas casas decimais."""
    try:
        atual = converter_distancia(valor_atual)
        calculado = converter_distancia(valor_calculado)

        return (
            atual.quantize(Decimal("0.01"))
            == calculado.quantize(Decimal("0.01"))
        )
    except (ValueError, InvalidOperation):
        return False


def _normalizar_caminho(caminho):
    if isinstance(caminho, (list, tuple)):
        nos = [str(no).strip() for no in caminho]
    elif isinstance(caminho, str):
        # Somente separadores inequivocos. Nao adivinhar formatos arbitrarios.
        nos = [no.strip() for no in caminho.split(' -> ')]
    else:
        raise ValueError('Caminho deve ser lista/tupla de nos ou string com " -> ".')
    if not nos or any(not no for no in nos):
        raise ValueError('Caminho vazio ou com nos invalidos.')
    return ' -> '.join(nos)


def _distancia_mm(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError('Distancia fisica deve ser numerica, em milimetros.')
    if not math.isfinite(valor) or valor < 0:
        raise ValueError('Distancia fisica invalida.')
    return valor


def preparar_atualizacoes_database(registros, resultados):
    """Retorna plano sem escrever; falha integralmente em inconsistencias.

    Exige resultado para cada sinal automatico representado em `resultados`.
    Nao altera sinais manuais, nao apaga rotas em falhas e nao aceita
    resultados sem linha original ou com tag diferente da Database.
    """
    por_linha = {}
    for registro in registros:
        linha = registro['linha_planilha']
        if linha in por_linha:
            raise ValueError(f'Linha repetida nos registros: {linha}')
        por_linha[linha] = registro

    atualizacoes = []
    aplicados = []
    preservados = []
    linhas_vistas = set()

    for resultado in resultados:
        linha = resultado.get('linha_planilha')
        if not isinstance(linha, int) or isinstance(linha, bool) or linha < 3:
            raise ValueError(f'Linha original invalida: {linha!r}')
        if linha in linhas_vistas:
            raise ValueError(f'Dois resultados para a mesma linha: {linha}')
        linhas_vistas.add(linha)

        if linha not in por_linha:
            raise ValueError(f'Linha {linha} nao encontrada na Database.')
        registro = por_linha[linha]
        tag_atual = str(registro.get('tag_via', '') or '').strip()
        tag_resultado = str(resultado.get('tag_via', '') or '').strip()
        if not tag_atual or tag_atual != tag_resultado:
            raise ValueError(
                f'Linha {linha}: tag mudou ou nao confere '
                f'({tag_resultado!r} != {tag_atual!r}).'
            )

        valores = list(registro.get('valores', []))
        valores.extend([''] * max(0, 14 - len(valores)))

        # Nunca sobrescrever L/N de um sinal manual.
        status = str(resultado.get('status', '') or '').strip().upper()
        if sinal_exige_roteamento_manual(tag_atual) or status != 'OK':
            if str(valores[12]).strip().casefold() != 'manual':
                atualizacoes.append({
                    'linha_planilha': linha, 'coluna': 'M', 'valor': 'manual'
                })
            preservados.append({'linha_planilha': linha, 'tag_via': tag_atual,
                                'motivo': 'manual' if sinal_exige_roteamento_manual(tag_atual)
                                else f'status {status or "ausente"}'})
            continue

        caminho = _normalizar_caminho(resultado.get('caminho'))
        distancia = _distancia_mm(resultado.get('distancia_fisica'))
        nos = caminho.split(' -> ')
        if len(nos) == 1 and distancia != 0:
            raise ValueError(f'Linha {linha}: caminho de um no exige distancia 0.')
        if len(nos) > 1 and distancia == 0:
            raise ValueError(f'Linha {linha}: caminho com varios nos tem distancia 0.')

        desejados = {'L': caminho, 'M': 'OK', 'N': distancia}

        for coluna, indice in [('L', 11), ('M', 12), ('N', 13)]:
            atual = valores[indice]
            novo = desejados[coluna]

            # Distancias sao comparadas numericamente.
            # Caminho e status continuam sendo comparados como texto.
            if coluna == 'N':
                precisa_atualizar = not distancias_iguais(atual, novo)
            else:
                precisa_atualizar = str(atual).strip() != str(novo)

            if precisa_atualizar:
                atualizacoes.append({
                    'linha_planilha': linha,
                    'coluna': coluna,
                    'valor': novo
                })
        aplicados.append({'linha_planilha': linha, 'tag_via': tag_atual,
                          'caminho': caminho, 'distancia_fisica': distancia})

    return {'atualizacoes_database': atualizacoes,
            'automaticos': aplicados, 'preservados': preservados}


def mostrar_resumo(plano):
    print('\n========== SIMULACAO: RESULTADOS -> DATABASE ==========')
    print('Rotas OK conferidas:', len(plano['automaticos']))
    print('Resultados preservados:', len(plano['preservados']))
    print('Celulas L/M/N a alterar:', len(plano['atualizacoes_database']))
    for item in plano['atualizacoes_database'][:25]:
        print(f"  {item['coluna']}{item['linha_planilha']} = {item['valor']}")
    if len(plano['atualizacoes_database']) > 25:
        print('  ... demais alteracoes omitidas nesta visualizacao')
    print('Nenhuma celula alterada durante a simulacao.')
    print('=====================================================\n')


def executar_atualizacao(registros, resultados, *, aplicar=False):
    """Simula ou, com confirmacao, atualiza exclusivamente L/M/N."""
    plano = preparar_atualizacoes_database(registros, resultados)
    mostrar_resumo(plano)
    if not aplicar:
        return plano
    if not plano['atualizacoes_database']:
        print('Nenhuma alteracao necessaria.')
        return plano
    resposta = input('Digite APLICAR para escrever na Database: ').strip()
    if resposta != 'APLICAR':
        print('Operacao cancelada.')
        return plano
    atualizar_celulas_database(
        plano['atualizacoes_database'], confirmar_escrita=True
    )
    print('Atualizacoes enviadas ao Google Sheets.')
    return plano