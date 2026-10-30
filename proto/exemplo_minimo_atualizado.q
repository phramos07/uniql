# UniQL — protótipo mínimo revisado (.q)
# NÃO executável. A sintaxe ainda precisa ser validada
# Só demonstra operações dos requisitos funcionais v0.2.

config {
    automap = True
}

# snake_case e drop de colunas sem mapeamento são padrões da linguagem.
# Todos os campos lidos/escritos são strings (ou None).
# O separador é a única configuração de CSV explicitada neste exemplo.

source cic17 = csv("data/CIC-IDS-2017/MachineLearningCVE/*.csv") {
    separator = ","
}

source cse18 = csv("data/CSE-CIC-IDS2018/Processed Traffic Data for ML Algorithms/*.csv") {
    separator = ","
}

source lycos18 = csv("data/LycoS-Unicas-IDS2018.csv") {
    separator = ","
}

schema unified {
    required flow_duration
    required fwd_pkt_count
    required bwd_pkt_count
    required label
    total_pkt_count
}

# Em map ... using, `value` representa o valor da coluna original.
# `number()` converte temporariamente para realizar a conta.
# O retorno volta a ser string (ou None).
rule duration_us_to_ms {
    if value == None {
        return None
    }
    return str(number(value) / 1000)
}

rule normalize_label {
    if value == None {
        return None
    }
    if lower(value) == "benign" {
        return "benign"
    }
    return "attack"
}

# Em create, a regra recebe duas colunas já mapeadas.
rule add_counts(a, b) {
    if a == None or b == None {
        return None
    }
    return str(number(a) + number(b))
}

transform cic17 -> unified {
    map flow_duration -> flow_duration using duration_us_to_ms
    map total_fwd_packets -> fwd_pkt_count
    map total_backward_packets -> bwd_pkt_count
    map label -> label using normalize_label

    create total_pkt_count using add_counts(fwd_pkt_count, bwd_pkt_count)
}

transform cse18 -> unified {
    map flow_duration -> flow_duration using duration_us_to_ms
    map tot_fwd_pkts -> fwd_pkt_count
    map tot_bwd_pkts -> bwd_pkt_count
    map label -> label using normalize_label

    create total_pkt_count using add_counts(fwd_pkt_count, bwd_pkt_count)
}

transform lycos18 -> unified {
    map flow_duration -> flow_duration using duration_us_to_ms
    map fwd_pkt_cnt -> fwd_pkt_count
    map bwd_pkt_cnt -> bwd_pkt_count
    map label -> label using normalize_label

    create total_pkt_count using add_counts(fwd_pkt_count, bwd_pkt_count)
}

# Unificação por linhas é opção de exportação, não comando concat_rows.
export unified to "output/nids_unificado.csv"
export unified separately to "output/por_origem/"

# Avisos de mapeamento/duplicatas e prévia de 100 linhas pertencem à runtime.
# Não há comandos report, preview, assert, replace, fill, cast ou convert.
