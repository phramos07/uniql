# UniQL — Requisitos funcionais revisados — 12 em vez dos 31 anteriores (proposta v0.2)

### RF-01 — Declarar fontes CSV (arquivo único ou conjunto)

**O UniQL deve permitir declarar uma fonte CSV por caminho e, quando necessário, agrupar vários arquivos da mesma origem com padrão** `*.csv`**.** A declaração deve permitir ao menos indicar o separador. Opções básicas de leitura, como cabeçalho e codificação, podem assumir padrões da runtime.

```q
source cic17 = csv("data/cic17/*.csv") {
    separator = ","
}
```

**Por que é necessário:** o CIC-IDS2017 e o CSE-CIC-IDS2018 são distribuídos em vários CSVs; o LycoS é um arquivo grande. Não é necessário ter um RF separado só para múltiplos arquivos.

**Não inclui:** `quote`, `infer_types`, `allow_schema_variants` como opções obrigatórias, nem uma gramática genérica de formatos de dados.

**Origem:** RF-01 + RF-02 antigos; 

### RF-02 — Normalizar nomes de colunas e sinalizar duplicidades

**A runtime deve disponibilizar os nomes de colunas normalizados em** `snake_case` **antes de resolver mapeamentos.** Se nomes originais diferentes colidirem após a normalização, deve emitir aviso e oferecer identificadores distintos e determinísticos, por exemplo `fwd_header_length_1` e `fwd_header_length_2`.

**Por que é necessário:** os três datasets usam nomenclaturas diferentes; CIC-IDS2017 possui um cabeçalho duplicado. Evita um comando genérico `deduplicate columns` e impede que colunas distintas sejam sobrescritas silenciosamente.

**Limite:** a decisão de fundir, escolher ou comparar duas colunas repetidas **não é automatizada** nesta versão. O comportamento definitivo das duplicatas ainda precisa ser visto.

**Origem:** RF-03 + parte dos RF-12 e RF-28 antigos;

### RF-03 — Declarar o schema de saída e os campos obrigatórios

**O programa deve declarar o nome das colunas da representação comum e quais são** `required`**.** As demais são implicitamente opcionais. Os campos não precisam de anotações de tipo, unidade nem papel de ML.

```q
schema unified {
    required flow_duration // required: precisar estar em todos os csv's. erro em tempo de execução
    required fwd_pkt_count
    required bwd_pkt_count
    required label
    // por default, todas as outras colunas de todos os outros csv's estao no unified
    drop total_pkt_count // exceto as dropadas
}
```

**Por que é necessário:** mapeamentos precisam de um destino bem definido, e `required` ajuda a identificar se uma fonte não consegue atender à representação mínima.

**Não inclui:** `int`, `float`, `date`, `category`, `target`, `optional`, `nullable (?)` ou conversão embutida de unidades. A política exata para um campo obrigatório ausente precisa ser vista.

**Origem:** RF-06 + RF-07 + RF-22 antigos;

### ~~RF-04 — Mapear automaticamente nomes coincidentes~~ -> sempre vai mapear colunas de mesmo nome

**Se** `automap = True`**, a linguagem deve aproveitar colunas cujo nome normalizado coincida exatamente com um campo do schema**, desde que não haja conflito com um mapeamento explícito.

```q
config {
    automap = false // por padrão é True
}
```

**Por que é necessário:** reduz trabalho repetitivo para nomes como `flow_duration` e `label`, sem inventar equivalências como `tot_fwd_pkts == fwd_pkt_count`.

**Limite:** igualdade lexical normalizada é *critério operacional de mapeamento*, não prova de que dois extratores calcularam a feature da mesma maneira. Uma correspondência explicitamente definida com `using rule` tem prioridade sobre o automapeamento no protótipo (proposta a validar).

**Origem:** RF-04 antigo;

### RF-05 — Mapear explicitamente uma coluna de origem para uma coluna canônica

**O usuário deve conseguir associar uma coluna original a exatamente um destino canônico e, opcionalmente, aplicar uma regra de transformação ao valor durante o mapeamento.**

