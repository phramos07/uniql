#!/usr/bin/env python3
"""
gerar_samples_nids.py

Gera 3 amostras de 100 linhas, uma para cada dataset:
- CIC-IDS2017
- CSE-CIC-IDS2018
- LycoS-Unicas-IDS2018

O script foi pensado para arquivos muito grandes. Ele NÃO carrega o CSV inteiro
na memória. Em vez disso, usa reservoir sampling (Algorithm R), mantendo apenas
100 linhas na RAM enquanto percorre o arquivo uma única vez.

Isso é especialmente importante para o LycoS-Unicas-IDS2018, que possui
milhões de linhas e vários GB.

Ambiente esperado:
WSL/Linux, com os datasets em:
    /mnt/c/Users/Felipe/Desktop/TCC/Datasets originais

Se a sua pasta estiver em outro lugar, altere apenas BASE_DIR abaixo.
"""

from pathlib import Path
import random
import sys
import time


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

BASE_DIR = Path("/mnt/c/Users/Felipe/Desktop/TCC/Datasets originais")

# Um CSV representativo do CIC-IDS2017
CIC_2017 = (
    BASE_DIR
    / "CIC-IDS-2017"
    / "MachineLearningCVE"
    / "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv"
)

# Um CSV representativo do CSE-CIC-IDS2018
CSE_CIC_2018 = (
    BASE_DIR
    / "CSE-CIC-IDS2018"
    / "Processed Traffic Data for ML Algorithms"
    / "Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv"
)

# CSV único do LycoS-Unicas-IDS2018
LYCOS_2018 = BASE_DIR / "LycoS-Unicas-IDS2018.csv"

# Pasta onde os samples serão criados
OUTPUT_DIR = BASE_DIR / "Samples_100"

# Quantidade de registros por sample
SAMPLE_SIZE = 100

# Seed fixa = mesma amostra se o script for executado novamente.
# Isso ajuda na reprodutibilidade do TCC.
RANDOM_SEED = 42

# Exibe progresso a cada N linhas do arquivo grande.
PROGRESS_EVERY = 1_000_000


# ============================================================================
# AMOSTRAGEM
# ============================================================================

