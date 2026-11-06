# dijkstra_tupa

Essa é uma tentativa de implementação do algoritimo Dijkstra na otimização do chicote elétrico do carro T11 do Tupã para a competição da Fórmula SAE - elétrica, e sua integração com o Mapa de Sinais.


Por **Maria Eduarda Bronzatto Esbízaro**, estudante da EESC-USP.

Iniciado em *09/09/2026*

Finalizada a versão principal (v.4) em *09/10/2026*

**Versão atual:** V5 — automação e sincronização das planilhas.


## Execução do projeto

O projeto possui dois scripts de execução na pasta principal, com finalidades diferentes.

### `executar.sh` — Dijkstra tradicional (V4)

```bash
./executar.sh
```

Inicia a aplicação tradicional do Dijkstra, coordenada por `src/main.py`. É o fluxo destinado a utilizar o programa pelo terminal, incluindo consultas de roteamento manual e o processamento de sinais disponível na V4.

**Quando usar:** para consultar caminhos, testar o grafo ou utilizar os recursos interativos da versão principal. Esse não é o comando recomendado para sincronizar automaticamente todas as abas da V5.

### `executar++.sh` — atualização integrada (V5)

```bash
./executar++.sh
```

É o comando principal para **recalcular o roteamento depois de alterações no Mapa de Sinais ou nos dados de origem**. O script chama `src/automatizacao_v5.py` e coordena o seguinte fluxo:

1. Lê a `Database`, os componentes associados aos nós e as configurações/conexões do grafo.
2. Identifica os sinais destinados ao processamento automático, preservando os sinais tratados manualmente, como CAN e SHUT, conforme as regras da integração.
3. Recalcula os caminhos pelo Dijkstra e suas distâncias físicas.
4. Compara os resultados calculados com as abas `Database`, `Sinais-Dijkstra` e `Resultados-Dijkstra`.
5. Se houver alterações, apresenta um resumo e solicita a confirmação **`APLICAR V5`** antes de escrever.
6. Cria backups das abas que precisam ser modificadas, realiza as atualizações necessárias e verifica os resultados.
7. Executa uma nova simulação para conferir o estado das três abas.

**Quando usar:** após os responsáveis pela planilha alterarem os registros que alimentam o roteamento. Se tudo já estiver sincronizado, o programa informa que não há alterações pendentes.

> **Atenção:** a V5 modifica uma planilha compartilhada após confirmação. Os backups não constituem uma transação atômica: se houver falha durante a escrita, pode ser necessária recuperação manual. Antes de usar com mudanças reais, o fluxo de escrita deve ser validado em uma cópia da planilha.



## Documentações de cada versão feita da implementação

- [Versão 1 - inicial](log/doc_v1.md)
- [Versão 2 - modularização e implementação externa de entrada](log/doc_v2.md)
- [Versão 3 - implementação de custos adicionais](log/doc_v3.md)
- [Versão 4 - implementação externa de saída e de nó intermediário e organização](log/doc_v4.md)
- [Versão 5 — automação do roteamento e sincronização das planilhas](log/doc_v5.md)

## Segurança

O arquivo `credentials/credentials.json` contém dados de autenticação e **não deve ser publicado no GitHub**. Utilize um `.gitignore` adequado e verifique se as credenciais não foram incluídas em commits anteriores.

O algoritmo calcula rotas sobre o grafo e as regras configuradas; seus resultados ainda precisam ser conferidos quanto à viabilidade física, elétrica e de montagem do chicote do T11.