#!/usr/bin/env bash
# TUPA — atualizacao completa do roteamento Dijkstra V5.
# Uso: ./executar++.sh
# Executa a automacao central, com confirmacao e backups antes de escrever.
set -Eeuo pipefail

PROJETO="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJETO"

if [[ ! -f src/automatizacao_v5.py ]]; then
  echo "ERRO: src/automatizacao_v5.py nao foi encontrado." >&2
  exit 1
fi

# Prioriza o ambiente Conda do projeto, mesmo que o terminal esteja no (base).
if [[ -x "$HOME/miniconda3/envs/ambiente_tupa/bin/python" ]]; then
  PYTHON="$HOME/miniconda3/envs/ambiente_tupa/bin/python"
elif [[ -x "$HOME/anaconda3/envs/ambiente_tupa/bin/python" ]]; then
  PYTHON="$HOME/anaconda3/envs/ambiente_tupa/bin/python"
elif [[ "${CONDA_DEFAULT_ENV:-}" == "ambiente_tupa" ]] && command -v python >/dev/null 2>&1; then
  PYTHON="$(command -v python)"
else
  echo "ERRO: ambiente_tupa nao encontrado." >&2
  echo "Ative o ambiente com 'conda activate ambiente_tupa' e tente novamente." >&2
  exit 1
fi

export PYTHONPATH="${PROJETO}${PYTHONPATH:+:${PYTHONPATH}}"

echo "==============================================="
echo "     TUPA | ATUALIZACAO COMPLETA DIJKSTRA V5"
echo "==============================================="
echo "Pasta: $PROJETO"
echo "Python: $PYTHON"
echo ""
echo "O programa ira:"
echo "  1. Ler a Database e os dados atuais do grafo."
echo "  2. Recalcular as rotas e conferir as tres abas."
echo "  3. Mostrar as mudancas e pedir 'APLICAR V5'."
echo "  4. Criar backups e atualizar apenas o necessario."
echo ""
echo "Nenhuma alteracao sera feita sem sua confirmacao."
echo ""

"$PYTHON" -m src.automatizacao_v5 --aplicar

echo ""
echo "Execucao encerrada. Conferindo o estado atual (mesmo se voce cancelou)..."
"$PYTHON" -m src.automatizacao_v5

echo ""
echo "PROCESSO ENCERRADO: confira se as tres abas aparecem sincronizadas no resumo acima."