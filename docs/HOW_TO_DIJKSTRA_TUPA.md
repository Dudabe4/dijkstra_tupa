# How To — Dijkstra TUPÃ

*Guia de instalação, execução e manutenção para as próximas equipes.*

Objetivo: configurar o acesso ao Mapa de Sinais, executar o algoritmo e conferir os resultados, sem precisar conhecer previamente o código.

## 1. Obter o projeto

Abra a aba “INSTRUÇÕES DE USO” do Mapa de Sinais do T11, onde está indicado o repositório dijkstra_tupa. No terminal, clone o projeto (o endereço SSH requer uma chave SSH configurada no GitHub):

```bash
git clone git@github.com:Dudabe4/dijkstra_tupa.git
cd dijkstra_tupa  # ou entre na pasta criada pelo clone; confira com ls
```

Alternativa HTTPS: https://github.com/Dudabe4/dijkstra_tupa (use o botão Code → HTTPS).

## 2. Preparar Python e bibliotecas

Instale Git, Python e Conda (Miniconda ou Anaconda). Ative o ambiente usado pela equipe:

```bash
conda activate ambiente_tupa
```

Se o ambiente não existir, crie-o e instale as bibliotecas utilizadas no projeto:

```bash
conda create -n ambiente_tupa python=3.12 -y
conda activate ambiente_tupa
pip install google-api-python-client google-auth google-auth-httplib2
```

Outras dependências podem ser necessárias conforme a versão do repositório. Consulte o README e os imports antes da primeira execução.

## 3. Configurar a Google Sheets API

No Google Cloud Console: crie ou selecione um projeto; habilite a Google Sheets API; crie uma conta de serviço (Service Account) e gere uma chave JSON. Guarde a chave localmente com o nome e caminho esperados pelo código:

`credentials/credentials.json`

Abra o JSON e copie o valor de client_email. No Google Sheets do Mapa de Sinais, clique em Compartilhar e adicione esse e-mail como Editor. Sem esse compartilhamento, o programa não conseguirá ler ou atualizar a planilha.

Confira também o `SPREADSHEET_ID` em src/google_sheets_sinais.py e src/google_sheets_nodes.py: ele deve apontar para a planilha da equipe que será utilizada. Nunca publique o JSON de credenciais nem o inclua em commits.

## 4. Conferir o Mapa de Sinais

Na Database, preencha/atualize sinais e componentes mantendo o padrão das tags e colunas. Em Nós-Dijkstra, confira a associação dos componentes aos nós, conexões, distâncias e parâmetros. Não altere nomes de abas ou cabeçalhos sem adaptar o código.

Sinais CAN e SHUT exigem definição manual de caminhos e distâncias; a instrução da planilha recomenda utilizar ./executar.sh para essa operação.

## 5. Executar com segurança

Na pasta principal do projeto, faça primeiro uma simulação sem escrita:

```bash
python -m src.automatizacao_v5
```

Para atualizar os resultados após mudanças na Database, execute:

```bash
chmod +x executar.sh executar++.sh
./executar++.sh
```

Leia o resumo das alterações. Se estiver correto, digite APLICAR V5. O programa cria backups das abas afetadas, grava as mudanças e executa uma nova conferência. Para consultas e roteamento manual, use ./executar.sh.

### 6. Conferir o resultado

Verifique Database, Sinais-Dijkstra e Resultados-Dijkstra. O terminal deve indicar as abas sincronizadas e zero células pendentes após uma atualização bem-sucedida. Revise caminhos fisicamente, sobretudo quando houver penalizações, sinais manuais ou rotas não resolvidas.

## 7. Se algo não funcionar

Erro de credenciais: confira credentials/credentials.json. Erro 403: confira API habilitada e compartilhamento com client_email. Erro de ambiente: ative ambiente_tupa e instale dependências. Aba não encontrada: confira nomes e ID da planilha. Antes de repetir uma escrita interrompida, confira backups e estado das abas.

## Para o próximo carro

Atualize nós, distâncias, componentes, restrições e ID da nova planilha; não reutilize rotas antigas sem validação física. Registre a versão do código e guarde uma cópia dos resultados para rastreabilidade.

Base deste guia: aba “INSTRUÇÕES DE USO” do Mapa de Sinais T11, README e código-fonte do ZIP dijkstra(3). A configuração da conta de serviço foi detalhada como orientação operacional.