```q
source cic17 = csv("data/cic17/*.csv") {
    separator = ","
}

source cic18 = csv("data/cic18/*.csv") {
    separator = ","
}

map cic17.tot_fwd_pkts -> fwd_pkt_count
map cic17.fwd_pkts_num -> fwd_pkt_count // erro semântico. já foi mapeado acima, não compila (se for estático), ou erro de runtime (se estiver rodando)

map cic18.tot_pkts_fwd -> fwd_pkt_count
map flow_duration -> flow_duration using us_to_ms
```

**Restrições fundamentais:**

1. O lado esquerdo refere-se a uma **coluna da fonte original**, nunca a uma coluna criada por `create`.
2. Não se pode mapear a mesma coluna original sucessivas vezes (sem encadeamento de `map`).
3. Dentro de uma transformação, **duas colunas de origem não podem ter o mesmo destino canônico**, pois haveria sobrescrita.
4. Mapeamentos duplicados ou conflitantes devem gerar aviso e não podem sobrescrever valores silenciosamente; não compila. ~~o comportamento exato após o aviso **erro** ainda precisa de decisão.~~

**Por que é necessário:** `map` é a operação central de compatibilização das três bases e substitui uma série de comandos antigos (`rename`, `cast`, `convert`, `parse`, `map_values`) que fariam a DSL crescer desnecessariamente.

**Origem:** RF-05, RF-08, RF-09, RF-20, RF-21, RF-28 antigos; 

### RF-06 — Definir e reutilizar regras de transformação (`rule`)

**A linguagem deve permitir escrever operações sobre valores por meio de** `rule`**, com sintaxe de expressões e condições inspirada em Python, mas com blocos** `{}`**.** Regras aplicadas via `map ... using` recebem implicitamente o valor corrente em `value`; na versão mínima, não recebem outro argumento.

```q
rule us_to_ms {
    if value == None {
        return None
    }
    return str(number(value) / 1000)
}
```

**Por que é necessário:** conversão de unidade, normalização de labels, ajustes de texto e tratamento específico de um valor passam a ser casos de uma única operação (`rule`), e não dezenas de palavras-chave distintas.

**Limites:** `number` e `str` representam operações temporárias dentro da regra; as células continuam textuais no dataset produzido. `return` foi escolhido **provisoriamente** para tornar o exemplo legível — (ver se return é necessário e como vai ser a atribuição a `value`.) 

Sugestão de implementação: gerar um script em linguagem dinâmica (python ou bash) para executar a regra. Regra pode ser Pythonica. Primeira versão pode ser em Python. Versões posteriores podem ter implementação nativa.

**Origem:** RF-19 antigo e consolidação de RF-09, RF-16, RF-17 e RF-21; 

### RF-07 — Criar coluna calculada após os mapeamentos (`create`)

**O UniQL deve permitir criar uma coluna de saída a partir de colunas já mapeadas, aplicando uma regra.** Na primeira versão, o caso necessário é **uma regra binária**, com dois campos como entradas.

```q
rule sum_counts(left, right) {
    if left == None or right == None {
        return None
    }
    return string(number(left) + number(right))
}

rule rand_rule() {
    return string(rand_int())
}

create total_pkt_count using sum_counts(fwd_pkt_count, bwd_pkt_count)
create total_count using rand_rule()
```

**Restrições:** `create` ocorre depois de `map` das colunas operandas;  o campo criado integra a saída final; o nome criado não pode colidir com uma coluna do dataset original nem com outro campo já criado/mapeado; uma coluna criada não pode depois ser utilizada como origem de `map`.

**Por que é necessário:** alguns atributos precisam ser calculados (por exemplo, contagens totais) mesmo quando não estão fisicamente presentes em uma das fontes. Isso cobre o caso relevante sem manter a primitiva `derive` ou uma operação `concat` genérica.

**Origem:** RF-18 + RF-19 antigos;

### RF-08 — Unificar ausência de valor como `None`

