# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/06_amrfinderplus.ipynb.

# %% auto 0
__all__ = ['process_amrfinderplus_data', 'process_amrfinderplus_data_from_cli']

# %% ../nbs/06_amrfinderplus.ipynb 2
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
from . import core

# %% ../nbs/06_amrfinderplus.ipynb 6
def process_amrfinderplus_data(
    input_path: str,
    output_path: str = "./output.tsv",
    replace_header: str = None,
    filter_columns: str = None,
    add_header: str = None,
):
    """
    Command-line interface for processing amrfinderplus data.

    This function sets up an argument parser to handle command-line arguments for processing amrfinderplus data files.
    It supports specifying input and output file paths, replacing headers, filtering columns, and handling the presence or absence of headers in the input file.

    Arguments:
        input_path (str): Path to the input file.
        output_path (str): Path to the output file (default: './output.tsv').
        replace_header (str): Header to replace the existing header (default: None).
        filter_columns (str): Columns to filter from the header (default: None).
        header_exists (int): Indicates if the header exists in the input file (default: 1).
        add_header (str): Header to add if the header does not exist in the input file (default: None).
    """

    df = core.DataFrame()
    df.import_data(input_path, file_type="tsv", add_header=add_header)

    # print(df.df.columns)
    def concatenate_vector(x, sep=","):
        return ",".join([str(i) for i in x])

    df_agg = df.df.apply(concatenate_vector, axis=0)
    df.df = df_agg.to_frame().T
    if replace_header:
        df.rename_header(replace_header)

    if filter_columns:
        df.filter_columns(filter_columns)

    # df.show()

    df.export_data(output_path, file_type="tsv")


@call_parse
def process_amrfinderplus_data_from_cli(
    input_path: str,
    output_path: str = "./output.tsv",
    replace_header: str = None,
    filter_columns: str = None,
    add_header: str = None,
):
    process_amrfinderplus_data(
        input_path, output_path, replace_header, filter_columns, add_header
    )
