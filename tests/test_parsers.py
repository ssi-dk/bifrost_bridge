import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

from bifrost_bridge.amrfinderplus import process_amrfinderplus_data
from bifrost_bridge.bifrost import process_qc_data
from bifrost_bridge.bracken import process_bracken_data
from bifrost_bridge.fastp import process_fastp_data
from bifrost_bridge.mlst import process_mlst_data
from bifrost_bridge.plasmidfinder import process_plasmidfinder_data
from bifrost_bridge.pmlst import process_pmlst_data
from bifrost_bridge.quast import process_quast_data
from bifrost_bridge.rmlst import process_rmlst_data
from bifrost_bridge.shovill import process_shovill_data
from bifrost_bridge.ssiamb import process_ssiamb_data


TEST_DATA = Path(__file__).resolve().parent.parent / "test_data"


def read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t")


def test_mlst_processes_and_combines_alleles(tmp_path: Path) -> None:
    output_path = tmp_path / "mlst.tsv"
    process_mlst_data(
        str(TEST_DATA / "mlst_report.tabular"),
        str(output_path),
        add_header="SampleID, Species, ST, Alleles",
        combine_alleles=True,
    )
    df = read_tsv(output_path)
    assert df.columns.tolist() == ["SampleID", "Species", "ST", "Alleles"]
    assert df.iloc[0]["Species"] == "campylobacter"
    assert "aspA(1)" in df.iloc[0]["Alleles"]


def test_fastp_flattens_json(tmp_path: Path) -> None:
    output_path = tmp_path / "fastp.tsv"
    process_fastp_data(
        str(TEST_DATA / "TestSample2.json"),
        str(output_path),
        filter_columns="summary£fastp_version, summary£before_filtering£total_reads",
        replace_header="fastp_version,total_reads",
    )
    df = read_tsv(output_path)
    assert df.iloc[0]["fastp_version"] == "0.23.4"
    assert int(df.iloc[0]["total_reads"]) == 4369610


def test_quast_transposes_output(tmp_path: Path) -> None:
    output_path = tmp_path / "quast.tsv"
    process_quast_data(
        str(TEST_DATA / "quast.tsv"),
        str(output_path),
        filter_columns="# contigs, Largest contig, Total length",
    )
    df = read_tsv(output_path)
    assert df.columns.tolist() == ["# contigs", "Largest contig", "Total length"]
    assert int(df.iloc[0]["# contigs"]) == 365


def test_plasmidfinder_converts_coverage_and_contig(tmp_path: Path) -> None:
    output_path = tmp_path / "plasmidfinder.tsv"
    process_plasmidfinder_data(
        str(TEST_DATA / "plasmidfinder.tsv"),
        str(output_path),
        filter_columns="Plasmid,Query / Template length,Contig",
        replace_header="plasmid,coverage,contig",
        convert_coverage=True,
        filter_contig=True,
    )
    df = read_tsv(output_path)
    cov = df.iloc[0]["coverage"]
    assert all(float(i) == 100.0 for i in cov.split("|"))
    assert df.iloc[0]["contig"].startswith("contig00135")


def test_amrfinderplus_filters_columns(tmp_path: Path) -> None:
    output_path = tmp_path / "amr.tsv"
    process_amrfinderplus_data(
        str(TEST_DATA / "amrfinderplus.tsv"),
        str(output_path),
        filter_columns="Contig id,Gene symbol,Subclass",
        replace_header="contig,gene,subclass",
    )
    df = read_tsv(output_path)
    assert df.iloc[0]["gene"].split("|")[0] == "blaOXA-193"
    assert df.iloc[0]["subclass"].split("|")[0] == "BETA-LACTAM"

    process_amrfinderplus_data(
        str(TEST_DATA / "amrfinderplus_long_example.tsv"),
        str(output_path),
        filter_columns="Contig id,Element symbol,Subclass",
        replace_header="contig,gene,subclass",
    )
    df = read_tsv(output_path)
    assert len(df) == 1
    row = df.iloc[0]
    assert row["gene"].split("|")[0] == "gyrA_A70A"
    assert row["subclass"].split("|")[:5] == ["QUINOLONE"] * 4 + [""]


def test_bracken_summarizes_top_species(tmp_path: Path) -> None:
    output_path = tmp_path / "bracken.tsv"
    process_bracken_data(str(TEST_DATA / "bracken_krakenreport.txt"), str(output_path))
    df = read_tsv(output_path)
    assert "Actinobacillus pleuropneumoniae" in df.iloc[0]["species1_name"]
    assert float(df.iloc[0]["unclassified_pct"]) == 6.15


def test_pmlst_passthrough(tmp_path: Path) -> None:
    output_path = tmp_path / "pmlst.tsv"
    process_pmlst_data(
        str(TEST_DATA / "simple_output.tsv"),
        str(output_path),
        replace_header="pMLST_plasmids,pMLST_IncF,pMLST_IncI1,pMLST_IncA/C,pMLST_IncHI1,pMLST_IncHI2,pMLST_IncN,pMLST_summary",
    )
    df = read_tsv(output_path)
    assert "incf" in df.iloc[0]["pMLST_summary"].lower()


def test_rmlst_json_extracts_taxon_prediction(tmp_path: Path) -> None:
    output_path = tmp_path / "rmlst.tsv"
    process_rmlst_data(str(TEST_DATA / "rmlst.json"), str(output_path), parsed=False)
    df = read_tsv(output_path)
    assert "support" in df.columns
    assert not df.empty


def test_shovill_extracts_average_coverage(tmp_path: Path) -> None:
    output_path = tmp_path / "shovill.tsv"
    process_shovill_data(str(TEST_DATA / "2506W58844.txt"), str(output_path))
    df = read_tsv(output_path)
    assert df.iloc[0]["Average_Coverage"] == 48.254


def test_ssiamb_filters_count(tmp_path: Path) -> None:
    output_path = tmp_path / "ssiamb.tsv"
    process_ssiamb_data(
        str(TEST_DATA / "ssiamb.tsv"),
        str(output_path),
        filter_columns="ambiguous_snv_count",
        replace_header="ssiamb_count",
    )
    df = read_tsv(output_path)
    assert int(df.iloc[0]["ssiamb_count"]) == 5388


def test_qc_combines_selected_outputs(tmp_path: Path) -> None:
    cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        process_qc_data(
            mlst_path=str(TEST_DATA / "mlst_report.tabular"),
            quast_path=str(TEST_DATA / "quast.tsv"),
            ssiamb_path=str(TEST_DATA / "ssiamb.tsv"),
            output_path="combined.tsv",
        )
        df = read_tsv(tmp_path / "combined.tsv")
        assert "MLST_Species" in df.columns
        assert "Quast_Total_Length" in df.columns
        assert "ssiamb_count" in df.columns
    finally:
        os.chdir(cwd)


def test_python_module_help() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "src")
    result = subprocess.run(
        [sys.executable, "-m", "bifrost_bridge", "--help"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0
    assert "--mlst_path" in result.stdout
