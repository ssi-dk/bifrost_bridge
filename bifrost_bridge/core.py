# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['PACKAGE_NAME', 'DEV_MODE', 'PACKAGE_DIR', 'PROJECT_DIR', 'config', 'set_env_variables', 'get_config',
           'show_project_env_vars', 'get_samplesheet', 'hello_world', 'cli', 'DataFrame', 'import_nested_json_data',
           'export_nested_json_data', 'import_nested_xml_data', 'export_nested_xml_data', 'import_data',
           'rename_header', 'filter_columns', 'filter_rows', 'export_data', 'print_header', 'show']

# %% ../nbs/00_core.ipynb 4
# Need the bifrost_bridge for a few functions, this can be considered a static var

import importlib
import importlib.util
import os

PACKAGE_NAME: str = "bifrost_bridge"  # Make sure to adjust this to your package name
DEV_MODE: bool = (
    False  # set below to override, as this is in an export block it'll be exported while the dev mode section is not
)

PACKAGE_DIR = None
try:
    spec = importlib.util.find_spec(PACKAGE_NAME)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    PACKAGE_DIR = os.path.dirname(module.__file__)
except ImportError:
    DEV_MODE = True
except AttributeError:
    DEV_MODE = True
PROJECT_DIR = os.getcwd()  # override value in dev mode
if PROJECT_DIR.endswith("nbs"):
    DEV_MODE = True
    PROJECT_DIR = os.path.split(PROJECT_DIR)[0]

# %% ../nbs/00_core.ipynb 10
# standard libs
import os
import re

# Common to template
# add into settings.ini, requirements, package name is python-dotenv, for conda build ensure `conda config --add channels conda-forge`
import dotenv  # for loading config from .env files, https://pypi.org/project/python-dotenv/
import envyaml  # Allows to loads env vars into a yaml file, https://github.com/thesimj/envyaml
import fastcore  # To add functionality related to nbdev development, https://github.com/fastai/fastcore/
import pandas  # For sample sheet manipulation
from fastcore import (
    test,
)
from fastcore.script import (
    call_parse,
)  # for @call_parse, https://fastcore.fast.ai/script

# Project specific libraries

# %% ../nbs/00_core.ipynb 13
import importlib
import importlib.util


def set_env_variables(config_path: str, overide_env_vars: bool = True) -> bool:
    # Load dot env sets environmental values from a file, if the value already exists it will not be overwritten unless override is set to True.
    # If we have multiple .env files then we need to apply the one which we want to take precedence last with overide.

    # Order of precedence: .env file > environment variables > default values
    # When developing, making a change to the config will not be reflected until the environment is restarted

    # Set the env vars first, this is needed for the card.yaml to replace ENV variables
    # NOTE: You need to adjust PROJECT_NAME to your package name for this to work, the exception is only for dev purposes
    # This here checks if your package is installed, such as through pypi or through pip install -e  [.dev] for development. If it is then it'll go there and use the config files there as your default values.
    try:
        dotenv.load_dotenv(f"{PACKAGE_DIR}/config/config.default.env", override=False)
    except Exception as e:
        print(f"Error: {PACKAGE_DIR}/config/config.default.env does not exist")
        return False

    # 2. set values from file:
    if os.path.isfile(config_path):
        dotenv.load_dotenv(config_path, override=overide_env_vars)

    return True

# %% ../nbs/00_core.ipynb 15
import importlib
import importlib.util


def get_config(config_path: str = None, overide_env_vars: bool = True) -> dict:
    if config_path is None:
        config_path = ""
    # First sets environment with variables from config_path, then uses those variables to fill in appropriate values in the config.yaml file, the yaml file is then returned as a dict
    # If you want user env variables to take precedence over the config.yaml file then set overide_env_vars to False
    set_env_variables(config_path, overide_env_vars)

    config: dict = envyaml.EnvYAML(
        os.environ.get(
            "CORE_YAML_CONFIG_FILE", f"{PACKAGE_DIR}/config/config.default.yaml"
        ),
        strict=False,
    ).export()

    return config

# %% ../nbs/00_core.ipynb 17
# create a os.PathLike object
config = get_config(os.environ.get("CORE_CONFIG_FILE", ""))

# %% ../nbs/00_core.ipynb 19
def show_project_env_vars(config: dict) -> None:
    # Prints out all the project environment variables
    # This is useful for debugging and seeing what is being set
    for k, v in config.items():
        # If ENV var starts with PROJECTNAME_ then print
        if k.startswith(config["CORE_PROJECT_VARIABLE_PREFIX"]):
            print(f"{k}={v}")

# %% ../nbs/00_core.ipynb 22
import pandas as pd


