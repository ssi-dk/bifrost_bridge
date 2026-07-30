from pathlib import Path

from bifrost_bridge.cli import build_parser
from bifrost_bridge import core


def process_amrfinderplus_data(
    input_path: str,
    output_path: str = "./output.tsv",
    replace_header: str | None = None,
    filter_columns: str | None = None,
) -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"The input file {input_path} does not exist.")

    df = core.DataFrame()
    df.import_data(input_file, file_type="tsv")
    if df.df.isna().iloc[0, 0] and len(df.df.columns) == 1:
        Path(output_path).write_text("", encoding="utf-8")
        return
    if df.df.shape[0] == 1 and list(df.df.columns) == list(range(df.df.shape[1])):
        df.df.columns = df.df.iloc[0]
        df.df = df.df.iloc[1:]
    version_column = None
    version_values: list[str] = []
    if filter_columns:
        aliases = {
            "Gene symbol": "Element symbol",
            "Sequence name": "Element name",
            "% Coverage of reference sequence": "% Coverage of reference",
            "% Identity to reference sequence": "% Identity to reference",
        }
        requested_columns = [column.strip() for column in filter_columns.split(",")]
        if "AMR_dbv_toolv" in requested_columns:
            if {"Database version", "Tool version"}.issubset(df.df.columns):
                df.df["AMR_dbv_toolv"] = (
                    df.df["Database version"].fillna("").astype(str)
                    + ","
                    + df.df["Tool version"].fillna("").astype(str)
                )
            else:
                df.df["AMR_dbv_toolv"] = ""
        resolved_columns = [
            aliases.get(column, column) if column not in df.df.columns else column
            for column in requested_columns
        ]
        df.filter_columns(",".join(resolved_columns))
        if "AMR_dbv_toolv" in resolved_columns:
            version_column = resolved_columns.index("AMR_dbv_toolv")
    if replace_header:
        df.rename_header(replace_header)
    if version_column is not None:
        version_column = df.df.columns[version_column]
        version_values = df.df[version_column].dropna().astype(str).drop_duplicates().tolist()
    df = df.collapse_rows()
    if version_column is not None and not df.df.empty:
        df.df = df.df.copy()
        df.df[version_column] = ["|".join(version_values)]
    df.export_data(output_path, file_type="tsv")


def process_amrfinderplus_data_from_cli() -> None:
    parser = build_parser(
        "Process AMRFinderPlus TSV output into a normalized TSV.",
        [
            {
                "names": ["input_path"],
                "kwargs": {"help": "Path to the input AMRFinderPlus TSV file."},
            },
            {"names": ["--output_path"], "kwargs": {"default": "./output.tsv"}},
            {"names": ["--replace_header"], "kwargs": {"default": None}},
            {"names": ["--filter_columns"], "kwargs": {"default": None}},
        ],
    )
    args = parser.parse_args()
    process_amrfinderplus_data(**vars(args))
