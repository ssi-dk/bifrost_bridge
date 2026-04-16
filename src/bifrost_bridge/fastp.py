from __future__ import annotations

from pathlib import Path

from bifrost_bridge.cli import build_parser
from bifrost_bridge import core


def process_fastp_data(
    input_path: str,
    output_path: str = "./output.tsv",
    replace_header: str | None = None,
    filter_columns: str | None = None,
) -> None:
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"The input file {input_path} does not exist.")

    df = core.DataFrame()
    df.import_data(input_file, file_type="json")
    if filter_columns:
        df.filter_columns(filter_columns)
    if replace_header:
        df.rename_header(replace_header)
    df.export_data(output_path, file_type="tsv")


def process_fastp_data_from_cli() -> None:
    parser = build_parser(
        "Process FASTP JSON output into a normalized TSV.",
        [
            {"names": ["input_path"], "kwargs": {"help": "Path to the input FASTP JSON file."}},
            {"names": ["--output-path"], "kwargs": {"default": "./output.tsv"}},
            {"names": ["--replace-header"], "kwargs": {"default": None}},
            {"names": ["--filter-columns"], "kwargs": {"default": None}},
        ],
    )
    args = parser.parse_args()
    process_fastp_data(**vars(args))
