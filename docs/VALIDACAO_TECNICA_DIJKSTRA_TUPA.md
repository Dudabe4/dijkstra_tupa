# Validação técnica do sistema de roteamento Dijkstra TUPÃ

**Comparação histórica TX × T11 | Validação matemática, funcional e operacional**  
**Documento de consolidação para apresentação técnica à Fórmula SAE**  
**Versão de trabalho:** novembro de 2026  
**Base:** mapas de sinais TX/T11, auditoria anterior, código-fonte V5 e registros de execução da equipe.

> **Escopo:** o mapa denominado T11 ainda utiliza o grafo e as distâncias de referência herdados do TX. Os ganhos descritos são estimativas na geometria-base comum, **não medições do chicote final fabricado do T11**.

## 1. Objetivo e alcance

Este documento reúne as verificações já realizadas sobre o sistema de roteamento de chicotes elétricos TUPÃ, explicando os resultados observados e os limites das conclusões. São consolidadas a comparação entre as planilhas TX e T11, a análise matemática, a inspeção do código-fonte e as execuções registradas.

## 2. Visão geral do processo

Cada sinal elétrico tem uma identificação (*tag*), um nó de origem e um nó de destino. O carro é representado por um **grafo**: os nós são pontos de passagem e as arestas são trechos possíveis entre eles, com comprimentos em milímetros. O programa lê os sinais, monta essa rede, calcula uma rota e registra separadamente a distância física e o custo utilizado para escolher o caminho.

Os sinais são processados sequencialmente: depois que uma rota é calculada com sucesso, a utilização dos nós é atualizada e pode influenciar o roteamento dos sinais seguintes. A automação V5 compara os resultados com os dados do Google Sheets e, quando autorizada, cria backup, escreve somente os campos necessários e confere a gravação.

## 3. Como o algoritmo decide os caminhos

O método utilizado é o **Dijkstra**, que busca o caminho de menor custo em uma rede com custos não negativos. Neste projeto, **custo não é sinônimo de comprimento físico**: existem preferências e penalizações para orientar o trajeto dos fios.

Para uma passagem do nó `u` ao nó `v`, o custo considerado é:

$$
c(u,v) = d(u,v) \cdot f(u,v) + \lambda \cdot U(v) + P(u,v)
$$

Onde:

- `d(u,v)`: comprimento físico do trecho;
- `f(u,v)`: fator da aresta — **0,2 no caminho principal** e **1,0 nas demais arestas**;
- `U(v)`: utilização acumulada do nó de destino;
- `λ`: penalização por utilização — **5** na configuração observada;
- `P(u,v)`: penalização direcional aplicável — **5.000** para a entrada no *hoop* na configuração observada.

O custo total da rota é a soma dos custos das transições. Já a distância física é calculada separadamente:

$$
L(R) = \sum_{(u,v)\in R} d(u,v)
$$

Assim, uma rota fisicamente maior pode ser escolhida quando apresenta custo configurado menor. O programa também permite um ponto intermediário obrigatório, calculando dois trechos e unindo os caminhos sem duplicar esse nó.

O caminho principal é reconhecido nos dois sentidos. A penalização de entrada no *hoop* é **direcional**: uma passagem `A → B` pode ser penalizada sem que `B → A` seja. A utilização só é atualizada depois do sucesso do roteamento completo.

## 4. Bases comparadas e qualidade dos dados

| Aspecto | TX | T11 |
|---|---:|---:|
| Registros com tag | 278 | 275 |
| Tags distintas comuns | 252 | 252 |
| Tags exclusivas | 6 | 4 |
| Coluna de comprimento real | Q | R |
| Registros com fórmula numérica conferida | 223/223 | 219/219 |

As colunas foram comparadas **pelo significado**, porque o T11 acrescentou a coluna `Dijkstra` e deslocou campos posteriores. Existem linhas separadoras (`---`) e pelo menos uma tag duplicada no TX; por isso, uma tag repetida não deve ser tomada automaticamente como uma via física única.

Nos registros pareados, foram observadas **nove alterações de origem**, **nove de destino** e **122 diferenças textuais de caminho**. Essas diferenças exigem rastreabilidade: não são necessariamente erros nem ganhos atribuíveis ao algoritmo.

## 5. Resultados quantitativos de otimização

| Amostra | Registros | TX (cm) | T11 (cm) | Redução |
|---|---:|---:|---:|---:|
| Mesmo par de nós e bitola, inclusive registros sem rota válida | 239 | 58.898,16 | 48.230,05 | **18,11%** |
| Mesmo par e bitola, com rota T11 explícita | 209 | 51.860,90 | 45.269,05 | **12,71%** |
| Rotas verificáveis nos dois mapas | 168 | 49.765,40 | 43.173,55 | **13,25%** |

A redução percentual é calculada por:

$$
\text{Redução} \; (\%) = 100 \times \frac{\sum L_{TX} - \sum L_{T11}}{\sum L_{TX}}
$$