## 8. O que o código faz (e como funciona)

O programa transforma o mapa elétrico em caminhos para os fios. Ele lê os sinais da Database, identifica os nós de origem e destino de cada componente e monta uma rede de nós e conexões com suas distâncias. Em seguida, calcula uma rota para cada sinal automático usando Dijkstra. O cálculo considera o comprimento, a preferência por caminhos principais, a utilização acumulada dos nós e as penalizações configuradas. Assim, a rota escolhida nem sempre é a menor distância física: é a de menor custo calculado para aquele momento.

Depois do roteamento, o programa calcula separadamente a distância física de cada caminho, prepara os resultados e compara tudo com o que já está na planilha. Se não houver diferenças, não escreve nada. Se houver, apresenta uma prévia, pede confirmação, cria backups das abas afetadas, atualiza somente os campos previstos e lê novamente para conferir. CAN e SHUT são tratados manualmente conforme as regras da equipe.

## 9. Quais abas e colunas são alteradas?

| Aba                                    | O que a V5 modifica          | Observação                                                                                                     |
|----------------------------------------|------------------------------|----------------------------------------------------------------------------------------------------------------|
| Database                               | H, I, L, M e N               | Atualiza os campos calculados de nós, caminho e distâncias conforme o plano; não substitui a Database inteira. |
| Sinais-Dijkstra                        | A:D                          | Reescreve a faixa de sinais automáticos gerada pelo fluxo V5.                                                  |
| Resultados-Dijkstra                    | A:I                          | Reescreve a faixa de resultados calculados.                                                                    |
| Nós-Dijkstra e cadastro de componentes | Somente leitura              | Fornecem o grafo, distâncias, parâmetros e associação entre componentes e nós.                                 |


## 10. Guia rápido dos arquivos da pasta

- **executar.sh —** Abre a versão interativa/tradicional (V4), útil para consultas manuais.

- **executar++.sh —** Inicia a sincronização integrada V5, com confirmação e conferência final.

- **src/dijkstra.py —** Busca caminhos e calcula o custo e a distância física.

- **src/construir_grafo.py e src/configs/ —** Montam a rede e aplicam parâmetros do roteamento.

- **src/roteamento_sinais.py e src/automatizar_sinais.py —** Organizam o processamento dos sinais e as regras automáticas/manuais.

- **src/integracao_v5.py e src/automatizacao_v5.py —** Conectam o cálculo à planilha e coordenam a simulação, os backups e a atualização.

- **src/google_sheets\_\.py —** Fazem a leitura e a comunicação com o Google Sheets.

- **relatorios/ —** Guarda arquivos de auditoria e prévias, quando gerados.

## 11. Antes de entregar para a próxima equipe

Confirme que o repositório contém a versão mais recente dos arquivos-fonte, especialmente os módulos opcionais da Fase 1; que o README e o How To estão atualizados; que as credenciais não foram enviadas ao GitHub; e que o ID da planilha, os nós, as distâncias, as penalizações e os sinais correspondem ao carro novo. Faça primeiro uma simulação e só autorize a escrita depois de conferir o resumo.

## 12. Primeira execução — roteiro completo

Este roteiro deve ser seguido por quem está configurando o projeto pela primeira vez. Execute os comandos no terminal, um por vez. Não é necessário alterar o código para fazer uma simulação.

### 1. Baixar e localizar a pasta

Abra o link do GitHub indicado na aba INSTRUÇÕES DE USO do mapa T11. No terminal, use o endereço HTTPS do repositório e entre na pasta clonada. O nome da pasta pode variar; use ls para confirmar.

```bash
git clone https://github.com/Dudabe4/dijkstra_tupa.git
```bash
ls
cd dijkstra_tupa  # ajuste se a pasta tiver outro nome
```
```

### 2. Ativar o ambiente

Confirme que Python está disponível no ambiente e que as bibliotecas necessárias foram instaladas. Se houver instruções mais recentes no README, dê preferência a elas.

```bash
conda activate ambiente_tupa
python --version
python -c "import googleapiclient, google.auth; print('Bibliotecas OK')"
```

### 3. Conferir o acesso à planilha

