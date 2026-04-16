from pathlib import Path

from bifrost_bridge.cli import build_parser
from bifrost_bridge import core


def process_quast_data(
    input_path: str,
    output_path: str = "./output.tsv",
    add_header: str = "",
    replace_header: str | None = None,
    filter_columns: str | None = None,
    transpose: bool = True,
) -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"The input file {input_path} does not exist.")

    df = core.DataFrame()
    df.import_data(input_file, file_type="tsv")
    if df.df.isna().iloc[0, 0]:
        Path(output_path).write_text("", encoding="utf-8")
        return

    if transpose:
        df.import_data(input_file, file_type="tsv", add_header=["column_names", "values"])
        df_df = df.df.T
        df_df = df_df.rename(columns=df_df.loc["column_names"])
        df_df.drop("column_names", axis=0, inplace=True)
        df.df = df_df
        if add_header:
            add_header_parts = add_header.replace(" ", "").split(",")
            if len(add_header_parts) != len(df.df.columns):
                raise ValueError(
                    f"Error: Number of new column names ({len(add_header_parts)}) must match the number of columns in the DataFrame ({len(df.df.columns)})."
                )
            df.df.columns = add_header_parts
    else:
        df.import_data(input_file, file_type="tsv", add_header=add_header)

    if filter_columns:
        df.filter_columns(filter_columns)
    if replace_header:
        df.rename_header(replace_header)
    df.export_data(output_path, file_type="tsv")


def process_quast_data_from_cli() -> None:
    parser = build_parser(
        "Process QUAST TSV output into a normalized TSV.",
        [
            {"names": ["input_path"], "kwargs": {"help": "Path to the input QUAST TSV file."}},
            {"names": ["--output-path"], "kwargs": {"default": "./output.tsv"}},
            {"names": ["--add-header"], "kwargs": {"default": ""}},
            {"names": ["--replace-header"], "kwargs": {"default": None}},
            {"names": ["--filter-columns"], "kwargs": {"default": None}},
            {"names": ["--no-transpose"], "kwargs": {"action": "store_false", "dest": "transpose"}},
        ],
    )
    args = parser.parse_args()
    process_quast_data(**vars(args))