def get_samplesheet(sample_sheet_config: dict) -> pd.DataFrame:
    # Load the sample sheet into a pandas dataframe
    # If columns is not None then it will only load those columns
    # If the sample sheet is a csv then it will load it as a csv, otherwise it will assume it's a tsv

    # Expected sample_sheet_config:
    # sample_sheet:
    #   path: path/to/sample_sheet.tsv
    #   delimiter: '\t' # Optional, will assume , for csv and \t otherwises
    #   header: 0 # Optional, 0 indicates first row is header, None indicates no header
    #   columns: ['column1', 'column2', 'column3'] # Optional, if not provided all columns will be used

    # Example sample sheet:
    # #sample_id	file_path	metadata1	metadata2
    # Sample1	/path/to/sample1.fasta	value1	option1
    # Sample2	/path/to/sample2.fasta	value2	option2
    # Sample3	/path/to/sample3.fasta	value3	option1
    # Sample4	/path/to/sample4.fasta	value1	option2
    # Sample5	/path/to/sample5.fasta	value2	option1

    # This function should also handle ensuring the sample sheet is in the correct format, such as ensuring the columns are correct and that the sample names are unique.
    if not os.path.isfile(sample_sheet_config["path"]):
        raise FileNotFoundError(f"File {sample_sheet_config['path']} does not exist")
    if "delimiter" in sample_sheet_config:
        delimiter = sample_sheet_config["delimiter"]
    else:
        # do a best guess based on file extension
        delimiter = "," if sample_sheet_config["path"].endswith(".csv") else "\t"
    header = 0
    # if "header" in sample_sheet_config:
    #     header = sample_sheet_config["header"]
    # else:
    #     # check if the first line starts with a #, if so lets assume it's a header otherwise assume there isn't one
    #     with open(sample_sheet_config["path"], "r") as f:
    #         first_line = f.readline()
    #         header = 0 if first_line.startswith("#") else None
    if "columns" in sample_sheet_config:
        columns = sample_sheet_config[
            "columns"
        ]  # note the # for the first item needs to be stripped to compare to the columns
    else:
        columns = None  # implies all columns
    try:
        # note when we have a header the first column may begin with a #, so we need to remove it
        df = pd.read_csv(
            sample_sheet_config["path"],
            delimiter=delimiter,
            header=header,
            comment=None,
        )
    except Exception as e:
        print(
            "Error: Could not load sample sheet into dataframe, you have a problem with your sample sheet or the configuration."
        )
        raise e

    # Check the first header has a # in it, if so remove it for only that item
    if df.columns[0].startswith("#"):
        df.columns = [col.lstrip("#") for col in df.columns]
    # Ensure the sample sheet has the correct columns
    if columns is not None and not all([col in df.columns for col in columns]):
        raise ValueError("Error: Sample sheet does not have the correct columns")
    # also drop columns which are not needed
    if columns is not None:
        df = df[columns]

    # Clean the df of any extra rows that can be caused by empty lines in the sample sheet
    df = df.dropna(how="all")
    return df

# %% ../nbs/00_core.ipynb 24
def hello_world(name: str = "Not given") -> str:
    return f"Hello World! My name is {name}"

# %% ../nbs/00_core.ipynb 28
from fastcore.script import call_parse


@call_parse
def cli(
    name: str,  # Your name
    config_file: str = None,  # config file to set env vars from
):
    """
    This will print Hello World! with your name
    """
    config = get_config(config_file)  # Set env vars and get config variables
    if name is not None:
        config["example"]["input"]["name"] = name

    print(hello_world(config["example"]["input"]["name"]))

# %% ../nbs/00_core.ipynb 32
import json
import pandas as pd
import json
import yaml
import xml.etree.ElementTree as ET
from xml.dom import minidom

# %% ../nbs/00_core.ipynb 34
class DataFrame:
    def __init__(self, data=None):
        """
        Initialize the DataFrame object.
        :param data: Optional initial data for the DataFrame.
        """
        if data is not None:
            self.df = pd.DataFrame(data)
        else:
            self.df = pd.DataFrame()

# %% ../nbs/00_core.ipynb 36
def import_nested_json_data(self, json_file_path):
    """
    Import nested JSON data from a file and create headers by combining headers with underscores.
    :param json_file_path: Path to the JSON file.
    """

    with open(json_file_path, "r") as file:
        nested_json = json.load(file)

    def flatten_json(y):
        out = {}

        def flatten(x, name=""):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + "£")
            elif type(x) is list:
                i = 1  # Start numbering from 1
                for a in x:
                    flatten(a, name + str(i) + "£")
                    i += 1
            else:
                out[name[:-1]] = x

        flatten(y)
        return out

    if isinstance(nested_json, list):
        flat_data = [flatten_json(item) for item in nested_json]
        self.df = pd.json_normalize(flat_data)
    else:
        flat_data = flatten_json(nested_json)
        self.df = pd.json_normalize(flat_data)


