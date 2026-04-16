from __future__ import annotations

from pathlib import Path

from bifrost_bridge._cli import build_parser
from bifrost_bridge import core


def process_pmlst_data(
    input_path: str,
    output_path: str = "./output.tsv",
    filter_columns: str | None = None,
    replace_header: str | None = None,
) -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"The input file {input_path} does not exist.")

    df = core.DataFrame()
    df.import_data(input_file, file_type="tsv")
    if df.df.isna().iloc[0, 0]:
        Path(output_path).write_text("", encoding="utf-8")
        return
    if filter_columns:
        df.filter_columns(filter_columns)
    if replace_header:
        df.rename_header(replace_header)
    df.export_data(output_path, file_type="tsv")


def process_pmlst_data_from_cli() -> None:
    parser = build_parser(
        "Process pMLST TSV output into a normalized TSV.",
        [
            {"names": ["input_path"], "kwargs": {"help": "Path to the input pMLST TSV file."}},
            {"names": ["--output-path"], "kwargs": {"default": "./output.tsv"}},
            {"names": ["--filter-columns"], "kwargs": {"default": None}},
            {"names": ["--replace-header"], "kwargs": {"default": None}},
        ],
    )
    args = parser.parse_args()
    process_pmlst_data(**vars(args))