No Google Cloud, habilite a Google Sheets API e crie uma conta de serviço com chave JSON. Coloque a chave em credentials/credentials.json. Compartilhe a planilha com o client_email dessa conta como Editor. Confira também o `SPREADSHEET_ID` dos módulos de integração.

```bash
ls credentials/credentials.json
 # NUNCA imprima ou compartilhe o conteúdo da chave JSON
```

### 4. Conferir os dados de entrada

Abra a Database e Nós-Dijkstra. Confira se as tags e associações de componentes estão preenchidas, se as conexões existem e se as distâncias estão na unidade esperada. Para o próximo carro, atualize o grafo antes de confiar nas rotas.

### 5. Executar somente a simulação

Esta é a primeira execução recomendada. Ela mostra o que mudaria sem atualizar a planilha.

```bash
python -m src.automatizacao_v5
```

### 6. Aplicar somente após revisão

Se o resumo estiver coerente e o mapa correto estiver selecionado, execute o script integrado. Digite APLICAR V5 apenas depois de conferir as alterações. O script cria backups das abas afetadas.

```bash
chmod +x executar.sh executar++.sh
./executar++.sh
```

### 7. Conferir o resultado

Uma execução concluída deve mostrar as abas sincronizadas e zero células pendentes. Em caso de falha, confira as abas e os backups antes de repetir --aplicar.

```bash
python -m src.automatizacao_v5
```

## 13. Como saber se deu certo?

Exemplo real de saída após a sincronização do T11 (os números mudam a cada carro):

Sinais automaticos: 201  
Sinais manuais preservados: 54  
Database: 0 celulas pendentes  
Sinais-Dijkstra: SINCRONIZADA  
Resultados-Dijkstra: SINCRONIZADA  
SUCESSO: as tres abas ja estao sincronizadas.

Atenção: “sincronizada” significa que os dados calculados coincidem com os dados gravados. Não substitui a verificação de montagem, restrições elétricas ou medidas físicas.

## 14. Problemas comuns e solução rápida

| Sintoma                         | O que conferir                                                                              |
|---------------------------------|---------------------------------------------------------------------------------------------|
| 403 / Permission denied         | Compartilhamento da planilha com client_email; Google Sheets API habilitada; conta correta. |
| credentials.json não encontrado | Localização da chave em credentials/credentials.json; nome e caminho esperados pelo código. |
| ModuleNotFoundError             | Ativação de ambiente_tupa e instalação das dependências indicadas no README.                |
| Aba não encontrada              | Nome exato da aba e `SPREADSHEET_ID`; evite renomear abas usadas pelo código.                 |
| Permissão negada no .sh         | Execute chmod +x executar.sh executar++.sh, ou use bash executar++.sh.                      |
| Rotas ausentes / Verificar Par  | Confira tags, nós associados, conectividade do grafo e tratamento de sinais manuais.        |
| Falha após iniciar escrita      | Não repita a aplicação às cegas; confira backups, abas alteradas e estado atual.            |

## 15. Checklist para migrar para o próximo carro

- Criar cópia do Mapa de Sinais e registrar seu ID; não editar o mapa anterior por engano.

- Atualizar a Database com os sinais do novo carro e revisar tags, origens, destinos e bitolas.

- Atualizar nós, conexões, comprimentos e associação dos componentes no grafo.

- Revisar parâmetros de custo e restrições, especialmente caminho principal, utilização e hoop.

- Configurar a conta de serviço e compartilhar o novo mapa com o e-mail correto.

- Conferir o `SPREADSHEET_ID` em todos os módulos que acessam o Google Sheets.

- Executar a simulação; analisar sinais sem rota e diferenças inesperadas.

- Aplicar com confirmação, conferir backups e repetir a simulação até zero pendências.

- Guardar data, versão/commit do GitHub, cópia do mapa e relatório de execução.


## 16. O que nunca fazer

Não publicar credentials.json no GitHub; não copiar rotas antigas para um novo carro sem revisar a geometria; não executar --aplicar sem conferir a planilha alvo; não interpretar um caminho calculado como aprovado para fabricação sem validação física.

Referências: README e scripts executar.sh / executar++.sh do ZIP dijkstra, How To anterior e execução V5 relatada pela equipe. A instalação da Fase 1 é opcional e depende dos arquivos adicionais estarem no clone.
