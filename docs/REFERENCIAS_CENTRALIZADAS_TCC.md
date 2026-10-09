# Central de referências — UniQL / TCC NIDS

> Documento pessoal de organização. O objetivo é centralizar os links usados ao
> longo do TCC, evitando que artigos, datasets, repositórios e documentos de
> projeto fiquem espalhados.

## 1. Repositórios do projeto

### 1.1 UniQL — repositório principal
- Link: https://github.com/phramos07/uniql
- Tipo: GitHub / projeto do TCC
- Descrição: repositório criado pelo orientador para o desenvolvimento do
  UniQL, descrito atualmente como uma DSL para unificação de benchmarks.
- Uso: código, samples, protótipos de sintaxe e documentação.

### 1.2 Protótipo `example1.uq`
- Link: https://github.com/phramos07/uniql/blob/main/proto/syntax/example1.uq
- Tipo: protótipo de sintaxe
- Descrição: rascunho inicial contendo `RULE`, `IMPORT`, `CONFIG`, `SCHEMA`,
  `MAP`, `MASK`, `FILL` e `DROP`.
- Uso: fonte histórica das ideias de sintaxe; não deve ser tratado como
  gramática definitiva.

### 1.3 Samples do projeto
- Link: https://github.com/phramos07/uniql/tree/main/data/samples
- Tipo: dados de desenvolvimento
- Conteúdo: 100 linhas de CIC-IDS2017, CSE-CIC-IDS2018 e
  LycoS-Unicas-IDS2018, além do script de amostragem.
- Uso: exemplos pequenos para inspeção e testes do UniQL.

### 1.4 Documentos do projeto
- Link: https://github.com/phramos07/uniql/tree/main/docs
- Tipo: documentação
- Conteúdo atual: relatório de features e dicionário XLSX.
- Uso: documentação viva da análise dos datasets.

---

## 2. Datasets oficiais

### 2.1 CIC-IDS2017
- Link oficial: https://www.unb.ca/cic/datasets/ids-2017.html
- Instituição: Canadian Institute for Cybersecurity, University of New Brunswick
- Descrição: dataset de 2017 com tráfego benigno e múltiplos ataques, PCAPs e
  fluxos extraídos por CICFlowMeter.
- Uso no TCC: uma das fontes principais; comparação de schema e avaliação
  cross-dataset.

### 2.2 CSE-CIC-IDS2018
- Link oficial: https://www.unb.ca/cic/datasets/ids-2018.html
- Instituição: Canadian Institute for Cybersecurity / Communications Security
  Establishment
- Descrição: dataset de 2018 com infraestrutura maior e 80 features extraídas
  com CICFlowMeter-V3.
- Uso no TCC: uma das fontes principais; possui múltiplos CSVs e variantes de
  schema.

### 2.3 LycoS-Unicas-IDS2018
- Repositório oficial: https://github.com/MarcoCantone/LycoS-Unicas-IDS2018
- Descrição: reprocessamento dos PCAPs do CSE-CIC-IDS2018 com o extrator
  LycoSTand.
- Estrutura informada pelo repositório: 13.691.268 amostras, 77 features +
  label.
- Uso no TCC: comparação cross-extractor e harmonização com CIC/CSE.

### 2.4 LYCOS-IDS2017
- Site: https://lycos-ids.univ-lemans.fr/
- Descrição: versão reextraída/corrigida do CIC-IDS2017 usando LycoSTand.
- Uso no TCC: dataset do artigo-base; download pode apresentar disponibilidade
  irregular, mas a página é importante para documentação e referências.

### 2.5 Coleção de datasets NIDS padronizados da University of Queensland
- Página atual: https://staff.itee.uq.edu.au/marius/NIDS_datasets/
- Página do projeto: https://www.cyber.uq.edu.au/node/824
- Descrição: versões de diversos datasets em conjuntos de features comuns
  NetFlow e CICFlowMeter.
- Uso no TCC: referência extremamente relevante para a ideia de schema comum e
  comparação cross-dataset; também é fonte de possíveis datasets futuros.

### 2.6 Catálogo geral do Canadian Institute for Cybersecurity
- Link: https://www.unb.ca/cic/datasets/
- Uso: localizar datasets atuais e páginas oficiais.

---

## 3. Extratores e ferramentas

### 3.1 CICFlowMeter
- GitHub: https://github.com/ahlashkari/CICFlowMeter
- Descrição: gerador/analisador de bi-flows usado em CIC-IDS2017 e outros
  datasets CIC.
- Uso no TCC: verificar significado das features, unidades e implementação de
  características.

### 3.2 LycoSTand / LYCOS
- Projeto: https://lycos-ids.univ-lemans.fr/
- Descrição: extrator desenvolvido para corrigir problemas identificados nos
  fluxos/CSV do CIC-IDS2017.
- Uso no TCC: entender diferenças semânticas entre features com nomes
  semelhantes e estudar efeito do extrator.

---

## 4. Artigos centrais

### 4.1 Cantone, Marrocco e Bria (2024)
**Machine Learning in Network Intrusion Detection: A Cross-Dataset
Generalization Study**
- DOI: https://doi.org/10.1109/ACCESS.2024.3472907
- Repositório de código:
  https://github.com/MarcoCantone/NIDS_cross-dataset_generalization