def reservoir_sample_csv(
    input_path: Path,
    output_path: Path,
    sample_size: int = 100,
    seed: int = 42,
) -> None:
    """
    Seleciona 'sample_size' registros uniformemente ao acaso usando
    reservoir sampling.

    Complexidade:
        Tempo:   O(N), pois cada linha é visitada uma vez.
        Memória: O(k), sendo k = sample_size.

    O processamento é feito em modo binário de propósito:
    - evita problemas de encoding nos labels;
    - é mais rápido;
    - preserva os bytes originais do CSV;
    - não precisa interpretar 78/80 colunas de milhões de registros.

    Os datasets usados neste TCC possuem um registro CSV por linha física.
    """

    if not input_path.exists():
        raise FileNotFoundError(
            f"\nArquivo não encontrado:\n{input_path}\n"
            "Confira o caminho configurado no início do script."
        )

    rng = random.Random(seed)
    reservoir = []

    valid_rows_seen = 0
    repeated_headers_skipped = 0
    blank_lines_skipped = 0

    file_size_gb = input_path.stat().st_size / (1024 ** 3)

    print("\n" + "=" * 78)
    print(f"Lendo: {input_path}")
    print(f"Tamanho: {file_size_gb:.2f} GB")
    print(f"Objetivo: escolher {sample_size} linhas aleatórias")
    print("=" * 78)

    start = time.time()

    with input_path.open("rb") as source:
        header = source.readline()

        if not header:
            raise ValueError(f"O arquivo está vazio: {input_path}")

        normalized_header = header.rstrip(b"\r\n")

        for physical_line_number, line in enumerate(source, start=2):
            normalized_line = line.rstrip(b"\r\n")

            # Ignora linhas completamente vazias.
            if not normalized_line:
                blank_lines_skipped += 1
                continue

            # Alguns arquivos do CSE-CIC-IDS2018 possuem cabeçalhos repetidos
            # no meio do CSV. Não queremos que um desses cabeçalhos vire
            # "registro" da amostra.
            if normalized_line == normalized_header:
                repeated_headers_skipped += 1
                continue

            valid_rows_seen += 1

            # Primeiras k linhas válidas entram diretamente no reservatório.
            if len(reservoir) < sample_size:
                reservoir.append(line)
            else:
                # Algorithm R:
                # cada registro já visto tem a mesma probabilidade k/N
                # de pertencer ao reservatório final.
                j = rng.randrange(valid_rows_seen)

                if j < sample_size:
                    reservoir[j] = line

            if (
                PROGRESS_EVERY
                and valid_rows_seen % PROGRESS_EVERY == 0
            ):
                elapsed = time.time() - start
                print(
                    f"  {valid_rows_seen:,} registros processados "
                    f"({elapsed:.1f} s)"
                )

    if valid_rows_seen < sample_size:
        raise ValueError(
            f"O arquivo possui apenas {valid_rows_seen} linhas válidas, "
            f"menos que as {sample_size} solicitadas."
        )

    # Embaralha apenas a ordem final dos 100 registros.
    # A seleção já é aleatória antes desta etapa.
    rng.shuffle(reservoir)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("wb") as destination:
        destination.write(header)

        for line in reservoir:
            destination.write(line)

    elapsed = time.time() - start
    output_mb = output_path.stat().st_size / (1024 ** 2)

    print(f"\nSample criado: {output_path}")
    print(f"Registros válidos examinados: {valid_rows_seen:,}")
    print(f"Cabeçalhos repetidos ignorados: {repeated_headers_skipped:,}")
    print(f"Linhas vazias ignoradas: {blank_lines_skipped:,}")
    print(f"Linhas salvas: {sample_size:,} + 1 cabeçalho")
    print(f"Tamanho do sample: {output_mb:.2f} MB")
    print(f"Tempo: {elapsed:.1f} s")


def main() -> int:
    datasets = [
        (
            "CIC-IDS2017",
            CIC_2017,
            OUTPUT_DIR / "sample_CIC-IDS2017_100.csv",
        ),
        (
            "CSE-CIC-IDS2018",
            CSE_CIC_2018,
            OUTPUT_DIR / "sample_CSE-CIC-IDS2018_100.csv",
        ),
        (
            "LycoS-Unicas-IDS2018",
            LYCOS_2018,
            OUTPUT_DIR / "sample_LycoS-Unicas-IDS2018_100.csv",
        ),
    ]

    print("\nGERADOR DE SAMPLES PARA O TCC")
    print(f"Pasta base: {BASE_DIR}")
    print(f"Saída: {OUTPUT_DIR}")
    print(f"Amostra por dataset: {SAMPLE_SIZE} registros")
    print(f"Seed: {RANDOM_SEED}")

    # Verificação inicial para não processar dois arquivos e só depois descobrir
    # que o terceiro caminho está errado.
    missing = [path for _, path, _ in datasets if not path.exists()]

    if missing:
        print("\nERRO: os seguintes arquivos não foram encontrados:")
        for path in missing:
            print(f"  - {path}")

        print(
            "\nAbra o script e confira BASE_DIR e os três caminhos "
            "na seção CONFIGURAÇÃO."
        )
        return 1

    for index, (name, input_path, output_path) in enumerate(datasets):
        print(f"\n[{index + 1}/3] {name}")

        # Seed diferente por dataset, mas reprodutível.
        dataset_seed = RANDOM_SEED + index

        reservoir_sample_csv(
            input_path=input_path,
            output_path=output_path,
            sample_size=SAMPLE_SIZE,
            seed=dataset_seed,
        )

    print("\n" + "=" * 78)
    print("CONCLUÍDO.")
    print("Os três arquivos para o orientador estão em:")
    print(OUTPUT_DIR)
    print("=" * 78)

    return 0


if __name__ == "__main__":
    sys.exit(main())
