# UniQL — Especificação preliminar de requisitos e sintaxe v0.1

> **Status:** documento de projeto. Não é ainda uma gramática formal, nem define
> um parser/compilador implementado. A função desta versão é responder à pergunta
> da reunião com o orientador: **“Se eu tivesse de unificar esses datasets na
> mão, o que eu precisaria fazer — e, portanto, o que a linguagem precisa ser
> capaz de expressar?”**

## 1. Motivação

O objetivo do UniQL é descrever **de forma declarativa, auditável e
reproduzível** como benchmarks/datasets heterogêneos devem ser transformados
até uma representação comum.

A linguagem não deve “adivinhar” silenciosamente a semântica dos dados. A
automação proposta é dividida em dois níveis:

1. **Automação mecânica segura:** operações que podem ser executadas
   deterministicamente, como `trim`, `snake_case`, detecção de duplicatas,
   inferência inicial de tipos, mapeamento por nome exatamente igual após
   normalização e alinhamento à ordem do schema.
2. **Harmonização declarada pelo pesquisador:** equivalências semânticas,
   unidades, labels, sentinelas, derivações e políticas de missing devem ser
   explicitamente descritas quando não forem mecanicamente inequívocas.

Mapeamento semântico por similaridade, embeddings ou LLM pode ser uma extensão
futura de **sugestão**, mas não deve ser requisito mínimo do núcleo.

---

## 2. Princípios de projeto

### 2.1 Python-like, mas com chaves

A sintaxe deve ser familiar para quem conhece Python:

- `if`, `elif`, `else`, `return`;
- `True`, `False`, `None`;
- operadores `+ - * /`, comparações e `in`;
- identificadores em `snake_case`;
- comentários com `#`.

Os blocos, porém, usam `{ ... }`.

### 2.2 Drop by default

O modo recomendado é **whitelist**:

```uniql
config {
    drop_unmapped = True
}
```

Uma coluna só aparece na saída se:

- tiver sido mapeada para um atributo do schema;
- tiver sido criada por `derive`;
- ou for explicitamente preservada.

Isso reduz a chance de identificadores, metadados e artefatos específicos do
ambiente entrarem acidentalmente no dataset harmonizado.

### 2.3 Schema separado da transformação

O **schema** responde:

> Como deve ser o dataset final?

A **transformação** responde:

> Como uma fonte específica chega a esse schema?

Assim, vários datasets diferentes podem ser convertidos para o mesmo contrato.

### 2.4 Separar harmonização de feature selection

Uma feature pode existir no schema canônico e ser excluída de um experimento
de Machine Learning. O UniQL não deve confundir “representar corretamente” com
“ser boa feature para determinado classificador”.

---

## 3. Pipeline manual que a linguagem deve automatizar

A pergunta central das anotações é: **“se fosse na unha, o que eu faria?”**

O pipeline manual típico é:

1. abrir os CSVs e informar separador, encoding, header e dialeto;
2. lidar com vários arquivos de um mesmo benchmark;
3. limpar nomes de colunas (`trim`, `snake_case`);
4. identificar variantes de schema;
5. detectar colunas duplicadas;
6. detectar/interpretar tipos;
7. identificar colunas correspondentes;
8. mapear/renomear colunas;
9. remover identificadores/metadados indesejados;
10. converter tipos;
11. converter unidades;
12. interpretar datas/tempos;
13. tratar `NaN`, `Inf`, `-Inf`, `None` e sentinelas;
14. remover linhas inválidas;
15. preencher valores quando houver regra justificável;
16. criar atributos derivados;
17. harmonizar labels;
18. validar invariantes;
19. reordenar/selecionar colunas segundo o schema;
20. concatenar os datasets já harmonizados;
21. exportar em formato controlado;
22. registrar tudo em um relatório de auditoria/proveniência.

**Esses passos são a base dos requisitos da linguagem.**

---

## 4. Requisitos funcionais