**A runtime deve representar internamente as formas usuais de ausência (**`NaN`**,** `NULL`**,** `undefined`**) como** `None` **antes de disponibilizar valores às regras.** Os campos permanecem strings quando presentes; `None` representa ausência.

**Por que é necessário:** regras precisam enxergar uma representação consistente para tratar valores ausentes sem cada programador escrever variações da mesma verificação.

**Limites:** `0` é um valor válido; `-1` ou outros sentinelas não são automaticamente interpretados como ausência. `Inf` não recebe tratamento global adicional nesta versão; se uma fonte tiver esse valor, seu comportamento poderá ser declarado em uma regra de `map` e precisará ser testado.

**Origem:** RF-15 + parte dos RF-16/RF-17 antigos;

### ~~RF-09 — Descartar da saída colunas não selecionadas~~

~~**Por padrão, somente as colunas que pertencem ao schema e foram resolvidas por mapeamento ou criadas por**~~ `create` ~~**devem integrar a saída.** As demais colunas da fonte não são copiadas para o resultado.~~

~~**Por que é necessário:** é a regra *drop by default*; elimina a necessidade de listar~~ `Flow ID`~~, IPs, timestamps e dezenas de atributos não utilizados.~~

~~**Limite:** um comando~~ `drop` ~~explícito pode ser considerado mera documentação opcional mais tarde, mas **não é necessário no protótipo mínimo**.~~

~~**Origem:** RF-10 + RF-11 antigos;~~ 

### RF-10 — Exportar resultados harmonizados -> não é prioritário

**O usuário deve poder escolher exportar um único CSV contendo as linhas das origens harmonizadas ou arquivos separados por origem, todos com o mesmo conjunto e ordem de colunas canônicas.**

```q
export unified to "output/unificado.csv"
export unified separately to "output/por_origem/"
```

**Por que é necessário:** permite tanto treinar com múltiplos datasets quanto preservar conjuntos independentes para experimentos cross-dataset. Não é necessária uma operação genérica de concatenação no programa.

**Limite:** os nomes exatos dessas construções são protótipos, não gramática aprovada. Excluem formatação avançada de números/datas e `datetime_format`.

**Origem:** RF-26 + RF-31; RF-24 removido;

### RF-11 — Emitir avisos e log básico da execução

**A ferramenta deve registrar avisos/ocorrências relevantes durante a leitura e transformação**, especialmente colisões de nomes, duplicatas e mapeamentos conflitantes. Isso é comportamento da ferramenta, **não** uma instrução `report` em `.q` nem um JSON de proveniência exigido do programa.

**Por que é necessário:** ajuda a detectar erros reais sem criar uma linguagem de auditoria adicional.

**Origem:** RF-25 + RF-27 + RF-28 anteriores, reduzidos;

### RF-12 — Executar uma prévia de 100 registros

**Antes do processamento completo, a runtime deve conseguir testar o programa sobre uma amostra/primeiros 100 registros e apresentar ocorrências relevantes.** Esta capacidade pode ser implementada automaticamente pela runtime ou pela CLI, sem criar a palavra-chave `preview` no `.q`.

**Por que é necessário:** validações rápidas são úteis antes de percorrer milhões de linhas do LycoS.

**Limite:** a prévia **não prova** que todas as linhas do dataset completo serão processadas sem erro; só exercita uma pequena parcela.

$ uniql . --preview=100

ou 

$ uniql folder/ --preview=100

**Origem:** RF-29;

---



FILL:

```
fill column1 using zeroes() // rule zeroes por exemplo pode ser nativa. fill vai preencher valores vazios com zero, por exemplo. quando apareceu no map (automap true, não precisou de map explicito. mas existem linhas (rows) vazios pra essa coluna e queremos preencher. entao precisa da regra fill)
```

## 3. Operações antigas excluídas ou incorporadas


