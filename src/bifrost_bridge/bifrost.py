from __future__ import annotations

from pathlib import Path

import pandas as pd

from bifrost_bridge._cli import build_parser
from bifrost_bridge.amrfinderplus import process_amrfinderplus_data
from bifrost_bridge.bracken import process_bracken_data
from bifrost_bridge.fastp import process_fastp_data
from bifrost_bridge.mlst import process_mlst_data
from bifrost_bridge.plasmidfinder import process_plasmidfinder_data
from bifrost_bridge.pmlst import process_pmlst_data
from bifrost_bridge.quast import process_quast_data
from bifrost_bridge.rmlst import process_rmlst_data
from bifrost_bridge.shovill import process_shovill_data
from bifrost_bridge.ssiamb import process_ssiamb_data


def _write_header_if_empty(path: str, header: str) -> None:
    output_file = Path(path)
    if output_file.stat().st_size == 0:
        output_file.write_text(header, encoding="utf-8")


def process_qc_data(
    mlst_path: str | None = None,
    fastp_path: str | None = None,
    quast_path: str | None = None,
    plasmidfinder_path: str | None = None,
    bracken_path: str | None = None,
    amrfinder_path: str | None = None,
    amrfinder_version_path: str | None = None,
    pmlst_path: str | None = None,
    rmlst_path: str | None = None,
    shovill_path: str | None = None,
    ssiamb_path: str | None = None,
    combine_output: bool = True,
    output_path: str = "./output.tsv",
) -> None:
    if mlst_path is not None:
        if not Path(mlst_path).exists():
            raise FileNotFoundError(f"File not found: {mlst_path}")
        process_mlst_data(
            input_path=mlst_path,
            output_path="parsed_mlst.tsv",
            replace_header=None,
            remove_sampleid=True,
            add_header="SampleID, MLST_Species, MLST_ST, MLST_Alleles",
            combine_alleles=True,
        )

    if fastp_path is not None:
        if not Path(fastp_path).exists():
            raise FileNotFoundError(f"File not found: {fastp_path}")
        process_fastp_data(
            input_path=fastp_path,
            output_path="parsed_fastp.tsv",
            filter_columns="summary£before_filtering£total_reads, summary£before_filtering£read1_mean_length, summary£before_filtering£read2_mean_length, summary£after_filtering£total_reads, summary£after_filtering£read1_mean_length, summary£after_filtering£read2_mean_length, filtering_result£low_quality_reads, filtering_result£too_many_N_reads, filtering_result£too_short_reads, filtering_result£too_long_reads, duplication£rate, adapter_cutting£adapter_trimmed_reads, adapter_cutting£adapter_trimmed_bases, read1_before_filtering£total_cycles, read1_after_filtering£total_cycles, read2_before_filtering£total_cycles, read2_after_filtering£total_cycles",
            replace_header="fastp_Before_Filtering_Total_Reads,fastp_Before_Filtering_Read1_Mean_Length,fastp_Before_Filtering_Read2_Mean_Length,fastp_After_Filtering_Total_Reads,fastp_After_Filtering_Read1_Mean_Length,fastp_After_Filtering_Read2_Mean_Length,fastp_Low_Quality_Reads,fastp_Too_Many_N_Reads,fastp_Too_Short_Reads,fastp_Too_Long_Reads,fastp_Duplication_Rate,fastp_Adapter_Trimmed_Reads,fastp_Adapter_Trimmed_Bases,fastp_Read1_Before_Filtering_Total_Cycles,fastp_Read1_After_Filtering_Total_Cycles,fastp_Read2_Before_Filtering_Total_Cycles,fastp_Read2_After_Filtering_Total_Cycles",
        )

    if quast_path is not None:
        if not Path(quast_path).exists():
            raise FileNotFoundError(f"File not found: {quast_path}")
        process_quast_data(
            input_path=quast_path,
            output_path="parsed_quast.tsv",
            filter_columns="# contigs, Largest contig, Total length, GC (%), N50, N90, L50, L90",
            replace_header="Quast_Contigs,Quast_Largest_Contig,Quast_Total_Length,Quast_GC_Pct,Quast_N50,Quast_N90,Quast_L50,Quast_L90",
            transpose=True,
        )
        _write_header_if_empty(
            "parsed_quast.tsv",
            "Quast_Contigs\tQuast_Largest_Contig\tQuast_Total_Length\tQuast_GC_Pct\tQuast_N50\tQuast_N90\tQuast_L50\tQuast_L90",
        )

    if plasmidfinder_path is not None:
        if not Path(plasmidfinder_path).exists():
            raise FileNotFoundError(f"File not found: {plasmidfinder_path}")
        process_plasmidfinder_data(
            input_path=plasmidfinder_path,
            output_path="parsed_plasmidfinder.tsv",
            filter_columns="Database,Plasmid,Identity,Query / Template length,Contig",
            replace_header="PFInder_Database,PFinder_Plasmid,PFinder_Identity,PFinder_Coverage,PFinder_Contig",
            convert_coverage=True,
            filter_contig=True,
        )
        _write_header_if_empty(
            "parsed_plasmidfinder.tsv",
            "PFInder_Database\tPFinder_Plasmid\tPFinder_Identity\tPFinder_Coverage\tPFinder_Contig",
        )

    if bracken_path is not None:
        if not Path(bracken_path).exists():
            raise FileNotFoundError(f"File not found: {bracken_path}")
        process_bracken_data(
            input_path=bracken_path,
            output_path="parsed_bracken.tsv",
            replace_header="Bracken_Species,Bracken_Species_Pct,Bracken_Species1,Bracken_Species1_Pct,Bracken_Species2,Bracken_Species2_Pct,Bracken_Unclassified,Bracken_Unclassified_Pct",
        )

    if amrfinder_path is not None:
        if not Path(amrfinder_path).exists():
            raise FileNotFoundError(f"File not found: {amrfinder_path}")
        process_amrfinderplus_data(
            input_path=amrfinder_path,
            output_path="parsed_amrfinder.tsv",
            filter_columns="Contig id,Start,Stop,Strand,Gene symbol,Sequence name,Subclass,% Coverage of reference sequence,% Identity to reference sequence",
            replace_header="AMR_ContigID,AMR_Start,AMR_Stop,AMR_Strand,AMR_ElementSymbol,AMR_ElementName,AMR_Subclass,AMR_Coverage,AMR_Identity",
        )
        _write_header_if_empty(
            "parsed_amrfinder.tsv",
            "AMR_ContigID\tAMR_Start\tAMR_Stop\tAMR_Strand\tAMR_ElementSymbol\tAMR_ElementName\tAMR_Subclass\tAMR_Coverage\tAMR_Identity",
        )

    if pmlst_path is not None:
        if not Path(pmlst_path).exists():
            raise FileNotFoundError(f"File not found: {pmlst_path}")
        process_pmlst_data(
            input_path=pmlst_path,
            output_path="parsed_pmlst.tsv",
            replace_header="pMLST_plasmids,pMLST_IncF,pMLST_IncI1,pMLST_IncA/C,pMLST_IncHI1,pMLST_IncHI2,pMLST_IncN,pMLST_summary",
        )
        _write_header_if_empty(
            "parsed_pmlst.tsv",
            "pMLST_plasmids\tpMLST_IncF\tpMLST_IncI1\tpMLST_IncA/C\tpMLST_IncHI1\tpMLST_IncHI2\tpMLST_IncN\tpMLST_summary",
        )

    if rmlst_path is not None:
        if not Path(rmlst_path).exists():
            raise FileNotFoundError(f"File not found: {rmlst_path}")
        process_rmlst_data(input_path=rmlst_path, output_path="parsed_rmlst.tsv", parsed=True)
        _write_header_if_empty("parsed_rmlst.tsv", "rMLST_match\trMLST_support")

    if shovill_path is not None:
        if not Path(shovill_path).exists():
            raise FileNotFoundError(f"File not found: {shovill_path}")
        process_shovill_data(
            input_path=shovill_path, output_path="parsed_shovill.tsv", average_coverage=True
        )

    if ssiamb_path is not None:
        if not Path(ssiamb_path).exists():
            raise FileNotFoundError(f"File not found: {ssiamb_path}")
        process_ssiamb_data(
            input_path=ssiamb_path,
            output_path="parsed_ssiamb.tsv",
            replace_header="ssiamb_count",
            filter_columns="ambiguous_snv_count",
        )
        _write_header_if_empty("parsed_ssiamb.tsv", "ssiamb_count")

    if combine_output:
        output_files = []
        if mlst_path is not None:
            output_files.append("parsed_mlst.tsv")
        if fastp_path is not None:
            output_files.append("parsed_fastp.tsv")
        if quast_path is not None:
            output_files.append("parsed_quast.tsv")
        if plasmidfinder_path is not None:
            output_files.append("parsed_plasmidfinder.tsv")
        if amrfinder_path is not None:
            output_files.append("parsed_amrfinder.tsv")
        if amrfinder_version_path is not None:
            output_files.append(amrfinder_version_path)
        if bracken_path is not None:
            output_files.append("parsed_bracken.tsv")
        if pmlst_path is not None:
            output_files.append("parsed_pmlst.tsv")
        if rmlst_path is not None:
            output_files.append("parsed_rmlst.tsv")
        if shovill_path is not None:
            output_files.append("parsed_shovill.tsv")
        if ssiamb_path is not None:
            output_files.append("parsed_ssiamb.tsv")

        combined_df = pd.concat([pd.read_csv(file, sep="\t") for file in output_files], axis=1)
        combined_df.to_csv(output_path, sep="\t", index=False)


def process_qc_data_from_cli() -> None:
    parser = build_parser(
        "Process and combine QC outputs from supported tools.",
        [
            {"names": ["--mlst-path"], "kwargs": {"default": None}},
            {"names": ["--fastp-path"], "kwargs": {"default": None}},
            {"names": ["--quast-path"], "kwargs": {"default": None}},
            {"names": ["--plasmidfinder-path"], "kwargs": {"default": None}},
            {"names": ["--bracken-path"], "kwargs": {"default": None}},
            {"names": ["--amrfinder-path"], "kwargs": {"default": None}},
            {"names": ["--amrfinder-version-path"], "kwargs": {"default": None}},
            {"names": ["--pmlst-path"], "kwargs": {"default": None}},
            {"names": ["--rmlst-path"], "kwargs": {"default": None}},
            {"names": ["--shovill-path"], "kwargs": {"default": None}},
            {"names": ["--ssiamb-path"], "kwargs": {"default": None}},
            {
                "names": ["--no-combine-output"],
                "kwargs": {"action": "store_false", "dest": "combine_output"},
            },
            {"names": ["--output-path"], "kwargs": {"default": "./output.tsv"}},
        ],
    )
    args = parser.parse_args()
    process_qc_data(**vars(args))