### RF-01 — Importar CSV com dialeto explícito — P0

A linguagem deve permitir configurar:

- caminho ou glob (`*.csv`);
- separador;
- encoding;
- presença de header;
- caractere de quote;
- tokens de null;
- inferência de tipos;
- aceitação de variantes de schema.

Exemplo:

```uniql
source data = csv("input/*.csv") {
    separator = ";"
    encoding = "utf-8"
    header = True
}
```

### RF-02 — Importar vários arquivos como uma fonte lógica — P0

CIC-IDS2017 e CSE-CIC-IDS2018 são distribuídos em múltiplos CSVs. A linguagem
deve tratar um glob como uma fonte lógica, mantendo informação sobre o arquivo
de origem para auditoria.

### RF-03 — Padronizar nomes de atributos — P0

Operações mínimas:

- remover espaços nas bordas;
- normalizar espaços internos;
- converter para `snake_case`;
- opcionalmente normalizar capitalização.

A normalização lexical **não implica equivalência semântica**.

### RF-04 — Mapear automaticamente colunas de mesmo nome — P0

`automap` deve mapear apenas quando:

1. o nome já foi normalizado;
2. existe exatamente um campo canônico com aquele nome;
3. não existe conflito.

Modo inicial recomendado:

```uniql
auto_map = "normalized_exact"
```

Mapeamento fuzzy/semântico não é requisito P0.

### RF-05 — Mapear/renomear explicitamente atributos — P0

Exemplo real:

```uniql
map tot_fwd_pkts -> fwd_pkt_count
map fwd_pkt_cnt -> fwd_pkt_count
```

`map` é a operação central de harmonização semântica.

### RF-06 — Declarar um schema canônico tipado — P0

O schema define:

- nome canônico;
- tipo;
- unidade;
- nullable ou não;
- papel `required`, `optional` ou `target`;
- ordem final.

### RF-07 — Sistema de tipos — P0

Tipos escalares mínimos:

- `int`
- `float`
- `bool`
- `string`
- `category`
- `date`
- `time`
- `datetime`

Tipos/unidades semânticos úteis:

- `duration[us]`, `duration[ms]`, `duration[s]`
- `size[byte]`
- `rate[bytes_per_second]`
- `rate[packets_per_second]`

`?` pode representar nullable:

```uniql
flow_pkt_rate: rate[packets_per_second]?
```

### RF-08 — Inferir e converter tipos — P0

A engine pode inferir tipos na leitura, mas o schema é a autoridade final.

```uniql
cast dst_port as int
```

Falhas de conversão precisam de política explícita: erro, `None`, drop de linha,
etc.

### RF-09 — Converter unidades — P0

Exemplo:

```uniql
convert flow_duration from us to ms
```

A conversão deve ser conhecida pela runtime ou por `rule` explícita.

### RF-10 — Dropar colunas explicitamente — P0

```uniql
drop timestamp
drop src_ip
```

### RF-11 — Dropar colunas não mapeadas — P0

```uniql
drop_unmapped = True
```

É a política recomendada do projeto.

### RF-12 — Dropar por regra estrutural — P0

A linguagem deve suportar ao menos:

- duplicatas;
- coluna constante;
- coluna por nome/padrão;
- coluna inexistente em determinado schema alvo.

Exemplo:

```uniql
deduplicate columns {
    keep = "first"
}
```

Uma forma genérica de `drop where ...` pode ser adicionada depois, mas o núcleo
precisa resolver os casos reais.

### RF-13 — Lidar com variantes de schema — P0

Um mesmo benchmark pode conter CSVs com schemas diferentes.

A linguagem precisa:

- detectar a variante;
- permitir regras condicionais com `has_column`;
- produzir relatório das diferenças;
- convergir todas as variantes para o mesmo schema.

### RF-14 — Filtrar/remover linhas inválidas — P0

Caso real do CSE-CIC-IDS2018:

