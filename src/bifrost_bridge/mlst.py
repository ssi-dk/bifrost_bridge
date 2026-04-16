from __future__ import annotations

from pathlib import Path

from bifrost_bridge._cli import build_parser
from bifrost_bridge import core


def process_mlst_data(
    input_path: str,
    output_path: str = "./output.tsv",
    add_header: str | None = None,
    replace_header: str | None = None,
    filter_columns: str | None = None,
    remove_sampleid: bool = False,
    combine_alleles: bool = False,
) -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"The input file {input_path} does not exist.")

    df = core.DataFrame()
    df.import_data(input_file, file_type="tsv")

    if df.df.isna().iloc[0, 0]:
        mlst_is_empty = True
    elif df.df.iloc[0, 1] == "-":
        mlst_is_empty = True
    else:
        mlst_is_empty = False

    if combine_alleles and not mlst_is_empty:
        combine_alleles_string = ",".join(df.df.iloc[0, 3:])
        df.df.iloc[0, 3] = str(combine_alleles_string)
        df.df = df.df.iloc[:, :4]

    if add_header:
        header_list = add_header.split(", ")
        if not combine_alleles:
            header_list[3] = header_list[3] + "1"
            for index in range(4, len(df.df.columns)):
                header_list.append(header_list[3][:-1] + str(index - 2))
        if mlst_is_empty:
            while len(header_list) > len(df.df.columns):
                extra_column_name = "extra" + str(len(header_list) - len(df.df.columns))
                df.df.insert(1, extra_column_name, "-")
        df.df.columns = header_list

    if mlst_is_empty:
        for col in df.df.columns[1:]:
            df.df[col] = ""

    if replace_header:
        df.rename_header(replace_header)
    if filter_columns:
        df.filter_columns(filter_columns)
    if remove_sampleid and df.df.columns[0] == "SampleID":
        df.df = df.df.iloc[:, 1:]

    df.export_data(output_path, file_type="tsv")


def process_mlst_data_from_cli() -> None:
    parser = build_parser(
        "Process MLST TSV output into a normalized TSV.",
        [
            {"names": ["input_path"], "kwargs": {"help": "Path to the input MLST TSV file."}},
            {"names": ["--output-path"], "kwargs": {"default": "./output.tsv"}},
            {"names": ["--add-header"], "kwargs": {"default": None}},
            {"names": ["--replace-header"], "kwargs": {"default": None}},
            {"names": ["--filter-columns"], "kwargs": {"default": None}},
            {"names": ["--remove-sampleid"], "kwargs": {"action": "store_true"}},
            {"names": ["--combine-alleles"], "kwargs": {"action": "store_true"}},
        ],
    )
    args = parser.parse_args()
    process_mlst_data(**vars(args))
