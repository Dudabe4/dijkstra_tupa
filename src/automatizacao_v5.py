import argparse
import sys
from dataclasses import dataclass
from typing import Any

from src.integracao_v5 import executar, configurar_ipv4
from src.google_sheets_sinais import (
    SPREADSHEET_ID,
    ABA_RESULTADOS,
    conectar_google_sheets,
    ler_database,
    criar_backup_database,
    atualizar_celulas_database,
    escrever_sinais_automatizados,
)
from src.google_sheets_nodes import ler_componentes_nos, ler_planilha
from src.sincronizar_sinais_v5 import (
    ler_linhas_aba,
    normalizar_linhas,
    criar_backup_aba,
)
from src.sincronizar_resultados_v5 import (
    gerar_linhas_resultados,
    ler_resultados,
    linhas_iguais,
    criar_backup as criar_backup_resultados,
)
from src.integracao_v5 import converter_numero


@dataclass
class Estado:
    plano: dict[str, Any]
    sinais_novos: list
    resultados_novos: list
    sinais_atuais: list
    resultados_atuais: list
    database_atual: list
    componentes_atuais: Any
    grafo_atual: Any
    precisa_sinais: bool
    precisa_resultados: bool
    precisa_database: bool


def _ler_estado(servico):
    """Calcula uma vez e captura os dados usados na validacao."""
    plano = executar(aplicar=False)
    sinais_novos = plano['plano_sinais']['linhas_sinais']
    resultados_novos = gerar_linhas_resultados(plano)

    if len(sinais_novos) != len(resultados_novos):
        raise ValueError('Quantidade de sinais e resultados diferente.')
    if len(sinais_novos) < 2:
        raise ValueError('Nenhum sinal automatico encontrado; escrita bloqueada.')
    if len(plano['resultados']) != len(sinais_novos) - 1:
        raise ValueError('Quantidade de resultados V5 inconsistente.')

    sinais_atuais = ler_linhas_aba(servico)
    resultados_atuais = ler_resultados(servico)
    database_atual = ler_database()
    componentes_atuais = ler_componentes_nos()
    grafo_atual = ler_planilha()

    return Estado(
        plano=plano,
        sinais_novos=sinais_novos,
        resultados_novos=resultados_novos,
        sinais_atuais=sinais_atuais,
        resultados_atuais=resultados_atuais,
        database_atual=database_atual,
        componentes_atuais=componentes_atuais,
        grafo_atual=grafo_atual,
        precisa_sinais=(normalizar_linhas(sinais_atuais)
                        != normalizar_linhas(sinais_novos)),
        precisa_resultados=not linhas_iguais(resultados_atuais, resultados_novos),
        precisa_database=bool(plano['atualizacoes_database']),
    )


def _resumo(estado):
    print('\n========== AUTOMATIZACAO COMPLETA V5 ==========')
    print('Sinais automaticos:', len(estado.sinais_novos) - 1)
    print('Sinais manuais preservados:',
          len(estado.plano['plano_sinais']['manuais']))
    print('Linhas ignoradas:',
          len(estado.plano['plano_sinais']['ignorados']))
    print('Database: ', len(estado.plano['atualizacoes_database']),
          'celulas pendentes')
    print('Sinais-Dijkstra:', 'ATUALIZAR' if estado.precisa_sinais else 'SINCRONIZADA')
    print('Resultados-Dijkstra:',
          'ATUALIZAR' if estado.precisa_resultados else 'SINCRONIZADA')
    print('Linhas de sinais atuais/novas:',
          max(0, len(estado.sinais_atuais) - 1), '/', len(estado.sinais_novos) - 1)
    print('Linhas de resultados atuais/novas:',
          max(0, len(estado.resultados_atuais) - 1), '/', len(estado.resultados_novos) - 1)
    print('================================================\n')


def _mesmos_dados_entrada(estado):
    return (ler_database() == estado.database_atual
            and ler_componentes_nos() == estado.componentes_atuais
            and ler_planilha() == estado.grafo_atual)


def _mesmas_abas(estado, servico):
    return (ler_linhas_aba(servico) == estado.sinais_atuais
            and ler_resultados(servico) == estado.resultados_atuais)


def _revalidar(estado, servico):
    """Revalida entradas e rotas antes de qualquer backup/escrita."""
    if not _mesmos_dados_entrada(estado):
        raise RuntimeError('Dados de origem mudaram. Nenhuma escrita iniciada.')
    if not _mesmas_abas(estado, servico):
        raise RuntimeError('Uma aba de destino mudou. Nenhuma escrita iniciada.')

    plano_novo = executar(aplicar=False)
    if plano_novo['atualizacoes_database'] != estado.plano['atualizacoes_database']:
        raise RuntimeError('Plano da Database mudou. Nenhuma escrita iniciada.')
    if normalizar_linhas(plano_novo['plano_sinais']['linhas_sinais']) != normalizar_linhas(estado.sinais_novos):
        raise RuntimeError('Sinais calculados mudaram. Nenhuma escrita iniciada.')
    if not linhas_iguais(gerar_linhas_resultados(plano_novo), estado.resultados_novos):
        raise RuntimeError('Resultados calculados mudaram. Nenhuma escrita iniciada.')
    if not _mesmos_dados_entrada(estado) or not _mesmas_abas(estado, servico):
        raise RuntimeError('Dados mudaram durante a revalidacao. Escrita cancelada.')