| RF anterior | Destino da revisão | Por quê                                                                                                 |
| ----------- | ------------------ | ------------------------------------------------------------------------------------------------------- |
| 01 + 02     | RF-01              | CSV e conjunto de arquivos são a mesma responsabilidade de entrada.                                     |
| 03          | RF-02              | `snake_case` é padrão; sem comando `trim` separado.                                                     |
| 04          | RF-04              | `automap = True` simples, apenas igualdade normalizada.                                                 |
| 05          | RF-05              | `map` permanece com restrições explícitas.                                                              |
| 06 + 07     | RF-03              | Schema sem tipos declarados, unidades, `optional` ou `target`.                                          |
| 08 + 09     | RF-05/06           | Sem `cast` ou `convert`; programação da conversão dentro de `rule`.                                     |
| 10 + 11     | RF-09              | `drop_unmapped` como comportamento padrão elimina a necessidade de `drop` explícito.                    |
| 12 + 13     | RF-02/RF-01        | Sem `deduplicate columns` ou comando `has_column`; variantes aceitas pela estrutura de origem e avisos. |
| 14          | Excluído           | Sem operação `drop_rows`/SQL-like por enquanto.                                                         |
| 15          | RF-08              | Somente `None` como marcador comum; sem catálogo genérico de sentinelas.                                |
| 16 + 17     | RF-06/08           | Sem `replace`/`fill` como comandos independentes nesta versão mínima.                                   |
| 18          | RF-07              | `derive` passa a `create`.                                                                              |
| 19          | RF-06/07           | Rules para transformação de valores e criação de campo calculado.                                       |
| 20 + 21     | RF-05/06           | Datas e labels, quando necessárias, são tratadas por regras durante `map`.                              |
| 22          | RF-03              | `required` pertence ao schema; sem comando `require` adicional.                                         |
| 23          | Excluído           | Sem `assert`.                                                                                           |
| 24          | RF-10              | Sem `concat_rows`; exportação pode ser unificada ou por origem.                                         |
| 25 + 27     | RF-11              | Apenas log básico da runtime; sem JSON/report/proveniência como DSL.                                    |
| 26 + 31     | RF-10              | Saída em CSV unificado ou arquivos separados.                                                           |
| 28          | RF-02/05/11        | Colisões: identificadores distinguíveis + aviso; sem opção `on_mapping_conflict`.                       |
| 29          | RF-12              | Prévia de 100 na runtime, sem keyword obrigatória.                                                      |
| 30          | Excluído           | Profiling não faz parte do escopo mínimo.                                                               |


Também ficam fora do núcleo: `MASK`, `REDUCE`, `validate`, tipos semânticos, classificadores de ML e seleção automática de features. **Machine Learning entra posteriormente apenas como forma de validação/aplicação dos datasets harmonizados; não é objetivo do UniQL provar que toda harmonização melhora desempenho.**

## 4. Pontos realmente abertos

1. `fill` **depois de** `map`**:** há anotações que o consideram necessário, mas outras pedem remover RF-16/RF-17 e realizar as alterações somente durante o mapeamento. **Proposta nesta v0.2:** não criar um RF nem um comando `fill` até decidirmos.
2. **Duplicatas:** aparece a possibilidade de manter a primeira, concatenar colunas ou numerá-las com avisos.
3. `rule` **e parâmetros:** a regra de `map` recebe somente `value` implícito; a de `create` recebe dois campos. Ainda é preciso decidir a sintaxe definitiva, inclusive se funções auxiliares com parâmetros constantes serão aceitas.
4. **Saída da** `rule`**:** `return` ou será atribuição a `value`? O exemplo usa `return` apenas como opção provisória.
5. **Conflitos de mapeamento:**  Vai dar avisos, mas falamos que não terá sobrescrita. Precisamos decidir se o processamento para ou apenas ignora o segundo mapeamento em conflito; **em nenhuma hipótese deve sobrescrever silenciosamente**.
6. **Obrigatoriedade:** `required` indica coluna obrigatória, mas ainda falta fechar a política quando a fonte não tem como produzi-la; não introduzir `assert` ou `require` separado antes disso.
7. **Semântica exata de** `snake_case`**:** formalizar como resolver espaços, pontuação e colisões sem oferecer uma primitiva `trim` genérica.