Essa é uma **razão entre os comprimentos totais**, não uma média simples dos percentuais de cada sinal.

A amostra mais rigorosa contém **168 registros** com origem, destino e bitola equivalentes e rotas verificáveis no grafo. A diferença é **6.591,85 cm**, aproximadamente **65,92 m** de comprimento estimado somado sobre esses registros. O resultado de **13,25%** é a principal referência histórica deste documento.

O valor de **18,11% não deve ser divulgado como ganho validado do algoritmo**: 30 dos 239 registros estavam sem rota T11 válida (`Verificar Par` ou vazio), e **4.076,26 cm** da redução aparente vinham desses casos. Na amostra de 209 rotas explícitas, **59 encurtaram**, **145 permaneceram iguais** e **5 ficaram mais longas**.

Na amostra de 209 registros, as reduções agregadas por bitola foram:

| Bitola | Registros | Redução agregada |
|---|---:|---:|
| AWG 16 | 8 | 2,76 cm |
| AWG 20 | 121 | 5.154,81 cm |
| AWG 22 | 80 | 1.434,28 cm |

**Não foram calculadas economias de massa ou custo**, pois ainda faltam densidade linear, preço por tipo de cabo e consolidação das vias físicas únicas.

### Exemplos de redução e aumento

O sinal `5V_BRAKE B_MSD` apresentou **60,51% de redução**, passando de **353,87 cm** no TX para **139,74 cm** no T11, uma diferença de **214,13 cm** por registro. A rota `K1 → K3 → K2 → L2 → L1` foi substituída por `K1 → L1`. Outros cinco sinais equivalentes tiveram a mesma redução percentual.

O sinal `24V_SENSOR[H]_PDM` apresentou redução de **29,23%** (**320,23 → 226,63 cm**), enquanto `24V_ICU[B]_PDM` apresentou redução de **32,64%** (**355,88 → 239,74 cm**).

Nem todos os caminhos encurtaram: `TSMS_PNLAT[A]_ICU[B]` aumentou **38,34%** (**212,14 → 293,47 cm**). Isso é **compatível** com uma função de custo que considera utilização e penalizações além da distância, mas a causa específica desse aumento não foi isolada. Mesmo com aumentos individuais, a amostra rigorosa apresentou redução agregada de **13,25%**.

## 6. Validação dos cálculos de comprimento

A aba `Nós-Dijkstra` contém **49 nós** e **87 conexões não direcionadas**. Em **175 rotas T11** com múltiplos nós e arestas verificáveis, a distância cadastrada coincidiu com a soma dos comprimentos dos trechos, com tolerância de **0,15 mm**.

Em **64 dessas 175 rotas**, o caminho escolhido não era o mais curto em distância física. Isso é compatível com a função de custo composta, mas não comprova isoladamente que cada desvio seja desejável para a montagem. Em **173 das 175 rotas**, o custo Dijkstra diferia numericamente da distância física, reforçando que são grandezas distintas.

## 7. Exemplos concretos de alteração de rotas

| Sinal | Mudança de rota (resumo) | Variação estimada |
|---|---|---:|
| `LEDIR+_PACK[A]_STARTBU` | Rota longa por K3/Y1/I1/H1/G3 → W2–L2–G2 | −268,26 cm |
| `FREIO_MSD_BRAKE F` | L1–L2–K2–K3–K1 → L1–K1 | −214,13 cm |
| `TSMS_PNLAT[A]_ICU[B]` | L2–L1 → L2–K2–K3–K1–L1 | +81,33 cm |
| `SHUT_PACK[B]_PUSHBP` | Rota TX existente → `Verificar Par` | **Não contabilizar como ganho** |

Esses exemplos ilustram tanto a eliminação de desvios quanto a escolha de trajetos mais longos pelos critérios de custo. **Ausência de rota não é evidência de otimização.**

## 8. Validação do código-fonte e do funcionamento

Na inspeção do pacote `dijkstra.zip`, foram identificados os módulos de grafo, cálculo de rotas, configurações, integração e auditoria V5. A análise anterior registrou **26 arquivos Python compilados sem erro de sintaxe** e **quatro casos sintéticos básicos executados com sucesso**. Essas evidências são limitadas ao escopo examinado e não constituem certificação de todos os cenários.

| Componente | Funcionamento observado |
|---|---|
| `construir_grafo.py` | Lê pares de nós e comprimentos, cria conexões nos dois sentidos, ignora duplicatas idênticas e sinaliza comprimentos conflitantes. |
| `dijkstra.py` | Calcula o menor custo composto e retorna separadamente caminho, custo e distância física; trata origem igual ao destino. |
| `roteamento_sinais.py` | Processa os sinais na ordem da planilha, aceita intermediário obrigatório, atualiza utilização após sucesso e registra erros individuais sem interromper o lote. |
| `configs/configs.py` | Interpreta os parâmetros do caminho principal, penalização por utilização e entrada no *hoop*. |
| `integracao_v5.py` | Associa os sinais calculados aos registros e prepara atualizações da `Database`. |
| `automatizacao_v5.py` | Coordena simulação, identificação de alterações, confirmação, backup, escrita e conferência posterior. |
| `auditoria_v5.py` | Reúne verificações e evidências de auditoria da V5. |

