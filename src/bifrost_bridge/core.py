import json
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

import pandas as pd
import yaml


def get_samplesheet(sample_sheet_config: dict) -> pd.DataFrame:
    path = Path(sample_sheet_config["path"])
    if not path.is_file():
        raise FileNotFoundError(f"File {path} does not exist")

    delimiter = sample_sheet_config.get("delimiter", "," if path.suffix.lower() == ".csv" else "\t")
    columns = sample_sheet_config.get("columns")

    try:
        df = pd.read_csv(path, delimiter=delimiter, header=0, comment=None)
    except Exception as exc:
        print(
            "Error: Could not load sample sheet into dataframe, you have a problem with your sample sheet or the configuration."
        )
        raise exc

    if str(df.columns[0]).startswith("#"):
        df.columns = [str(col).lstrip("#") for col in df.columns]
    if columns is not None and not all(col in df.columns for col in columns):
        raise ValueError("Error: Sample sheet does not have the correct columns")
    if columns is not None:
        df = df[columns]
    return df.dropna(how="all")


class DataFrame:
    def __init__(self, data=None):
        self.df = pd.DataFrame(data) if data is not None else pd.DataFrame()

    def import_nested_json_data(self, json_file_path: str | Path) -> None:
        with Path(json_file_path).open("r", encoding="utf-8") as file:
            nested_json = json.load(file)

        def flatten_json(obj, prefix=""):
            out = {}
            if isinstance(obj, dict):
                for key, value in obj.items():
                    out.update(flatten_json(value, prefix + key + "£"))
            elif isinstance(obj, list):
                for index, value in enumerate(obj, start=1):
                    out.update(flatten_json(value, prefix + str(index) + "£"))
            else:
                out[prefix[:-1]] = obj
            return out

        if isinstance(nested_json, list):
            self.df = pd.json_normalize([flatten_json(item) for item in nested_json])
        else:
            self.df = pd.json_normalize(flatten_json(nested_json))

    def export_nested_json_data(self, json_file_path: str | Path) -> None:
        def unflatten_json(flat_dict):
            out = {}
            for key, value in flat_dict.items():
                parts = key.split("£")
                cursor = out
                for part in parts[:-1]:
                    cursor = cursor.setdefault(part, {})
                cursor[parts[-1]] = value
            return out

        def convert_to_list(node):
            for key, value in list(node.items()):
                if isinstance(value, dict):
                    if value and all(k.isdigit() for k in value):
                        node[key] = [
                            v for _, v in sorted(value.items(), key=lambda item: int(item[0]))
                        ]
                    else:
                        convert_to_list(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            convert_to_list(item)

        def has_more_layers(node):
            for value in node.values():
                if isinstance(value, dict):
                    if any(k.isdigit() for k in value):
                        return True
                    if has_more_layers(value):
                        return True
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and has_more_layers(item):
                            return True
            return False

        nested_json_list = [unflatten_json(row) for row in self.df.to_dict(orient="records")]
        for index, nested_json in enumerate(nested_json_list):
            while has_more_layers(nested_json):
                convert_to_list(nested_json)
            if nested_json and all(key.split("£")[0].isdigit() for key in nested_json):
                nested_json_list[index] = [
                    nested_json[str(i)] for i in range(1, len(nested_json) + 1)
                ]

        output = nested_json_list[0] if len(nested_json_list) == 1 else nested_json_list
        with Path(json_file_path).open("w", encoding="utf-8") as file:
            json.dump(output, file, indent=4)

    def import_nested_xml_data(self, xml_file_path: str | Path) -> None:
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

        self.df = pd.json_normalize([flatten_xml(child) for child in root])

    def export_nested_xml_data(self, xml_file_path: str | Path) -> None:
        root = ET.Element("Invetory")
        for _, row in self.df.iterrows():
            tag_created = False
            for col in self.df.columns:
                tags = col.split("_")
                for tag in tags[:-1]:
                    if tag_created is False:
                        new_tag = ET.SubElement(root, tag)
                        tag_created = True
                    ET.SubElement(new_tag, tags[-1]).text = str(row[col])

        xml_str = ET.tostring(root, encoding="utf-8")
        pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
        Path(xml_file_path).write_text(pretty_xml_str, encoding="utf-8")

    def import_data(self, file_path: str | Path, file_type: str = "csv", add_header="") -> None:
        path = Path(file_path)
        if isinstance(add_header, str) and add_header:
            add_header = add_header.replace(" ", "").split(",")

        if file_type == "csv":
            self.df = pd.read_csv(
                path, delimiter=",", header=None if add_header else 0, index_col=False
            )
            if len(self.df) == 0:
                self.df = pd.read_csv(path, delimiter=",", header=None)
        elif file_type == "tsv":
            self.df = pd.read_csv(
                path, delimiter="\t", header=None if add_header else 0, index_col=False
            )
            if len(self.df) == 0:
                self.df = pd.read_csv(path, delimiter="\t", header=None)
        elif file_type == "json":
            self.import_nested_json_data(path)
            return
        elif file_type == "yaml":
            with path.open("r", encoding="utf-8") as file:
                self.df = pd.json_normalize(yaml.safe_load(file))
            return
        elif file_type == "xml":
            self.import_nested_xml_data(path)
            return
        else:
            raise ValueError(
                "Unsupported file type. Supported types: 'csv', 'tsv', 'json', 'yaml', 'xml'."
            )

        if add_header:
            if len(add_header) != len(self.df.columns):
                raise ValueError(
                    f"Error: Number of new column names ({len(add_header)}) must match the number of columns in the DataFrame ({len(self.df.columns)})."
                )
            self.df.columns = add_header

    def rename_header(self, new_columns: str) -> None:
        new_columns_list = [col.strip() for col in new_columns.split(",")]
        if len(new_columns_list) != len(self.df.columns):
            print(
                "Error: Number of new column names must match the number of columns in the DataFrame."
            )
            print("Current header:", self.df.columns.tolist())
            return
        self.df.columns = new_columns_list

    def filter_columns(self, columns) -> None:
        if isinstance(columns, str):
            columns_list = [col.strip() for col in columns.split(",")]
            if not all(col in self.df.columns for col in columns_list):
                missing_cols = [col for col in columns_list if col not in self.df.columns]
                raise ValueError(
                    f"Error: The following columns do not exist in the DataFrame: {missing_cols}"
                )
            self.df = self.df[columns_list]
            return
        if all(isinstance(col, bool) for col in columns):
            if len(columns) != len(self.df.columns):
                raise ValueError(
                    "Error: Number of boolean values must match the number of columns in the DataFrame."
                )
            self.df = self.df.loc[:, columns]
            return
        raise ValueError(
            "Error: columns parameter must be a list of column names or a list of boolean values."
        )

    def filter_rows(self, condition) -> None:
        if all(isinstance(cond, bool) for cond in condition):
            if len(condition) != len(self.df):
                raise ValueError(
                    "Error: Number of boolean values must match the number of rows in the DataFrame."
                )
            self.df = self.df[condition]
        elif all(isinstance(cond, int) for cond in condition):
            if any(cond < 1 or cond > len(self.df) for cond in condition):
                raise ValueError(
                    "Error: One or more row indices are outside the scope of the DataFrame."
                )
            self.df = self.df.iloc[[cond - 1 for cond in condition]]
        else:
            raise ValueError(
                "Error: condition parameter must be a list of integers or a list of boolean values."
            )
        self.df.index = range(1, len(self.df) + 1)

    def export_data(self, file_path: str | Path, file_type: str = "csv") -> None:
        path = Path(file_path)
        if file_type == "csv":
            self.df.to_csv(path, index=False, sep=",")
        elif file_type == "tsv":
            self.df.to_csv(path, index=False, sep="\t")
        elif file_type == "json":
            self.export_nested_json_data(path)
        elif file_type == "yaml":
            with path.open("w", encoding="utf-8") as file:
                yaml.dump(self.df.to_dict(orient="records"), file, sort_keys=False)
        elif file_type == "xml":
            self.export_nested_xml_data(path)
        else:
            raise ValueError(
                "Unsupported file type. Supported types: 'csv', 'tsv', 'json', 'yaml', 'xml'."
            )

    def add_column(self, column_name: str, data) -> None:
        if column_name in self.df.columns:
            raise ValueError(f"Error: Column '{column_name}' already exists in the DataFrame.")
        if len(self.df) == 0:
            self.df = pd.DataFrame({column_name: data})
            return
        if len(data) != len(self.df):
            raise ValueError(
                "Error: Length of data must match the number of rows in the DataFrame."
            )
        self.df[column_name] = data

    def print_header(self) -> None:
        print(self.df.columns.tolist())

    def show(self) -> None:
        print(self.df)

    # We choose | as delimiter because it's ASCII and we don't think it's used
    # by any of our outputs.
    # This is a workaround; the long term solution is to output in JSON.
    def collapse_rows(self, delimiter: str = "|") -> "DataFrame":
        str_df = self.df.fillna("").apply(lambda col: col.map(str))

        if str_df.empty:
            return DataFrame(str_df)

        if str_df.apply(lambda col: col.str.contains("|", regex=False)).any().any():
            raise ValueError("Fields contain '|' separator")

        return DataFrame(str_df.agg("|".join).to_frame().T)