def export_nested_json_data(self, json_file_path):
    """
    Export the DataFrame to a nested JSON file by unraveling headers with underscores.
    :param json_file_path: Path to the JSON file.
    """

    def unflatten_json(flat_dict):
        out = {}

        for key, value in flat_dict.items():
            keys = key.split("£")
            d = out
            for k in keys[:-1]:
                d = d.setdefault(k, {})
            d[keys[-1]] = value
        return out

    nested_json_list = [
        unflatten_json(row) for row in self.df.to_dict(orient="records")
    ]

    def convert_to_list(d):
        for key, value in d.items():
            if isinstance(value, dict):
                if all(k.isdigit() for k in value.keys()):
                    d[key] = [
                        v
                        for k, v in sorted(value.items(), key=lambda item: int(item[0]))
                    ]
                else:
                    convert_to_list(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        convert_to_list(item)

    def has_more_layers(d):
        for key, value in d.items():
            if isinstance(value, dict):
                if any(k.isdigit() for k in value.keys()):
                    return True
                else:
                    if has_more_layers(value):
                        return True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and has_more_layers(item):
                        return True
        return False

    for i, nested_json in enumerate(nested_json_list):
        while has_more_layers(nested_json):
            convert_to_list(nested_json)

        if all(key.split("£")[0].isdigit() for key in nested_json.keys()):
            nested_json_list[i] = [
                nested_json[str(i)] for i in range(1, len(nested_json) + 1)
            ]

    if len(nested_json_list) == 1:
        nested_json_list = nested_json_list[0]

    with open(json_file_path, "w") as file:
        json.dump(nested_json_list, file, indent=4)


DataFrame.import_nested_json_data = import_nested_json_data
DataFrame.export_nested_json_data = export_nested_json_data

# %% ../nbs/00_core.ipynb 38
def import_nested_xml_data(self, xml_file_path):
    """
    Import nested XML data from a file and create headers by combining headers with underscores.
    :param xml_file_path: Path to the XML file.
    """
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    def flatten_xml(element, parent_name=""):
        items = {}
        for child in element:
            child_name = f"{parent_name}{element.tag}_{child.tag}_"
            if len(child):
                items.update(flatten_xml(child, child_name))
            else:
                items[child_name[:-1]] = child.text
        return items

    flat_data = [flatten_xml(child) for child in root]
    self.df = pd.json_normalize(flat_data)


def export_nested_xml_data(self, xml_file_path):
    root = ET.Element("Invetory")
    for _, row in self.df.iterrows():
        tag_created = False
        for col in self.df.columns:
            tags = col.split("_")
            for tag in tags[:-1]:
                # print(tags[:-1])
                if tag_created is False:
                    new_tag = ET.SubElement(root, tag)
                    tag_created = True
                ET.SubElement(new_tag, tags[-1]).text = str(row[col])

    # Convert to string and pretty print using minidom
    xml_str = ET.tostring(root, encoding="utf-8")
    parsed_str = minidom.parseString(xml_str)
    pretty_xml_str = parsed_str.toprettyxml(indent="  ")

    with open(xml_file_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml_str)


DataFrame.import_nested_xml_data = import_nested_xml_data
DataFrame.export_nested_xml_data = export_nested_xml_data

# %% ../nbs/00_core.ipynb 40
def import_data(self, file_path, file_type="csv", add_header=""):
    """
    Import data from a CSV, TSV, JSON, XML, or YAML file.
    :param file_path: Path to the file.
    :param file_type: Type of the file ('csv', 'tsv', 'json', 'xml', 'yaml').
    :param delimiter: Delimiter used in the file (default is comma for CSV).
    """

    # Check if add_header is a string and split it into a list
    if isinstance(add_header, str):
        if len(add_header) > 0:
            add_header = add_header.replace(" ", "").split(",")

    if file_type == "csv":
        self.df = pd.read_csv(
            file_path, delimiter=",", header=None if add_header else 0, index_col=False
        )
        if add_header:
            if len(add_header) != len(self.df.columns):
                raise ValueError(
                    f"Error: Number of new column names ({len(add_header)}) must match the number of columns in the DataFrame ({len(self.df.columns)})."
                )
            else:
                self.df.columns = add_header

    elif file_type == "tsv":
        self.df = pd.read_csv(
            file_path, delimiter="\t", header=None if add_header else 0, index_col=False
        )
        if add_header:
            if len(add_header) != len(self.df.columns):
                raise ValueError(
                    f"Error: Number of new column names ({len(add_header)}) must match the number of columns in the DataFrame ({len(self.df.columns)})."
                )
            else:
                self.df.columns = add_header

    elif file_type == "json":
        self.import_nested_json_data(file_path)
    elif file_type == "yaml":
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
            self.df = pd.json_normalize(data)
    elif file_type == "xml":
        self.import_nested_xml_data(file_path)
    #    tree = ET.parse(file_path)
    #    root = tree.getroot()
    #    data = self._xml_to_dict(root)
    #    self.df = pd.json_normalize(data)
    #    self.df.columns = [col.replace('item.', '') for col in self.df.columns]
    # else:
    #    raise ValueError("Unsupported file type. Supported types: 'csv', 'tsv', 'json', 'xml', 'yaml'.")


def rename_header(self, new_columns):
    """
    Rename columns in the DataFrame.
    :param new_columns: Comma-separated string of new column names.
    """
    new_columns_list = [col.strip() for col in new_columns.split(",")]
    if len(new_columns_list) != len(self.df.columns):
        print(
            "Error: Number of new column names must match the number of columns in the DataFrame."
        )
        print("Current header:", self.df.columns.tolist())
    else:
        self.df.columns = new_columns_list


def filter_columns(self, columns):
    """
    Filter the DataFrame to include only specified columns.
    :param columns: List of columns to include or list of boolean values.
    """
    if all(isinstance(col, str) for col in columns):
        # Case 1: Comma-separated string of column names
        columns_list = [col.strip() for col in columns.split(",")]
        if not all(col in self.df.columns for col in columns_list):
            missing_cols = [col for col in columns_list if col not in self.df.columns]
            raise ValueError(
                f"Error: The following columns do not exist in the DataFrame: {missing_cols}"
            )
        self.df = self.df[columns_list]
    elif all(isinstance(col, bool) for col in columns):
        # Case 2: List of boolean values
        if len(columns) != len(self.df.columns):
            raise ValueError(
                "Error: Number of boolean values must match the number of columns in the DataFrame."
            )
        self.df = self.df.loc[:, columns]
    else:
        raise ValueError(
            "Error: columns parameter must be a list of column names or a list of boolean values."
        )


def filter_rows(self, condition):
    """
    Filter the DataFrame to include only rows that meet the condition.
    :param condition: List of integers (row indices starting with 1) or list of boolean values.
    """
    if all(isinstance(cond, bool) for cond in condition):
        # Case 1: List of boolean values
        if len(condition) != len(self.df):
            raise ValueError(
                "Error: Number of boolean values must match the number of rows in the DataFrame."
            )
        self.df = self.df[condition]
    elif all(isinstance(cond, int) for cond in condition):
        # Case 2: List of integers (row indices starting with 1)
        if any(cond < 1 or cond > len(self.df) for cond in condition):
            raise ValueError(
                "Error: One or more row indices are outside the scope of the DataFrame."
            )
        self.df = self.df.iloc[[cond - 1 for cond in condition]]
    else:
        raise ValueError(
            "Error: condition parameter must be a list of integers or a list of boolean values."
        )
    # Renumber the rows starting from 1
    self.df.index = range(1, len(self.df) + 1)


def export_data(self, file_path, file_type="csv"):
    """
    Export data to a CSV, TSV, JSON, YAML, or XML file.
    :param file_path: Path to the file.
    :param file_type: Type of the file ('csv', 'tsv', 'json', 'yaml', 'xml').
    :param delimiter: Delimiter to use in the file (default is comma for CSV/TSV).
    """
    if file_type == "csv":
        self.df.to_csv(file_path, index=False, sep=",")
    elif file_type == "tsv":
        self.df.to_csv(file_path, index=False, sep="\t")
    elif file_type == "json":
        self.export_nested_json_data(file_path)
    elif file_type == "yaml":
        with open(file_path, "w") as f:
            yaml.dump(self.df.to_dict(orient="records"), f, sort_keys=False)
    elif file_type == "xml":
        self.export_nested_xml_data(file_path)
    else:
        raise ValueError(
            "Unsupported file type. Supported types: 'csv', 'tsv', 'json', 'yaml', 'xml'."
        )


def print_header(self):
    """
    Print the header of the DataFrame as a list.
    """
    print(self.df.columns.tolist())


def show(self):
    """
    Display the DataFrame.
    """
    print(self.df)


DataFrame.import_data = import_data
DataFrame.rename_header = rename_header
DataFrame.filter_columns = filter_columns
DataFrame.filter_rows = filter_rows
DataFrame.export_data = export_data
DataFrame.print_header = print_header
DataFrame.show = show