```uniql
drop_rows where label == "Label"
```

Isso remove headers repetidos que aparecem no meio dos dados.

### RF-15 — Tratar missing values — P0

Distinguir:

- `None` / null real;
- `NaN`;
- `Inf` e `-Inf`;
- string vazia;
- sentinelas (`-1`, por exemplo);
- coluna completamente ausente.

**Zero não deve ser tratado como missing genericamente.**

### RF-16 — Preencher valores por regra — P0

```uniql
fill feature with 0 where feature is None
```

Essa operação precisa ser explícita e semanticamente justificada.

### RF-17 — Substituir valores/sentinelas — P0

```uniql
replace [Inf, -Inf] with None in numeric_columns
```

Ou:

```uniql
replace -1 with None in tcp_initial_window
```

quando a semântica da feature justificar.

### RF-18 — Criar atributos derivados — P0

Requisito direto das anotações.

```uniql
derive total_pkt_count = fwd_pkt_count + bwd_pkt_count
```

A runtime deve montar dependências entre atributos derivados.

### RF-19 — Suportar funções/regras reutilizáveis — P0

```uniql
rule safe_div(a, b) {
    if b == 0 {
        return None
    }
    return a / b
}
```

As regras permitem encapsular conversões, categorização e normalização.

### RF-20 — Manipular datas e tempos — P0

```uniql
parse timestamp as datetime format "%d/%m/%Y %H:%M:%S"
```

Também deve existir formatação controlada no `export`.

### RF-21 — Harmonizar valores categóricos e labels — P0

```uniql
map_values label using normalize_binary_label
```

O `label` é `target`, nunca feature preditiva.

### RF-22 — Validar presença de colunas — P0

```uniql
require [flow_duration, fwd_pkt_count, label]
```

### RF-23 — Validar invariantes — P0

```uniql
assert flow_duration >= 0
```

A engine deve produzir erro claro e contagem de violações.

### RF-24 — Concatenar benchmarks harmonizados por linhas — P0

```uniql
dataset unified = concat_rows(a, b, c)
```

Só pode ocorrer após compatibilidade de schema, tipos e unidades.

**Join horizontal não é requisito mínimo atual.**

### RF-25 — Preservar proveniência — P0

Ao concatenar, deve ser possível registrar a fonte:

```uniql
preserve_source = True as "_source_dataset"
```

Essa coluna pode ser metadado de auditoria e ser excluída do ML.

### RF-26 — Formatar e exportar saída — P0

Configurações mínimas:

- CSV;
- separador;
- encoding;
- símbolo de null;
- decimal;
- formato de data/hora;
- ordem de colunas.

### RF-27 — Produzir relatório de auditoria — P0

O relatório deve informar:

- arquivos lidos;
- schemas de entrada;
- variantes;
- auto-maps;
- maps explícitos;
- drops;
- linhas removidas;
- casts;
- conversões de unidade;
- derives;
- políticas de missing;
- assertions;
- schema final.

Esse requisito é central para reprodutibilidade científica.

### RF-28 — Resolver conflitos de forma explícita — P0

Casos:

- duas colunas de origem para um mesmo target;
- duplicata depois de `snake_case`;
- um auto-map contradiz um map explícito.

Modo recomendado no TCC:

```uniql
on_mapping_conflict = "error"
```

Nunca “escolher uma” silenciosamente.

### RF-29 — Preview / dry-run — P1

Antes de processar 5 GB:

```uniql
preview transform lycos18 rows 100
```

ou modo de CLI equivalente.

Deve mostrar plano de transformação sem escrever a saída definitiva.

### RF-30 — Profiling simples — P1

Operação útil para o fluxo de pesquisa:

- dtype;
- missing;
- zero;
- min/max;
- cardinalidade.

Pode ser built-in da ferramenta, sem necessariamente fazer parte da gramática
do programa.

---

## 5. Requisitos não funcionais