Os casos sintéticos verificaram origem igual ao destino, escolha de rota alternativa após penalização, comportamento distinto entre sentidos opostos e influência da utilização acumulada em sinais consecutivos.

O algoritmo é determinístico para uma mesma sequência de entradas e configurações, mas **depende da ordem dos sinais**. Ele encontra o menor custo para cada sinal no estado de utilização daquele momento; **não foi demonstrado ótimo global de todo o chicote**.

## 9. Evidências operacionais da integração com Google Sheets

Na execução registrada, a V5 processou **201 sinais automáticos**, preservou **54 sinais manuais** e ignorou **20 linhas não aplicáveis**. A simulação apontou **104 células pendentes** na `Database`, enquanto `Sinais-Dijkstra` e `Resultados-Dijkstra` já estavam sincronizadas.

Após confirmação explícita, o programa criou o backup `Database-BACKUP-TX-20261110-101036`, aplicou as atualizações e informou `OK: Database conferida`. Uma nova simulação encontrou **zero células pendentes** e confirmou as duas abas de sinais e resultados sincronizadas.

Essa sequência fornece evidência prática de consistência entre cálculo, atualização e leitura posterior **para o conjunto executado**. Não comprova transação atômica entre abas: uma falha durante a escrita pode deixar atualizações parciais.

## 10. Cobertura dos sinais e rastreabilidade

Na aba `Resultados-Dijkstra` do arquivo T11, **201 registros automáticos** apresentavam status `OK`, com caminhos correspondentes aos registros associados na `Database`. Esse resultado sustenta a consistência do subconjunto automático, mas não substitui a avaliação dos sinais manuais, derivações e registros sem rota.

Foram observadas **seis tags exclusivas do TX**, **quatro do T11** e pares de sinais em sentidos opostos. Assim, a soma dos comprimentos das linhas não equivale automaticamente ao comprimento de cabos físicos independentes.

## 11. O que está comprovado e o que não está

| Afirmação | Situação |
|---|---|
| Distância de rotas T11 verificáveis | Sustentada pela conferência de **175 rotas** no grafo. |
| Redução histórica de **13,25%** | Sustentada para a amostra definida de **168 registros**. |
| **201 sinais automáticos** com status `OK` | Sustentada pelo mapa T11 e registros de execução. |
| Sincronização V5 e backup | Sustentados pelo log e pela simulação posterior sem pendências. |
| O Dijkstra sozinho causou 13,25% de economia | **Não isolado** em comparação experimental controlada. |
| O T11 físico economizará 65,92 m de cabo | **Não demonstrado**: geometria final e vias físicas ainda não estão consolidadas. |
| Todos os sinais estão liberados | **Não demonstrado**: permanecem sinais manuais, pendências e alertas. |
| Economia de massa, custo ou tempo de montagem | **Não quantificada** com os dados disponíveis. |

## 12. Conclusão para apresentação à Fórmula SAE

A evolução do sistema TUPÃ demonstrou consistência matemática no cálculo de distâncias e comprimentos, funcionamento das regras de custo personalizado e integração operacional com o mapa de sinais. Na comparação histórica de **168 registros equivalentes e geometricamente verificáveis**, o comprimento estimado agregado diminuiu **13,25%**, equivalente a aproximadamente **65,92 m** somados nesses registros.

O sistema também processou **201 sinais automáticos** com resultados `OK` e demonstrou sincronização com backup e conferência posterior. Essas evidências sustentam a utilidade da ferramenta para **apoiar o planejamento e a padronização do roteamento**, com potencial mensurável de redução de comprimento estimado na geometria de referência.

A apresentação deve deixar claro que o ganho é **histórico e amostral**, que o custo otimizado **não considera somente distância** e que o chicote físico definitivo do T11 ainda depende da geometria final e da validação de fabricação.

## 13. Fontes e rastreabilidade

1. `Mapa de Sinais - TX.xlsx` — `Database`, geometria e rotas.
2. `Mapa de Sinais - T11.xlsx` — `Database`, `Nós-Dijkstra`, `Resultados-Dijkstra` e `Sinais-Dijkstra`.
3. `Validacao_Tecnica_Dijkstra_TUPA_TX_T11.md` — auditoria quantitativa e ressalvas metodológicas.
4. `dijkstra.zip` — código-fonte V5, cálculo, roteamento, integração e auditoria.
5. Registros de terminal apresentados pela equipe — 104 atualizações, backup, conferência, nova simulação.

> **Nota de controle documental:** “verificado” se refere às evidências citadas. Onde não houve execução controlada ou medição física, a conclusão está delimitada explicitamente.