def _conferir_database(atualizacoes):
    """Compara H/I/L/M/N; N pode ser formatada na localidade brasileira."""
    registros = ler_database()
    por_linha = {r['linha_planilha']: r for r in registros}
    indices = {'H': 7, 'I': 8, 'L': 11, 'M': 12, 'N': 13}
    divergencias = []
    for item in atualizacoes:
        linha = item['linha_planilha']
        coluna = item['coluna']
        registro = por_linha.get(linha)
        if registro is None:
            divergencias.append(f'{coluna}{linha}: linha ausente')
            continue
        valores = list(registro.get('valores', []))
        valor = valores[indices[coluna]] if len(valores) > indices[coluna] else ''
        esperado = item['valor']
        if coluna == 'N':
            try:
                igual = converter_numero(valor).quantize(__import__('decimal').Decimal('0.01')) == converter_numero(esperado).quantize(__import__('decimal').Decimal('0.01'))
            except (ValueError, __import__('decimal').InvalidOperation):
                igual = False
        else:
            igual = str(valor).strip() == str(esperado).strip()
        if not igual:
            divergencias.append(f'{coluna}{linha}: {valor!r} != {esperado!r}')
    if divergencias:
        raise RuntimeError('Database gravada, mas verificacao falhou: '
                           + '; '.join(divergencias[:10]))


def _gravar_resultados(servico, linhas):
    """Escreve apenas A:I, como no modulo de sincronizacao validado."""
    servico.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{ABA_RESULTADOS}'!A:I",
    ).execute()
    servico.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{ABA_RESULTADOS}'!A1",
        valueInputOption='RAW',
        body={'values': linhas},
    ).execute()
    if not linhas_iguais(ler_resultados(servico), linhas):
        raise RuntimeError('Resultados gravados, mas a conferencia falhou.')


def automatizar(*, aplicar=False):
    configurar_ipv4()
    servico = conectar_google_sheets()
    estado = _ler_estado(servico)
    _resumo(estado)

    tarefas = []
    if estado.precisa_sinais:
        tarefas.append('Sinais-Dijkstra (A:D)')
    if estado.precisa_resultados:
        tarefas.append('Resultados-Dijkstra (A:I)')
    if estado.precisa_database:
        tarefas.append('Database (H/I/L/M/N)')

    if not tarefas:
        print('SUCESSO: as tres abas ja estao sincronizadas. Nenhuma escrita necessaria.')
        return estado.plano
    if not aplicar:
        print('SIMULACAO: nenhuma escrita realizada.')
        print('Para atualizar, execute: python -m src.automatizacao_v5 --aplicar')
        return estado.plano

    print('ATENCAO: as seguintes abas/colunas serao modificadas:')
    for tarefa in tarefas:
        print(' -', tarefa)
    print('Sinais e Resultados sao substituidos nas faixas indicadas.')
    print('Backups serao criados ANTES da primeira escrita.')
    print('A API nao garante transacao atomica entre abas.')
    if input('Digite APLICAR V5 para confirmar: ').strip() != 'APLICAR V5':
        print('Operacao cancelada. Nenhuma escrita realizada.')
        return estado.plano

    _revalidar(estado, servico)

    # Todos os backups sao feitos antes de modificar qualquer aba.
    print('\nCriando backups obrigatorios...')
    if estado.precisa_sinais:
        criar_backup_aba(servico)
    if estado.precisa_resultados:
        criar_backup_resultados(servico)
    if estado.precisa_database:
        criar_backup_database()
    print('Backups concluidos. Iniciando escrita...')

    concluidas = []
    try:
        # Cada escrita e seguida de leitura e verificacao.
        if estado.precisa_sinais:
            if ler_linhas_aba(servico) != estado.sinais_atuais:
                raise RuntimeError('Sinais-Dijkstra mudou antes da escrita.')
            escrever_sinais_automatizados(
                estado.sinais_novos, confirmar_substituicao=True)
            if normalizar_linhas(ler_linhas_aba(servico)) != normalizar_linhas(estado.sinais_novos):
                raise RuntimeError('Sinais gravados, mas a conferencia falhou.')
            concluidas.append('Sinais-Dijkstra')
            print('OK: Sinais-Dijkstra conferida.')

        if estado.precisa_resultados:
            if ler_resultados(servico) != estado.resultados_atuais:
                raise RuntimeError('Resultados-Dijkstra mudou antes da escrita.')
            _gravar_resultados(servico, estado.resultados_novos)
            concluidas.append('Resultados-Dijkstra')
            print('OK: Resultados-Dijkstra conferida.')

        if estado.precisa_database:
            if not _mesmos_dados_entrada(estado):
                raise RuntimeError('Origem da Database mudou antes da escrita.')
            atualizar_celulas_database(
                estado.plano['atualizacoes_database'], confirmar_escrita=True)
            _conferir_database(estado.plano['atualizacoes_database'])
            concluidas.append('Database')
            print('OK: Database conferida.')
    except Exception:
        print('\nERRO: processo interrompido. Nao execute --aplicar novamente sem conferir as abas e os backups.', file=sys.stderr)
        print('Etapas confirmadas:', ', '.join(concluidas) or 'nenhuma', file=sys.stderr)
        print('A etapa que falhou PODE ter sido parcialmente gravada.', file=sys.stderr)
        raise

    print('\nSUCESSO: todas as atualizacoes necessarias foram conferidas.')
    print('Execute sem --aplicar para uma verificacao final.')
    return estado.plano


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aplicar', action='store_true',
                        help='Habilita escrita apos validacoes, backups e confirmacao.')
    args = parser.parse_args()
    try:
        automatizar(aplicar=args.aplicar)
    except Exception as erro:
        print(f'\nFALHA: {erro}', file=sys.stderr)
        raise SystemExit(1) from erro


if __name__ == '__main__':
    main()