### RNF-01 — Determinismo e reprodutibilidade

Mesmo input + mesmo programa + mesma versão da runtime devem produzir a mesma
saída.

### RNF-02 — Streaming / baixo uso de memória

LycoS-Unicas-IDS2018 tem vários GB. A implementação deve trabalhar por chunks
quando possível.

### RNF-03 — Não modificar fontes

Arquivos originais são somente leitura. Resultados vão para outro caminho.

### RNF-04 — Fail fast em ambiguidades

Modo `strict=True` deve interromper o pipeline em situações que possam alterar
a semântica sem decisão explícita.

### RNF-05 — Diagnósticos úteis

Erros devem informar:

- arquivo;
- linha quando aplicável;
- coluna;
- regra;
- valor problemático;
- ação sugerida.

### RNF-06 — Auditabilidade

Toda transformação deve poder ser reconstruída a partir do programa e do
relatório de execução.

### RNF-07 — Escalabilidade

Operações colunares simples devem ser compatíveis com execução streaming.
Operações que exigem dataset completo precisam ser claramente sinalizadas.

### RNF-08 — Extensibilidade

Novos tipos, formatos de entrada/saída e funções built-in devem poder ser
adicionados sem alterar a sintaxe central.

### RNF-09 — Testabilidade

Cada `rule` e cada `transform` deve ser testável isoladamente em pequenos
samples.

---

## 6. Modelo conceitual da linguagem

### `config`

Configuração global e políticas de segurança.

### `source`

Declara uma fonte física/lógica de dados.

### `schema`

Contrato da saída canônica.

### `rule`

Função reutilizável, determinística, idealmente sem efeitos colaterais.

### `transform`

Especifica como uma fonte é adaptada a um schema.

### `dataset`

Resultado material/lógico de operações como concatenação.

### `validate`

Validação final contra schema e invariantes.

### `export`

Serialização da saída.

### `report`

Geração de proveniência/auditoria.

---

## 7. Primitivas / operações propostas

| Operação | Função |
|---|---|
| `automap` | mapeia nomes exatamente iguais após normalização |
| `map` | liga explicitamente uma coluna fonte a uma coluna canônica |
| `drop` | remove coluna |
| `deduplicate columns` | resolve duplicatas estruturais |
| `drop_rows` | remove registros por condição |
| `cast` | converte tipo |
| `convert` | converte unidade |
| `parse` | interpreta string como data/tempo/tipo semântico |
| `replace` | substitui valores/sentinelas |
| `fill` | preenche missing por política |
| `derive` | cria atributo calculado |
| `map_values` | harmoniza categorias/labels |
| `require` | exige presença/não ausência estrutural |
| `assert` | valida uma condição/invariante |
| `concat_rows` | concatena datasets já harmonizados |
| `validate` | valida o resultado contra o schema |
| `export` | grava saída |
| `report` | grava auditoria |

### Sobre `MASK`

O protótipo `example1.uq` usa `MASK` para categorizar uma porta. Recomenda-se
**não estabilizar `MASK` com esse significado**.

“Masking” normalmente sugere anonimização/ocultação. Para transformação
semântica, `map`, `derive` ou uma `rule` são mais claros.

Se `MASK` for mantido, sugere-se reservá-lo para:

```uniql
mask src_ip using ipv4_prefix(24)
```

e não para categorização.

### Sobre `REDUCE`

Ainda não há um caso real obrigatório que justifique `REDUCE` como keyword
central. Não deve entrar no núcleo apenas porque “pode ser útil”. Primeiro deve
existir um caso de uso concreto.

---

## 8. Sistema de tipos e unidades

### Tipos escalares

```text
int
float
bool
string
category
date
time
datetime
```

### Tipos físicos/semânticos

```text
duration[us]
duration[ms]
duration[s]
size[byte]
rate[bytes_per_second]
rate[packets_per_second]
```

### Nullable

```text
float?
datetime?
```

