# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/99_bifrost.ipynb.

# %% auto 0
__all__ = ['process_qc_data']

# %% ../nbs/99_bifrost.ipynb 2
# That export there, it makes sure this code goes into the module.

# standard libs
import os
import re

# Common to template
# add into settings.ini, requirements, package name is python-dotenv, for conda build ensure `conda config --add channels conda-forge`
import dotenv  # for loading config from .env files, https://pypi.org/project/python-dotenv/
import envyaml  # Allows to loads env vars into a yaml file, https://github.com/thesimj/envyaml
import fastcore  # To add functionality related to nbdev development, https://github.com/fastai/fastcore/
from fastcore import (
    test,
)
from fastcore.script import (
    call_parse,
)  # for @call_parse, https://fastcore.fast.ai/script
import json  # for nicely printing json and yaml
from fastcore import test

#!export
from . import core

# %% ../nbs/99_bifrost.ipynb 5
from .mlst import process_mlst_data
from .fastp import process_fastp_data
from .quast import process_quast_data
from .plasmidfinder import process_plasmidfinder_data
from .amrfinderplus import process_amrfinderplus_data
from .bracken import process_bracken_data
from .pmlst import process_pmlst_data
import pandas as pd


@call_parse
def process_qc_data(
    mlst_path: str = None,
    fastp_path: str = None,
    quast_path: str = None,
    plasmidfinder_path: str = None,
    bracken_path: str = None,
    amrfinder_path: str = None,
    pmlst_path: str = None,
    combine_output: bool = True,
    output_path: str = "./output.tsv",
):
    """
    Command-line interface for processing QC data.

    This function processes MLST, FASTP, QUAST, PlasmidFinder, and Bracken data files based on the provided command-line arguments.
    It supports specifying input file paths for MLST, FASTP, QUAST, PlasmidFinder, and Bracken data, and outputs the processed data to specified paths.

    Arguments:
        mlst_path (str): Path to the MLST input file.
        fastp_path (str): Path to the FASTP input file.
        quast_path (str): Path to the QUAST input file.
        plasmidfinder_path (str): Path to the PlasmidFinder input file.
        bracken_path (str): Path to the Bracken input file.
        amrfinder_path (str): Path to the AMRFinder input file.
        pmlst_path (str): Path to the PMLST input file.
        output_path (str): Path to the output file (default: './output.tsv').
    """
    if mlst_path is not None:
        if not os.path.exists(mlst_path):
            raise FileNotFoundError(f"File not found: {mlst_path}")
        process_mlst_data(
            input_path=mlst_path,
            output_path="parsed_mlst.tsv",
            replace_header=None,
            filter_columns="SampleID, Species, ST",
            add_header="SampleID, Species, ST, Allele",
        )

    if fastp_path is not None:
        if not os.path.exists(fastp_path):
            raise FileNotFoundError(f"File not found: {fastp_path}")
        process_fastp_data(
            input_path=fastp_path,
            output_path="parsed_fastp.tsv",
            filter_columns="summary£fastp_version, summary£sequencing, summary£before_filtering£total_reads",
            replace_header="fastp_version, sequencing, total_reads",
        )

    if quast_path is not None:
        if not os.path.exists(quast_path):
            raise FileNotFoundError(f"File not found: {quast_path}")
        process_quast_data(
            input_path=quast_path,
            output_path="parsed_quast.tsv",
            filter_columns="Assembly,# contigs (>= 0 bp), N50",
            transpose=True,
        )

    if plasmidfinder_path is not None:
        if not os.path.exists(plasmidfinder_path):
            raise FileNotFoundError(f"File not found: {plasmidfinder_path}")
        process_plasmidfinder_data(
            input_path=plasmidfinder_path,
            output_path="parsed_plasmidfinder.tsv",
        )

    if bracken_path is not None:
        if not os.path.exists(bracken_path):
            raise FileNotFoundError(f"File not found: {bracken_path}")
        process_bracken_data(
            input_path=bracken_path,
            output_path="parsed_bracken.tsv",
        )

    if amrfinder_path is not None:
        if not os.path.exists(amrfinder_path):
            raise FileNotFoundError(f"File not found: {amrfinder_path}")
        process_amrfinderplus_data(
            input_path=amrfinder_path, output_path="parsed_amrfinder.tsv"
        )

    if pmlst_path is not None:
        if not os.path.exists(pmlst_path):
            raise FileNotFoundError(f"File not found: {pmlst_path}")
        process_pmlst_data(input_path=pmlst_path, output_path="parsed_pmlst.tsv")

    if combine_output:
        # List of output files that were actually created
        output_files = []
        if mlst_path is not None:
            if os.path.getsize("parsed_mlst.tsv") > 0:
                output_files.append("parsed_mlst.tsv")
        if fastp_path is not None:
            output_files.append("parsed_fastp.tsv")
        if quast_path is not None:
            output_files.append("parsed_quast.tsv")
        if plasmidfinder_path is not None:
            output_files.append("parsed_plasmidfinder.tsv")
        if amrfinder_path is not None:
            output_files.append("parsed_amrfinder.tsv")
        if bracken_path is not None:
            output_files.append("parsed_bracken.tsv")
        if pmlst_path is not None:
            output_files.append("parsed_pmlst.tsv")

        # Read and concatenate all output files
        combined_df = pd.concat(
            [pd.read_csv(file, sep="\t") for file in output_files], axis=1
        )

        # Save the combined dataframe to the specified output path
        combined_df.to_csv(output_path, sep="\t", index=False)