- PDF institucional:
  https://iris.unicas.it/retrieve/a40146bd-61d7-4a77-98c7-cf72f480c839/2024%20-%20Machine%20Learning%20in%20Network%20Intrusion%20Detection%20-%20A%20Cross-Dataset%20Generalization%20Study.pdf
- Descrição: estudo-base do TCC. Avalia generalização cross-dataset usando
  CIC-IDS2017, CSE-CIC-IDS2018, LycoS-IDS2017 e LycoS-Unicas-IDS2018.
- Uso: desenho experimental, mapeamento LycoS→CIC, evidência da degradação
  cross-dataset.

### 4.2 Sarhan, Layeghy e Portmann (2022)
**Towards a Standard Feature Set for Network Intrusion Detection System
Datasets**
- DOI: https://doi.org/10.1007/s11036-021-01843-0
- arXiv: https://arxiv.org/abs/2101.11315
- Descrição: discute a falta de um feature set comum e propõe conjuntos NetFlow
  padronizados.
- Uso: uma das melhores justificativas científicas para um schema comum.

### 4.3 Rosay, Carlier, Cheval e Leroux (2021)
**From CIC-IDS2017 to LYCOS-IDS2017: A corrected dataset for better performance**
- DOI: https://doi.org/10.1145/3486622.3493973
- Site do projeto: https://lycos-ids.univ-lemans.fr/
- Descrição: apresenta LYCOS-IDS2017 e correções relacionadas ao CIC-IDS2017.
- Uso: justificar LycoSTand/LYCOS e discutir problemas de extração.

### 4.4 Rosay, Cheval, Carlier e Leroux (2022)
**Network Intrusion Detection: A Comprehensive Analysis of CIC-IDS2017**
- DOI: https://doi.org/10.5220/0010774000003120
- Página SciTePress: https://www.scitepress.org/Papers/2022/107740/
- PDF:
  https://www.scitepress.org/PublishedPapers/2022/107740/107740.pdf
- Descrição: análise detalhada de CIC-IDS2017; identifica problemas como
  duplicação de features, cálculos incorretos, detecção de protocolo,
  terminação TCP e dúvidas de rotulagem.
- Uso: base técnica para decisões de saneamento e para a existência do
  LycoSTand.

### 4.5 Sharafaldin, Habibi Lashkari e Ghorbani (2018)
**Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic
Characterization**
- DOI: https://doi.org/10.5220/0006639801080116
- Página SciTePress:
  https://www.scitepress.org/PublicationsDetail.aspx?ID=K3WXGO8%2F3O4%3D
- Descrição: artigo associado à criação/caracterização do CIC-IDS2017.
- Uso: contextualização do dataset, geração de tráfego e features.

### 4.6 Sarhan, Layeghy, Moustafa e Portmann (2021)
**NetFlow Datasets for Machine Learning-Based Network Intrusion Detection
Systems**
- DOI: https://doi.org/10.1007/978-3-030-72802-1_9
- Página: https://eudl.eu/doi/10.1007/978-3-030-72802-1_9
- Descrição: fornece datasets NIDS convertidos para um feature set comum
  NetFlow.
- Uso: precedente direto para comparação com datasets padronizados.

### 4.7 Mishra et al. (2026)
**A cross-dataset harmonized intrusion detection framework with statistically
validated multi-model learning**
- DOI: https://doi.org/10.1371/journal.pone.0346982
- PLOS ONE:
  https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0346982
- Descrição: trabalho recente focado explicitamente em harmonização
  cross-dataset e avaliação multi-modelo.
- Uso: trabalho correlato importante para posicionar a contribuição declarativa
  do UniQL.
- Nota: houve uma correção posterior apenas na declaração de financiamento:
  https://doi.org/10.1371/journal.pone.0349626

---

## 5. Repositório/código do artigo-base

### 5.1 NIDS cross-dataset generalization
- Link:
  https://github.com/MarcoCantone/NIDS_cross-dataset_generalization
- Descrição: código do artigo de Cantone et al.
- Uso: pré-processamento, experimentos, classifiers e mapeamentos.

### 5.2 Script de pré-processamento
- Link raw:
  https://raw.githubusercontent.com/MarcoCantone/NIDS_cross-dataset_generalization/main/preprocess_dataset.py
- Descrição: contém operações imperativas de harmonização e o dicionário
  `lycos_cic_association`.
- Uso: excelente evidência de que várias transformações hoje hardcoded podem
  ser descritas por uma DSL.

---

## 6. Padrões e referências auxiliares

### 6.1 IANA — Service Name and Transport Protocol Port Number Registry
- Link:
  https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
- Uso: fonte oficial para ranges/serviços de portas caso o UniQL tenha regras
  de categorização de porta.

---

## 7. Ferramentas de linguagem/gramática para fase futura

> Não são prioridade da etapa atual; ficam registradas para quando a sintaxe
> estiver estável.

### 7.1 ANTLR
- Link: https://www.antlr.org/
- Uso: geração de lexer/parser a partir de gramática.

### 7.2 Lark
- Link: https://lark-parser.readthedocs.io/
- Uso: biblioteca Python para implementar gramáticas e parsers.

### 7.3 textX
- Link: https://textx.github.io/textX/stable/
- Uso: framework Python focado em criação de DSLs textuais.

---