### Papéis de atributo

```text
required
optional
target
```

No futuro podem existir:

```text
metadata
identifier
```

para separar rastreabilidade de features preditivas.

---

## 9. Regras para automap

`automap` só deve mapear automaticamente quando houver certeza mecânica.

Exemplo:

```text
Flow Duration
  -> trim
  -> snake_case
  -> flow_duration
```

Se o schema possui `flow_duration`, o map é seguro.

Por outro lado:

```text
Tot Fwd Pkts
  -> tot_fwd_pkts
```

não é igual a:

```text
fwd_pkt_count
```

Logo, precisa de:

```uniql
map tot_fwd_pkts -> fwd_pkt_count
```

Esse limite é deliberado. O UniQL não deve trocar auditabilidade por
“inteligência” heurística nesta primeira versão.

---

## 10. Ordem lógica de execução

Apesar da aparência de código, o UniQL é principalmente declarativo. A runtime
pode organizar as operações em fases:

1. leitura/parsing;
2. normalização lexical;
3. saneamento estrutural;
4. resolução de schema e maps;
5. casts e unidades;
6. normalização de valores;
7. derives;
8. missing policies;
9. assertions;
10. alinhamento ao schema;
11. concatenação;
12. export/audit.

Dentro de `rule`, a ordem é imperativa como em Python.

---

## 11. Palavras-chave provisórias

```text
config
source
csv
schema
rule
transform
dataset
validate
export
report

automap
map
drop
drop_rows
deduplicate
cast
convert
parse
replace
fill
derive
map_values
require
assert
concat_rows

if
elif
else
return
where
with
using
from
to
as

True
False
None
required
optional
target
```

Esta lista **não é ainda uma gramática**.

---

## 12. O que fica fora do escopo mínimo v0.1

1. Treinar Random Forest/XGBoost/MLP dentro da DSL.
2. Seleção automática de features para ML.
3. Join relacional genérico entre tabelas.
4. Execução arbitrária de Python dentro do programa.
5. Inferência semântica automática de colunas diferentes por LLM.
6. Compilador/parser definitivo.
7. Otimizador complexo de consultas.
8. Distribuição em cluster.

Esses itens podem ser extensões futuras.

---

## 13. Questões ainda abertas para discutir com o orientador

1. Extensão definitiva: `.uq` ou `.uniql`?
2. `map` deve também substituir um `rename` local?
3. `MASK` permanece? Se sim, significa anonimização?
4. `REDUCE` possui caso de uso real?
5. `profile` pertence à linguagem ou à CLI?
6. O schema canônico declara unidade no tipo ou em atributo separado?
7. Labels serão binários, multiclass ou suportarão ambos?
8. O runtime preserva metadados de origem fora do vetor de ML?
9. Programas podem importar outros programas/rules?
10. Como versionar schemas (`nids_core@1`)?
11. A linguagem terá bibliotecas padrão de unidades e funções de rede?
12. Qual será a política para transforms que não produzem todos os campos
    `required`?

---

## 14. Traceabilidade com a reunião

As anotações pedem explicitamente:

- configurar separador no import;
- mapeamento automático de nomes iguais;
- regras de drop, incluindo duplicatas;
- padronização de nomes;
- tipos;
- renomear/mapear;
- manipular/criar atributos a partir de outros;
- concatenar;
- formatar data/tempo e saída;
- listar requisitos antes de escrever a gramática.

Todos esses pontos estão cobertos pelos requisitos RF-01 a RF-30 deste
documento.

---

## 15. Recomendação de próximos artefatos

Antes de escrever EBNF/ANTLR/Lark:

1. revisar este documento com Pedro;
2. marcar P0/P1 que realmente entram no TCC I;
3. estabilizar 2–3 programas-exemplo reais;
4. estabilizar schema canônico v0.1;
5. só então escrever a gramática;
6. parser/runtime ficam para a etapa de implementação.

